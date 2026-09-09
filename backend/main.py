import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.indexing_service import IndexingService
from services.hybrid_retrieval_service import HybridRetrievalService
from services.answer_service import AnswerService


# ----------------------------------
# Create FastAPI application
# ----------------------------------

app = FastAPI(
    title="Supplier Graph RAG API",
    description=(
        "API for uploading supplier policy PDFs "
        "and asking questions using FAISS + Graph RAG."
    ),
    version="1.0.0"
)


# ----------------------------------
# CORS
# ----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ----------------------------------
# Data directory
# ----------------------------------

DATA_DIRECTORY = "data"

os.makedirs(
    DATA_DIRECTORY,
    exist_ok=True
)


# ----------------------------------
# Services
# ----------------------------------

indexing_service = IndexingService()

answer_service = AnswerService()


# ----------------------------------
# Health check
# ----------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "application": "Supplier Graph RAG"
    }


# ----------------------------------
# Upload PDF
# ----------------------------------

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # Check file type

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


    # Create file path

    file_path = os.path.join(
        DATA_DIRECTORY,
        file.filename
    )


    # Save uploaded file

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    try:

        # ----------------------------------
        # Index document
        # ----------------------------------

        indexing_result = (
            indexing_service.index_pdf(
                file_path
            )
        )


        # ----------------------------------
        # Handle duplicate document
        # ----------------------------------

        if indexing_result.get("status") == "already_indexed":

            return {
                "message": (
                    "This document has already "
                    "been indexed."
                ),
                "filename": file.filename,
                "status": "already_indexed",
                "pages": None,
                "chunks": None,
                "graph_nodes": (
                    indexing_service
                    .graph_store
                    .graph
                    .number_of_nodes()
                ),
                "graph_edges": (
                    indexing_service
                    .graph_store
                    .graph
                    .number_of_edges()
                )
            }


        # ----------------------------------
        # Handle newly indexed document
        # ----------------------------------

        return {
            "message": (
                "PDF uploaded and indexed "
                "successfully."
            ),
            "filename": file.filename,
            "status": indexing_result.get(
                "status"
            ),
            "pages": indexing_result.get(
                "pages"
            ),
            "chunks": indexing_result.get(
                "chunks"
            ),
            "graph_nodes": (
                indexing_service
                .graph_store
                .graph
                .number_of_nodes()
            ),
            "graph_edges": (
                indexing_service
                .graph_store
                .graph
                .number_of_edges()
            )
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ----------------------------------
# Ask question
# ----------------------------------

@app.post("/ask")
async def ask_question(
    question: str
):

    # Check question

    if not question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    # Check whether documents exist

    if (
        indexing_service
        .vector_store
        .index
        .ntotal == 0
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "No document has been indexed yet. "
                "Please upload a PDF first."
            )
        )


    try:

        # ----------------------------------
        # Hybrid retrieval
        # ----------------------------------

        retrieval_service = (
            HybridRetrievalService(
                indexing_service.vector_store,
                indexing_service.graph_store
            )
        )


        retrieval_result = (
            retrieval_service.retrieve(
                question
            )
        )


        # ----------------------------------
        # Generate answer
        # ----------------------------------

        answer_result = (
            answer_service.generate_answer(
                question,
                retrieval_result[
                    "vector_results"
                ],
                retrieval_result[
                    "graph_results"
                ]
            )
        )


        return answer_result


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
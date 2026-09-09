import os

from services.pdf_service import extract_pdf_pages
from services.chunk_service import chunk_text
from services.embedding_service import create_embedding
from services.graph_service import GraphStore
from database.vector_store import VectorStore
from services.entity_service import EntityService
from services.relationship_service import RelationshipService
from database.document_store import DocumentStore


class IndexingService:

    def __init__(self):

        self.vector_store = VectorStore()
        self.graph_store = GraphStore()
        self.entity_service = EntityService()
        self.relationship_service = RelationshipService()
        self.document_store = DocumentStore()


    def index_pdf(self, pdf_path: str):

        # ----------------------------------
        # Step 1: Check for duplicate document
        # ----------------------------------

        if self.document_store.is_indexed(pdf_path):

            return {
                "status": "already_indexed",
                "message": (
                    "This document has already been indexed."
                )
            }


        # ----------------------------------
        # Step 2: Get document name
        # ----------------------------------

        document_name = os.path.basename(pdf_path)


        # ----------------------------------
        # Step 3: Extract pages from PDF
        # ----------------------------------

        pages = extract_pdf_pages(pdf_path)

        total_chunks = 0
        previous_chunk_id = None


        # ----------------------------------
        # Step 4: Process each page
        # ----------------------------------

        for page in pages:

            page_number = page["page"]
            page_text = page["text"]


            # ----------------------------------
            # Step 5: Split page into chunks
            # ----------------------------------

            chunks = chunk_text(page_text)


            # ----------------------------------
            # Step 6: Process each chunk
            # ----------------------------------

            for chunk_number, chunk in enumerate(chunks):

                total_chunks += 1


                # ----------------------------------
                # Step 7: Create unique chunk ID
                # ----------------------------------

                chunk_id = (
                    f"{document_name}_"
                    f"page_{page_number}_"
                    f"chunk_{chunk_number}"
                )


                # ----------------------------------
                # Step 8: Create embedding
                # ----------------------------------

                embedding = create_embedding(chunk)


                # ----------------------------------
                # Step 9: Create metadata
                # ----------------------------------

                metadata = {
                    "document": document_name,
                    "chunk_id": chunk_id,
                    "page": page_number,
                    "text": chunk
                }


                # ----------------------------------
                # Step 10: Store vector in FAISS
                # ----------------------------------

                self.vector_store.add(
                    embedding,
                    metadata
                )


                # ----------------------------------
                # Step 11: Add chunk to Graph
                # ----------------------------------

                self.graph_store.add_chunk(
                    chunk_id=chunk_id,
                    text=chunk,
                    page=page_number
                )


                # ----------------------------------
                # Step 12: Extract entities
                # ----------------------------------

                entities = self.entity_service.extract_entities(
                    chunk
                )


                # ----------------------------------
                # Step 13: Add entities and
                # "mentions" relationships
                # ----------------------------------

                for entity in entities:

                    entity_id = (
                        entity["type"]
                        + "_"
                        + entity["name"]
                        .lower()
                        .replace(" ", "_")
                    )


                    # Add entity as graph node
                    self.graph_store.add_entity(
                        entity_id=entity_id,
                        name=entity["name"],
                        entity_type=entity["type"]
                    )


                    # Connect chunk to entity
                    self.graph_store.add_relationship(
                        chunk_id,
                        entity_id,
                        "mentions"
                    )


                # ----------------------------------
                # Step 14: Extract meaningful
                # relationships
                # ----------------------------------

                relationships = (
                    self.relationship_service
                    .extract_relationships(chunk)
                )


                # ----------------------------------
                # Step 15: Add meaningful
                # relationships to graph
                # ----------------------------------

                for rel in relationships:


                    # Create source entity ID
                    source_id = (
                        rel["source_type"]
                        + "_"
                        + rel["source"]
                        .lower()
                        .replace(" ", "_")
                    )


                    # Create target entity ID
                    target_id = (
                        rel["target_type"]
                        + "_"
                        + rel["target"]
                        .lower()
                        .replace(" ", "_")
                    )


                    # Ensure source entity exists
                    self.graph_store.add_entity(
                        entity_id=source_id,
                        name=rel["source"],
                        entity_type=rel["source_type"]
                    )


                    # Ensure target entity exists
                    self.graph_store.add_entity(
                        entity_id=target_id,
                        name=rel["target"],
                        entity_type=rel["target_type"]
                    )


                    # Add meaningful relationship
                    self.graph_store.add_relationship(
                        source_id,
                        target_id,
                        rel["relationship"]
                    )


                # ----------------------------------
                # Step 16: Connect with previous chunk
                # ----------------------------------

                if previous_chunk_id:

                    self.graph_store.add_relationship(
                        previous_chunk_id,
                        chunk_id,
                        "next_chunk"
                    )


                # ----------------------------------
                # Step 17: Save current chunk ID
                # ----------------------------------

                previous_chunk_id = chunk_id


        # ----------------------------------
        # Step 18: Save vector store
        # ----------------------------------

        self.vector_store.save()


        # ----------------------------------
        # Step 19: Save knowledge graph
        # ----------------------------------

        self.graph_store.save()


        # ----------------------------------
        # Step 20: Register indexed document
        # ----------------------------------

        self.document_store.add_document(
            file_path=pdf_path,
            pages=len(pages),
            chunks=total_chunks
        )


        # ----------------------------------
        # Step 21: Return indexing result
        # ----------------------------------

        return {
            "status": "indexed",
            "document": document_name,
            "pages": len(pages),
            "chunks": total_chunks
        }
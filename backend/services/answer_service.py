from openai import OpenAI


class AnswerService:

    def __init__(self):
        self.client = OpenAI()

    def generate_answer(
        self,
        question: str,
        vector_results: list,
        graph_results: list
    ):
        """
        Generate a grounded answer using:

        1. Retrieved document chunks from FAISS
        2. Retrieved relationships from the knowledge graph
        """

        # ----------------------------------
        # Step 1: Build document context
        # ----------------------------------

        document_context = ""

        for result in vector_results:

            metadata = result["metadata"]

            document = metadata.get("document")
            page = metadata.get("page")
            chunk_id = metadata.get("chunk_id")
            text = metadata.get("text")

            document_context += (
                f"\n--- Document: {document} | "
                f"Page: {page} | "
                f"Chunk: {chunk_id} ---\n"
                f"{text}\n"
            )

        # ----------------------------------
        # Step 2: Build graph context
        # ----------------------------------

        graph_context = ""

        for result in graph_results:

            graph_context += (
                f"{result['source']} "
                f"-- {result['relationship']} --> "
                f"{result['target']}\n"
            )

        # ----------------------------------
        # Step 3: Build prompt
        # ----------------------------------

        prompt = f"""
You are a helpful assistant answering questions about supplier policies.

Answer the user's question using ONLY the provided document
context and graph context.

Important rules:

1. Do not make up information.
2. Use only the supplied context.
3. If the answer cannot be found in the supplied context, say:
   "I could not find the answer in the supplier policy."
4. When useful, mention the relevant document and page.
5. Do not use outside knowledge.

DOCUMENT CONTEXT:

{document_context}


GRAPH CONTEXT:

{graph_context}


USER QUESTION:

{question}
"""

        # ----------------------------------
        # Step 4: Call the LLM
        # ----------------------------------

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions accurately using only "
                        "the supplied document and graph context."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # ----------------------------------
        # Step 5: Extract answer
        # ----------------------------------

        answer = response.choices[0].message.content

        # ----------------------------------
        # Step 6: Build source information
        # ----------------------------------

        sources = []

        for result in vector_results:

            metadata = result["metadata"]

            source = {
                "document": metadata.get("document"),
                "page": metadata.get("page"),
                "chunk_id": metadata.get("chunk_id"),
                "distance": result.get("distance")
            }

            sources.append(source)

        # ----------------------------------
        # Step 7: Identify primary source
        # ----------------------------------

        primary_source = (
            sources[0]
            if sources
            else None
        )

        # ----------------------------------
        # Step 8: Identify supporting sources
        # ----------------------------------

        supporting_sources = (
            sources[1:]
            if len(sources) > 1
            else []
        )

        # ----------------------------------
        # Step 9: Return final response
        # ----------------------------------

        return {
            "answer": answer,
            "primary_source": primary_source,
            "supporting_sources": supporting_sources,
            "graph_results": graph_results
        }
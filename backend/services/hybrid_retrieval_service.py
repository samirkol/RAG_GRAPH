from services.embedding_service import create_embedding
from services.graph_retrieval_service import GraphRetrievalService
from services.semantic_entity_service import SemanticEntityService


class HybridRetrievalService:

    def __init__(
        self,
        vector_store,
        graph_store
    ):
        self.vector_store = vector_store
        self.graph_store = graph_store

        self.graph_retrieval_service = (
            GraphRetrievalService()
        )

        self.semantic_entity_service = (
            SemanticEntityService()
        )

    # ----------------------------------
    # Normalize text for entity matching
    # ----------------------------------

    def normalize_text(self, text: str):
        """
        Normalize text so simple variations can match.

        Examples:

            "Non-Compliant Invoices"
                -> "non compliant invoice"

            "Selected Suppliers"
                -> "selected supplier"
        """

        text = text.lower().strip()

        # Treat hyphens as spaces
        text = text.replace("-", " ")

        # Normalize repeated spaces
        text = " ".join(text.split())

        # Simple singularization for common words
        words = text.split()

        normalized_words = []

        for word in words:

            if word.endswith("ies") and len(word) > 3:

                word = word[:-3] + "y"

            elif (
                word.endswith("s")
                and not word.endswith("ss")
                and len(word) > 3
            ):

                word = word[:-1]

            normalized_words.append(word)

        return " ".join(normalized_words)

    # ----------------------------------
    # Find exact / normalized entities
    # ----------------------------------

    def find_exact_entities(
        self,
        question: str
    ):
        """
        Find graph entities appearing in the question
        after normalization.

        More specific entity names are preferred.

        Example:

            "non-compliant invoices"

        can match:

            Invoice
            Non-Compliant Invoice

        The more specific entity is preferred.
        """

        normalized_question = self.normalize_text(
            question
        )

        matches = []

        for node_id, node_data in (
            self.graph_store.graph.nodes(data=True)
        ):

            entity_name = node_data.get("name")

            if not entity_name:
                continue

            normalized_entity = self.normalize_text(
                entity_name
            )

            if normalized_entity in normalized_question:

                matches.append({
                    "entity_id": node_id,
                    "entity_name": entity_name,
                    "entity_type": node_data.get(
                        "type"
                    ),
                    "match_type": "normalized_exact",
                    "specificity": len(
                        normalized_entity.split()
                    )
                })

        # Most specific entity first
        matches.sort(
            key=lambda item: item["specificity"],
            reverse=True
        )

        return matches

    # ----------------------------------
    # Main hybrid retrieval
    # ----------------------------------

    def retrieve(
        self,
        question: str,
        top_k: int = 3
    ):
        """
        Perform hybrid retrieval using:

        1. Vector similarity search
        2. Exact entity matching
        3. Semantic entity matching fallback
        4. Graph traversal

        Exact entity matches have priority over
        semantic matching.
        """

        # ----------------------------------
        # Step 1: Vector retrieval
        # ----------------------------------

        question_embedding = create_embedding(
            question
        )

        vector_results = self.vector_store.search(
            question_embedding,
            top_k=top_k
        )

        # ----------------------------------
        # Step 2: Exact / normalized entity matching
        # ----------------------------------

        exact_entities = (
            self.find_exact_entities(
                question
            )
        )

        # ----------------------------------
        # Step 3: Choose graph entities
        # ----------------------------------

        if exact_entities:

            # Use only the most specific entity.
            #
            # Example:
            #
            # Invoice
            # Non-Compliant Invoice
            #
            # We prefer:
            #
            # Non-Compliant Invoice

            graph_entities = [
                exact_entities[0]
            ]

        else:

            # ----------------------------------
            # Semantic fallback
            # ----------------------------------

            semantic_entities = (
                self.semantic_entity_service
                .find_similar_entities(
                    question,
                    self.graph_store.graph,
                    top_k=1
                )
            )

            graph_entities = semantic_entities

        # ----------------------------------
        # Step 4: Graph retrieval
        # ----------------------------------

        graph_results = []

        # Only meaningful business relationships
        # should be returned to the LLM.

        allowed_relationships = {
            "may_apply_to",
            "requires_approval",
            "may_be_placed_on_hold",
            "requires"
        }

        for entity in graph_entities:

            entity_name = entity[
                "entity_name"
            ]

            # ----------------------------------
            # Forward relationships
            # ----------------------------------

            forward_results = (
                self.graph_retrieval_service
                .get_related_entities(
                    self.graph_store.graph,
                    entity_name
                )
            )

            # ----------------------------------
            # Reverse relationships
            # ----------------------------------

            reverse_results = (
                self.graph_retrieval_service
                .get_related_entities_reverse(
                    self.graph_store.graph,
                    entity_name
                )
            )

            # ----------------------------------
            # Keep business relationships only
            # ----------------------------------

            for result in (
                forward_results
                + reverse_results
            ):

                if (
                    result["relationship"]
                    in allowed_relationships
                ):

                    graph_results.append(
                        result
                    )

        # ----------------------------------
        # Step 5: Remove duplicate relationships
        # ----------------------------------

        unique_results = []

        seen = set()

        for result in graph_results:

            key = (
                result["source"],
                result["relationship"],
                result["target"]
            )

            if key not in seen:

                seen.add(key)

                unique_results.append(
                    result
                )

        # ----------------------------------
        # Step 6: Return hybrid results
        # ----------------------------------

        return {
            "vector_results": vector_results,
            "graph_results": unique_results
        }
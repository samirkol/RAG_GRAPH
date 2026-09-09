from services.embedding_service import create_embedding
from services.entity_embedding_store import EntityEmbeddingStore


class SemanticEntityService:

    def __init__(self):
        self.embedding_store = EntityEmbeddingStore()

    def _build_entity_description(
        self,
        graph,
        node_id,
        node_data
    ):
        entity_name = node_data.get(
            "name",
            node_id
        )

        entity_type = node_data.get(
            "type",
            "entity"
        )

        description = (
            f"{entity_name} is a {entity_type}."
        )

        relationships = []

        # Outgoing relationships
        for neighbor_id in graph.successors(node_id):

            edge_data = graph.edges[
                node_id,
                neighbor_id
            ]

            neighbor_data = graph.nodes[
                neighbor_id
            ]

            neighbor_name = neighbor_data.get(
                "name",
                neighbor_id
            )

            relationship = edge_data.get(
                "relationship",
                "related_to"
            )

            relationships.append(
                f"It {relationship} {neighbor_name}."
            )

        # Incoming relationships
        for neighbor_id in graph.predecessors(node_id):

            edge_data = graph.edges[
                neighbor_id,
                node_id
            ]

            neighbor_data = graph.nodes[
                neighbor_id
            ]

            neighbor_name = neighbor_data.get(
                "name",
                neighbor_id
            )

            relationship = edge_data.get(
                "relationship",
                "related_to"
            )

            relationships.append(
                f"{neighbor_name} {relationship} this entity."
            )

        if relationships:
            description += " " + " ".join(
                relationships
            )

        return description

    def build_embeddings(self, graph):
        """
        Create and persist embeddings for graph entities
        that do not already have stored embeddings.
        """

        updated = False

        for node_id, node_data in graph.nodes(
            data=True
        ):

            entity_name = node_data.get("name")

            if not entity_name:
                continue

            # Do not recreate existing embeddings
            if self.embedding_store.get(node_id):
                continue

            description = self._build_entity_description(
                graph,
                node_id,
                node_data
            )

            embedding = create_embedding(
                description
            )

            self.embedding_store.add(
                entity_id=node_id,
                entity_name=entity_name,
                entity_type=node_data.get(
                    "type",
                    "entity"
                ),
                description=description,
                embedding=embedding
            )

            updated = True

        if updated:
            self.embedding_store.save()

    def find_similar_entities(
        self,
        question: str,
        graph,
        top_k: int = 5
    ):
        """
        Search stored graph entity embeddings.

        Only the question is embedded at query time.
        Entity embeddings are reused from storage.
        """

        # Create missing entity embeddings if necessary
        self.build_embeddings(graph)

        # Embed the user's question
        question_embedding = create_embedding(
            question
        )

        # Search locally against stored embeddings
        return self.embedding_store.search(
            question_embedding,
            top_k=top_k
        )
import os
import json
import networkx as nx


class GraphStore:

    def __init__(self):

        # Storage path
        self.graph_path = "storage/knowledge_graph.json"

        # Create storage folder if it does not exist
        os.makedirs("storage", exist_ok=True)

        # Load existing graph if available
        if os.path.exists(self.graph_path):

            with open(
                self.graph_path,
                "r",
                encoding="utf-8"
            ) as file:

                graph_data = json.load(file)

            self.graph = nx.node_link_graph(
                graph_data,
                directed=True
            )

        else:

            # Create a new directed graph
            self.graph = nx.DiGraph()


    def add_chunk(
        self,
        chunk_id: str,
        text: str,
        page: int
    ):
        """
        Add a document chunk as a node in the graph.
        """

        self.graph.add_node(
            chunk_id,
            type="chunk",
            text=text,
            page=page
        )


    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str
    ):
        """
        Add an entity as a node in the graph.
        """

        self.graph.add_node(
            entity_id,
            type=entity_type,
            name=name
        )


    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: str
    ):
        """
        Create a relationship between two nodes.
        """

        self.graph.add_edge(
            source_id,
            target_id,
            relationship=relationship
        )


    def get_neighbors(self, chunk_id: str):
        """
        Return all directly connected nodes.
        """

        if chunk_id not in self.graph:
            return []

        neighbors = []

        for neighbor_id in self.graph.neighbors(chunk_id):

            node_data = self.graph.nodes[neighbor_id]

            neighbors.append({
                "id": neighbor_id,
                "type": node_data.get("type"),
                "text": node_data.get("text"),
                "page": node_data.get("page"),
                "relationship": self.graph.edges[
                    chunk_id,
                    neighbor_id
                ].get("relationship")
            })

        return neighbors


    def save(self):
        """
        Persist the knowledge graph to disk.
        """

        graph_data = nx.node_link_data(
            self.graph
        )

        with open(
            self.graph_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                graph_data,
                file,
                indent=4
            )
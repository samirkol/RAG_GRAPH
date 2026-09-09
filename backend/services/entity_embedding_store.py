import json
import os

import numpy as np


class EntityEmbeddingStore:

    def __init__(self):
        self.storage_path = (
            "storage/entity_embeddings.json"
        )

        os.makedirs(
            "storage",
            exist_ok=True
        )

        self.embeddings = {}

        self.load()

    def load(self):
        """
        Load saved entity embeddings from disk.
        """

        if not os.path.exists(
            self.storage_path
        ):
            self.embeddings = {}
            return

        with open(
            self.storage_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.embeddings = json.load(file)

    def save(self):
        """
        Persist entity embeddings to disk.
        """

        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.embeddings,
                file,
                indent=4
            )

    def add(
        self,
        entity_id: str,
        entity_name: str,
        entity_type: str,
        description: str,
        embedding: list
    ):
        """
        Store one entity embedding.
        """

        self.embeddings[entity_id] = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "description": description,
            "embedding": embedding
        }

    def get(self, entity_id: str):
        """
        Get one stored entity embedding.
        """

        return self.embeddings.get(
            entity_id
        )

    def search(
        self,
        query_embedding: list,
        top_k: int = 5
    ):
        """
        Compare a query embedding against
        all stored entity embeddings using
        cosine similarity.
        """

        query_vector = np.array(
            query_embedding,
            dtype="float32"
        )

        query_norm = np.linalg.norm(
            query_vector
        )

        if query_norm == 0:
            return []

        results = []

        for entity_id, data in (
            self.embeddings.items()
        ):

            entity_vector = np.array(
                data["embedding"],
                dtype="float32"
            )

            entity_norm = np.linalg.norm(
                entity_vector
            )

            if entity_norm == 0:
                continue

            similarity = float(
                np.dot(
                    query_vector,
                    entity_vector
                )
                / (
                    query_norm
                    * entity_norm
                )
            )

            results.append({
                "entity_id": entity_id,
                "entity_name": data[
                    "entity_name"
                ],
                "entity_type": data[
                    "entity_type"
                ],
                "description": data[
                    "description"
                ],
                "similarity": similarity
            })

        results.sort(
            key=lambda item: item[
                "similarity"
            ],
            reverse=True
        )

        return results[:top_k]
import os
import json

import faiss
import numpy as np


class VectorStore:

    def __init__(self, dimension: int = 1536):

        self.dimension = dimension

        # Storage paths
        self.index_path = "storage/vector_index.faiss"
        self.metadata_path = "storage/vector_metadata.json"

        # Create storage folder if it does not exist
        os.makedirs("storage", exist_ok=True)

        # Load existing FAISS index if available
        if os.path.exists(self.index_path):

            self.index = faiss.read_index(
                self.index_path
            )

        else:

            # Create new FAISS index
            self.index = faiss.IndexFlatL2(
                dimension
            )


        # Load existing metadata if available
        if os.path.exists(self.metadata_path):

            with open(
                self.metadata_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.metadata = json.load(file)

        else:

            self.metadata = []


    def add(self, embedding, metadata):

        """
        Add one embedding vector and its metadata.
        """

        vector = np.array(
            [embedding],
            dtype="float32"
        )

        self.index.add(vector)

        self.metadata.append(metadata)


    def search(self, embedding, top_k: int = 5):

        """
        Search for the most similar vectors.
        """

        vector = np.array(
            [embedding],
            dtype="float32"
        )

        distances, indices = self.index.search(
            vector,
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index != -1:

                results.append({
                    "distance": float(distance),
                    "metadata": self.metadata[index]
                })

        return results


    def save(self):

        """
        Persist FAISS index and metadata to disk.
        """

        # Save FAISS vector index
        faiss.write_index(
            self.index,
            self.index_path
        )

        # Save metadata
        with open(
            self.metadata_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.metadata,
                file,
                indent=4
            )
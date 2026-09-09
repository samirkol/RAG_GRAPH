import os
import json
import hashlib
from datetime import datetime


class DocumentStore:

    def __init__(self):

        self.storage_path = "storage/documents.json"

        # Ensure storage directory exists
        os.makedirs("storage", exist_ok=True)

        # Load existing registry
        if os.path.exists(self.storage_path):

            with open(
                self.storage_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.documents = json.load(file)

        else:

            self.documents = {
                "documents": {}
            }


    def get_file_hash(self, file_path: str):
        """
        Create SHA-256 hash for a file.
        """

        sha256 = hashlib.sha256()

        with open(file_path, "rb") as file:

            while True:

                data = file.read(8192)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()


    def is_indexed(self, file_path: str):
        """
        Check whether the same document has already
        been indexed.
        """

        file_hash = self.get_file_hash(file_path)

        return file_hash in self.documents["documents"]


    def add_document(
        self,
        file_path: str,
        pages: int,
        chunks: int
    ):
        """
        Add indexed document information to registry.
        """

        file_hash = self.get_file_hash(file_path)

        self.documents["documents"][file_hash] = {
            "file_name": os.path.basename(file_path),
            "pages": pages,
            "chunks": chunks,
            "indexed_at": datetime.now().isoformat()
        }

        self.save()


    def save(self):
        """
        Save document registry to disk.
        """

        with open(
            self.storage_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.documents,
                file,
                indent=4
            )
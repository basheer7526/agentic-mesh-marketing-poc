from typing import Dict, List

import faiss
import numpy as np

from app.tools.embedding_tool import embedding_tool


class VectorStore:
    """
    Simple FAISS-based semantic vector store.
    """

    def __init__(self) -> None:

        self.index = None
        self.documents: List[Dict[str, str]] = []

    def build(
        self,
        documents: List[Dict[str, str]],
    ) -> None:

        if not documents:
            self.index = None
            self.documents = []
            return

        texts = [
            document["content"]
            for document in documents
        ]

        embeddings = embedding_tool.embed_documents(
            texts
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

        self.documents = documents

        print(
            f"[VECTOR STORE] Indexed "
            f"{len(documents)} documents"
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict]:

        if self.index is None:
            return []

        query_embedding = embedding_tool.embed_query(
            query
        )

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.documents)),
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            document = self.documents[index].copy()

            document["score"] = float(score)

            results.append(document)

        return results
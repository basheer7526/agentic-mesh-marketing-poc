from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingTool:
    """
    Converts text into semantic vector embeddings.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:

        print(
            f"[EMBEDDING] Loading model: {model_name}"
        )

        self.model = SentenceTransformer(
            model_name
        )

    def embed_documents(
        self,
        documents: List[str],
    ):

        if not documents:
            return []

        return self.model.encode(
            documents,
            normalize_embeddings=True,
        )

    def embed_query(self, query: str):

        return self.model.encode(
            [query],
            normalize_embeddings=True,
        )[0]


embedding_tool = EmbeddingTool()
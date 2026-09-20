from pathlib import Path
from typing import Dict, List

from app.config.settings import settings
from app.tools.vector_store import VectorStore


class RAGTool:
    """
    Retrieves relevant knowledge-base documents
    using semantic vector search.
    """

    def __init__(self) -> None:
        self.base_path = Path(
            settings.KNOWLEDGE_BASE_PATH
        )

        self.vector_store = VectorStore()

        self._initialize_vector_store()

    def load_documents(self) -> List[Dict[str, str]]:
        documents = []

        if not self.base_path.exists():
            return documents

        for file_path in self.base_path.glob("*.md"):

            try:
                content = file_path.read_text(
                    encoding="utf-8"
                )

                documents.append(
                    {
                        "source": file_path.name,
                        "content": content,
                    }
                )

            except OSError as exc:

                print(
                    f"[RAG ERROR] Could not read "
                    f"{file_path}: {exc}"
                )

        return documents

    def _initialize_vector_store(self) -> None:
        """
        Load the knowledge base and build the
        FAISS vector index.
        """

        documents = self.load_documents()

        if not documents:

            print(
                "[RAG] No knowledge-base documents found."
            )

            return

        self.vector_store.build(
            documents
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict]:

        if not query.strip():
            return []

        return self.vector_store.search(
            query=query,
            top_k=top_k,
        )


rag_tool = RAGTool()
from app.tools.rag_tool import rag_tool
from app.tools.vector_store import VectorStore


def main():

    print("\n===== VECTOR STORE TEST =====\n")

    documents = rag_tool.load_documents()

    print(
        f"Knowledge base documents: "
        f"{len(documents)}"
    )

    vector_store = VectorStore()

    vector_store.build(documents)

    query = (
        "How can intelligent technology "
        "help increase customer growth?"
    )

    print(f"\nQuery:\n{query}\n")

    results = vector_store.search(
        query=query,
        top_k=3,
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print("=" * 80)
        print(f"RESULT {index}")
        print("=" * 80)

        print(
            f"Source : {result['source']}"
        )

        print(
            f"Score  : {result['score']:.4f}"
        )

        print(
            f"\nContent:\n"
            f"{result['content'][:500]}"
        )

        print()


if __name__ == "__main__":
    main()
    
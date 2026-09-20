from app.tools.rag_tool import rag_tool


def main():

    print("\n===== RAG RETRIEVAL TEST =====\n")

    query = """
    AI marketing personalization customer acquisition
    """

    results = rag_tool.retrieve(
        query=query,
        top_k=3,
    )

    print(f"Query: {query.strip()}")
    print(f"Documents retrieved: {len(results)}\n")

    for index, result in enumerate(results, start=1):

        print("=" * 80)
        print(f"RESULT {index}")
        print("=" * 80)

        print(f"Source: {result['source']}")
        print(f"Score : {result['score']}")

        print("\nContent:")
        print(result["content"][:1000])
        print()


if __name__ == "__main__":
    main()
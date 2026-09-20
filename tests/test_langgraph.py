from app.orchestration.graph import (
    marketing_graph,
)


def main():

    print(
        "\n===== LANGGRAPH FULL WORKFLOW TEST =====\n"
        "(Research > Dedup > Relevance > Analysis "
        "> RAG > Priority > Digest > Notification)\n"
    )

    initial_state = {
        "task": (
            "Collect the latest marketing news "
            "for further relevance analysis."
        ),
        "workflow_id": "test-workflow-001",

        "articles": [],
        "unique_articles": [],
        "research_results": [],
        "relevance_results": [],
        "relevant_articles": [],
        "analysis_results": [],
        "rag_context": [],
        "priority_results": [],
        "digest": {},
        "errors": [],
        "execution_metadata": {
            # Limit to 5 articles to keep the test fast
            # while still exercising the full pipeline.
            "max_articles": 5,
        },
    }

    result = marketing_graph.invoke(initial_state)

    print(
        "\n===== FINAL STATE ====="
    )

    print(
        "Current Agent:",
        result.get("current_agent"),
    )

    print(
        "Current Step:",
        result.get("current_step"),
    )

    print(
        "Articles:",
        len(result.get("articles", [])),
    )

    print(
        "Unique Articles:",
        len(result.get("unique_articles", [])),
    )

    print(
        "Duplicates Removed:",
        len(result.get("articles", []))
        - len(result.get("unique_articles", [])),
    )

    print(
        "Research Results:",
        result.get("research_results"),
    )

    print(
        "Relevance Results:",
        len(result.get("relevance_results", [])),
    )

    print(
        "Relevant Articles:",
        len(result.get("relevant_articles", [])),
    )

    print(
        "Analysis Results:",
        len(result.get("analysis_results", [])),
    )

    print(
        "RAG Context:",
        len(result.get("rag_context", [])),
    )

    print(
        "Priority Results:",
        len(result.get("priority_results", [])),
    )

    digest = result.get("digest", {})

    print(
        "Digest Items:",
        len(digest.get("items", [])) if digest else 0,
    )

    print(
        "Digest High Priority:",
        digest.get("high_priority", 0) if digest else 0,
    )

    print(
        "Digest Medium Priority:",
        digest.get("medium_priority", 0) if digest else 0,
    )

    print(
        "Digest Low Priority:",
        digest.get("low_priority", 0) if digest else 0,
    )

    print(
        "Errors:",
        result.get("errors"),
    )


if __name__ == "__main__":
    main()
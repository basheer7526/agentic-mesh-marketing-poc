from app.tools.rss_tool import rss_tool
from app.tools.deduplication_tool import deduplication_tool
from app.agents.relevance_agent import relevance_agent


def main():

    print("\n===== REAL ARTICLE RELEVANCE TEST =====\n")

    articles = rss_tool.fetch_all()

    unique_articles = deduplication_tool.deduplicate(
        articles
    )

    print(
        f"Processing first 5 of "
        f"{len(unique_articles)} unique articles\n"
    )

    relevant_count = 0

    for index, article in enumerate(
        unique_articles[:5],
        start=1,
    ):

        print("=" * 80)
        print(f"ARTICLE {index}")
        print("=" * 80)

        print(f"Source : {article.source}")
        print(f"Title  : {article.title}")

        result = relevance_agent.analyze(article)

        print(f"Relevant : {result.relevant}")
        print(f"Category : {result.category}")
        print(f"Score    : {result.score}")
        print(f"Reason   : {result.reason}")

        if result.relevant:
            relevant_count += 1

        print()

    print("=" * 80)
    print(f"Relevant articles: {relevant_count}/5")
    print("=" * 80)


if __name__ == "__main__":
    main()
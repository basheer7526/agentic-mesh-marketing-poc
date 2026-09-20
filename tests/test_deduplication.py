from app.tools.rss_tool import rss_tool
from app.tools.deduplication_tool import deduplication_tool


def main():

    print("\n===== DEDUPLICATION TEST =====\n")

    articles = rss_tool.fetch_all()

    print(
        f"Articles before deduplication: "
        f"{len(articles)}"
    )

    unique_articles = (
        deduplication_tool.deduplicate(
            articles
        )
    )

    print(
        f"Articles after deduplication: "
        f"{len(unique_articles)}"
    )

    print(
        f"Duplicates removed: "
        f"{len(articles) - len(unique_articles)}"
    )


if __name__ == "__main__":
    main()
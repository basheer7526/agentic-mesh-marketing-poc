from app.tools.rss_tool import rss_tool


def main():
    print("\n===== RSS INGESTION TEST =====\n")

    articles = rss_tool.fetch_all()

    print(
        f"\nTotal articles collected: {len(articles)}"
    )

    print("\n===== SAMPLE ARTICLES =====\n")

    for article in articles[:10]:

        print(f"Source : {article.source}")
        print(f"Title  : {article.title}")
        print(f"URL    : {article.url}")
        print(f"Date   : {article.published_at}")
        print("-" * 80)


if __name__ == "__main__":
    main()
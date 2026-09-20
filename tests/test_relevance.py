from app.agents.relevance_agent import relevance_agent
from app.models.article import Article


def main():

    print("\n===== RELEVANCE AGENT TEST =====\n")

    article = Article(
        title="AI-powered marketing platform improves campaign personalization",
        url="https://example.com/ai-marketing",
        source="Test Source",
        description=(
            "A marketing technology company launched an AI platform "
            "that helps marketers personalize campaigns, analyze "
            "customer behavior, and optimize engagement."
        ),
    )

    print("ARTICLE")
    print("-" * 80)
    print(f"Source      : {article.source}")
    print(f"Title       : {article.title}")
    print(f"Description : {article.description}")
    print("-" * 80)

    result = relevance_agent.analyze(article)

    print("\n===== AGENT RESULT =====\n")

    print(f"Relevant : {result.relevant}")
    print(f"Category : {result.category}")
    print(f"Score    : {result.score}")
    print(f"Reason   : {result.reason}")


if __name__ == "__main__":
    main()
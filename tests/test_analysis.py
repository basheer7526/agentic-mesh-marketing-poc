from app.tools.rss_tool import rss_tool
from app.tools.deduplication_tool import deduplication_tool
from app.agents.relevance_agent import relevance_agent
from app.agents.analysis_agent import analysis_agent


def main():

    print("\n===== ANALYSIS AGENT TEST =====\n")

    articles = rss_tool.fetch_all()

    unique_articles = deduplication_tool.deduplicate(
        articles
    )

    for article in unique_articles:

        relevance = relevance_agent.analyze(article)

        if relevance.relevant:

            print("=" * 80)
            print("RELEVANT ARTICLE")
            print("=" * 80)

            print(f"Source   : {article.source}")
            print(f"Title    : {article.title}")
            print(f"Category : {relevance.category}")
            print(f"Score    : {relevance.score}")

            print("\nRunning Analysis Agent...\n")

            analysis = analysis_agent.analyze(article)

            print("HEADLINE")
            print(analysis.headline)

            print("\nSUMMARY")
            print(analysis.summary)

            print("\nWHY IT MATTERS")
            print(analysis.why_it_matters)

            print("\nRECOMMENDED ACTION")
            print(analysis.recommended_action)

            print("\nSUPPORTING POINTS")

            for point in analysis.supporting_points:
                print(f"- {point}")

            break


if __name__ == "__main__":
    main()
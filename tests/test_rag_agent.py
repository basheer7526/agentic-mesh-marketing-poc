from app.tools.rss_tool import rss_tool
from app.tools.deduplication_tool import deduplication_tool
from app.agents.relevance_agent import relevance_agent
from app.agents.analysis_agent import analysis_agent
from app.agents.rag_agent import rag_agent


def main():

    print("\n===== RAG AGENT TEST =====\n")

    articles = rss_tool.fetch_all()

    unique_articles = deduplication_tool.deduplicate(
        articles
    )

    for article in unique_articles:

        relevance = relevance_agent.analyze(article)

        if not relevance.relevant:
            continue

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

        print("\nRunning RAG Agent...\n")

        rag_result = rag_agent.analyze(
            analysis
        )

        print("RAG INSIGHT")
        print(rag_result.insight)

        print("\nSUPPORTING SOURCES")

        for source in rag_result.supporting_sources:
            print(f"- {source}")

        print("\nCONTEXT USED")
        print(rag_result.context_used)

        break


if __name__ == "__main__":
    main()
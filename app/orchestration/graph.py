"""
LangGraph orchestration for the Marketing News Intelligence Agent.

Workflow:
    START
      → research
      → deduplication
      → relevance
      → analysis
      → rag
      → priority
      → digest
      → notification
      → END
"""

from datetime import datetime, timezone

from langgraph.graph import END, START, StateGraph

from app.agents.analysis_agent import analysis_agent
from app.agents.priority_agent import priority_agent
from app.agents.rag_agent import rag_agent
from app.agents.relevance_agent import relevance_agent
from app.agents.research_agent import research_agent
from app.config.settings import settings
from app.models.analysis import AnalysisResult
from app.models.article import Article
from app.models.digest import (
    DailyDigest,
    DigestItem,
    Priority,
    PriorityResult,
)
from app.orchestration.state import MarketingIntelligenceState
from app.services.notification_service import notification_service
from app.tools.deduplication_tool import deduplication_tool


# ---------------------------------------------------------------------------
# RESEARCH NODE
# ---------------------------------------------------------------------------

def research_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Execute the Research Agent inside LangGraph.
    """

    print(
        "\n[LANGGRAPH] "
        "Research node started"
    )

    state["current_agent"] = "research_agent"
    state["current_step"] = "research"

    task = state.get(
        "task",
        (
            "Collect the latest marketing news "
            "relevant to the workflow."
        ),
    )

    try:

        result = research_agent.run(task=task)

        state["research_results"] = [
            {
                "success": result["success"],
                "iterations": result["iterations"],
                "final_response": result["final_response"],
                "error": result["error"],
            }
        ]

        if result["success"]:

            tool_results = result.get("tool_results", [])
            articles = []

            for tool_result in tool_results:

                if not tool_result.get("success", False):
                    continue

                articles.extend(
                    tool_result.get("articles", [])
                )

            state["articles"] = articles

        if not result["success"]:

            errors = state.get("errors", [])

            errors.append(
                {
                    "agent": "research_agent",
                    "step": "research",
                    "error": result["error"],
                }
            )

            state["errors"] = errors

    except Exception as exc:

        print(
            "[LANGGRAPH] "
            f"Research agent raised an exception: {exc}"
        )

        errors = state.get("errors", [])

        errors.append(
            {
                "agent": "research_agent",
                "step": "research",
                "error": str(exc),
            }
        )

        state["errors"] = errors
        state["research_results"] = []
        state["articles"] = []

    print(
        "[LANGGRAPH] "
        "Research node completed"
    )

    return state



# ---------------------------------------------------------------------------
# DEDUPLICATION NODE
# ---------------------------------------------------------------------------

def deduplication_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Remove duplicate articles before expensive LLM processing.
    """

    print(
        "\n[LANGGRAPH] "
        "Deduplication node started"
    )

    state["current_agent"] = "deduplication"
    state["current_step"] = "deduplication"

    articles = state.get("articles", [])

    try:
        article_models = [
            Article(**article)
            for article in articles
        ]

        unique_articles = (
            deduplication_tool.deduplicate(article_models)
        )

        state["unique_articles"] = [
            article.model_dump()
            for article in unique_articles
        ]

        print(
            "[LANGGRAPH] "
            f"Articles before deduplication: {len(articles)}"
        )

        print(
            "[LANGGRAPH] "
            f"Articles after deduplication: {len(unique_articles)}"
        )

        print(
            "[LANGGRAPH] "
            f"Duplicates removed: "
            f"{len(articles) - len(unique_articles)}"
        )

    except Exception as exc:

        print(
            "[LANGGRAPH] "
            f"Deduplication error: {exc}"
        )

        errors = state.get("errors", [])

        errors.append(
            {
                "agent": "deduplication",
                "step": "deduplication",
                "error": str(exc),
            }
        )

        state["errors"] = errors

        # Fail safely rather than losing all articles.
        state["unique_articles"] = articles

    print(
        "[LANGGRAPH] "
        "Deduplication node completed"
    )

    return state


# ---------------------------------------------------------------------------
# RELEVANCE NODE
# ---------------------------------------------------------------------------

def relevance_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Execute the Relevance Agent for each collected article.
    """

    print(
        "\n[LANGGRAPH] "
        "Relevance node started"
    )

    state["current_agent"] = "relevance_agent"
    state["current_step"] = "relevance"

    articles = state.get("unique_articles", [])
    import random
    
    # Shuffle to ensure we get a diverse mix of articles from ALL 6 RSS feeds,
    # rather than just taking the first N articles from the first feed.
    random.shuffle(articles)
    
    # HARD CAP: Process a maximum number of articles in the relevance agent
    # based on the user's frontend input (max_evaluations).
    max_evals = state.get("max_evaluations", 30)
    articles = articles[:max_evals]

    relevance_results = []
    relevant_articles = []

    print(
        "[LANGGRAPH] "
        f"Articles received (capped): {len(articles)}"
    )

    for index, article_data in enumerate(articles, start=1):

        try:

            article = Article(**article_data)

            result = relevance_agent.analyze(article)

            relevance_results.append(
                {
                    "article": article.model_dump(),
                    "relevance": result.model_dump(),
                }
            )

            if result.relevant:
                relevant_articles.append(article.model_dump())

            print(
                "[LANGGRAPH] "
                f"Relevance {index}/{len(articles)}: "
                f"{result.relevant} | "
                f"{result.category} | "
                f"{result.score}"
            )

        except Exception as exc:

            print(
                "[LANGGRAPH] "
                f"Relevance error for article {index}: {exc}"
            )

            errors = state.get("errors", [])

            errors.append(
                {
                    "agent": "relevance_agent",
                    "step": "relevance",
                    "article_index": index,
                    "error": str(exc),
                }
            )

            state["errors"] = errors

    state["relevance_results"] = relevance_results
    state["relevant_articles"] = relevant_articles

    print("[LANGGRAPH] Relevance node completed")
    print(
        "[LANGGRAPH] "
        f"Relevant articles: {len(relevant_articles)}"
    )

    return state


# ---------------------------------------------------------------------------
# ANALYSIS NODE
# ---------------------------------------------------------------------------

def analysis_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Generate business intelligence for relevant articles.

    Respects max_articles from execution_metadata when present,
    falls back to settings.MAX_RELEVANT_ARTICLES for direct
    graph invocations that do not supply it.
    """

    print(
        "\n[LANGGRAPH] "
        "Analysis node started"
    )

    state["current_agent"] = "analysis_agent"
    state["current_step"] = "analysis"

    relevant_articles = state.get("relevant_articles", [])

    # Resolve processing cap: API request takes precedence.
    execution_metadata = state.get("execution_metadata", {})
    max_articles = execution_metadata.get(
        "max_articles",
        settings.MAX_RELEVANT_ARTICLES,
    )

    articles_to_analyze = relevant_articles[:max_articles]

    print(
        "[LANGGRAPH] "
        f"Relevant articles received: {len(relevant_articles)}"
    )

    print(
        "[LANGGRAPH] "
        f"Articles selected for analysis: "
        f"{len(articles_to_analyze)} "
        f"(cap={max_articles})"
    )

    analysis_results = []

    for index, article_data in enumerate(
        articles_to_analyze,
        start=1,
    ):

        try:

            article = Article(**article_data)

            result = analysis_agent.analyze(article)

            analysis_results.append(
                {
                    "article": article.model_dump(),
                    "analysis": result.model_dump(),
                }
            )

            print(
                "[LANGGRAPH] "
                f"Analysis {index}/{len(articles_to_analyze)} "
                "completed"
            )

        except Exception as exc:

            print(
                "[LANGGRAPH] "
                f"Analysis error for article {index}: {exc}"
            )

            errors = state.get("errors", [])

            errors.append(
                {
                    "agent": "analysis_agent",
                    "step": "analysis",
                    "article_index": index,
                    "error": str(exc),
                }
            )

            state["errors"] = errors

    state["analysis_results"] = analysis_results

    print("[LANGGRAPH] Analysis node completed")
    print(
        "[LANGGRAPH] "
        f"Successful analyses: {len(analysis_results)}"
    )

    return state


# ---------------------------------------------------------------------------
# RAG NODE
# ---------------------------------------------------------------------------

def rag_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Enrich each analysis result with organizational RAG context.

    For each analysis result:
      1. Reconstruct AnalysisResult from state dict.
      2. Call rag_agent.analyze(analysis).
      3. Append RAGResult to rag_context.

    Individual failures are recorded and skipped.
    """

    print(
        "\n[LANGGRAPH] "
        "RAG node started"
    )

    state["current_agent"] = "rag_agent"
    state["current_step"] = "rag"

    analysis_results = state.get("analysis_results", [])

    rag_context = []

    print(
        "[LANGGRAPH] "
        f"Analysis results received: {len(analysis_results)}"
    )

    for index, item in enumerate(analysis_results, start=1):

        try:

            analysis = AnalysisResult(**item["analysis"])

            rag_result = rag_agent.analyze(analysis)

            rag_context.append(
                {
                    "article": item["article"],
                    "rag": rag_result.model_dump(),
                }
            )

            print(
                "[LANGGRAPH] "
                f"RAG {index}/{len(analysis_results)}: "
                f"context_used={rag_result.context_used}"
            )

        except Exception as exc:

            print(
                "[LANGGRAPH] "
                f"RAG error for analysis {index}: {exc}"
            )

            errors = state.get("errors", [])

            errors.append(
                {
                    "agent": "rag_agent",
                    "step": "rag",
                    "analysis_index": index,
                    "error": str(exc),
                }
            )

            state["errors"] = errors

    state["rag_context"] = rag_context

    print("[LANGGRAPH] RAG node completed")
    print(
        "[LANGGRAPH] "
        f"RAG results: {len(rag_context)}"
    )

    return state


# ---------------------------------------------------------------------------
# PRIORITY NODE
# ---------------------------------------------------------------------------

def priority_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Assign business priority to each analysis result.

    For each analysis result:
      1. Reconstruct AnalysisResult from state dict.
      2. Call priority_agent.assign_priority(analysis).
      3. Append PriorityResult to priority_results.

    Individual failures are recorded and skipped.
    """

    print(
        "\n[LANGGRAPH] "
        "Priority node started"
    )

    state["current_agent"] = "priority_agent"
    state["current_step"] = "priority"

    analysis_results = state.get("analysis_results", [])

    priority_results = []

    print(
        "[LANGGRAPH] "
        f"Analysis results received: {len(analysis_results)}"
    )

    for index, item in enumerate(analysis_results, start=1):

        try:

            analysis = AnalysisResult(**item["analysis"])

            result = priority_agent.assign_priority(analysis)

            priority_results.append(
                {
                    "article": item["article"],
                    "analysis": item["analysis"],
                    "priority": result.model_dump(),
                }
            )

            print(
                "[LANGGRAPH] "
                f"Priority {index}/{len(analysis_results)}: "
                f"{result.priority.value}"
            )

        except Exception as exc:

            print(
                "[LANGGRAPH] "
                f"Priority error for analysis {index}: {exc}"
            )

            errors = state.get("errors", [])

            errors.append(
                {
                    "agent": "priority_agent",
                    "step": "priority",
                    "analysis_index": index,
                    "error": str(exc),
                }
            )

            state["errors"] = errors

    state["priority_results"] = priority_results

    print("[LANGGRAPH] Priority node completed")
    print(
        "[LANGGRAPH] "
        f"Priority results: {len(priority_results)}"
    )

    return state


# ---------------------------------------------------------------------------
# DIGEST NODE  (pure Python — no LLM call)
# ---------------------------------------------------------------------------

def digest_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Assemble a DailyDigest from priority + analysis results.

    This node makes no LLM calls.

    For each priority result, combines:
      - analysis fields  → DigestItem headline/summary/etc.
      - priority value   → DigestItem.priority
      - article metadata → DigestItem.source / url

    Stores digest as a plain dict (model_dump) so that
    LangGraph can serialize it without Pydantic objects.
    """

    print(
        "\n[LANGGRAPH] "
        "Digest node started"
    )

    state["current_agent"] = "digest_agent"
    state["current_step"] = "digest"

    priority_results = state.get("priority_results", [])

    items = []

    for item in priority_results:

        try:

            analysis_data = item["analysis"]
            article_data = item["article"]
            priority_data = item["priority"]

            digest_item = DigestItem(
                headline=analysis_data["headline"],
                summary=analysis_data["summary"],
                why_it_matters=analysis_data["why_it_matters"],
                recommended_action=analysis_data[
                    "recommended_action"
                ],
                priority=Priority(priority_data["priority"]),
                source=article_data.get("source", "Unknown"),
                url=article_data.get("url", ""),
            )

            items.append(digest_item)

        except Exception as exc:

            print(
                "[LANGGRAPH] "
                f"Digest item error: {exc}"
            )

            errors = state.get("errors", [])

            errors.append(
                {
                    "agent": "digest_node",
                    "step": "digest",
                    "error": str(exc),
                }
            )

            state["errors"] = errors

    high = sum(
        1 for i in items
        if i.priority == Priority.HIGH
    )
    medium = sum(
        1 for i in items
        if i.priority == Priority.MEDIUM
    )
    low = sum(
        1 for i in items
        if i.priority == Priority.LOW
    )

    digest = DailyDigest(
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        total_articles=len(items),
        high_priority=high,
        medium_priority=medium,
        low_priority=low,
        items=items,
    )

    # Store as plain dict — no Pydantic objects in LangGraph state.
    state["digest"] = digest.model_dump()

    print("[LANGGRAPH] Digest node completed")
    print(
        "[LANGGRAPH] "
        f"Digest items: {len(items)} "
        f"(High={high}, Medium={medium}, Low={low})"
    )

    return state


# ---------------------------------------------------------------------------
# NOTIFICATION NODE
# ---------------------------------------------------------------------------

def notification_node(
    state: MarketingIntelligenceState,
) -> MarketingIntelligenceState:
    """
    Deliver the completed digest via the notification service.

    Uses ConsoleNotificationService by default.
    Swap notification_service in notification_service.py
    to change the delivery channel.
    """

    print(
        "\n[LANGGRAPH] "
        "Notification node started"
    )

    state["current_agent"] = "notification"
    state["current_step"] = "notification"

    digest_data = state.get("digest")

    if not digest_data:

        print(
            "[LANGGRAPH] "
            "No digest available — skipping notification."
        )

        return state

    try:

        digest = DailyDigest(**digest_data)

        notification_service.send(digest)

    except Exception as exc:

        print(
            "[LANGGRAPH] "
            f"Notification error: {exc}"
        )

        errors = state.get("errors", [])

        errors.append(
            {
                "agent": "notification",
                "step": "notification",
                "error": str(exc),
            }
        )

        state["errors"] = errors

    print("[LANGGRAPH] Notification node completed")

    return state


# ---------------------------------------------------------------------------
# GRAPH BUILDER
# ---------------------------------------------------------------------------

def build_graph():

    graph = StateGraph(MarketingIntelligenceState)

    # Register all nodes
    graph.add_node("research", research_node)
    graph.add_node("deduplication", deduplication_node)
    graph.add_node("relevance", relevance_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("rag", rag_node)
    graph.add_node("priority", priority_node)
    graph.add_node("digest", digest_node)
    graph.add_node("notification", notification_node)

    # Wire the linear pipeline
    graph.add_edge(START, "research")
    graph.add_edge("research", "deduplication")
    graph.add_edge("deduplication", "relevance")
    graph.add_edge("relevance", "analysis")
    graph.add_edge("analysis", "rag")
    graph.add_edge("rag", "priority")
    graph.add_edge("priority", "digest")
    graph.add_edge("digest", "notification")
    graph.add_edge("notification", END)

    return graph.compile()


marketing_graph = build_graph()
from typing import Any, Dict, List, TypedDict


class MarketingIntelligenceState(TypedDict, total=False):
    """
    Shared workflow state for the Marketing News Intelligence Agent.

    The state acts as the controlled context passed
    between agents and LangGraph nodes.
    """

    # --------------------------------------
    # WORKFLOW INFORMATION
    # --------------------------------------

    task: str
    workflow_id: str

    # --------------------------------------
    # WORKFLOW EXECUTION
    # --------------------------------------

    current_agent: str
    current_step: str

    # --------------------------------------
    # RAW COLLECTED ARTICLES
    # --------------------------------------

    articles: List[Dict[str, Any]]

    # --------------------------------------
    # DEDUPLICATED ARTICLES
    # --------------------------------------

    unique_articles: List[Dict[str, Any]]

    # --------------------------------------
    # RELEVANT ARTICLES
    # --------------------------------------

    relevant_articles: List[Dict[str, Any]]

    # --------------------------------------
    # RESEARCH OUTPUTS
    # --------------------------------------

    research_results: List[Dict[str, Any]]

    # --------------------------------------
    # RELEVANCE OUTPUTS
    # --------------------------------------

    relevance_results: List[Dict[str, Any]]

    # --------------------------------------
    # BUSINESS ANALYSIS OUTPUTS
    # --------------------------------------

    analysis_results: List[Dict[str, Any]]

    # --------------------------------------
    # RAG CONTEXT
    # --------------------------------------

    rag_context: List[Dict[str, Any]]

    # --------------------------------------
    # PRIORITY OUTPUTS
    # --------------------------------------

    priority_results: List[Dict[str, Any]]

    # --------------------------------------
    # FINAL DIGEST
    # --------------------------------------

    digest: List[Dict[str, Any]]

    # --------------------------------------
    # WORKFLOW ERRORS
    # --------------------------------------

    errors: List[Dict[str, Any]]

    # --------------------------------------
    # EXECUTION METADATA
    # --------------------------------------

    execution_metadata: Dict[str, Any]

    max_evaluations: int
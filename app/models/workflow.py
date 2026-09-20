"""
Public API request/response models.

These models define the external contract of the FastAPI backend.
They deliberately do NOT expose the raw LangGraph state.

Existing models (WorkflowRequest, WorkflowMetadata) are preserved.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# EXISTING MODELS — do not modify
# ---------------------------------------------------------------------------

class WorkflowRequest(BaseModel):
    """
    Input received when a marketing intelligence workflow
    is started.
    """

    task: str = (
        "Monitor marketing news and identify important "
        "developments in AI marketing, demand generation, "
        "customer experience, Martech, and competitor activity."
    )

    max_articles: int = 20


class WorkflowMetadata(BaseModel):
    """
    Metadata used for tracking workflow execution.
    """

    workflow_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    articles_collected: int = 0
    articles_processed: int = 0

    errors_count: int = 0


# ---------------------------------------------------------------------------
# NEW MODELS
# ---------------------------------------------------------------------------

class DigestItemResponse(BaseModel):
    """
    A single item in the marketing intelligence digest.
    """

    headline: str
    summary: str
    why_it_matters: str
    recommended_action: str
    priority: str
    source: str
    url: str


class DigestResponse(BaseModel):
    """
    The assembled daily digest returned by the workflow.
    """

    date: str
    total_articles: int
    high_priority: int
    medium_priority: int
    low_priority: int
    items: List[DigestItemResponse] = Field(
        default_factory=list
    )


class WorkflowRunRequest(BaseModel):
    """
    Request body for POST /api/v1/workflows/run.
    """

    task: str = (
        "Monitor marketing news and identify important "
        "developments in AI marketing, demand generation, "
        "customer experience, Martech, and competitor activity."
    )

    max_articles: int = Field(
        default=20,
        ge=1,
        le=100,
        description=(
            "Maximum number of relevant articles to process "
            "through analysis, RAG and priority scoring."
        ),
    )
    
    max_evaluations: int = Field(
        default=30,
        ge=1,
        le=200,
        description="Max raw articles to evaluate in the Relevance Node.",
    )


class WorkflowRunResponse(BaseModel):
    """
    Response body for POST /api/v1/workflows/run.

    Exposes business output without leaking raw LangGraph state.
    """

    workflow_id: str
    status: str                         # "completed" | "failed"
    started_at: datetime
    completed_at: Optional[datetime] = None

    articles_collected: int = 0
    unique_articles: int = 0
    relevant_articles: int = 0
    analyses_completed: int = 0

    digest: Optional[DigestResponse] = None
    errors: List[Dict[str, Any]] = Field(
        default_factory=list
    )


class HealthResponse(BaseModel):
    """
    Response body for GET /api/v1/health.
    """

    status: str = "healthy"
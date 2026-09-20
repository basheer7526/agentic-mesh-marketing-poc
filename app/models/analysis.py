from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class RelevanceCategory(str, Enum):
    AI_IN_MARKETING = "AI in Marketing"
    DEMAND_GENERATION = "Demand Generation"
    CUSTOMER_EXPERIENCE = "Customer Experience"
    MARTECH = "Martech"
    COMPETITOR_ACTIVITY = "Competitor Activity"


class RelevanceResult(BaseModel):
    """
    Structured output produced by the Relevance Agent.
    """

    relevant: bool

    category: RelevanceCategory | None = None

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    reason: str


class AnalysisResult(BaseModel):
    """
    Business intelligence generated from a relevant article.
    """

    headline: str

    summary: str = Field(
        min_length=20,
        max_length=500,
    )

    why_it_matters: str

    recommended_action: str

    supporting_points: List[str] = Field(
        default_factory=list,
    )

class RAGResult(BaseModel):
    insight: str
    supporting_sources: List[str] = Field(default_factory=list)
    context_used: bool
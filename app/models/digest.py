from enum import Enum
from typing import List

from pydantic import BaseModel


class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class PriorityResult(BaseModel):
    priority: Priority


class DigestItem(BaseModel):
    headline: str
    summary: str
    why_it_matters: str
    recommended_action: str
    priority: Priority
    source: str
    url: str


class DailyDigest(BaseModel):
    date: str
    total_articles: int
    high_priority: int
    medium_priority: int
    low_priority: int
    items: List[DigestItem]
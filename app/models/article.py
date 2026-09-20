from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Article(BaseModel):
    """
    Normalized representation of an article collected
    from RSS feeds or news APIs.
    """

    title: str
    url: str
    source: str

    description: Optional[str] = None
    content: Optional[str] = None

    published_at: Optional[datetime] = None
    author: Optional[str] = None

    category: Optional[str] = None

    # Used later for deduplication
    content_hash: Optional[str] = None
    
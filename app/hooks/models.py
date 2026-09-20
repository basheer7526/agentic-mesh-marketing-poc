from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class HookAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"


class PreToolUseResult(BaseModel):
    action: HookAction
    reason: str


class PostToolUseResult(BaseModel):
    success: bool
    reason: str
    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )
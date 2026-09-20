from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AgentAction(str, Enum):
    TOOL = "tool"
    FINISH = "finish"


class AgentDecision(BaseModel):
    """
    Structured decision produced by the Research Agent.
    """

    action: AgentAction

    tool: Optional[str] = None

    reason: Optional[str] = None
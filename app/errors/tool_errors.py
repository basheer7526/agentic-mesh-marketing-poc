from typing import Optional

from pydantic import BaseModel


class ToolError(BaseModel):
    """
    Structured representation of a tool execution failure.
    """

    tool_name: str
    error_type: str
    message: str
    retryable: bool = False
    attempt: int = 1
    details: Optional[str] = None
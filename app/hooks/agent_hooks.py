from typing import Any, Dict

from app.hooks.models import (
    HookAction,
    PostToolUseResult,
    PreToolUseResult,
)


def validate_tool_access(
    tool_name: str,
    arguments: Dict[str, Any],
) -> PreToolUseResult:
    """
    Ensure that the requested tool is permitted.
    """

    allowed_tools = {
        "fetch_marketing_news",
    }

    if tool_name not in allowed_tools:

        return PreToolUseResult(
            action=HookAction.BLOCK,
            reason=(
                f"Tool '{tool_name}' is not "
                "permitted for the Research Agent."
            ),
        )

    return PreToolUseResult(
        action=HookAction.ALLOW,
        reason=(
            f"Tool '{tool_name}' is authorized."
        ),
    )


def audit_tool_execution(
    tool_name: str,
    arguments: Dict[str, Any],
    result: Dict[str, Any],
) -> PostToolUseResult:
    """
    Record basic information about tool execution.
    """

    return PostToolUseResult(
        success=result.get(
            "success",
            False,
        ),
        reason="Tool execution audited.",
        metadata={
            "tool_name": tool_name,
            "success": result.get(
                "success",
                False,
            ),
            "article_count": result.get(
                "count",
                0,
            ),
        },
    )

from typing import Any, Callable, Dict, List

from app.hooks.models import (
    HookAction,
    PostToolUseResult,
    PreToolUseResult,
)


PreToolHook = Callable[
    [str, Dict[str, Any]],
    PreToolUseResult,
]

PostToolHook = Callable[
    [str, Dict[str, Any], Dict[str, Any]],
    PostToolUseResult,
]


class HookManager:
    """
    Manages lifecycle hooks around tool execution.
    """

    def __init__(self) -> None:

        self._pre_tool_hooks: List[
            PreToolHook
        ] = []

        self._post_tool_hooks: List[
            PostToolHook
        ] = []

    def register_pre_tool_hook(
        self,
        hook: PreToolHook,
    ) -> None:

        self._pre_tool_hooks.append(hook)

    def register_post_tool_hook(
        self,
        hook: PostToolHook,
    ) -> None:

        self._post_tool_hooks.append(hook)

    def run_pre_tool_hooks(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> PreToolUseResult:

        for hook in self._pre_tool_hooks:

            result = hook(
                tool_name,
                arguments,
            )

            if result.action == HookAction.BLOCK:
                return result

        return PreToolUseResult(
            action=HookAction.ALLOW,
            reason="All pre-tool hooks allowed execution.",
        )

    def run_post_tool_hooks(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
    ) -> List[PostToolUseResult]:

        hook_results = []

        for hook in self._post_tool_hooks:

            hook_result = hook(
                tool_name,
                arguments,
                result,
            )

            hook_results.append(
                hook_result
            )

        return hook_results


hook_manager = HookManager()
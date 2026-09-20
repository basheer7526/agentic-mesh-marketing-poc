from app.hooks.hook_manager import HookManager
from app.hooks.models import (
    HookAction,
    PostToolUseResult,
    PreToolUseResult,
)


def allow_all_hook(
    tool_name: str,
    arguments: dict,
) -> PreToolUseResult:

    print(
        f"[PRE-HOOK] Allowing tool: {tool_name}"
    )

    return PreToolUseResult(
        action=HookAction.ALLOW,
        reason="Tool execution is allowed.",
    )


def block_dangerous_tool_hook(
    tool_name: str,
    arguments: dict,
) -> PreToolUseResult:

    if tool_name == "dangerous_test_tool":

        print(
            f"[PRE-HOOK] Blocking tool: {tool_name}"
        )

        return PreToolUseResult(
            action=HookAction.BLOCK,
            reason=(
                "Tool execution blocked by "
                "security policy."
            ),
        )

    return PreToolUseResult(
        action=HookAction.ALLOW,
        reason="Tool is allowed.",
    )


def log_tool_result_hook(
    tool_name: str,
    arguments: dict,
    result: dict,
) -> PostToolUseResult:

    print(
        f"[POST-HOOK] Tool completed: {tool_name}"
    )

    return PostToolUseResult(
        success=result.get(
            "success",
            False,
        ),
        reason="Tool result processed.",
        metadata={
            "tool_name": tool_name,
            "article_count": result.get(
                "count",
                0,
            ),
        },
    )


def main():

    print(
        "\n===== HOOK SYSTEM TEST =====\n"
    )

    manager = HookManager()

    # --------------------------------------
    # REGISTER HOOKS
    # --------------------------------------

    manager.register_pre_tool_hook(
        allow_all_hook
    )

    manager.register_pre_tool_hook(
        block_dangerous_tool_hook
    )

    manager.register_post_tool_hook(
        log_tool_result_hook
    )

    # --------------------------------------
    # TEST 1: ALLOWED TOOL
    # --------------------------------------

    print(
        "\n--- TEST 1: ALLOWED TOOL ---"
    )

    pre_result = manager.run_pre_tool_hooks(
        tool_name="fetch_marketing_news",
        arguments={},
    )

    print(
        "Action:",
        pre_result.action,
    )

    print(
        "Reason:",
        pre_result.reason,
    )

    # --------------------------------------
    # TEST 2: BLOCKED TOOL
    # --------------------------------------

    print(
        "\n--- TEST 2: BLOCKED TOOL ---"
    )

    pre_result = manager.run_pre_tool_hooks(
        tool_name="dangerous_test_tool",
        arguments={},
    )

    print(
        "Action:",
        pre_result.action,
    )

    print(
        "Reason:",
        pre_result.reason,
    )

    # --------------------------------------
    # TEST 3: POST TOOL HOOK
    # --------------------------------------

    print(
        "\n--- TEST 3: POST TOOL HOOK ---"
    )

    tool_result = {
        "success": True,
        "articles": [
            {
                "title": "Test Article"
            }
        ],
        "count": 1,
    }

    post_results = manager.run_post_tool_hooks(
        tool_name="fetch_marketing_news",
        arguments={},
        result=tool_result,
    )

    for result in post_results:

        print(
            "Success:",
            result.success,
        )

        print(
            "Reason:",
            result.reason,
        )

        print(
            "Metadata:",
            result.metadata,
        )


if __name__ == "__main__":
    main()
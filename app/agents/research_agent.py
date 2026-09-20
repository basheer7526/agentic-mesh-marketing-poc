from typing import Any, Dict

# Import app.hooks so the registered hooks in
# app/hooks/__init__.py are loaded.
import app.hooks

from app.config.settings import settings
from app.errors.tool_errors import ToolError
from app.hooks.hook_manager import hook_manager
from app.hooks.models import HookAction
from app.models.agent import AgentDecision
from app.services.llm_gateway import llm_gateway
from app.tools.tool_registry import tool_registry


class ResearchAgent:
    """
    Agent responsible for researching marketing news.

    The agent reasons about whether it needs to use
    an available tool and iterates until it has enough
    information or reaches the iteration limit.
    """

    SYSTEM_PROMPT = """
You are a Research Agent for a Marketing News
Intelligence system.

Your responsibility is to collect and organize
marketing news relevant to the workflow.

You have access to the tools listed under
AVAILABLE TOOLS.

Use a tool when additional information is genuinely
required to complete the research task.

IMPORTANT:

Once a tool has successfully returned the required
information, do not call the same tool again unless
there is a specific reason that requires another
retrieval.

The tool result will be available in CURRENT CONTEXT.

Use the information already available in the context
before requesting another tool execution.

If you need to use a tool, return:

{
    "action": "tool",
    "tool": "<tool_name>",
    "reason": "..."
}

If you have enough information and want to finish,
return:

{
    "action": "finish",
    "tool": null,
    "reason": "..."
}

IMPORTANT:

- Never invent article data.
- Only use tools listed in AVAILABLE TOOLS.
- Do not repeatedly call a successfully executed tool
  when its result is already available.
- Return ONLY valid JSON.
- The action must be either "tool" or "finish".
- If action is "tool", tool must be an available tool.
"""

    def __init__(self) -> None:
        self.max_iterations = settings.MAX_AGENT_ITERATIONS

    def _ask_llm(
        self,
        task: str,
        context: str,
    ) -> AgentDecision:

        available_tools = "\n".join(
            [
                f"- {tool.name}: {tool.description}"
                for tool in tool_registry.get_all()
            ]
        )

        prompt = f"""
{self.SYSTEM_PROMPT}

AVAILABLE TOOLS:

{available_tools}

TASK:

{task}

CURRENT CONTEXT:

{context}

The CURRENT CONTEXT contains observations from tools
that have already been executed.

If the required information is already available
in the context, do not call the same tool again.

If the research task has been completed, choose:

{{
    "action": "finish",
    "tool": null,
    "reason": "..."
}}

If additional information is genuinely required,
choose the appropriate available tool.

Return ONLY valid JSON.
"""

        structured_llm = llm_gateway.structured(
            AgentDecision
        )

        import time
        from app.config.settings import settings
        
        last_exception = None
        for attempt in range(1, settings.MAX_LLM_RETRIES + 1):
            try:
                return structured_llm.invoke(prompt)
            except Exception as exc:
                last_exception = exc
                print(f"[RESEARCH AGENT] JSON Parse / LLM Error on attempt {attempt}: {exc}")
                if attempt >= settings.MAX_LLM_RETRIES:
                    break
                time.sleep(settings.LLM_RETRY_BASE_DELAY)

        raise last_exception

    def run(self, task: str) -> Dict[str, Any]:

        context = ""
        iterations = 0
        tool_results = []

        # Tracks tools that completed successfully.
        # Failed tools are not added here so they can
        # be retried when the error is retryable.
        executed_tools = set()

        while iterations < self.max_iterations:

            iterations += 1

            print(
                f"[RESEARCH AGENT] "
                f"Iteration {iterations}"
            )

            # ------------------------------------------
            # ASK LLM FOR NEXT ACTION
            # ------------------------------------------

            decision = self._ask_llm(
                task=task,
                context=context,
            )

            print(
                "[RESEARCH AGENT] "
                f"Action: {decision.action}"
            )

            print(
                "[RESEARCH AGENT] "
                f"Tool: {decision.tool}"
            )

            print(
                "[RESEARCH AGENT] "
                f"Reason: {decision.reason}"
            )

            # ------------------------------------------
            # TOOL ACTION
            # ------------------------------------------

            if decision.action.value == "tool":

                # --------------------------------------
                # VALIDATE TOOL NAME
                # --------------------------------------

                if not decision.tool:

                    return {
                        "success": False,
                        "iterations": iterations,
                        "tool_results": tool_results,
                        "final_response": None,
                        "error": (
                            "Agent selected tool action "
                            "but did not provide a tool name."
                        ),
                    }

                if not tool_registry.has(
                    decision.tool
                ):

                    return {
                        "success": False,
                        "iterations": iterations,
                        "tool_results": tool_results,
                        "final_response": None,
                        "error": (
                            f"Unknown tool requested: "
                            f"{decision.tool}"
                        ),
                    }

                # --------------------------------------
                # PREVENT REDUNDANT TOOL EXECUTION
                # --------------------------------------

                if decision.tool in executed_tools:

                    print(
                        "[RESEARCH AGENT] "
                        f"Tool already executed: "
                        f"{decision.tool}"
                    )

                    context += (
                        "\nSYSTEM OBSERVATION:\n"
                        f"The tool '{decision.tool}' "
                        "has already been executed "
                        "successfully.\n"
                        "Its result is already available "
                        "in the current context.\n"
                        "Do not call the same tool again. "
                        "Use the existing result and "
                        "finish the research task if "
                        "sufficient."
                    )

                    continue

                # --------------------------------------
                # PRE-TOOL HOOK
                # --------------------------------------

                print(
                    "[RESEARCH AGENT] "
                    "Running PreToolUse hooks for: "
                    f"{decision.tool}"
                )

                pre_hook_result = (
                    hook_manager.run_pre_tool_hooks(
                        tool_name=decision.tool,
                        arguments={},
                    )
                )

                print(
                    "[RESEARCH AGENT] "
                    f"PreToolUse: "
                    f"{pre_hook_result.action}"
                )

                print(
                    "[RESEARCH AGENT] "
                    f"Hook reason: "
                    f"{pre_hook_result.reason}"
                )

                # --------------------------------------
                # BLOCK TOOL IF HOOK DENIES EXECUTION
                # --------------------------------------

                if (
                    pre_hook_result.action
                    == HookAction.BLOCK
                ):

                    print(
                        "[RESEARCH AGENT] "
                        "Tool execution blocked "
                        "by PreToolUse hook."
                    )

                    return {
                        "success": False,
                        "iterations": iterations,
                        "tool_results": tool_results,
                        "final_response": None,
                        "error": (
                            "Tool execution blocked "
                            "by PreToolUse hook: "
                            f"{pre_hook_result.reason}"
                        ),
                    }

                # --------------------------------------
                # TOOL EXECUTION
                # --------------------------------------

                print(
                    "[RESEARCH AGENT] "
                    f"Calling tool: {decision.tool}"
                )

                tool = tool_registry.get(
                    decision.tool
                )

                try:

                    tool_result = tool.run()

                except Exception as exc:

                    print(
                        "[RESEARCH AGENT] "
                        f"Unexpected tool exception: {exc}"
                    )

                    tool_result = {
                        "success": False,
                        "articles": [],
                        "count": 0,
                        "error": str(exc),
                        "tool_error": ToolError(
                            tool_name=decision.tool,
                            error_type=type(exc).__name__,
                            message=str(exc),
                            retryable=False,
                            attempt=1,
                        ).model_dump(),
                    }

                tool_results.append(
                    tool_result
                )

                # --------------------------------------
                # POST-TOOL HOOK
                # --------------------------------------

                print(
                    "[RESEARCH AGENT] "
                    "Running PostToolUse hooks for: "
                    f"{decision.tool}"
                )

                post_hook_results = (
                    hook_manager.run_post_tool_hooks(
                        tool_name=decision.tool,
                        arguments={},
                        result=tool_result,
                    )
                )

                for post_hook_result in (
                    post_hook_results
                ):

                    print(
                        "[RESEARCH AGENT] "
                        f"PostToolUse success: "
                        f"{post_hook_result.success}"
                    )

                    print(
                        "[RESEARCH AGENT] "
                        f"PostToolUse reason: "
                        f"{post_hook_result.reason}"
                    )

                    if post_hook_result.metadata:

                        print(
                            "[RESEARCH AGENT] "
                            f"PostToolUse metadata: "
                            f"{post_hook_result.metadata}"
                        )

                # --------------------------------------
                # HANDLE TOOL FAILURE
                # --------------------------------------

                if not tool_result.get(
                    "success",
                    False,
                ):

                    raw_tool_error = (
                        tool_result.get(
                            "tool_error"
                        )
                    )

                    if raw_tool_error:

                        tool_error = ToolError(
                            **raw_tool_error
                        )

                        print(
                            "[RESEARCH AGENT] "
                            f"Tool failed: "
                            f"{tool_error.message}"
                        )

                        # ----------------------------------
                        # RETRYABLE FAILURE
                        # ----------------------------------

                        if tool_error.retryable:

                            print(
                                "[RESEARCH AGENT] "
                                "Tool error is retryable."
                            )

                            context = (
                                "TOOL EXECUTION FAILED:\n"
                                f"Tool: "
                                f"{tool_error.tool_name}\n"
                                f"Error Type: "
                                f"{tool_error.error_type}\n"
                                f"Message: "
                                f"{tool_error.message}\n"
                                "The failure may be "
                                "temporary. Decide whether "
                                "retrying is appropriate."
                            )

                            continue

                        # ----------------------------------
                        # NON-RETRYABLE FAILURE
                        # ----------------------------------

                        return {
                            "success": False,
                            "iterations": iterations,
                            "tool_results": tool_results,
                            "final_response": None,
                            "error": (
                                "Non-retryable tool error: "
                                f"{tool_error.message}"
                            ),
                        }

                    # ----------------------------------
                    # UNSTRUCTURED TOOL FAILURE
                    # ----------------------------------

                    return {
                        "success": False,
                        "iterations": iterations,
                        "tool_results": tool_results,
                        "final_response": None,
                        "error": (
                            f"Tool '{decision.tool}' "
                            "failed without a "
                            "structured error."
                        ),
                    }

                # --------------------------------------
                # SUCCESSFUL TOOL EXECUTION
                # --------------------------------------

                executed_tools.add(
                    decision.tool
                )

                # --------------------------------------
                # BUILD TOOL CONTEXT
                # --------------------------------------

                articles = tool_result.get(
                    "articles",
                    [],
                )

                context = (
                    f"TOOL RESULT:\n"
                    f"Tool: {decision.tool}\n"
                    f"Success: "
                    f"{tool_result.get('success')}\n"
                    f"Articles collected: "
                    f"{tool_result.get('count', 0)}\n\n"
                    f"ARTICLE DATA:\n"
                )

                # Limit the amount of article data
                # inserted into the LLM context.
                for article in articles[:20]:

                    context += (
                        f"- Title: "
                        f"{article.get('title')}\n"
                        f"  Source: "
                        f"{article.get('source')}\n"
                        f"  URL: "
                        f"{article.get('url')}\n"
                        f"  Description: "
                        f"{article.get('description')}\n\n"
                    )

                # Add normal tool error information
                # if present.
                if tool_result.get("error"):

                    context += (
                        "\nTOOL ERROR:\n"
                        f"{tool_result['error']}\n"
                    )

                # Add structured tool error information
                # if present.
                tool_error = tool_result.get(
                    "tool_error"
                )

                if tool_error:

                    context += (
                        "\nSTRUCTURED TOOL ERROR:\n"
                        f"Tool: "
                        f"{tool_error.get('tool_name')}\n"
                        f"Error Type: "
                        f"{tool_error.get('error_type')}\n"
                        f"Message: "
                        f"{tool_error.get('message')}\n"
                        f"Retryable: "
                        f"{tool_error.get('retryable')}\n"
                        f"Attempt: "
                        f"{tool_error.get('attempt')}\n"
                    )

                continue

            # ------------------------------------------
            # FINISH ACTION
            # ------------------------------------------

            if decision.action.value == "finish":

                print(
                    "[RESEARCH AGENT] "
                    "Agent decided to finish."
                )

                return {
                    "success": True,
                    "iterations": iterations,
                    "tool_results": tool_results,
                    "final_response": decision.reason,
                    "error": None,
                }

        # ----------------------------------------------
        # MAX ITERATIONS REACHED
        # ----------------------------------------------

        return {
            "success": False,
            "iterations": iterations,
            "tool_results": tool_results,
            "final_response": None,
            "error": (
                "Maximum agent iterations reached."
            ),
        }


research_agent = ResearchAgent()
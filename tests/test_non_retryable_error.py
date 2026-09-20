from typing import Any, Dict

from app.agents.research_agent import ResearchAgent
from app.errors.tool_errors import ToolError
from app.tools.base import BaseTool
from app.tools.tool_registry import tool_registry


class NonRetryableTestTool(BaseTool):

    name = "non_retryable_test_tool"

    description = """
Test tool used to verify non-retryable
error handling.
"""

    def run(self, **kwargs: Any) -> Dict[str, Any]:

        print(
            "[NON-RETRYABLE TEST TOOL] "
            "Executing tool"
        )

        error = ToolError(
            tool_name=self.name,
            error_type="ConfigurationError",
            message="Required configuration is missing.",
            retryable=False,
            attempt=1,
        )

        return {
            "success": False,
            "articles": [],
            "count": 0,
            "error": error.message,
            "tool_error": error.model_dump(),
        }


non_retryable_tool = NonRetryableTestTool()


def main():

    print(
        "\n===== NON-RETRYABLE ERROR TEST =====\n"
    )

    tool_registry.register(
        non_retryable_tool
    )

    agent = ResearchAgent()

    result = agent.run(
        task=(
            "Use the non_retryable_test_tool "
            "to retrieve marketing information."
        )
    )

    print(
        "\n===== FINAL RESULT ====="
    )

    print(
        "Success    :",
        result["success"],
    )

    print(
        "Iterations :",
        result["iterations"],
    )

    print(
        "Error      :",
        result["error"],
    )

    print(
        "Tool calls :",
        len(result["tool_results"]),
    )


if __name__ == "__main__":
    main()
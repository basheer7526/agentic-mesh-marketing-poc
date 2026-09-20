from typing import Any, Dict

from app.agents.research_agent import ResearchAgent
from app.errors.tool_errors import ToolError
from app.tools.base import BaseTool
from app.tools.tool_registry import tool_registry


class FlakyTestTool(BaseTool):
    """
    Test tool that fails once and succeeds on retry.
    """

    name = "flaky_test_tool"

    description = """
Test tool used to verify retry behavior.
"""

    def __init__(self) -> None:
        self.attempts = 0

    def run(self, **kwargs: Any) -> Dict[str, Any]:

        self.attempts += 1

        print(
            f"[FLAKY TEST TOOL] Attempt {self.attempts}"
        )

        # First attempt deliberately fails
        if self.attempts == 1:

            error = ToolError(
                tool_name=self.name,
                error_type="TemporaryError",
                message="Temporary test failure.",
                retryable=True,
                attempt=self.attempts,
            )

            return {
                "success": False,
                "articles": [],
                "count": 0,
                "error": error.message,
                "tool_error": error.model_dump(),
            }

        # Second attempt succeeds
        return {
            "success": True,
            "articles": [
                {
                    "title": "Test Marketing Article",
                    "source": "Test Source",
                    "url": "https://example.com/test",
                    "description": (
                        "Test article retrieved "
                        "after retry."
                    ),
                }
            ],
            "count": 1,
            "error": None,
            "tool_error": None,
        }


flaky_tool = FlakyTestTool()


def main():

    print(
        "\n===== RETRY BEHAVIOR TEST =====\n"
    )

    # Register the temporary test tool
    tool_registry.register(flaky_tool)

    agent = ResearchAgent()

    result = agent.run(
        task=(
            "Use the flaky_test_tool to retrieve "
            "the marketing article."
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
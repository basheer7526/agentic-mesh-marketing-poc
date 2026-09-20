from typing import Any, Dict

from app.errors.tool_errors import ToolError
from app.tools.base import BaseTool
from app.tools.rss_tool import rss_tool


class RSSAgentTool(BaseTool):
    """
    Agent-accessible wrapper around the existing RSS tool.
    """

    name = "fetch_marketing_news"

    description = """
Fetch the latest marketing news articles from the
configured RSS sources.

Use this tool when you need to collect recent news
related to marketing, AI in marketing, demand generation,
customer experience, Martech, or competitor activity.

Returns structured article data including:
- title
- URL
- source
- description
- publication date
- author
"""

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the RSS collection tool and return
        a structured result.
        """

        try:
            from app.config.settings import settings
            articles = rss_tool.fetch_all()
            
            # Enforce the global MAX_ARTICLES limit to prevent API token exhaustion
            articles = articles[:settings.MAX_ARTICLES]

            return {
                "success": True,
                "articles": [
                    article.model_dump()
                    for article in articles
                ],
                "count": len(articles),
                "error": None,
                "tool_error": None,
            }

        except Exception as exc:

            tool_error = ToolError(
                tool_name=self.name,
                error_type=type(exc).__name__,
                message=str(exc),
                retryable=True,
                attempt=1,
            )

            return {
                "success": False,
                "articles": [],
                "count": 0,
                "error": str(exc),
                "tool_error": tool_error.model_dump(),
            }


rss_agent_tool = RSSAgentTool()
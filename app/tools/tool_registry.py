from typing import Dict

from app.tools.base import BaseTool
from app.tools.rss_agent_tool import rss_agent_tool


class ToolRegistry:
    """
    Registry containing the tools that agents are
    allowed to use.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool using its declared name.
        """

        if not tool.name:
            raise ValueError(
                "Tool must have a name before registration."
            )

        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """
        Retrieve a registered tool by name.
        """

        if name not in self._tools:
            raise KeyError(
                f"Unknown tool: {name}"
            )

        return self._tools[name]

    def has(self, name: str) -> bool:
        """
        Check whether a tool exists.
        """

        return name in self._tools

    def list_tools(self) -> list[str]:
        """
        Return the names of all registered tools.
        """

        return list(self._tools.keys())

    def get_all(self) -> list[BaseTool]:
        """
        Return all registered tool instances.
        """

        return list(self._tools.values())


tool_registry = ToolRegistry()

tool_registry.register(rss_agent_tool)
from app.tools.tool_registry import tool_registry


print("\n===== TOOL REGISTRY TEST =====\n")

print(
    "Registered tools:",
    tool_registry.list_tools(),
)

print(
    "RSS tool available:",
    tool_registry.has(
        "fetch_marketing_news"
    ),
)

rss_tool = tool_registry.get(
    "fetch_marketing_news"
)

print(
    "Tool name:",
    rss_tool.name,
)

print(
    "Tool description:",
    rss_tool.description.strip(),
)
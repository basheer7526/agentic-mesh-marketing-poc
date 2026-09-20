from app.tools.rss_agent_tool import rss_agent_tool


print("\n===== RSS AGENT TOOL TEST =====\n")

result = rss_agent_tool.run()

print("Success :", result["success"])
print("Count   :", result["count"])
print("Error   :", result["error"])

if result["articles"]:
    first_article = result["articles"][0]

    print("\nFIRST ARTICLE")
    print("Title  :", first_article["title"])
    print("Source :", first_article["source"])
    print("URL    :", first_article["url"])
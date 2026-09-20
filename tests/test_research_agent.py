from app.agents.research_agent import research_agent


print("\n===== RESEARCH AGENT TEST =====\n")

result = research_agent.run(
    task=(
        "Collect the latest marketing news and "
        "prepare the information needed for further "
        "relevance analysis."
    )
)

print("\n===== FINAL RESULT =====")

print("Success    :", result["success"])
print("Iterations :", result["iterations"])
print("Error      :", result["error"])

print(
    "Tool calls :",
    len(result["tool_results"])
)

print(
    "Final response:",
    result["final_response"]
)
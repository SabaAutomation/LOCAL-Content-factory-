
# ---------- STEP 5: WIRE THE GRAPH ----------
graph = StateGraph(PostState)
graph.add_node("writer", writer)
graph.add_node("critic", critic)
graph.add_node("publish", publish)
graph.add_node("human_review", human_review)

graph.set_entry_point("writer")
graph.add_edge("writer", "critic")
graph.add_conditional_edges("critic", route,
    {"writer": "writer", "publish": "publish", "human_review": "human_review"})
graph.add_edge("publish", END)
graph.add_edge("human_review", END)
app = graph.compile()

# ---------- STEP 6: RUN IT ----------
if __name__ == "__main__":
    import sys
    if "--graph" in sys.argv:                      # prints a diagram you can paste into mermaid.live
        print(app.get_graph().draw_mermaid())
        sys.exit()
    topic = " ".join(a for a in sys.argv[1:] if not a.startswith("--")) or "free AI tools for clinics"
    banner(f"TOPIC: {topic}", YELLOW)
    final = app.invoke({"topic": topic, "draft": "", "feedback": "", "score": 0, "attempts": 0, "history": []})
    banner("RESULT", GREEN)
    line("Scores by round:", " -> ".join(str(s) for s in final["history"]))
    line("Final caption:", final["draft"], GREEN)

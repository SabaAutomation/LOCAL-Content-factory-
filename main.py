import json, re, requests
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from helpers import *

# ---------- SETTINGS (change these, not the code) ----------
MODEL = "gpt-oss:20b"        # any model you pulled with: ollama pull <name>
PASS_SCORE = 8               # critic must give at least this to publish
MAX_ATTEMPTS = 3             # stop looping after this many rounds
MAX_CHARS = 220              # hard rule checked by plain Python
LAZY_FIRST_DRAFT = True      # round 1 = quick draft, so the loop has work to do
N8N_WEBHOOK_URL = ""         # paste your n8n webhook URL (Episode 1) or leave empty

llm = ChatOllama(model=MODEL, temperature=0.7)

def ask(prompt: str) -> str:
    content = llm.invoke(prompt).content
    if isinstance(content, list):
        content = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
    return content.strip()

# ---------- STEP 1: THE STATE (our shared notebook) ----------
class PostState(TypedDict):
    topic: str
    draft: str
    feedback: str
    score: int
    attempts: int
    history: list

# ---------- STEP 2: THE WRITER NODE ----------
def writer(state: PostState):
    n = state["attempts"] + 1
    banner(f"ROUND {n}  |  WRITER", CYAN)
    if n == 1 and LAZY_FIRST_DRAFT:
        prompt = f"Write a quick Instagram caption about: {state['topic']}. Return only the caption."
    else:
        prompt = f"""You are a social media copywriter.
Write ONE Instagram caption about: {state['topic']}
Rules: under {MAX_CHARS} characters, a strong hook in the first line, one clear call to action, max 3 hashtags.
Fix EVERY point from the editor's feedback below.
Previous draft: {state['draft'] or 'none'}
Editor feedback: {state['feedback'] or 'none'}
Return ONLY the new caption."""
    draft = ask(prompt).strip('"').strip()
    line("Draft:", draft, YELLOW)
    line("Length:", f"{len(draft)} characters", DIM)
    return {"draft": draft, "attempts": n}

# ---------- STEP 3: THE CRITIC NODE (AI for taste, Python for rules) ----------
def critic(state: PostState):
    banner(f"ROUND {state['attempts']}  |  CRITIC", MAG)
    prompt = f"""You are a strict social media editor.
Score this Instagram caption from 1 to 10 for hook strength, clarity, and a clear call to action.
Be tough: 8 or higher means ready to publish with no changes.
Caption: {state['draft']}
Reply with ONLY JSON: {{"score": <integer 1-10>, "feedback": "<one sentence: what to fix>"}}"""
    raw = ask(prompt)
    try:
        data = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
        score, feedback = int(float(data["score"])), str(data["feedback"])
    except Exception:
        score, feedback = 1, "Critic reply was not valid JSON - rewrite more clearly."

    # hard rules: plain Python beats AI opinion
    if len(state["draft"]) > MAX_CHARS:
        score = min(score, 5)
        feedback = f"Too long ({len(state['draft'])} chars), cut to under {MAX_CHARS}. " + feedback
    if len(re.findall(r"#\w+", state["draft"])) > 3:
        score = min(score, 6)
        feedback = "Use max 3 hashtags. " + feedback

    score = max(1, min(10, score))
    line("Score:", score_bar(score))
    line("Feedback:", feedback, YELLOW)
    return {"score": score, "feedback": feedback, "history": state["history"] + [score]}

# ---------- STEP 4: THE ROUTER + END NODES ----------
def route(state: PostState):
    if state["score"] >= PASS_SCORE:
        line("Decision:", "APPROVED -> publishing", GREEN)
        return "publish"
    if state["attempts"] >= MAX_ATTEMPTS:
        line("Decision:", "Out of attempts -> sending to a human", RED)
        return "human_review"
    line("Decision:", f"REJECTED (needs {PASS_SCORE}+) -> back to the writer", RED)
    return "writer"

def publish(state: PostState):
    banner("PUBLISH", GREEN)
    if N8N_WEBHOOK_URL:
        try:
            r = requests.post(N8N_WEBHOOK_URL, json={"caption": state["draft"], "score": state["score"]}, timeout=15)
            line("n8n webhook:", f"HTTP {r.status_code}", GREEN)
        except Exception as e:
            line("n8n webhook failed:", str(e), RED)
    else:
        with open("published_posts.txt", "a", encoding="utf-8") as f:
            f.write(f"[score {state['score']}] {state['draft']}\n")
        line("Saved to:", "published_posts.txt (no webhook set)", GREEN)
    return {}

def human_review(state: PostState):
    banner("HUMAN REVIEW", RED)
    with open("review_queue.txt", "a", encoding="utf-8") as f:
        f.write(f"[score {state['score']}] {state['draft']}\n")
    line("Saved to:", "review_queue.txt - not posted", RED)
    return {}

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

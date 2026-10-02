
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

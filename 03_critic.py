
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


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

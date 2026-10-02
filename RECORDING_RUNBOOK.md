# Ep 14 — LangGraph Self-Correcting Workflow: Screen-Recording Runbook

**Tested:** Python 3.12, `langgraph 1.2.12`, `langchain-ollama 1.1.0`. The graph logic was tested end to end with a scripted fake model (rejection → rewrite → approval, and the "send to human" path). It was **not** tested with a real Ollama model, so do the dry run below before you record.

## Files
```
ep14-langgraph/
  helpers.py          colors + pretty output (don't explain on camera)
  blocks/01_state.py … 05_graph_and_run.py   <- the 5 pieces you paste live
  main.py             the finished file (all 5 blocks joined) - your backup
  requirements.txt
```

---
## PART A — Prep (off camera, 20 min)

1. **Check Python (3.10 or newer):** `python --version` (Mac: `python3 --version`)
2. **Install Ollama** from https://ollama.com/ and open it (it must be running in the background).
3. **Download the model** (big download, roughly 13–14 GB; needs about 16 GB RAM):
   ```
   ollama pull gpt-oss:20b
   ```
4. **Quick model test:** `ollama run gpt-oss:20b "say hi"` → you should get a reply. Type `/bye` to exit.
5. **Make the project folder + virtual environment**
   - Windows:
     ```
     mkdir ep14 && cd ep14
     python -m venv venv
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```
     mkdir ep14 && cd ep14
     python3 -m venv venv
     source venv/bin/activate
     ```
6. Copy `helpers.py` and `requirements.txt` into the `ep14` folder, then: `pip install -r requirements.txt`
7. Open the folder in **VS Code**.

### DRY RUN (do this once before filming — it also warms up the model)
Copy `main.py` into the folder and run: `python main.py`
You should see ROUND 1 writer → critic → decision, repeating until APPROVED or HUMAN REVIEW.
**The first run is slow because the model loads. Run it twice so the second run (the one you film) is fast.**
When happy, **delete `main.py`** and the `.txt` files it created. Keep `helpers.py`.

---
## PART B — Recording setup (5 min)
- Screen 1920×1080, record at 1080p / 30 fps.
- VS Code zoom in (Ctrl/Cmd + `+`) until code is readable on a phone. Terminal font ≥ 18.
- Use VS Code's built-in terminal (colors work best). Split screen: editor on top, terminal below.
- Turn on Do Not Disturb. Close other heavy apps so the model runs fast.
- Record **mic and screen separately** if you can, so you can re-do the voiceover.

---
## PART C — The live build (matches your script, 8:30 → 13:30)

Create an empty file `main.py`. For each step, **paste the block from `blocks/`**, then explain it (or type it if you prefer).

| Step | Script time | Do this | Say / show |
|---|---|---|---|
| 0 | 8:30 | Show terminal: `ollama list` | "Local model, zero cost." |
| 1 | 9:30 | Paste `blocks/01_state.py` | Point at **SETTINGS** ("change these, not the code") and the `PostState` class: "five fields, our notebook". |
| 2 | 10:00 | Paste `blocks/02_writer.py` | "Writer reads the critic's feedback from last round." Show `LAZY_FIRST_DRAFT`: "Round 1 is a quick draft, so you can see the loop work." |
| 3 | 10:30 | Paste `blocks/03_critic.py` | "AI for taste, Python for rules." Highlight the `if len(...) > MAX_CHARS` lines. |
| 4 | 11:30 | Paste `blocks/04_router.py` | Highlight `route()`: "score 8+ → publish, otherwise back to writer. 3 tries max, then a human." |
| 5 | 12:00 | Paste `blocks/05_graph_and_run.py` | Walk the `add_node`, `add_edge`, `add_conditional_edges` lines. |
| 6 | 12:30 | **Show the graph:** run `python main.py --graph`, copy the output, paste into https://mermaid.live | Great visual: writer → critic → three exits. |
| 7 | 12:45 | **LIVE RUN:** `python main.py "free AI tools for clinics"` | Let the colors do the work. Don't talk over the first score. |

### Live-run tips
- **Want a guaranteed rejection on camera?** Keep `LAZY_FIRST_DRAFT = True`. Say honestly: "I told the writer to go quick on round 1, so we can watch it get corrected."
- **Want the real result?** Set it to `False` and see what happens. If round 1 passes at 8+, the loop never triggers — fine for a test, boring for a video.
- Run it 2–3 times and **use the best take**. Models vary each time.
- To make it stricter: set `PASS_SCORE = 9`.
- Note the real scores, you'll need them for the **[FILL]** spots in your script ("Scores by round: 5 -> 6 -> 9" is printed at the end).

### Optional: publish through n8n (Episode 1 callback)
1. In n8n create a **Webhook** node (POST) → connect to your posting nodes. Use the **Test URL** while recording.
2. Paste the URL into `N8N_WEBHOOK_URL = "..."` in block 01.
3. Click "Listen for test event" in n8n, then run the script. The n8n node should light up. The webhook gets `{"caption": "...", "score": 9}`.
4. Leave it empty and the post is saved to `published_posts.txt` instead (good enough for the demo).

---
## PART D — Show the "wait, it really checks" proof (optional, 30 sec)
Run once with `MAX_CHARS = 60` and `PASS_SCORE = 10`. It will fail every round and land in **HUMAN REVIEW** (`review_queue.txt`). This shows the safety net: "it refuses to post bad work."

---
## Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: langgraph` | Virtual env not active. Re-run the `activate` command. |
| `ConnectError` / connection refused | Ollama isn't running. Open the Ollama app, then retry. |
| `model not found` | Run `ollama pull gpt-oss:20b`, or change `MODEL` to a model from `ollama list`. |
| Very slow / computer freezing | Not enough RAM. Use a smaller model (`ollama pull qwen3:8b`, change `MODEL`). |
| Critic always says "not valid JSON" | The model is chatty. Re-run, or switch model. The code already extracts `{...}` from the reply. |
| Weird symbols in the terminal | Use the VS Code terminal or Windows Terminal, not old `cmd`. |
| Always scores 8+ on round 1 | Set `PASS_SCORE = 9` or keep `LAZY_FIRST_DRAFT = True`. |

### If your computer is too weak for Ollama: Gemini free-tier fallback (untested)
1. `pip install langchain-google-genai`
2. Get a key at https://aistudio.google.com/ and set it: Windows `set GOOGLE_API_KEY=your_key` · Mac `export GOOGLE_API_KEY=your_key`
3. In block 01 replace the `llm = ChatOllama(...)` line (and the ChatOllama import) with:
   ```python
   from langchain_google_genai import ChatGoogleGenerativeAI
   llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
   ```
   Check AI Studio for the current free model name first, since model names change.
   Free tiers have rate limits, which is a nice example for your on-camera honesty note.

---
## One script change I recommend
Your script says "after three tries we publish." The code is safer: after three failed tries it **sends the draft to a human instead of posting**. Use that line on camera, it fits your "autonomy needs a checker" story better.

## After recording
- Fill the **[FILL]** values in your script with the real scores.
- Say your real LangGraph version: run `pip show langgraph`.

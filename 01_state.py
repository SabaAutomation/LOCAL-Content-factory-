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

# helpers.py - pretty terminal output so the screen recording looks great.
# You do NOT need to explain this file on camera.
import sys, os, time
if sys.platform == "win32":
    os.system("")  # turns on colors in Windows terminals
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"; CYAN = "\033[96m"; MAG = "\033[95m"

def banner(text, color=CYAN):
    print(f"\n{color}{BOLD}{'-' * 62}\n  {text}\n{'-' * 62}{RESET}")
    time.sleep(0.6)

def line(label, text, color=RESET):
    print(f"{BOLD}{label}{RESET} {color}{text}{RESET}")
    time.sleep(0.4)

def score_bar(score):
    color = GREEN if score >= 8 else (YELLOW if score >= 6 else RED)
    return f"{color}{'#' * score}{'.' * (10 - score)}  {score}/10{RESET}"

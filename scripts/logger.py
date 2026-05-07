# scripts/logger.py
import time
import os
from datetime import datetime

LOG_PATH = "reports/pipeline.log"
os.makedirs("reports", exist_ok=True)

_script_start = time.time()
_step_start   = time.time()
_script_name  = ""

def init(script_name: str):
    """Call at the top of every pipeline script."""
    global _script_start, _script_name
    _script_start = time.time()
    _script_name  = script_name
    _write(f"\n{'='*55}")
    _write(f"STARTED  {script_name}  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    _write(f"{'='*55}")
    print(f"[LOG] {script_name} started")

def step(label: str):
    """Call before each major step to log it."""
    global _step_start
    _step_start = time.time()
    _write(f"  >> {label}")
    print(f"[LOG] {label}...")

def done(label: str = ""):
    """Call after a step finishes — logs elapsed time."""
    elapsed = time.time() - _step_start
    msg = f"  OK {label}  ({elapsed:.1f}s)" if label else f"  OK ({elapsed:.1f}s)"
    _write(msg)
    print(f"[LOG] done ({elapsed:.1f}s)")

def finish():
    """Call at the very end of a script."""
    total = time.time() - _script_start
    _write(f"FINISHED {_script_name}  — total {total:.1f}s  [{datetime.now().strftime('%H:%M:%S')}]")
    print(f"[LOG] {_script_name} finished in {total:.1f}s")

def error(msg: str):
    """Log an error."""
    _write(f"  ERROR: {msg}")
    print(f"[LOG][ERROR] {msg}")

def _write(msg: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
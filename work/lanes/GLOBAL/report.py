"""Refresh the current completed GLOBAL handoff and append only new receipt hashes."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent/"finish_current.py"),run_name="__main__")

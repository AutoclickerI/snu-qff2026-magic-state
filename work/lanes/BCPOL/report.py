"""Render the current BCPOL report."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent/"v35/report35.py"))

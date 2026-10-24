"""Run the original EVAL/exact2.py CLI, with cache writes kept in LNS."""
from core import *
# No evaluator monkeypatch is installed by importing core/fast_third.
exact2.main()

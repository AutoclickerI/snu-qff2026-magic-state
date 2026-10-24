#!/usr/bin/env python
"""ablate_multi.py with grid adjacency ignored (grid-free pricing only)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "EVAL"))
import model  # noqa: E402,F401
import tprep.qasm  # noqa: E402

tprep.qasm.adjacent = lambda a, b: True
import ablate_multi  # noqa: E402

if __name__ == "__main__":
    ablate_multi.main()

#!/usr/bin/env python
"""exact2.py with grid adjacency ignored (grid-free pricing only; never for submissions)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "EVAL"))
import model  # noqa: E402,F401  (puts tprep on the path)
import tprep.qasm  # noqa: E402

tprep.qasm.adjacent = lambda a, b: True
import exact2  # noqa: E402

if __name__ == "__main__":
    exact2.main()

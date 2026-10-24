import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'))
sys.path.insert(0,str(HERE/'inputs/EVAL'))
import tprep.qasm
if '--grid-free' in sys.argv:
 sys.argv.remove('--grid-free');tprep.qasm.adjacent=lambda a,b:True
import exact2
exact2.main()

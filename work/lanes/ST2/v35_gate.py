import sys,runpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v
sys.argv=[str(v.H/'gate_budget.py'),*sys.argv[1:]];runpy.run_path(str(v.H/'gate_budget.py'),run_name='__main__')

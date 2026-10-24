"""Run the unchanged fast_check CLI with its xtim cache confined to ST1."""
from common import *
import runpy
sys.argv[0]=str(ROOT/'work/fast_check.py')
runpy.run_path(sys.argv[0],run_name='__main__')

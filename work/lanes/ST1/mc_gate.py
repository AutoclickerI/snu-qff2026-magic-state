"""Run the unchanged prescribed MC3 with cache confined to ST1."""
from common import *
import runpy
runpy.run_path(str(H/'mc3.py'),run_name='__main__')

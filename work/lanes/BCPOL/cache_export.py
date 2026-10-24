"""Isolated full-model preparation for boundary_api; JSON on stdout, no writes."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
from cache import setup
import json
if __name__=='__main__':
 ev,b,classes,prep,external,fingerprint=setup(Path(sys.argv[1]))
 json.dump(dict(fingerprint=fingerprint,channels=[[(int(k),float(ev.fp[i])) for i,k in items] for items in prep.values()],n_classes=len(classes)),sys.stdout)

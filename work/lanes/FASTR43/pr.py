import sys
from fr import *
procs=int(sys.argv[1]); 
for s in sys.argv[2:]:
    r=price(C/s,procs); print(s, json.dumps(r), flush=True)

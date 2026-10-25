import sys
from fr import *
for s in sys.argv[2:]:
    r=speed(C/s,int(sys.argv[1]),2); print(s, r['median_seconds_per_1e6'], r['classification'], flush=True)

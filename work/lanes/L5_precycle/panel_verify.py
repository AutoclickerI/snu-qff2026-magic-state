"""Independent MC panel for finalists; each seed uses the official shot count and noise."""
from search_v10 import *
p=argparse.ArgumentParser();p.add_argument('labels',nargs='+');p.add_argument('--procs',type=int,default=12);p.add_argument('--count',type=int,default=12);args=p.parse_args()
seeds=tuple(range(6000,6000+1000*args.count,1000))
for label in args.labels:
    check_one(label,args.procs,seeds,10**8,'validation_panel')

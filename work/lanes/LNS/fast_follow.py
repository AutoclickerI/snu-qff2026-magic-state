"""Exact local search with pre-stage RX kept, for normal judge sampling speed."""
from moves import *
from round_lns import proposals
import hops
import argparse

def make(base):
 parent=base['meta']['lns_result']['total']
 for gen in [hops.moves,timing_moves,commute_moves,init_moves,phase_moves,readout_moves,detector_moves,proposals]:
  for c,d in gen(base):
   if c is None:continue
   # Keep the pre-stage q8 RX; other reuse variants still receive runtime checks.
   if d.get('move')=='reuse_mx'and d.get('q')==8:continue
   d.update(parent_total=parent,local_track=True)
   yield c,d
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--label',default='fast_follow');a=ap.parse_args();batch(list(make(read(a.stem))),a.label,a.workers)

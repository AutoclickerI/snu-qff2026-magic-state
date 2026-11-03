"""Explicit coherent route from native v37j source to four-square geometry.

The original output q22 is temporarily parked on q28, then swapped with the
q16 state arriving through q22. The other two moves use freshly measured
source cells, optionally reset. Every original source detector is retained.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,hashlib,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for d in ('work/tools','work/lanes/END2_20261027'):sys.path.insert(0,str(ROOT/d))
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem
from joint import emit
OLD=[6,20,19,10,2,22,16]; NEW=[10,20,19,16,2,22,28]
SOURCES={'original':ROOT/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16',
         'contracted':ROOT/'work/lanes/PREFIX2_20261027/retimed/source_aligned_f4c43ebcb17bfa49_d6_20_19_10_2_22_16'}

def build(source='original',reset=False):
 parent=SOURCES[source];ops,dets=f.parse_current(parent.with_suffix('.qasm').read_text());oldbits={o.bit for o in ops if o.bit is not None};assert {317,320,321}<=set.union(*dets)
 def add(k,qs,t):ops.append(f.Op(k,tuple(qs),t))
 add('R',[28],37)
 # q22 -> q28, preserving that state while q16 moves into q22.
 for k,qs,t in [('CX',[22,28],38),('CX',[28,22],39),('CX',[16,22],40),('CX',[22,16],41),
                ('CX',[22,28],42),('CX',[28,22],43),('CX',[22,28],44),
                ('CX',[10,16],42),('CX',[16,10],43)]:add(k,qs,t)
 # q7/q8/q9 were read in Z and their recorded outcomes were postselected 0.
 # An explicit reset version is also emitted for a full-noise comparison.
 if reset:
  for q,t in [(7,41),(8,37),(9,40)]:add('R',[q],t)
 start=42 if reset else 41
 for j,(a,b) in enumerate(((6,7),(7,8),(8,9),(9,10))):
  add('CX',[a,b],start+2*j);add('CX',[b,a],start+2*j+1)
 ops.sort(key=lambda o:(o.time,o.kind,o.qs));occupied={}
 for o in ops:
  if o.kind=='CX':
   a,b=o.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1,o
  for q in o.qs:
   key=(o.time,q);assert key not in occupied,(o,occupied.get(key));occupied[key]=o
 text=emit(ops,dets);raw=raw_check(text,NEW);assert raw['ok'],raw
 name=f'tile_source_{source}_{"reset" if reset else "reuse"}'
 stem=write_stem(text,NEW,H/'tile_boundary',name,source=dict(parent=str(parent),route='q6-7-8-9-10, q10-16, q16-22-28 with q22 parked and swapped',raw=raw))
 release={str(q):max((o.time+1 for o in ops if q in o.qs),default=0) for q in range(36) if q not in NEW}
 lastop={str(q):max((o.time for o in ops if q in o.qs),default=-1)for q in range(36)}
 data_ready={str(q):lastop[str(q)]+1 for q in NEW}
 meta=dict(stem=str(stem),parent=str(parent),source_type=source,measured_cells_reset=reset,data_qubits=NEW,
  roles=dict(D=NEW,A=[9,14,13,15,8,21,27],B=[4,26,18,17,1,23,34],C=[3,32,12,11,7,29,33]),
  square_mask=85,raw=raw,cx=sum(o.kind=='CX'for o in ops),source_cx=sum(o.kind=='CX'for o in ops)-17,
  route_cx=17,ticks=max(o.time for o in ops)+1,release=release,data_ready=data_ready,last_operation=lastop,
  original_source_detector_count=len(dets),original_source_measurements=sorted(oldbits),
  route_operations=[dict(kind=o.kind,qs=list(o.qs),time=o.time)for o in ops if o.kind=='CX' and ((o.qs,o.time)in [((22,28),38),((28,22),39),((16,22),40),((22,16),41),((22,28),42),((28,22),43),((22,28),44),((10,16),42),((16,10),43)] or o.time>=41 and o.qs in [(6,7),(7,6),(7,8),(8,7),(8,9),(9,8),(9,10),(10,9)])],
  qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
  scope='Actual native noisy source and coherent route only. Complete final resource, checks, acceptance and exact score remain required.')
 (H/'tile_boundary'/f'{name}.release.json').write_text(json.dumps(meta,indent=2)+'\n');return meta
if __name__=='__main__':
 for source in SOURCES:
  for reset in (False,True):
   try:
    x=build(source,reset);print(json.dumps({k:x[k] for k in ('stem','raw','cx','ticks','release','data_ready')}),flush=True)
   except Exception as e:
    import traceback;print('ERROR',source,reset,repr(e),traceback.format_exc(),flush=True)

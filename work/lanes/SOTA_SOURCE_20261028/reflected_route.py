"""Reflect native v37j source, then coherently route two adjacent data cells.

Tile roles come from the labeled native geometry solve. All source gates and
measurement identities are preserved under the 6x6 reflection. Reset/reuse
variants are separate, complete noisy source-boundary witnesses.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for d in ('work/tools','work/lanes/END2_20261027'):sys.path.insert(0,str(ROOT/d))
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem
from joint import emit

def reflect(q):return 6*(q//6)+5-q%6
SOURCES={'original':ROOT/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16',
         'contracted':ROOT/'work/lanes/PREFIX2_20261027/retimed/source_aligned_f4c43ebcb17bfa49_d6_20_19_10_2_22_16'}
D=[10,21,28,7,3,19,13];A=[16,15,22,8,9,20,14];B=[11,27,29,1,4,25,12];C=[17,33,23,2,5,26,18]
def build(source,reset):
 parent=SOURCES[source];base,dets=f.parse_current(parent.with_suffix('.qasm').read_text());ops=[f.Op(o.kind,tuple(reflect(q)for q in o.qs),o.time,o.bit) for o in base]
 assert any(o.bit==317 and o.kind=='M' and o.qs==(10,) for o in ops) and {317} in dets
 def add(k,qs,t):ops.append(f.Op(k,tuple(qs),t))
 # q28 held a source helper: explicit reset just before q22's release.
 add('R',[28],39);add('CX',[22,28],40);add('CX',[28,22],41)
 # q10's source read c317 is postselected zero; compare reset and reuse.
 if reset:add('R',[10],41)
 t=42 if reset else 41
 add('CX',[11,10],t);add('CX',[10,11],t+1)
 ops.sort(key=lambda o:(o.time,o.kind,o.qs));seen={}
 for o in ops:
  if o.kind=='CX':
   a,b=o.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1,o
  for q in o.qs:
   key=(o.time,q);assert key not in seen,(o,seen.get(key));seen[key]=o
 text=emit(ops,dets);raw=raw_check(text,D);assert raw['ok'],raw
 name=f'reflected_source_{source}_{"reset" if reset else "reuse"}'
 stem=write_stem(text,D,H/'tile_boundary',name,source=dict(parent=str(parent),reflection='horizontal',route='11→10 and 22→28',raw=raw))
 release={str(q):max((o.time+1 for o in ops if q in o.qs),default=0) for q in range(36) if q not in D}
 data_ready={str(q):max((o.time+1 for o in ops if q in o.qs),default=0) for q in D}
 meta=dict(stem=str(stem),parent=str(parent),source_type=source,reflection='horizontal',reset=reset,data_qubits=D,
  roles=dict(D=D,A=A,B=B,C=C),square_mask=45,raw=raw,cx=sum(o.kind=='CX'for o in ops),source_cx=sum(o.kind=='CX'for o in base),route_cx=4,
  ticks=max(o.time for o in ops)+1,release=release,data_ready=data_ready,detectors=[sorted(z)for z in dets],
  route_operations=[dict(kind='R',qs=[28],time=39),dict(kind='CX',qs=[22,28],time=40),dict(kind='CX',qs=[28,22],time=41)]+([dict(kind='R',qs=[10],time=41)]if reset else[])+[dict(kind='CX',qs=[11,10],time=t),dict(kind='CX',qs=[10,11],time=t+1)],
  qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),scope='Actual reflected native source and four noisy route CX gates. Full resource, terminal and noise score remain required.')
 (H/'tile_boundary'/f'{name}.release.json').write_text(json.dumps(meta,indent=2)+'\n');return meta
if __name__=='__main__':
 for source in SOURCES:
  for reset in (False,True):
   try:
    x=build(source,reset);print(json.dumps({k:x[k]for k in ('stem','raw','cx','ticks','release','data_ready')}),flush=True)
   except Exception as e:
    import traceback;print('ERROR',source,reset,repr(e),traceback.format_exc(),flush=True)

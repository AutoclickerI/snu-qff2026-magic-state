"""Full noisy source + native square tail with instantaneous perfect resources.

Only resource encoder gates, resets, and artificial inserted-time waiting are
made perfect. Source, coherent route, data waits and terminal operations keep
their real full noise. The nonlocal resource encoders and noise intervention
make this a diagnostic, not a legal candidate or a global bound.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,copy,contextlib,io,concurrent.futures,traceback
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for d in ('work/tools','work/lanes/END2_20261027','upstream/snu-qff2026-problem'):sys.path.insert(0,str(ROOT/d))
from qtools.evaluator import frontend as f
from partial_square import prep,ideal_contract_check
from joint import emit
from record_contract import complete
from partial_incumbent import diagnose
D=[6,20,19,10,2,22,16];A=[7,21,18,4,8,23,17];B=[12,26,25,11,3,28,15];C=[13,27,24,5,9,29,14]
SOURCES={'original':ROOT/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16', 'contracted':ROOT/'work/lanes/PREFIX2_20261027/retimed/source_aligned_f4c43ebcb17bfa49_d6_20_19_10_2_22_16'}

def build(source,tail):
 ops,dets=f.parse_current(SOURCES[source].with_suffix('.qasm').read_text());assert max(o.time for o in ops)<tail
 # A full-idle barrier is collapsed by the native scheduler. An identity
 # on live D0 at each physical wait tick supplies exactly the same p
 # depolarizing channel as that wire's idle, and advances the global clock.
 for tick in range(max(o.time for o in ops)+1,tail):ops.append(f.Op('ID',(D[0],),tick))
 start=tail; inserted=list(range(start,start+5));terminal=start+5
 for block,plus in ((A,True),(B,False)):prep(ops,block,start,plus)
 # C shortened span(012,034,135,6), with an ideal B->C pre-entangler.
 for i,q in enumerate(C):ops.append(f.Op('RX' if i in (2,4,5,6) else 'R',(q,),start))
 for j,layer in enumerate([[(2,0),(4,3),(5,1)],[(2,1),(4,0),(5,3)]],1):
  for a,b in layer:ops.append(f.Op('CX',(C[a],C[b]),start+j))
 ops += [f.Op('CX',(b,c),start+4)for b,c in zip(B,C)]
 for i in range(7):
  ops += [f.Op('CX',(D[i],A[i]),terminal),f.Op('CX',(B[i],C[i]),terminal),
          f.Op('CX',(B[i],D[i]),terminal+1)]
  if i<6:ops.append(f.Op('CX',(C[i],A[i]),terminal+1))
 bit=max((o.bit for o in ops if o.bit is not None),default=-1)+1;first=bit
 for block,k in ((A,'M'),(B,'MX'),(C,'MX')):
  for q in block:ops.append(f.Op(k,(q,),terminal+2,bit));bit+=1
 ops.sort(key=lambda o:o.time);f.DATA=D
 native,labels=f.native_text(ops);_,steps,_=f.schedule(native)
 assert all(st[0][1]==o.time for o,st in zip(labels,steps)), [(o.time,st[0][1],o.kind,o.qs)for o,st in zip(labels,steps)if st[0][1]!=o.time][:8]
 model=f.make_model(*f.parse_current(emit(ops,dets)));contract=complete(model,dets)
 extra=[r for r in contract['missing'] if any(b>=first for b in r['bits'])];assert all(not r['reference']for r in extra)
 dets.extend(set(r['bits'])for r in extra);text=emit(ops,dets);raw=ideal_contract_check(text,D);assert raw['ok'],raw
 stem=H/'diagnostic'/f'unmoved_six_{source}_tail{tail}';stem.parent.mkdir(exist_ok=True);stem.with_suffix('.qasm').write_text(text)
 meta=dict(data_qubits=D,ideal_contract=raw,gate_valid=False,diagnostic_only=True,square_mask=63,inserted_ticks=inserted,
  source=str(SOURCES[source]),resource_state='Perfect instantaneous A plusL, B zeroL, shortened C and ideal B-to-C pre-entangler',actual_terminal_times=[tail,tail+1,tail+2],
  resource_contract=extra,scope='Noisy real source and route, noisy terminal and real waits; nonlocal perfect instantaneous resource. Not a candidate.')
 stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');return stem

def run(job):
 source,tail=job
 try:
  stem=build(source,tail)
  with contextlib.redirect_stdout(io.StringIO()):r=diagnose(stem)
  return dict(source=source,tail=tail,stem=str(stem),raw=r['ideal_contract']['ok'],loss=r['loss'],acceptance=r['acceptance'],
              single_fault_numerator=r['single_fault_numerator'],harmful_single_components=len(r['harmful_single_components']))
 except Exception as e:return dict(source=source,tail=tail,error=repr(e),traceback=traceback.format_exc())
if __name__=='__main__':
 jobs=[(s,t)for s in SOURCES for t in (41,42,44,46)];rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for row in pool.map(run,jobs):
   rows.append(row);print(json.dumps(row),flush=True);(H/'unmoved_six_headroom_results.json').write_text(json.dumps(rows,indent=2)+'\n')

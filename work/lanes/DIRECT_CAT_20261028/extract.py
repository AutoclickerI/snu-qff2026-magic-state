import os,sys,json,collections,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
import smallcat as s
from joint import emit
D=list(range(7));original,_=s.f.parse_current((H/'source_original.qasm').read_text());final,det=s.f.parse_current((R/'work/lanes/SOTA_DETECT_20261028/deep_extra_best/flag_9_0_5.qasm').read_text())
def sig(o):return o.kind,o.qs,o.bit
need=collections.Counter(map(sig,original));selected=[]
for o in sorted(final,key=lambda o:o.time):
 if need[sig(o)]>0:selected.append(copy.deepcopy(o));need[sig(o)]-=1
assert not any(need.values()),need
extra=[copy.deepcopy(o) for o in final if 35 in o.qs and o.time<=12];assert [(o.kind,o.qs,o.bit) for o in extra]==[('R',(35,),None),('CX',(21,35),None),('CX',(26,35),None),('M',(35,),50)]
selected+=extra;keepbits={o.bit for o in selected if o.bit is not None};ds=[r for r in det if r<=keepbits]
assert set(map(frozenset,ds))==set(map(frozenset,[*s.f.parse_current((H/'source_original.qasm').read_text())[1],{50}]))
# Place all data TDG at latest source-read clock or immediately after each data's last source touch, whichever is later.
last_nontdg=max(o.time for o in selected if o.kind!='TDG');original_tdgs={o.qs[0]:o.time for o in selected if o.kind=='TDG'}
for o in selected:
 if o.kind=='TDG':o.time=max(last_nontdg,max(x.time for x in selected if x.kind!='TDG' and o.qs[0] in x.qs)+1)
selected.sort(key=lambda o:(o.time,o.kind,o.qs));occ=set()
for o in selected:
 for q in o.qs:assert (o.time,q) not in occ,(o.time,q,o.kind);occ.add((o.time,q))
text=emit(selected,ds);raw=s.ideal_contract_check(text,D);print('raw',raw,flush=True)
stem=H/'source_direct';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':D,'abstract':True,'source_reference':'deep_extra_best/flag_9_0_5','source_ops':len(selected),'source_checks':len(ds),'last_non_tdg':last_nontdg,'tdg_original':original_tdgs,'tdg_new':{str(o.qs[0]):o.time for o in selected if o.kind=='TDG'}},indent=2)+'\n')
s.f.DATA=D;model=s.f.make_model(*s.f.parse_current(text));audit=s.record_contract.singles(model);print('c1',audit['c1'],'harmful',len(audit['harmful_faults']),flush=True)
p=s.exact(stem);print('PRICE',p['loss'],p['acceptance'],flush=True);(H/'source_direct.result.json').write_text(json.dumps({'raw':raw,'singles':audit,'exact':p,'ops':len(selected),'cx':sum(o.kind=='CX' for o in selected),'clocks':max(o.time for o in selected)+1},indent=2)+'\n')

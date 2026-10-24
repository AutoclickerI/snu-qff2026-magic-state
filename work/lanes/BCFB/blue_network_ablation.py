import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['BCFB_BLUE_DB']='neighbors.sqlite'
import json,collections
from blue_evaluate import price,H
from build import S,native_times
old=json.loads((H.parent/'finalists/fast_d15_c105_s526_00356.json').read_text())['prep'];out=[]
for c,tag in [('v25k','blue_d15_c105_s706_00405'),('v26n','blue_d15_c90_s712_00074')]:
 p=H/'finalists'/tag;md=json.loads(p.with_suffix('.json').read_text());d=md['prep'];a=collections.Counter(tuple(e) for l in old['ops'] for e in l);b=collections.Counter(tuple(e) for l in d['ops'] for e in l)
 port=json.loads((H/'finalists'/(c+'_fast_d15_c105_s526_00356_preserve_rt1')).with_suffix('.json').read_text());opt=dict(md['options'],force_times=port['non_BC_time_changes'],retime_window=0)
 row=price(d,opt,'ablate_'+c+'_86_moved','blue_network_ablation',threshold=1)
 wires={str(q):dict(old=[e for l in old['ops'] for e in l if q in e],new=[e for l in d['ops'] for e in l if q in e]) for q in d['cells']}
 rec=dict(context=c,stem=tag,removed=[dict(edge=list(e),count=n) for e,n in (a-b).items()],added=[dict(edge=list(e),count=n) for e,n in (b-a).items()],wire_orders=wires,retimed_score=row);out.append(rec);print(c,rec['removed'],rec['added'],row.get('total'),flush=True)
(H/'network_ablation.json').write_text(json.dumps(out,indent=2))

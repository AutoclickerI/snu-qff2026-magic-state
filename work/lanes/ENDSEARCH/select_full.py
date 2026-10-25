import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,hashlib,subprocess,sys
from build_candidates import H,perfect,suffix
rows=[json.loads(l) for pat in ('search_*.jsonl','ties_*.jsonl') for p in (H/'logs').glob(pat) for l in p.read_text().splitlines() if l]
choices={}
for label,pred in [
 ('square',lambda t:t['n']==4 and t['output']==0 and t['product_plus_mask']>=0 and t['second_order_p2']<26.7),
 ('square_leaf',lambda t:t['n']==5 and t['output']==0 and t['product_plus_mask']>=0 and t['logical_resource_guard'] and t['second_order_p2']<26.7),
 ('tree',lambda t:t['graph']=='tree' and t['output']==0 and t['product_plus_mask']>=0 and t['logical_resource_guard']),
 ('unmeasured',lambda t:t['terminal']=='unmeasured' and t['output']==0 and t['product_plus_mask']>=0)]:
    tt=[t for t in rows if pred(t)]
    if not tt:continue
    choices[label]=min(tt,key=lambda t:(t['second_order_p2'],len({x//4 for x in t['dangerous_resource_paulis']}),-len(t['logical_detectors']),t['depth'],t['n']))
for label,t in choices.items():
    perfect(t,'chosen_round_'+label)
    name=suffix(t,'suffix_'+label)
    print(label,t,flush=True)
    for nn in ('chosen_round_'+label,name):
        p=subprocess.run([sys.executable,str(H/'price.py'),nn,'1'],capture_output=True,text=True)
        (H/'logs'/f'{nn}.process.log').write_text(p.stdout+p.stderr)
        print(p.stdout if not p.returncode else p.stderr,flush=True)
(H/'choices.json').write_text(json.dumps(choices,indent=2)+'\n')

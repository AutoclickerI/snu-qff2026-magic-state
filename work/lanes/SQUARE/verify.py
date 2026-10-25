import sys,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'sparse'))
import frontend as fa
receipts=[json.loads(p.read_text()) for p in sorted((H/'logs').glob('*.receipt.json'))]
checked={}
for r in receipts:
    p=H/(r['stem']+'.qasm');sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==r['sha256']
    if sha in checked:continue
    ops,_=fa.parse_current(p.read_text());native,_=fa.native_text(ops);_,steps,_=fa.schedule(native)
    assert all(len(ss)==1 and ss[0][1]==o.time for ss,o in zip(steps,ops)),p
    checked[sha]=dict(stem=r['stem'],native_ticks=max(o.time for o in ops)+1)
grid=[r for r in receipts if r['stem'].split('/')[-1].startswith('grid_') and not any(k in r['metadata'] for k in ('noise_start','perfect_resource','perfect_data_wait','dropped_detectors'))]
ft=[r for r in grid if r['single_fault_loss']<1e-12]
best=min(ft,key=lambda r:r['loss'])
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
sys.path.insert(0,str(H))
import fast_check
p=H/(best['stem']+'.qasm')
rep=fast_check.check(p.read_text(),best['metadata']['data_qubits'],shots=10**6,procs=1)
judge=dict(stem=best['stem'],sha256=best['sha256'],shots=10**6,format_ok=rep.format_ok,class_ok=rep.class_ok,
           correctness_ok=rep.correct_ok,gates_ok=bool(rep.format_ok and rep.class_ok and rep.correct_ok),passed=rep.passed,
           acceptance=rep.acceptance,loss=rep.score,sem=rep.sem,cx=rep.n_2q)
out=dict(checked_circuits=checked,best_first_order_safe_grid=best['stem'],judge=judge)
(H/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(judge),flush=True)
# Exact signature witnesses for the shortened layout's failed repairs.
diagnostic=[]
for name in ('grid_grid_compact_s18_both_s18','grid_grid_compact_fenced_s34_both_s34'):
    import sparse_walsh as sw
    m,e,*_=sw.prepare(H/'builds'/name,True);cache={};bad=[]
    for f in m.faults:
        k=(f['s'],f['d'])
        if k not in cache:cache[k]=e.ntable(*k)
        a,n=cache[k]
        if n is not None and n[f['e']]>1e-9 and f['p']:
            bad.append(dict(label=f['label'],time=m.labels[f['ins']].time,detector_flip_mask=f['d'],rotation_flip_mask=f['s'],
                output_z_syndrome=f['e']&7,output_x_syndrome=(f['e']>>3)&7,z_parity=(f['e']>>6)&1,x_parity=(f['e']>>7)&1,
                record_flips=f['record_flips'],loss=float(n[f['e']]),probability=f['p']))
    diagnostic.append(dict(stem=name,harmful_single_faults=bad))
(H/'fault_witnesses.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
print(json.dumps(diagnostic),flush=True)

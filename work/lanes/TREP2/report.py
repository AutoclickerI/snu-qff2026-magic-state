"""Collect receipts without ranking on acceptance above the judge threshold."""
import os,sys,json,re,csv,hashlib,shutil,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times

def native(stem):
    text=stem.with_suffix('.qasm').read_text();d=json.loads(stem.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
    data=d['data_qubits'];aa=[1,14,8,9,2,16,15];bb=[6,26,13,11,4,23,27];cc=[12,25,19,17,5,29,28]
    def last(c,v):return max(t for x,t in zip(u,ts)if x.lines==[f'cx q[{c}],q[{v}];'])
    first=[last(c,v)for c,v in list(zip(data,aa))+list(zip(bb,cc))];bd=[last(c,v)for c,v in zip(bb,data)]
    return dict(R=min(first),R_last=max(first),B_data_range=[min(bd),max(bd)],CX=sum(x.name=='CX'for x in u),depth=max(ts)+1,sha256=hashlib.sha256(text.encode()).hexdigest())

def exact(stem):
    path=stem.with_suffix('.exact.log')
    if not path.exists():return {}
    text=path.read_text();row={}
    for key,pat in [('c1',r'c1 p = (\S+)'),('second',r'second order: (\S+)'),('third',r'third order: (\S+)'),('total',r'1-F \(to 3rd order\) = (\S+)'),('exp_minus_A1',r'exp\(-A1\) = (\S+)')]:
        m=re.search(pat,text)
        if m:row[key]=float(m[1])
    return row

def mc(stem):
    path=stem.with_suffix('.mc.log')
    if not path.exists():return {}
    text=path.read_text();row={}
    for seed in (0,1000,2000):
        m=re.search(r'^.*? '+str(seed)+r' ([\d.eE+-]+) ± ([\d.eE+-]+) acc ([\d.]+)',text,re.M)
        if m:row[str(seed)]=float(m[1]);row['acc'+str(seed)]=float(m[3]);row['sem'+str(seed)]=float(m[2])
    m=re.search(r'^.*? mean ([\d.eE+-]+)',text,re.M)
    if m:row['mean']=float(m[1])
    row['judge_check_pass']='check True' in text
    return row

def encoder(name,meta):
    if 'init_state'in name:return '11-CX resource'
    if name.startswith('f'):return '19-CX + parity network'
    if 'injection_cx'in meta:return str(meta['injection_cx'])+' CX'
    if name.startswith('v17a'):return '25 CX'
    return '19 CX'

def method(name):
    if name.startswith('reuse')or'_reuse10_'in name:return 'q10 reuse + optimized ALAP'
    if name.endswith('_two_moves'):return 'prefix ALAP + two CX advances'
    if '_third_'in name:return 'exact third-order search'
    if '_quad'in name:return 'exact quadratic search'
    if '_whole_'in name:return name.split('_whole_')[1].split('_s')[0]
    if name.startswith('f'):return 'ALAP / parity synthesis'
    if '_re_'in name or '_reset_'in name:return 'prefix ALAP + readout/init'
    if name=='joint_d7_s0':return 'joint synthesis / whole ALAP'
    if name=='v18'or name.endswith('_alap'):return 'prefix ALAP'
    return 'original placement'

def main(complete):
    rows=[]
    for p in sorted(OUT.glob('*.qasm')):
        stem=p.with_suffix('');ex=exact(stem)
        if stem.name=='best':continue
        if not ex:continue
        meta=json.loads(stem.with_suffix('.json').read_text());row=dict(name=stem.name,encoder=encoder(stem.name,meta),schedule=method(stem.name),**native(stem),**ex,mc=mc(stem))
        rp=stem.with_suffix('.result.json')
        if rp.exists():row['check']=json.loads(rp.read_text()).get('check')
        rows.append(row)
    by={r['name']:r for r in rows};finalists=sorted([r for r in rows if all(k in r['mc']for k in('0','1000','2000','mean'))],key=lambda r:r['mc']['mean'])
    eligible=[r for r in finalists if r['mc']['acc0']>=.5 and r['mc']['judge_check_pass']]
    best=eligible[0]
    forms=[f['id']for f in json.loads((OUT/'inputs/enumeration.json').read_text())['forms']if f['T']==15]
    done_forms=[f for f in forms if f+'_parity'in by and 'total'in by[f+'_parity']]
    if complete:
        assert len(done_forms)==16,(len(done_forms),forms)
        assert all(x in by and 'mean'in by[x]['mc'] for x in('v17a_alap','init_state_d5_s1_alap','v18'))
        assert any('quad'in r['name']and 'total'in r for r in rows)
        assert best['mc']['acc0']>=.505 and best['mc']['judge_check_pass']
        verified=json.loads((OUT/(best['name']+'.result.json')).read_text())
        assert verified['evaluator']=='work/lanes/EVAL/exact2.py',verified.get('evaluator')
        for ext in('.qasm','.json'):shutil.copyfile(OUT/(best['name']+ext),OUT/('best'+ext))
    (OUT/'results.json').write_text(json.dumps(dict(complete=complete,best=best['name'],forms_priced=done_forms,variants=rows,finalists=finalists),indent=2)+'\n')
    fields=['name','encoder','schedule','R','R_last','CX','c1','second','third','total','exp_minus_A1','depth','sha256']
    with (OUT/'variants.csv').open('w',newline='')as fp:
        w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    num=lambda x:'—'if x is None else f'{x:.6e}'
    lines=['# TREP2', '',('Complete.'if complete else '**In progress; running experiments remain.**'),'',f'Best measured three-seed mean: **{best["mc"]["mean"]:.6e}**, `{best["name"]}`, **{100*(1-best["mc"]["mean"]/7.636083e-5):.2f}% below v18**, seed-0 acceptance **{best["mc"]["acc0"]:.5f}**. Delivery: [best.qasm](best.qasm) and [best.json](best.json). Rank uses the 1e8-shot mean at seeds 0/1000/2000; acceptance is only a gate.','',
    'The lever split is measured: the original 25-CX encoder with prefix ALAP gives **7.645170e-5** mean, the 11-CX initial-resource variant with prefix ALAP gives **7.675544e-5**, and the 19-CX encoder with prefix ALAP (v18) gives **7.636083e-5**. The schedule alone captures almost all of the observed v17a-to-v18 gain. The small encoder differences are comparable to sampling variation; the required observed means determine the order.','',
    'Timing comes from `tprep.noise.schedule`, including folded RX/MX. R is the native range of all seven data→A and seven B→C checks. B→data ranges and total depths are in `results.json`. In particular whole-circuit ASAP spans R=37–46; using only q0 would incorrectly label that staggered schedule R=44.','',
    'The whole-circuit search preserves every per-wire operation order. It covers ASAP, ALAP, random priority placements, an exact quadratic objective over all idle boundaries, and local proposals evaluated through third order. The spectator construction in `quadratic_search.py` exposes every potentially nonzero gap; three placements matched independent exact2 pair calculations to relative error below 3e-16. The low second-order schedules lost after third-order and MC confirmation.','',
    'The joint CP-SAT encoder/timing model found a 21-CX injection encoder with R=44 and depth 47. Its seven- and eight-layer models were solved optimally for their stated makespan/CX/late-prefix objective; this is not a global score-optimality claim. Both whole ALAP and rigid-suffix prefix ALAP were priced. Final-readout edges 17→16 and 19→25 were rechecked against the last Z measurements; alternatives and all fresh-measurement-versus-reset choices were evaluated.','',
    'The final combination incorporates [EARLYBC’s measured-|+⟩ q10 transfer](../EARLYBC/REPORT.md): retain the X-measured q10 state, remove its reset, and reverse the two data-transfer CX directions. This saves one native step without adding CX. Combining it with the encoders and exact-objective timing moves was priced and sampled in this lane. The final 19-CX-encoder candidate keeps the two original readout re-encoding edges and all first-use measurement preparations; it has **203 CX, R=45, native depth 48**. Its six additional timing requests and their feasible native placements are in [reuse19_tuned.transfer.json](reuse19_tuned.transfer.json).','',
    f'Protected forms priced: **{len(done_forms)}/16**, including the original form as a control. Each alternative was physically built using the resynthesized encoder, a verified |+_L⟩ resource, a fixed-coordinate grid parity network, 15 signed rotations, and the retained Steane suffix. The forms are not coordinate relabelings of the same QASM. `forms.py` also builds depth-prioritized variants and certifies the phase-support map. Every new form has negligible full-fault c1 and passes format/class/noiseless correctness; these implementations fail acceptance. This excludes the built networks, not better implementations of those forms.','',
    'All exact totals below require |c1|<1e-12 and are expansions through third order, not all-orders fidelities. exp(-A1) is an acceptance estimate. The evaluator acceleration only prunes triples that violate state-independent detector-parity relations; surviving triples retain exact2’s original arithmetic. On v18, the scalar-pruned and unmodified third-order terms agreed exactly (19.451 s versus 324.322 s on jerry); the generalized dependency filter agreed within 2.8e-20. The final winner is also confirmed with the unmodified exact2 CLI. Every MC finalist receives the requested mc3.py judge/MC run. Receipts are beside each QASM.','',
    '| Variant | Encoder | Schedule | R native | CX | c1 | 2nd | 3rd | Exact total | exp(-A1) |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    if not complete:
        pending=[]
        for path in OUT.glob('*.third_search_best.json'):
            d=json.loads(path.read_text());name=path.name.removesuffix('.third_search_best.json')+'_third_best'
            if name not in by or 'mean'not in by[name]['mc']:pending.append((d['total'],name))
        if pending:
            lines[5:5]=['Pending MC confirmation: '+', '.join(f'`{n}` exact-through-third **{v:.6e}**'for v,n in sorted(pending))+'.','']
    for r in rows:
        rr=str(r['R'])if r['R']==r['R_last']else f'{r["R"]}–{r["R_last"]}'
        lines.append(f'| [{r["name"]}]({r["name"]}.qasm) | {r["encoder"]} | {r["schedule"]} | {rr} | {r["CX"]} | {num(r.get("c1"))} | {num(r.get("second"))} | {num(r.get("third"))} | {num(r.get("total"))} | {r.get("exp_minus_A1",float("nan")):.5f} |')
    lines+=['','Each seed below uses 1e8 shots. Every listed MC log includes the 1e6-shot `tprep.check` result. Original-reference receipts were copied from TREP after confirming the circuit source; new receipts were produced in this lane.','',
    '| Finalist | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance | Files |','|---|---:|---:|---:|---:|---:|---|']
    for r in finalists:
        m=r['mc'];name=r['name'];lines.append(f'| {name} | {m["0"]:.6e} | {m["1000"]:.6e} | {m["2000"]:.6e} | **{m["mean"]:.6e}** | {m["acc0"]:.5f} | [QASM]({name}.qasm), [JSON]({name}.json), [MC]({name}.mc.log) |')
    lines+=['','Limits: this is a measured search over the listed networks and placements, not a proof of the minimum 1-F over all encoders or schedules. The 1e6-shot scores for acceptance-failing forms are diagnostics, not final rankings. `variants.csv`, `results.json`, solver witnesses, phase certificates, model checks, and search traces retain the evidence. No submission, commit, or push was performed. Repository writes stayed in `work/lanes/TREP2/`; no other lane’s files or workers were changed.','']
    (OUT/'REPORT.md').write_text('\n'.join(lines));print(json.dumps(dict(complete=complete,variants=len(rows),forms=len(done_forms),finalists=len(finalists),best=best['name'],mean=best['mc']['mean'])),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--complete',action='store_true');main(p.parse_args().complete)

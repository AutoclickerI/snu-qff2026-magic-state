"""Lane L5 experiments. All artifacts are confined to this directory."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path('/home/jihoon/competitions/quantumn/work')
HERE = ROOT / 'lanes/L5_precycle'
sys.path.insert(0, str(ROOT))
import json, time, copy, random, math, hashlib
import tprep
import batch_score, cultiv_port as cp
from qcirc import Circ
from fast_check import check
from sched_report import report as schedule_report
BASE_SCORE=0.0001310302140991363
BASE_N2Q=113
SPEC={'kind':'gen2','file':str(ROOT/'gen2_t1c13+t2c42_8_1792739653.json'),'idx':0}

def base():
    return batch_score.make(SPEC)[0]

def emit(ops, template):
    c=Circ(template.n)
    c.nbits=template.nbits
    c.detectors=copy.deepcopy(template.detectors)
    c.postselect=copy.deepcopy(template.postselect)
    c.frame=copy.deepcopy(template.frame)
    for kind, qs, b in ops:
        if kind=='cx': c.cx(*qs)
        elif kind=='RX': c.rx(*qs)
        elif kind=='R': c.reset(*qs)
        elif kind=='barrier': c.barrier(*qs)
        elif kind in ('M','MX'):
            if kind=='MX': c.ops.append(f'h q[{qs[0]}];')
            c.ops.append(f'measure q[{qs[0]}] -> c[{b}];')
            c.sops.append((kind,qs,b))
        else: c.g(kind[2:],*qs)
    return c

def from_times(ops, times, template):
    used=sorted({q for k,qs,b in ops for q in qs})
    out=[]
    for t in range(max(times)+1):
        out.extend(op for op,s in zip(ops,times) if s==t)
        if t<max(times):out.append(('barrier',tuple(used),None))
    return emit(out,template)

def report():
    rows=[]
    if (HERE/'results.jsonl').exists():
        rows=[json.loads(l) for l in (HERE/'results.jsonl').read_text().splitlines()]
    now=time.strftime('%Y-%m-%d %H:%M:%S KST',time.gmtime(time.time()+9*3600))
    lines=['# Lane L5: pre-cycle optimization','',f'Updated {now}.',
      '', 'Scope: injection, double-cat check, and their boundary with the v6 final cycle. No submissions. All generated files stay in this lane. At most one parent plus seven worker processes; numerical-library threads capped at one.',
      '', 'Baseline reference: v6, 1-F = 0.0001310302140991363; 113 CX. Official setting is 100,000,000 shots, seed 0, unmodified real-grid STANDARD noise. A candidate is eligible only with passed=True and fault_scan c1=0. Ranking uses score rounded to 3 significant figures, then CX count.',
      '', '| Change | 1-F (official) | Δ vs v6 | 2q | Acceptance | passed | c1 | Depth | Eligible win |',
      '|---|---:|---:|---:|---:|---|---:|---:|---|']
    for r in rows:
        score=r.get('score')
        f=lambda v: f'{v:.10g}' if isinstance(v,(int,float)) else '—'
        lines.append(f"| {r['label']} | {f(score)} | {f(score-BASE_SCORE) if score is not None else '—'} | {r.get('n_2q','—')} | {f(r.get('acceptance'))} | {r.get('passed')} | {f(r.get('c1'))} | {r.get('depth','—')} | {r.get('winner',False)} |")
    wins=[r for r in rows if r.get('winner')]
    lines += ['', '## Verified improvements', '']
    if not wins: lines += ['None measured yet.']
    for r in sorted(wins,key=lambda r:(float(f"{r['score']:.3g}"),r['n_2q'])):
        lines.append(f"- [{r['label']}]({r['label']}.qasm), [metadata]({r['label']}.json): {r['score']:.12g}, {r['n_2q']} CX, c1={r['c1']}.")
    if (HERE/'NOTES.md').exists():lines+=['', (HERE/'NOTES.md').read_text()]
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')

def evaluate(label,c,notes='',scan=True):
    text=c.text() if isinstance(c,Circ) else c
    qpath=HERE/f'{label}.qasm'
    qpath.write_text(text)
    start=time.time()
    rep=check(text,cp.DATA,shots=10**8,seed=0,procs=7)
    row={'label':label,'data_qubits':cp.DATA,'score':rep.score,'sem':rep.sem,'acceptance':rep.acceptance,
      'n_2q':rep.n_2q,'passed':rep.passed,'shots':10**8,'seed':0,'notes':notes,'report':str(rep)}
    row['depth'],_,row['idle_total'],row['tail']=schedule_report(text,cp.DATA,quiet=True)
    if rep.passed and scan:
        fs=tprep.fault_scan(text,cp.DATA,processes=7)
        row.update(c1=fs.c1,n_faults=fs.n_faults,fault_report=str(fs))
    row['seconds']=time.time()-start
    row['winner']=bool(row['passed'] and row.get('c1')==0 and (float(f"{row['score']:.3g}"),row['n_2q'])<(float(f'{BASE_SCORE:.3g}'),BASE_N2Q))
    (HERE/f'{label}.json').write_text(json.dumps(row,indent=2)+'\n')
    with (HERE/'results.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    report()
    print(json.dumps({k:v for k,v in row.items() if k not in ('report','fault_report')}),flush=True)
    if not rep.passed:print(rep,flush=True)
    return row

if __name__=='__main__':
    report()
    evaluate('v6_recheck',(ROOT/'submissions/v6_gen2_extras.qasm').read_text(),'Exact submitted baseline')

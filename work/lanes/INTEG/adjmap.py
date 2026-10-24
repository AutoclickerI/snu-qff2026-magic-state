"""Run the all-orders adjoint on c/<name> and print channels mapped to (qubit, tick, op)."""
import os, sys, json, math
from pathlib import Path
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
SP = H.parent / 'MAIN' / 'sparse'
sys.path.insert(0, str(SP))
os.chdir(SP)
import sparse_walsh as sw
import adjoint_ablation as aa

name = sys.argv[1]
st = H / 'c' / name
out = H / 'res' / (name + '.adjoint.json')
if not out.exists():
    aa.run(st, out, 72)
d = json.loads(out.read_text())
m = sw.prepare(st, True)[0]
rows = []
for r in d['channel_ablations']:
    ch = r['original_noise']
    lab = m.labels[ch['ins']]
    n = None
    if ch['name'] == 'DEPOLARIZE1' and ch['jl'] > 2:
        pass
    rows.append(dict(ch=r['channel'], name=ch['name'], p=ch['p'], qs=ch['qs'], t=lab.time, op=lab.kind, opqs=list(lab.qs),
                     jl=ch['jl'], gain=r['hypothetical_loss_reduction'], dacc=r['perfect_channel_acceptance'] - d['acceptance']))
(H / 'res' / (name + '.adjmap.json')).write_text(json.dumps(rows))
rows.sort(key=lambda r: -r['gain'])
for r in rows[:int(sys.argv[2]) if len(sys.argv) > 2 else 80]:
    nrep = round(math.log(1 - 4 * r['p'] / 3) / math.log(1 - 4e-3 / 3)) if r['name'] == 'DEPOLARIZE1' else ''
    print(f"{r['gain']:.3e} {r['dacc']:+.5f} {r['name']:12s} p={r['p']:.2e} n={nrep} qs={r['qs']} after t{r['t']} {r['op']}{r['opqs']} jl{r['jl']}")

import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
import sys, json, re, time, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/lanes/EVAL'))
import xtim
xtim.cache_dir = HERE / '.xtim_cache'
from exact2 import Eval, run, third_order
from model import Basis
from tprep.exact import run as ideal_run, _parity
from tprep.qasm import convert
from tprep.noise import STANDARD

TARGETS = {'v12': ROOT/'work/submissions/v12_L5lns12', 'cand2': ROOT/'work/lanes/ST_BC/cand2'}

def bits(x):
    return [i for i in range(x.bit_length()) if x >> i & 1]

def parity_space(text):
    stimtext, _, errors = convert(text, 36, STANDARD)
    assert not errors
    st, inv, rec, det, _ = ideal_run(stimtext, 36)
    declared = [sum(1 << i for i in d) for d in det]
    b = Basis()
    for d in declared:
        b.add(d)
    independent = list(b.vecs)
    complement = []
    for i in range(len(rec)):
        if b.express(1 << i) is None:
            b.add(1 << i)
            complement.append(1 << i)
    missing, vals = [], []
    max_random_abs = 0.0
    b = Basis()
    for d in independent:
        b.add(d)
    for k in range(1, 1 << len(complement)):
        d = 0
        for i in bits(k):
            d ^= complement[i]
        val = st.expectation(_parity(st, [rec[i] for i in bits(d)]), inv)
        if abs(abs(val) - 1) < 1e-9:
            if b.express(d) is None:
                b.add(d)
                missing.append(d)
                vals.append(val)
        else:
            max_random_abs = max(max_random_abs,abs(val))
    # The QASM clbit numbering differs from measurement-record order.
    names = re.findall(r'measure\s+q\[\d+\]\s*->\s*c\[(\d+)\]', text)
    def clbits(d):
        return [int(names[i]) for i in bits(d)]
    return dict(n_measurements=len(rec), declared_count=len(declared), declared_rank=len(independent),
                full_rank=len(b.vecs), quotient_checked=1 << len(complement),
                independent_records=independent, missing_records=missing,
                independent_clbits=[clbits(d) for d in independent],
                missing_clbits=[clbits(d) for d in missing], missing_values=vals,
                max_random_abs=max_random_abs,
                full_records=list(b.vecs), record_clbits=list(map(int,names)))

def scalar(r):
    return {k: v for k, v in r.items() if isinstance(v, (float, int))}

def main():
    for name, stem in TARGETS.items():
        text = stem.with_suffix('.qasm').read_text()
        data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
        p = parity_space(text)
        (HERE/f'{name}_space.json').write_text(json.dumps(p, indent=2))
        print(name, 'PARITY', json.dumps(p), flush=True)
        t = time.time()
        ev = Eval(text, data)
        r = run(ev, procs=8, third=True)
        r['T3a'], _ = third_order(ev, 8)
        r['loss3'] = r['T3a'] + r['t3bc']
        r['total3'] = r['loss'] + r['loss3']
        r['exp_acc'] = math.exp(-r['A1'])
        out = scalar(r)
        out.update(seconds=time.time()-t, frame=ev.m.frame, n_groups=len(ev.gkeys), n_faults=ev.n_f)
        (HERE/f'{name}_baseline.json').write_text(json.dumps(out, indent=2))
        print(name, 'BASELINE', json.dumps(out), flush=True)

if __name__ == '__main__':
    main()

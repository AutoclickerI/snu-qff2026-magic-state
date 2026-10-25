"""Create the required exact-mean certificate using the installed validated evaluator."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys

from race_identity import file_hash, mean_identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stem', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evaluator', type=Path, default=Path(__file__).parent/'lanes/MAIN/sparse')
    args = parser.parse_args()
    sys.path.insert(0, str(args.evaluator.resolve()))
    import sparse_walsh as sw
    # run() writes a result beside the evaluator. Invoke its pure stages so the
    # only write is the explicit certificate path, also when using a live reader.
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(args.stem, True)
    compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
    rows = []
    for key in [None] + eng.keys:
        states, weights, bound = sw.sparse_kernel(eng,ks,psi,where,key)
        vec, _ = sw.contract_quotient(compiled,states,0 if key is None else sw.emask_for(key),elim['order'])
        rows.append(float(sw.np.dot(weights,vec)/(1 << len(ks))))
    a = rows[0]
    obs = sum(w*b*r for w,b,r in zip(eng.W,eng.beta,rows[1:]))
    loss = (a-obs)/(2*a)
    text = args.stem.with_suffix('.qasm').read_text()
    data = json.loads(args.stem.with_suffix('.json').read_text())['data_qubits']
    obj = dict(identity=mean_identity(text,data),A=a.hex(),N=float(a*loss).hex(),L=float(loss).hex(),
               evaluator={p.name:file_hash(p) for p in sorted(args.evaluator.glob('*.py'))},
               moments=[r.hex() for r in rows])
    args.output.write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(dict(A=a,N=a*loss,L=loss,output=str(args.output))))


if __name__ == '__main__':
    main()

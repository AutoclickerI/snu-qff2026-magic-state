"""Stage 1: build all 14 partially coherent C contracts on v36h and write evaluator specs; run a slice of the jobs.
usage: stage1.py build            -> s1/<name>.{qasm,json}, s1/jobs.json
       stage1.py run <i> <n> <procs> -> runs jobs i, i+n, ... ; appends to s1/res_<i>.jsonl (skips done ones)"""
import sys, json, itertools, os
from pathlib import Path
import build1, lin
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PCC/ev')
D = Path('/home/jihoon/competitions/quantumn/work/lanes/PCC/s1')
HELP = [18, 31, 35, 34]


def subspaces():
    words = [w for w in lin.C2 if w]
    out = [[w] for w in words]
    seen = set()
    for a, b in itertools.combinations(words, 2):
        S = frozenset({0, a, b, a ^ b})
        if S not in seen:
            seen.add(S)
            out.append(sorted([a, b]))
    return out


def readout_drop(stem, meta):
    from frontend import parse_current
    ops, _ = parse_current(Path(str(stem) + '.qasm').read_text())
    sup = set(meta['support'])
    helpers = {build1.COPY[i][0] for i in build1.COPY if i not in sup}
    cells = set(build1.C)
    drops = set()
    for o in ops:
        qs = set(o.qs)
        if o.time in (46, 47) and qs & (cells | helpers):
            drops.add((o.time, tuple(o.qs)))
        if o.time == 45 and qs & helpers and o.kind in ('R', 'RX'):
            drops.add((o.time, tuple(o.qs)))
    return [[t, list(q)] for t, q in sorted(drops)]


def build():
    jobs = []
    for basis in [[]] + subspaces():
        name = 'k0' if not basis else 'v' + '_'.join(map(str, basis))
        meta = build1.build(basis, str(D / name))
        ops, _ = lin.load(str(D / name))
        st = lin.cstate(lin.simulate(ops, 45, nq=48), nq=48)
        V = set(meta['V']) - {0}
        assert st['B0L'] and set(st['X']) == V and st['rZ'] == 7 - len(basis), (name, st)
        mq, rq = meta['map_qubits'], meta['readout_qubits']
        ra = readout_drop(D / name, meta)
        base = dict(ins_tick=44, drop_qubits=mq)
        jobs.append(dict(stem=str(D / name), name=name + ':a', spec=dict(base, name=name + ':a', drop_qubits=mq + rq, drop_ops=ra)))
        if basis:
            jobs.append(dict(stem=str(D / name), name=name + ':b', spec=dict(base, name=name + ':b')))
            kc = [[44, [mq[j], build1.C[i]]] for j, i in enumerate(meta['support'])]
            jobs.append(dict(stem=str(D / name), name=name + ':c', spec=dict(base, name=name + ':c', keep_ops=kc)))
    (D / 'jobs.json').write_text(json.dumps(jobs, indent=1))
    print(len(jobs), 'jobs')


def build2():
    """controls: per V, copies of supp(V) removed with no X check (strip); (b) with an ideal readout block"""
    jobs = []
    for basis in subspaces():
        name = 'v' + '_'.join(map(str, basis))
        meta = json.loads((D / (name + '.json')).read_text())
        sup = meta['support']
        sname = 'strip' + ''.join(map(str, sup))
        if not any(j['name'] == sname + ':s' for j in jobs):
            build1.build([], str(D / sname), sup)
            jobs.append(dict(stem=str(D / sname), name=sname + ':s',
                             spec=dict(name=sname + ':s', ins_tick=44, drop_qubits=[build1.MAPQ[0]])))
        mq, rq = meta['map_qubits'], meta['readout_qubits']
        jobs.append(dict(stem=str(D / name), name=name + ':bi',
                         spec=dict(name=name + ':bi', ins_tick=44, drop_qubits=mq + rq)))
    (D / 'jobs2.json').write_text(json.dumps(jobs, indent=1))
    print(len(jobs), 'jobs')


def run(i, n, procs, jf='jobs.json', tag='res'):
    import pcc_eval
    jobs = json.loads((D / jf).read_text())
    out = D / f'{tag}_{i}.jsonl'
    done = set()
    if out.exists():
        done = {json.loads(l)['spec'] for l in out.read_text().splitlines() if l.strip()}
    for j in range(i, len(jobs), n):
        jb = jobs[j]
        if jb['name'] in done:
            continue
        r = pcc_eval.run(jb['stem'], jb['spec'], procs)
        with open(out, 'a') as f:
            f.write(json.dumps(r) + '\n')


if __name__ == '__main__':
    if sys.argv[1] == 'build':
        build()
    elif sys.argv[1] == 'build2':
        build2()
    elif sys.argv[1] == 'run2':
        run(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), 'jobs2.json', 'res2')
    else:
        run(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

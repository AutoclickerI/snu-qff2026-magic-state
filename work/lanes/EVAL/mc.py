"""Official-judge Monte Carlo at several p (parallel chunks, bit-identical to tprep.check). usage: mc.py qasm p1,p2.. shots seeds procs out.json"""
import sys, json, time
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work')
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
import fast_check
q = sys.argv[1]; ps = [float(x) for x in sys.argv[2].split(',')]; shots = int(float(sys.argv[3]))
seeds = [int(x) for x in sys.argv[4].split(',')]; procs = int(sys.argv[5]); out = sys.argv[6]
data = json.load(open(q.rsplit('.', 1)[0] + '.json'))['data_qubits']
text = open(q).read(); res = []
for p in ps:
    for sd in seeds:
        t = time.time()
        r = fast_check.check(text, data, shots=shots, seed=sd, procs=procs, p=p)
        res.append(dict(p=p, seed=sd, shots=shots, score=r.score, sem=r.sem, acc=r.acceptance))
        print(res[-1], f'{time.time()-t:.0f}s', flush=True)
        json.dump(res, open(out, 'w'), indent=1)

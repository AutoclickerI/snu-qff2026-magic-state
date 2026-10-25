"""Long basis search on one stem; writes its ops keyed by detector record sets: mkwarm.py <stem> <out.json> [trials] [seed]"""
import os, sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ev2
sw = ev2.sw
st = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
trials = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 80353
ev2._DETKEYS = ev2.detkeys(st.with_suffix('.qasm').read_text())
os.chdir(ev2.SP)
m, eng, groups, nd, ks, psi, where, de = sw.prepare(st, True)
t = time.time()
steps, base, best = ev2.find_ops(m, eng, groups, nd, set(ks), trials=trials, seed=seed)
print('base', base, 'best', best, len(steps), 'ops', time.time() - t, 's')
out.write_text(json.dumps(dict(stem=str(st), trials=trials, seed=seed, best=best,
                                             ops=[[ev2._DETKEYS[a], ev2._DETKEYS[b]] for a, b in steps])))

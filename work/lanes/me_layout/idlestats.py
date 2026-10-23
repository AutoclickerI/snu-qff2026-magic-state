import glob, json, sys
import numpy as np
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep.noise as tn
from tprep.qasm import to_stim
rows = []
files = sorted(glob.glob("alapvar/*.json")) + ["cand_A1_0.json", "cand_A1_alap.json", "cand_A1_alap_cm.json"]
for f in files:
    d = json.load(open(f)); q = f[:-5] + ".qasm"
    text = open(q).read()
    prog, steps, gaps = tn.schedule(to_stim(text)[0])
    data = set(d["data_qubits"])
    end = max(s for g in steps for _, s in g) + 1
    idle_d = sum(n for i, qq, s0, n in gaps if qq in data)
    idle_a = sum(n for i, qq, s0, n in gaps if qq not in data)
    # idle of data before cycle start: approximate with steps < end-12
    rows.append((d["score"], idle_d, idle_a, end, d["acceptance"], f))
rows.sort()
for r in rows: print(f"{r[0]:.5e} idle_data {r[1]:3d} idle_anc {r[2]:3d} depth {r[3]} acc {r[4]:.4f} {r[5]}")
a = np.array([r[:4] for r in rows], float)
print("corr score~idle_data", np.corrcoef(a[:,0], a[:,1])[0,1], " ~idle_anc", np.corrcoef(a[:,0], a[:,2])[0,1], " ~depth", np.corrcoef(a[:,0], a[:,3])[0,1])

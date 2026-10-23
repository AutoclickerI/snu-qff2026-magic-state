import glob, json, collections, statistics as st, sys
d = collections.defaultdict(list)
for f in glob.glob(sys.argv[1] if len(sys.argv) > 1 else "panels/panel_*.log"):
    for l in open(f):
        if l.startswith("{"):
            r = json.loads(l); d[r["stem"]].append((r["seed"], r["score"], r["passed"]))
for k, v in sorted(d.items(), key=lambda kv: st.mean(x[1] for x in kv[1])):
    s = [x[1] for x in v]
    print(f"{k.split('/')[-1]:24s} n={len(v):2d} mean={st.mean(s):.4e} se={st.stdev(s)/len(s)**.5 if len(s)>1 else 0:.1e} allpass={all(x[2] for x in v)}")

from pathlib import Path
H=Path(__file__).resolve().parent.parent
p=H/'build.py';s=p.read_text();s=s.replace('def source():','def source(context="v23h_c2c9"):\n base=H/("inputs" if context=="v23h_c2c9" else "blue/inputs")/context')
s=s.replace("(H/'inputs/v23h_c2c9.qasm').read_text()","base.with_suffix('.qasm').read_text()").replace("(H/'inputs/v23h_c2c9.json').read_text()","base.with_suffix('.json').read_text()")
s=s.replace('source();sourceR','source(opt.get("context","v23h_c2c9"));sourceR')
s=s.replace("for layer in d['ops']:",'''for q in opt.get('init_checks',[]):
  basis=q in piv;lines=[f'h q[{q}];',f'measure q[{q}] -> c[{nb}];',f'h q[{q}];'] if basis else [f'measure q[{q}] -> c[{nb}];']
  newdets.append(f'// DETECTOR c[{nb}]');nb+=1;cand.append(len(us));us.append(S.Unit(lines,[]))
 for layer in d['ops']:''')
s=s.replace("for j in cand:m.Add(tv[j]<R+min(delta,0))","for j in cand:m.Add(tv[j]<R+min(delta,0))\n if opt.get('late_mx'):\n  lastT=max(t for u,t in zip(old,ots) if u.name in ('T','TDG'))\n  for q in mx&piv:m.Add(tv[init[q]]>lastT)")
s=s.replace("key=tuple(us[j].lines);k=used[key];used[key]+=1", "key=tuple(us[j].lines);k=used[key];used[key]+=1\n   if j in init.values():\n    q=next(q for q,v in init.items() if v==j);z=m.NewIntVar(0,70,'initdev');m.AddAbsEquality(z,tv[j]-ots[oinit[q]]);dev.append(z);continue")
s=s.replace("source='v23h_c2c9'", "source=opt.get('context','v23h_c2c9')")
p.write_text(s)

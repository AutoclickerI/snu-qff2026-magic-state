import sys, json, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SP=ROOT/'quantumn_snapshot/work/lanes/MAIN/sparse'
sys.path.insert(0,str(SP))
import frontend as f
from judge_subset.noise import schedule
base=ROOT/'quantumn_snapshot/work/lanes/MAIN/v37d'
out=ROOT/'schedule_probes'
out.mkdir(exist_ok=True)
text=base.with_suffix('.qasm').read_text()
meta=json.loads(base.with_suffix('.json').read_text())
lines=text.splitlines()
barriers=[i for i,l in enumerate(lines) if l.startswith('barrier')]

def summary(txt):
 ops,dets=f.parse_current(txt)
 native,_=f.native_text(ops)
 prog,steps,gaps=schedule(native)
 return {'ticks':1+max(t for items in steps for qs,t in items),
         'idles':sum(g[-1] for g in gaps),
         'data_idles':sum(g[-1] for g in gaps if g[1] in meta['data_qubits']),
         'schedule_hash':hashlib.sha256(json.dumps([steps,gaps]).encode()).hexdigest()}

variants={'baseline':set(),'remove_all':set(barriers)}
variants.update({f'remove_{j:02d}':{line} for j,line in enumerate(barriers)})
variants.update({f'remove_after_{j:02d}':set(barriers[j:]) for j in [12,24,36,40,43] if j<len(barriers)})
results=[]
for name,remove in variants.items():
 txt='\n'.join(l for i,l in enumerate(lines) if i not in remove)+'\n'
 st=out/name
 st.with_suffix('.qasm').write_text(txt)
 st.with_suffix('.json').write_text(json.dumps(meta)+'\n')
 results.append(dict(name=name,**summary(txt)))
(out/'schedule_summary.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))

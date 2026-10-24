"""Current-base finalist gates and complete official three-seed receipts."""
import sys,json,time,runpy,contextlib,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v

def gate(p):
 saved=sys.argv;sys.argv=['gate_budget.py',str(p)];threshold=v.a.BASE_LOSS;v.a.BASE_LOSS=v.INCUMBENT
 try:runpy.run_path(str(v.H/'gate_budget.py'),run_name='__main__')
 finally:sys.argv=saved;v.a.BASE_LOSS=threshold
 return json.loads(p.with_suffix('.gate.json').read_text())

def mc(p,procs):
 r=json.loads(p.with_suffix('.gate.json').read_text());assert r['gated']
 if isinstance(r.get('MC3'),dict):return r
 saved=sys.argv;sys.argv=['mc3.py',str(p),'--procs',str(procs)]
 try:
  with p.with_suffix('.mc3.log').open('w')as f,contextlib.redirect_stdout(f),contextlib.redirect_stderr(f):runpy.run_path(str(v.H/'pop35_mc3.py'),run_name='__main__')
 finally:sys.argv=saved
 import re
 vals=re.findall(r' (0|1000|2000) ([\deE+.-]+) ± ([\deE+.-]+) acc ([\deE+.-]+)',p.with_suffix('.mc3.log').read_text());assert len(vals)==3,vals
 r['MC3']={seed:dict(loss=float(loss),sem=float(sem),acceptance=float(acc))for seed,loss,sem,acc in vals};r['MC3_mean']=sum(x['loss']for x in r['MC3'].values())/3;p.with_suffix('.gate.json').write_text(json.dumps(r,indent=2))
 report=v.H/'REPORT.md';s=report.read_text();rel=str(p.relative_to(v.H));s='\n'.join(z.replace('MC3 pending',f"MC3 mean {r['MC3_mean']:.9e}")if f'`{rel}`'in z else z for z in s.split('\n'));report.write_text(s);print('MC3_DONE',rel,r['MC3_mean'],flush=True);return r
if __name__=='__main__':
 for name in sys.argv[1:-1]:
  p=Path(name).resolve();g=gate(p)
  if g['gated']:mc(p,int(sys.argv[-1]))

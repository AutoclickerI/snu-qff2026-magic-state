"""Lane-local finalist gates and exact three-seed validation; immediate report entry."""
import os,sys,json,runpy,time
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v

def gate(st):
 saved=sys.argv;sys.argv=['v35_gate',str(st)]
 try:runpy.run_path(str(v.H/'gate_budget.py'),run_name='__main__')
 finally:sys.argv=saved
 return json.loads(st.with_suffix('.gate.json').read_text())

def mc(st,procs):
 log=st.with_suffix('.mc3.log');saved=sys.argv
 import contextlib
 sys.argv=['mc3.py',str(st),'--procs',str(procs)]
 try:
  with log.open('w')as f,contextlib.redirect_stdout(f),contextlib.redirect_stderr(f):runpy.run_path(str(v.H/'pop35_mc3.py'),run_name='__main__')
 finally:sys.argv=saved
 import re
 text=log.read_text();lines=re.findall(r' (0|1000|2000) ([\deE+.-]+) ± ([\deE+.-]+) acc ([\deE+.-]+)',text);assert len(lines)==3,text
 r=json.loads(st.with_suffix('.gate.json').read_text());r['MC3']={seed:dict(loss=float(loss),sem=float(sem),acceptance=float(acc))for seed,loss,sem,acc in lines};r['MC3_mean']=sum(x['loss']for x in r['MC3'].values())/3
 st.with_suffix('.gate.json').write_text(json.dumps(r,indent=2));report=v.H/'REPORT.md';s=report.read_text();rel=str(st.relative_to(v.H));s='\n'.join(line.replace('MC3 pending',f"MC3 mean {r['MC3_mean']:.9e}")if f'`{rel}`'in line else line for line in s.split('\n'));report.write_text(s)
 print('MC3_DONE',rel,r['MC3_mean'],flush=True);return r

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=5);args=p.parse_args()
 for name in args.stems:
  st=Path(name).resolve();g=gate(st)
  if g['gated']:mc(st,args.procs)

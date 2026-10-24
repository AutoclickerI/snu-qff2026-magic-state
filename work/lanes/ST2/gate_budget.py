"""Record judge and speed gates immediately; MC3 is a separate receipt."""
import sys,os,json,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
sys.path.insert(0,str(a.H.parents[2]/'work'));import fast_check
from speed_predict import predict
for st in sys.argv[1:]:
 p=Path(st).resolve();r=json.loads(p.with_suffix('.score.json').read_text());text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text());sha=hashlib.sha256(text.encode()).hexdigest();out=None
 if p.with_suffix('.gate.json').exists():
  prev=json.loads(p.with_suffix('.gate.json').read_text())
  if prev.get('qasm_sha256')==sha:out=prev
 if out is None:
  speed=predict(str(p));out=dict(stem=str(p),loss=r['loss'],allorders_acceptance=r['acceptance'],exp_minus_A1=r['exp_minus_A1'],qasm_sha256=sha,MC3='pending',speed=speed,gated=False)
  if speed['classification']=='FAST':
   start=time.monotonic();rep=fast_check.check(text,md['data_qubits'],shots=1000000,seed=0,procs=1);sec=time.monotonic()-start
   out.update(judge_passed=bool(rep.passed),judge_acceptance=float(rep.acceptance),judge_loss=float(rep.score),judge_seconds=sec,cx=rep.n_2q)
   out['gated']=rep.passed and rep.acceptance>=.5 and sec<=20 and r['acceptance']>=a.FLOOR
 out['stem']=str(p);p.with_suffix('.gate.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
 if out['gated']and r['loss']<a.BASE_LOSS-1e-13:
  report=a.H/'REPORT.md';s=report.read_text();line=f"**New gated finalist `{p.relative_to(a.H)}`: all-orders {r['loss']:.12e}, acceptance {r['acceptance']:.9f}; judge PASS, acceptance {out['judge_acceptance']:.6f}, {out['judge_seconds']:.3f}s/1e6; XTIM FAST {out['speed']['median_seconds_per_1e6']:.3f}s/1e6; MC3 {out['MC3']}.**\n\n"
  if line not in s:
   import re
   s=line+s;head=[z for z in s.splitlines()if z.startswith('**New gated finalist')]
   body='\n'.join(z for z in s.splitlines()if not z.startswith('**New gated finalist')).lstrip()
   head.sort(key=lambda z:float(re.search(r'all-orders ([0-9.eE+-]+)',z)[1]))
   report.write_text('\n\n'.join(head)+'\n\n'+body+'\n')

import json,re,statistics,math,hashlib,datetime
from pathlib import Path
O=Path(__file__).resolve().parent;ROOT=O.parents[2]
rows={};src=[]
for p in sorted((ROOT/'work/reorder').glob('v23h_c2c9_*.log')):
 src.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 for m in re.finditer(r'v23h_c2c9_r(\d+) 1-F ([\deE.+-]+) acc ([\d.]+) 2q (\d+) pass (\w+)',p.read_text()):
  k=int(m[1]);v=dict(score=float(m[2]),acceptance=float(m[3]),cx=int(m[4]),passed=m[5]=='True')
  assert k not in rows or rows[k]==v
  rows[k]=v
ys=[r['score'] for r in rows.values()]
s=dict(count=len(ys),mean=statistics.mean(ys),sem=statistics.stdev(ys)/math.sqrt(len(ys)),minimum=min(ys),sources=src,all_pass=all(r['passed'] for r in rows.values()),note='Aggregated existing completed 1e8-shot seed-0 redraws; printed scores rounded, not new MC.')
(O/'redraws.json').write_text(json.dumps(s,indent=2));print('REDRAWS',json.dumps(s))
a=json.loads((O/'ablations.json').read_text());b=a['all']['total'];rnd=a['only_round']['total']
ledger=dict(baseline_third=b,mean=s['mean'],higher_order_residual=s['mean']-b,standalone_round=rnd,nonround_and_cross=b-rnd,delta_target=s['mean']-5e-5,delta_leader_observation=s['mean']-5.612e-5,acceptance_log_budget=math.log(a['all']['exp_minus_A1']/.5),stage_removal_deltas={g:b-a['no_'+g]['total'] for g in ['pre','A','BC','hop','round']},standalone={g:a['only_'+g]['total'] for g in ['pre','A','BC','hop','round']},cross=b-sum(a['only_'+g]['total'] for g in ['pre','A','BC','hop','round']))
(O/'ledger.json').write_text(json.dumps(ledger,indent=2));print('LEDGER',json.dumps(ledger))
ctx=O/'context';ctx.mkdir(exist_ok=True)
manifest={'read_at':datetime.datetime.now().isoformat(),'reports':{}}
for lane in ['BCFB','KNAP','BCPOL','WALSH','LNS','GAP']:
 p=ROOT/'work/lanes'/lane/'REPORT.md'
 if p.exists():
  data=p.read_bytes();(ctx/(lane+'.md')).write_bytes(data);manifest['reports'][lane]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
 else:manifest['reports'][lane]={'absent':True}
(O/'context_manifest.json').write_text(json.dumps(manifest,indent=2))

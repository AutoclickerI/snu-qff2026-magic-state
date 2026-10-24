from core import *
old={r['stem']:r for r in json.loads((V/'results.json').read_text())}if(V/'results.json').exists()else{};rows=[]
for p in V.glob('*.screen.json'):
 n=p.name.removesuffix('.screen.json');mdf=V/(n+'.json');r=dict(stem=n,metadata=json.loads(mdf.read_text())if mdf.exists()else old[n]['metadata'],screen=json.loads(p.read_text()))
 for ext,key in [('.allorders.json','allorders'),('.speed_prediction.json','speed'),('.static_speed.json','static_speed')]:
  q=V/(n+ext)
  if q.exists():r[key]=json.loads(q.read_text())
 for ext,key in [('.judge.log','judge'),('.mc.log','mc')]:
  q=V/(n+ext)
  if q.exists():r[key]=q.read_text()
 m=re.search(r' mean ([\deE+.-]+)',r.get('mc',''));r['mc_mean']=float(m[1])if m else None
 m=re.search(r'\(([\d.]+)s, 1 procs\)',r.get('judge',''));r['judge_seconds']=float(m[1])if m else None
 m=re.search(r'acc=([\d.]+)',r.get('judge',''));r['judge_acceptance']=float(m[1])if m else None
 r['qualified']=('allorders'in r and r['allorders']['loss']<4.1460519583256424e-5 and r['allorders']['acceptance']>=.5002 and 'passed=True'in r.get('judge','')and r.get('speed',{}).get('classification')=='FAST'and r['judge_seconds']<=20 and r['judge_acceptance']>=.5)
 rows.append(r)
rows.sort(key=lambda r:r.get('allorders',{}).get('loss',1));(V/'results.json').write_text(json.dumps(rows,indent=2))
text='Status: RUNNING — P75 integration on v36a; all-orders acceptance floor0.5002. Prior delivery: [REPORT_v36a_delivery.md](REPORT_v36a_delivery.md).\n\n'+(V/'LEDGER.md').read_text()+'\n## Verified finalists below v36a\n\n| Stem | All orders | Acceptance | Judge | MC3 mean |\n|---|---:|---:|---|---:|\n'
for r in rows:
 if r['qualified']:text+=f'| [v36/{r["stem"]}](v36/{r["stem"]}.qasm) | {r["allorders"]["loss"]:.12e} | {r["allorders"]["acceptance"]:.9f} | PASS, {r["judge_seconds"]:.1f}s, FAST | '+(f'{r["mc_mean"]:.7e}'if r['mc_mean']is not None else'pending')+' |\n'
text+='\n## Current integration findings\n\n'+(V/'NOTES.md').read_text()if(V/'NOTES.md').exists()else'\n'
(H/'REPORT.md').write_text(text);print('published',len(rows),'screens',sum('allorders'in r for r in rows),'all-orders prices',sum(r['qualified']for r in rows),'gated finalists')

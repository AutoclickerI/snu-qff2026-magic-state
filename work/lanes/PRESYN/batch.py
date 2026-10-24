from core import *
import concurrent.futures,traceback
import tprep

def price(job):
 stem=Path(job['stem']);stem=OUT/stem.name
 try:
  row=score(stem,1)
  text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text())
  r=tprep.check(text,meta['data_qubits'],shots=10**6,seed=0)
  check=dict(passed=r.passed,acceptance=float(r.acceptance),repr=str(r))
  stem.with_suffix('.check.json').write_text(json.dumps(check,indent=2)+'\n')
  row.update(check=check['passed'],check_acceptance=check['acceptance'])
 except Exception as e:row=dict(error=str(e),traceback=traceback.format_exc())
 row.update(stem=stem.name,change=job['change']);return row

def report():
 rows=[json.loads(x)for f in sorted(OUT.glob('*results.jsonl')) for x in f.read_text().splitlines()]
 mc={}
 for f in OUT.glob('*mc3.log'):
  for l in f.read_text().splitlines():
   m=re.match(r'.*/([^/ ]+) (0|1000|2000) ([\deE+.-]+).* acc ([\d.]+)',l)
   if m:mc.setdefault(m[1],{})[m[2]]=dict(score=float(m[3]),acceptance=float(m[4]),file=f.name)
 (OUT/'mc_results.json').write_text(json.dumps(mc,indent=2)+'\n')
 lines=['# PRESYN','','Status: running — full-circuit structural screens; MC finalists pending.','',
 'Bar: v22h_c2c9. Losses are at p=1e-3; exact third-order is used only for |c1|<1e-12. exp(-A1) is an acceptance estimate. Judge checks use 1e6 shots, seed 0; final acceptance/score require 1e8-shot MC.','']
 good=[r for r in rows if r.get('check')and r.get('exp_minus_A1',0)>=.505 and 'total'in r]
 if good:
  best=min(good,key=lambda r:r['total']);lines+=['Best verified exact screen so far: **%s, %.10e** (%+.3f%% vs bar); MC unverified.'%(best['stem'],best['total'],100*(best['total']/BAR-1)),'']
 sampled=[(sum(x['score']for x in seeds.values())/3,n,seeds)for n,seeds in mc.items()if len(seeds)==3 and seeds['0']['acceptance']>=.505]
 if sampled:
  mean,n,seeds=min(sampled);lines+=['Best measured three-seed mean: **%s, %.10e**, seed-0 acceptance %.8f. [MC receipt](%s). The small difference from the base remains subject to sampling uncertainty.'%(n,mean,seeds['0']['acceptance'],seeds['0']['file']),'']
 if (OUT/'decomposition.json').exists():
  d=json.loads((OUT/'decomposition.json').read_text());lines+=['Measured loss decomposition: second %.10e; raw weight-3 sets %.10e; pair-times-others %.10e; net cubic %.10e; total %.10e. [Complete receipt](decomposition.json).'%(d['second'],d['weight3'],d['pair_times_others'],d['third'],d['total']),'','| Region pair | Loss |','|---|---:|']
  for k,v in d['pairs_region'].items():lines.append('| %s | %.8e |'%(k,v))
  lines+=['','| Region triple (raw weight-3) | Loss |','|---|---:|']
  for k,v in list(d['triples_region'].items())[:25]:lines.append('| %s | %.8e |'%(k,v))
  lines+=['','| Pre-stage component pair (all partners) | Loss |','|---|---:|']
  for k,v in d['pairs_component'].items():
   if any(x in k for x in ('injection','stabilizer','T_layers','check1','check2','internal_idle')):lines.append('| %s | %.8e |'%(k,v))
  lines+=['','The complete component triple partition is in decomposition.json. Components are disjoint: injection encoder; injection stabilizer verification; T/T-dagger layers; forward compression/check 1 through central MX; reverse reconstruction/check 2 and cat readout; internal idles after any of those operations. Native noise attaches each idle to its preceding operation, as implemented by MAIN/regions.py; that file’s docstring says the opposite. Check 1 and check 2 label the two halves of Gidney’s double-cat construction, not two independent full H_XY blocks.','']
 if (OUT/'ablation.json').exists():
  lines+=['| Noiseless diagnostic region | 2nd | Net cubic | Total |','|---|---:|---:|---:|']
  for a in json.loads((OUT/'ablation.json').read_text()):lines.append('| %s %s | %.8e | %.8e | %.8e |'%(a['mode'],a['region'],a['second'],a['third'],a['total']))
 lines+=['','| Variant / change | CX | R | c1 | 2nd | 3rd | Exact total | exp(-A1) | Check / MC | Files |','|---|---:|---:|---:|---:|---:|---:|---:|---|---|']
 for r in rows:
  if 'error'in r:lines.append('| %s: %s | %s | %s | — | — | — | — | — | Judge FAIL: %s | [%s](%s.check.json); results JSONL |'%(r['stem'],r['change'],r.get('CX','—'),r.get('R','—'),r['error'].replace('|','/'),r['stem'],r['stem']));continue
  seeds=mc.get(r['stem'],{});mct='MC '+(' / '.join('%.8e'%seeds[s]['score']for s in ('0','1000','2000'))if len(seeds)==3 else'not run')
  lines.append('| %s: %s | %s | %s | %.3e | %.8e | %s | %s | %.6f | %s, acc %.6f; %s | [%s](%s.exact.json) |'%(r['stem'],r['change'],r['CX'],r['R'],r['c1'],r['second'],'%.8e'%r['third']if'third'in r else'—','%.8e'%r['total']if'total'in r else'—',r['exp_minus_A1'],'PASS'if r['check']else'FAIL',r['check_acceptance'],mct,r['stem'],r['stem']))
 lines+=['','Verified: native grid adjacency and emitted schedule, exact and judge receipts listed above. Raw triple attribution is distinct from the signed cubic normalization.','Inferred: a losing recipe excludes only its specific construction/schedule. No global no-go claim is made.','']
 (OUT/'REPORT.md').write_text('\n'.join(lines))

if __name__=='__main__':
 manifest=sys.argv[2]if len(sys.argv)>2 else'manifest.json'
 outfile=OUT/(manifest.replace('_manifest.json','_results.jsonl')if manifest!='manifest.json'else'results.jsonl')
 jobs=json.loads((OUT/manifest).read_text());done=set()
 if outfile.exists():done={json.loads(x)['stem']for x in outfile.read_text().splitlines()}
 jobs=[j for j in jobs if 'stem'in j and Path(j['stem']).name not in done]
 with concurrent.futures.ProcessPoolExecutor(int(sys.argv[1]))as pool,outfile.open('a')as f:
  futures=[pool.submit(price,j)for j in jobs]
  for future in concurrent.futures.as_completed(futures):
   row=future.result()
   f.write(json.dumps(row)+'\n');f.flush();report();print(json.dumps(row),flush=True)

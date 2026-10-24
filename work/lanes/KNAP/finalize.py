"""Compact delivery from measured receipts; remove regenerable circuit bulk."""
from search import *
import csv

def main():
 rows=[]
 for path in sorted(OUT.glob('*results.jsonl')):
  for line in path.read_text().splitlines():
   r=json.loads(line);r['receipt_file']=path.name;rows.append(r)
 by={}
 for r in rows:by.setdefault(r['stem'],{}).update(r)
 base=by['base'];mc={}
 for f in OUT.glob('*.mc3.log'):
  for line in f.read_text().splitlines():
   mt=re.search(r'/KNAP/([^ ]+) (0|1000|2000) ([\deE.+-]+).* acc ([\d.]+)',line)
   if mt:mc.setdefault(mt[1],{})[mt[2]]=dict(score=float(mt[3]),acceptance=float(mt[4]),receipt=f.name)
 ranked=sorted((sum(v['score']for v in ss.values())/3,n,ss)for n,ss in mc.items()if len(ss)==3 and ss['0']['acceptance']>=.5 and by.get(n,{}).get('check')and by[n].get('runtime_pass'))
 assert ranked,'No fully verified MC finalist'
 mean,name,seeds=ranked[0];best=by[name]
 ref=(OUT/(name+'.reference.log'))
 assert ref.exists()and'1-F (to 3rd order)'in ref.read_text(),'independent exact reference unfinished'
 ref_value=float(re.search(r'1-F \(to 3rd order\) = ([\deE+.-]+)',ref.read_text())[1]);assert abs(ref_value-best['total'])<5e-11
 coverage={}
 for path in OUT.glob('*_manifest.json'):
  jobs=json.loads(path.read_text());expected={j['stem']for j in jobs if isinstance(j,dict)and'stem'in j};missing=expected-set(by)
  assert not missing,(path.name,'unpriced',sorted(missing))
  coverage[path.name]=len(expected)
 (OUT/'mc_results.json').write_text(json.dumps(dict(ranked=[dict(mean=m,stem=n,seeds=s)for m,n,s in ranked]),indent=2)+'\n')
 with(OUT/'items.csv').open('w')as f:
  cols=['stem','source','kind','c1','second','third','total','A1','exp_minus_A1','delta_loss','delta_A1','ratio','check','runtime_1e5_seconds','error'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
  for r in by.values():
   source=r['recipe'].get('source','base');b=by.get(source,base);rec={k:r.get(k)for k in cols};rec.update(source=source,kind=r['recipe']['kind'])
   if'total'in r:
    dl=r['total']-b['total'];da=r['A1']-b['A1'];rec.update(delta_loss=dl,delta_A1=da,ratio=dl/da if abs(da)>1e-12 else None)
   w.writerow(rec)
 lines=['# KNAP','', 'Status: complete for the tested item menu; verified delivery below. No submission, commit, push or other-lane writes.','',
 f'Best MC-ranked finalist: **`{name}`** ([QASM]({name}.qasm), [metadata]({name}.json)).',
 'Exact: c1 `%.12g`, second `%.12g`, weight-3 `%.12g`, pair-times-others `%.12g`, net cubic `%.12g`, total **%.12g**. exp(-A1) **%.9f**, A1 %.12g; %d CX, R%d.'%(best['c1'],best['second'],best['T3a'],best['t3bc'],best['third'],best['total'],best['exp_minus_A1'],best['A1'],best['CX'],best['R']),
 'Three-seed 1e8 MC mean **%.12g**. Seed-0 acceptance **%.8f**; 1e6 judge PASS (%.6f), 1e5 fast_check **%.3f s**.'%(mean,seeds['0']['acceptance'],best['check_acceptance'],best['runtime_1e5_seconds']),
 'Exact gain versus supplied v24: **%.4f%%**. This is an exact-screen comparison; v24 full MC is unmeasured here because it fails the runtime screen.'%(100*(best['total']/base['total']-1)), '',
 '| Seed | 1-F | Acceptance |','|---|---:|---:|']
 for s in ('0','1000','2000'):lines.append('| %s | %.9g | %.8f |'%(s,seeds[s]['score'],seeds[s]['acceptance']))
 lines+=['','| Fully sampled candidate | Exact total | Three-seed MC mean | Seed-0 acceptance |','|---|---:|---:|---:|']
 for m,n,ss in ranked:lines.append('| `%s` | %.12g | %.12g | %.8f |'%(n,by[n]['total'],m,ss['0']['acceptance']))
 lines+=['','Receipts: [MC](%s.mc3.log), [judge and runtime](%s.verified.json), [unmodified exact2](%s.reference.log), [full coefficients](%s.exact.json).'%(name,name,name,name),'',
 '## Acceptance-budget items','',
 'Prices below are exact full-circuit marginal differences from v24. Negative delta A1 frees acceptance; positive delta A1 spends it. Ratios are signed delta loss / delta A1. The complete table, including failures and prices against later source circuits, is [items.csv](items.csv).','',
 '| Item | delta 1-F | delta A1 | Ratio |','|---|---:|---:|---:|']
 chosen=['drop_d03','reset_u3','reset_u1','reset_u6','check_u247','drop_d39','drop_d40','drop_d41','drop_d42','time_u125_t10','time_u126_t14','time_u306_t49','time_u237_t41','bcreset_04','bcreset_08','bcreset_20']
 for n in chosen:
  r=by[n];dl=r['total']-base['total'];da=r['A1']-base['A1'];lines.append('| `%s` | %+.9g | %+.9g | %s |'%(n,dl,da,'%.6g'%(dl/da)if abs(da)>1e-12 else '—'))
 lines+=['','## Verified combinations','', '| Stem | Exact total | exp(-A1) | 1e6 acceptance | 1e5 seconds |','|---|---:|---:|---:|---:|']
 for r in sorted(by.values(),key=lambda r:r.get('total',1)):
  if r.get('check')and r.get('total',1)<base['total']:lines.append('| `%s` | %.12g | %.9f | %.6f | %.3f |'%(r['stem'],r['total'],r['exp_minus_A1'],r['check_acceptance'],r['runtime_1e5_seconds']))
 lines+=['','## Mechanisms','',
 '- Read c[3] on q19 at native step 10 instead of 32, and c[6] on q13 at 14 instead of 32. This removes ancillary idle rejection noise. Advancing c[6] also lowers logical loss.',
 '- Read available A/C output qubits at step 49 instead of 50. Early measurement is legal on those wires while the other final-round operations continue, and it removes idle faults before their readout.',
 '- Add the block-A q1 MX check and affordable prefix RX checks. Weak first-use measurement checks can fund them, but the final timing changes already supply enough budget.',
 '- Runtime matters: supplied v24 took %.3f s at 1e5 shots. BC q19 MX-to-RX is the dominant measured repair; q17 and q4 resets further reduce runtime without changing exact loss through third order. The repair costs %.9g exact loss on v24 and is included in every claimed delivery result.'%(base['runtime_1e5_seconds'],by['bcreset_04']['total']-base['total']),
 '- `parity_0f` additionally advances CX 10→4 to native step 10, replaces three RX initializations (q1/q9/q13) with native MX and q11’s Z reset with a Z measurement, and adds each new record to its specified detector parities. These four explicit parity couplings were selected by full physical-circuit scoring, not assumed from a frame-propagation formula. Their exact gain over `final_m2c_l2` is only 9.0983e-8, so it is smaller than three-seed sampling uncertainty.',
 '- The first frame-init generator confused converter detector order with QASM declaration order. The corrected `frame2` pass uses the converter labels. Most corrected candidates fail code-space correctness or c1; q19 MX recovers exact loss but restores the slow branch. The valid first-pass physical parity choices were retained as explicit detector recipes and rechecked in all 16 combinations. Both passes and their failures are preserved.',
 '- Larger colour-check tiles, detector merging, extra watches and gate timing are recorded in the complete screen. All 171 selected detector merges were evaluated; none lowers exact loss versus v24. A negative recipe result excludes that construction, not all circuits of the same type.','',
 '## Verified versus inferred','',
 '- Verified: legal native/grid emission, exact noiseless correctness in the judge, |c1| < 1e-12, full-circuit Fourier-moment coefficients, the unmodified exact2 third-order cross-check, 1e6 judge PASS, 1e5 runtime, and all three required 1e8 seeds. The copied mc3.py and exact2.py are byte-identical to MAIN/spec/mc3.py and EVAL/exact2.py; the remote MAIN/spec path was absent.',
 '- Inferred: exp(-A1) is an acceptance estimate; the measured seed-0 acceptance is the gate. Third-order gain is not a measured MC gain over v24. No global optimality, statistical significance of sub-percent changes, or official server timing/result is claimed.',
 '- Search coverage and every invalid/budget-failing item remain in the JSONL receipts. Only retained finalists, small inputs, receipts and regeneration tools remain; regenerable candidate QASM/JSON and evaluator caches are removed.',
 '- Primary sources: local [judge noise](../../../upstream/snu-qff2026-problem/tprep/noise.py), [judge checks](../../../upstream/snu-qff2026-problem/tprep/check.py), [exact2](../EVAL/exact2.py), [PRESYN](../PRESYN/REPORT.md), [P23](../P23/REPORT.md), and the measured receipts in this directory. No claims rely on memory.','']
 (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
 (OUT/'coverage.json').write_text(json.dumps(dict(manifests=coverage,unique_screen_rows=len(by),reference_absolute_difference=abs(ref_value-best['total'])),indent=2)+'\n')
 keep={n for _,n,_ in ranked}
 for source in ('base','enc21_joint_d7_rigid'):
  for suffix in('.qasm','.json'):
   p=OUT/(source+suffix)
   if p.exists():p.replace(OUT/'inputs'/p.name)
 # Each JSONL preserves recipes, coefficients, hashes and exclusions before removing bulk.
 for p in OUT.glob('*.qasm'):
  if p.stem not in keep:
   p.unlink();p.with_suffix('.json').unlink(missing_ok=True)
 for p in OUT.glob('*.exact.json'):
  if p.name[:-11]not in keep:p.unlink()
 import shutil
 shutil.rmtree(OUT/'.xtim_cache',ignore_errors=True)
 print(json.dumps(dict(best=name,mean=mean,exact=best['total'],acceptance=seeds['0']['acceptance'],screen_rows=len(by))),flush=True)

if __name__=='__main__':main()

"""Keep selected comparisons and compact evidence; remove regenerable bulk."""
import csv,json,subprocess,sys,shutil
from pathlib import Path
OUT=Path(__file__).resolve().parent
assert json.loads((OUT/'regeneration.receipt.json').read_text())['verified']>3000
subprocess.run([sys.executable,str(OUT/'report.py')],check=True)
records=list(csv.DictReader((OUT/'results.csv').open()))
keep={'matched_ref','matched_cat13_BC','tree2_BC_v22','tree2_ABC_v22','spine_BC_sep','spine_BC_v22','physical_hybrid2t','runs/sep_ref','runs/v22_BC_redundant_201'}
for p in OUT.rglob('*.mc.json'):keep.add(str(p.relative_to(OUT)).removesuffix('.mc.json'))
for blocks,kind in [('A','flag'),('BC','direct'),('BC','redundant'),('BC','hybrid2t'),('BC','cat3spinered')]:
    rs=[r for r in records if r['pre']=='v22h' and r['blocks']==blocks and r['kind']==kind and r.get('red_mask','7') in ('','7') and r['total']]
    keep.add(min(rs,key=lambda r:float(r['total']))['name'])
removed=[]
for r in records:
    name=r['name']
    if name in keep:continue
    for ext in ['.qasm','.json','.result.json','.log']:
        p=OUT/(name+ext)
        assert OUT in p.resolve().parents
        if p.exists():p.unlink();removed.append(str(p.relative_to(OUT)))
for p in list(OUT.glob('*.receipt.json')):
    r=json.loads(p.read_text())
    if not isinstance(r,list) or len(r)<20:continue
    bad=[x for x in r if x.get('exit',0)!=0]
    p.write_text(json.dumps(dict(status='COMPLETE' if not bad else 'FAILED',entries=len(r),cached=sum(bool(x.get('cached')) for x in r),failures=bad,numerical_rows='results.csv'),indent=2)+'\n')
bulk=['single.log','combined.log','extended.log','cat_orders.log','cat_orders_fast.log','finish.log','matched_sunfish.log','matched_zebra.log','matched_all.log','cover.log','cover_remote.log','grid_initial.py','local_matched_files.txt']
for name in bulk:
    p=OUT/name
    if p.exists():p.unlink();removed.append(name)
cache=OUT/'.xtim_cache'
if cache.exists():shutil.rmtree(cache)
(OUT/'cleanup.receipt.json').write_text(json.dumps(dict(retained_circuit_stems=sorted(keep),removed_files=len(removed),archived_measurements=len(records),policy='Per-variant QASM, JSON and logs kept only for selected comparisons/diagnostic. Numerical rows and exact regeneration recipes remain in CSV; compact solver and verification receipts preserve negative evidence.'),indent=2)+'\n')
(OUT/'DONE').write_text('No eligible physical improvement found; pricing complete for listed recipes, broad grid embedding unresolved.\n')
subprocess.run([sys.executable,str(OUT/'report.py')],check=True)
print('retained',len(keep),'circuit stems; removed',len(removed),'bulk files')

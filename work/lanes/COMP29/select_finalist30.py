"""Select only a finalist with complete independent, speed and MC receipts."""
import json,re,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent
def read(name,suffix):
    p=H/(name+suffix);return json.loads(p.read_text()) if p.exists() else {}
eligible=[]
for af in H.glob('f_*.allorders.json'):
    n=af.name.removesuffix('.allorders.json');a=json.loads(af.read_text());g=read(n,'.gate.json');s=read(n,'.screen.json');e=read(n,'.exact.json');mp=H/(n+'.mc.log')
    if not (a.get('validated') and g.get('passed') and g.get('speed',{}).get('classification')=='FAST' and s.get('exp_minus_A1',0)>=.5002 and e.get('unchanged_cli') and mp.exists()):continue
    text=mp.read_text();m=re.search(r' mean (\S+)',text)
    seeds={int(m[1]):dict(loss=float(m[2]),acceptance=float(m[3])) for m in re.finditer(r' (0|1000|2000) (\S+) ± .* acc (\S+)',text)}
    if not m or set(seeds)!={0,1000,2000} or seeds[0]['acceptance']<.5:continue
    sha=hashlib.sha256((H/(n+'.qasm')).read_bytes()).hexdigest()
    if 'source_sha256' in e:assert e['source_sha256']==sha
    if 'source_sha256' in a:assert a['source_sha256']==sha
    assert abs(e['total']-s['total'])<6e-11
    eligible.append(dict(stem=n,sha256=sha,allorders=a,exact=e,screen=s,gate=g,mc=dict(mean=float(m[1]),seeds=seeds)))
assert eligible
best=min(eligible,key=lambda r:r['allorders']['loss'])
for ext in ('.qasm','.json'):shutil.copyfile(H/(best['stem']+ext),H/('best'+ext))
best['improvement_percent_vs_v30f']=100*(1-best['allorders']['loss']/read('f_base','.allorders.json')['loss'])
(H/'best.verification.json').write_text(json.dumps(best,indent=2)+'\n')
print(best['stem'],best['allorders']['loss'],best['mc']['mean'])

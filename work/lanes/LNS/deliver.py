"""Promote only a completed, passing three-seed finalist and write its evidence."""
from core import *
import shutil
from collections import Counter

def main():
 mc={}
 for f in OUT.glob('*.mc.log'):
  for l in f.read_text().splitlines():
   m=re.match(r'(\S+) check (True|False)',l)
   if m:mc.setdefault(Path(m[1]).name,dict(seeds={},logs=set()))['check']=m[2]=='True'
   m=re.match(r'(\S+) (0|1000|2000) (\S+) ± (\S+) acc (\S+)',l)
   if m:
    z=mc.setdefault(Path(m[1]).name,dict(seeds={},logs=set()));z['seeds'][int(m[2])]=dict(loss=float(m[3]),sem=float(m[4]),acceptance=float(m[5]));z['logs'].add(f.name)
   m=re.match(r'(\S+) mean (\S+)',l)
   if m:mc.setdefault(Path(m[1]).name,dict(seeds={},logs=set()))['mean']=float(m[2])
 eligible=[(v['mean'],k,v)for k,v in mc.items()if 'mean'in v and len(v['seeds'])==3 and v.get('check')and v['seeds'][0]['acceptance']>=.5]
 val,stem,receipt=min(eligible);receipt['logs']=sorted(receipt['logs']);c=read(OUT/stem);r=c['meta']['lns_result'];assert abs(r['c1'])<1e-12
 for ext in ['.qasm','.json']:shutil.copyfile(OUT/(stem+ext),OUT/('best'+ext))
 mcscript=OUT/'inputs/mc3.py';original=ROOT/'work/lanes/MAIN/spec/mc3.py';assert mcscript.read_bytes()==original.read_bytes()
 artifact=dict(stem=stem,sha256=hashlib.sha256((OUT/'best.qasm').read_bytes()).hexdigest(),data_qubits=c['meta']['data_qubits'],mc=receipt,exact=r,R=c['meta']['R'],native_depth=c['meta']['native_depth'],CX=c['meta']['cx'],shots_per_seed=10**8,mc3_sha256=hashlib.sha256(mcscript.read_bytes()).hexdigest(),native_grid_verified=True)
 normalize(clone(c));(OUT/'delivery.json').write_text(json.dumps(artifact,indent=2))
 b=read(BASE);ops=lambda z:Counter(tuple(u.lines)for u in z['u']);removed=ops(b)-ops(c);added=ops(c)-ops(b)
 diff=dict(base=str(BASE),candidate=stem,base_R=b['meta']['R'],candidate_R=c['meta']['R'],added=[dict(lines=k,count=v)for k,v in added.items()],removed=[dict(lines=k,count=v)for k,v in removed.items()],added_declarations=sorted(set(c['tail'])-set(b['tail'])),removed_declarations=sorted(set(b['tail'])-set(c['tail'])))
 (OUT/'delivery_diff.json').write_text(json.dumps(diff,indent=2));report();print(json.dumps(artifact),flush=True)

if __name__=='__main__':main()

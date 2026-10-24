from search import *
from combine import apply_recipes
import concurrent.futures

def build():
 c=loadc(OUT/'base');sites=[i for i,u in enumerate(c['u'])if u.name=='MX'and len(u.lines)==3 and c['tags'][i]=='suffix'and detbits(' '.join(u.lines))[0]in range(47,53)]
 jobs=[]
 for mask in range(1,1<<len(sites)):
  recipes=[dict(kind='bc_reset',unit=i,q=c['u'][i].qs[0],bit=detbits(' '.join(c['u'][i].lines))[0])for j,i in enumerate(sites)if mask>>j&1]
  jobs.append(apply_recipes(recipes,f'bcreset_{mask:02x}'))
 (OUT/'runtime_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('sites',sites,'jobs',len(jobs),flush=True)

def profile_one(name):
 p=OUT/name;text=p.with_suffix('.qasm').read_text();data=json.loads(p.with_suffix('.json').read_text())['data_qubits'];tc=sys.modules['tprep.check'];original=tc._sample;parts=[];start=time.monotonic()
 def timed(circuit,shots,seed,plan=None):
  t=time.monotonic();r=original(circuit,shots,seed,plan);parts.append(dict(shots=shots,wall_seconds=time.monotonic()-t));return r
 tc._sample=timed
 try:
  r=tprep.check(text,data,shots=10000,seed=0);row=dict(stem=name,parts=parts,elapsed=time.monotonic()-start,passed=r.passed,correct=r.correct_ok,repr=str(r))
 except Exception as e:row=dict(stem=name,error=repr(e))
 finally:tc._sample=original
 p.with_suffix('.runtime.json').write_text(json.dumps(row,indent=2)+'\n');return row

if __name__=='__main__':
 if sys.argv[1]=='build':build()
 else:
  names=sys.argv[1:];workers=min(4,len(names),int(os.getenv('KNAP_CPUS','4')))
  with concurrent.futures.ProcessPoolExecutor(workers)as pool,(OUT/'runtime_profile.jsonl').open('a')as f:
   for row in pool.map(profile_one,names):f.write(json.dumps(row)+'\n');f.flush();print(json.dumps(row),flush=True)

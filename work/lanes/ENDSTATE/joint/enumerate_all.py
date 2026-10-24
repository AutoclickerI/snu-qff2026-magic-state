import os,sys,json,subprocess,concurrent.futures,time
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;P=H.parent

def one(arg):
 name,ei,release_time=arg;d=json.loads((P/(name+'.prefix.json')).read_text());em=d['embeddings'][ei];mp={int(q):v for q,v in em['mapping'].items()};outputs={mp[q]for q in d['data_qubits']};release={mp[int(q)]:t for q,t in d['release_asap'].items()};available=[q for q in range(36)if q not in outputs and(q not in mp.values()or release.get(q,999)<=release_time)];stem=H/f'enum_{name}_e{ei}_t{release_time}';start=time.monotonic()
 with stem.with_suffix('.jsonl').open('w')as out,stem.with_suffix('.stats.json').open('w')as err:r=subprocess.run([str(H/'enumerate_regions')],input=str(len(available))+' '+' '.join(map(str,available))+'\n',text=True,stdout=out,stderr=err)
 rec=dict(prefix=name,embedding=ei,release_window=release_time,available=available,returncode=r.returncode,seconds=time.monotonic()-start);stem.with_suffix('.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True);return rec
if __name__=='__main__':
 tasks=[('v30f',i,t)for t in[0,16]for i in range(6)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:rows=list(pool.map(one,tasks))
 (H/'enumeration_batch.json').write_text(json.dumps(rows,indent=2))

"""MAIN/ablate.py exact engine with moving-token labels and split idle gaps."""
import os,sys,json,re,argparse,math
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent/'MAIN'))
import ablate
from packing import P,D
from tprep.noise import schedule
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=5);p.add_argument('--regions',default='O_exposed,B_exposed,prep');a=p.parse_args()
stem=H/a.stem;r=json.loads((H/'joint52.json').read_text());meta=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text();end=49
live={}
for k,v in r['tokens'].items():
 arrivals=[0]+v['reset'];departures=v['en']+[end+1 if k[0]=='o' else v['tc']+2]
 for j,q in enumerate(v['pos']):
  for t in range(arrivals[j],departures[j]):live[t,q]=k
for i,d in enumerate(D):
 for t in range(33,r['tokens'][f'o{i}']['tc']+2):live[t,d]='d'+str(i)
def lab(q,t):
 if q in P and t<=32:return 'pre'
 k=live.get((t,q))
 if k:
  if k[0]=='d':return 'data_wait'
  if k[0]=='b' and t>30:return 'B_exposed'
  if k[0]=='o' and t>=r['tokens'][k]['tc']:return 'O_exposed'
 return 'prep'
orig=ablate.model.noise_blocks

def patched(remove):
 def nb(txt,p,noise,first_order=False):
  prog,blocks=orig(txt,p,noise,first_order);_,steps,gaps=schedule(txt)
  for i,(ins,block) in enumerate(zip(prog,blocks)):
   st=min((s for _,s in steps[i]),default=0)
   if any(lab(q,st)==remove for q in ins.qubits):
    n_idle=sum(g[0]==i for g in gaps);k=block.index(ins.text)
    for j in range(len(block)-n_idle):
     if j!=k:block[j]=re.sub(r'\(([^)]*)\)','(0)',block[j],count=1)
  for i,q,first,n in gaps:
   keep=sum(lab(q,t)!=remove for t in range(first,first+n))
   if keep==n:continue
   for j in range(len(blocks[i])-1,-1,-1):
    if blocks[i][j].startswith('DEPOLARIZE1(') and blocks[i][j].split()[-1]==str(q):
     blocks[i][j]=f'DEPOLARIZE1({.75*(1-(1-4*p/3)**keep)}) {q}';break
  return prog,blocks
 return nb
rows=[]
for region in a.regions.split(','):
 ablate.model.noise_blocks=patched(region)
 try:c1,l2,l3,A1=ablate.score(text,meta['data_qubits'],a.procs)
 finally:ablate.model.noise_blocks=orig
 row=dict(no_region=region,c1=c1,second=l2,third=l3,total=l2+l3,exp_A1=math.exp(-A1));rows.append(row);print(row,flush=True)
 Path(str(stem)+'.price.json').write_text(json.dumps(rows,indent=2)+'\n')

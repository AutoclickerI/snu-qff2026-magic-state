"""Paper's ideal X/Y destructive tomography, with software physical gauge frame.
Uses ideal coherent frame after all original measurement flips, exactly equivalent to
record-dependent correction. No idles or extra-frame gate noise. Fault-count expansion.
"""
import os,sys
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
sys.dont_write_bytecode=True
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import numpy as np, json, copy,itertools,math,collections,time
import tprep.qasm as tq
tq.adjacent=lambda a,b:True
from build import build,DATA
import model
from model import Model,comm
from engine import Engine
from tprep.noise import NoiseModel,noise_blocks,STANDARD

PAPER=NoiseModel(native_x=True)
_orig_noise=model.noise_blocks

def paper_blocks(text,p,noise):
 prog,blocks=noise_blocks(text,p,PAPER)
 # First 82 CX are physical. Last 12 implement noiseless physical software frame.
 nc=0;frame=False;first_frame=None;bulk={q:False for q in range(7,15)}
 for i,ins in enumerate(prog):
  if ins.name=='CX':
   nc+=1
   if nc==83:first_frame=i;frame=True
  if frame:blocks[i]=[ins.text]
 # The eight live bulk measurement flips occur before the ideal frame, so their
 # changed records generate the correct physical (not merely logical) frame.
 blocks[first_frame]=[f'Z_ERROR({p}) '+ ' '.join(map(str,range(7,15)))]+blocks[first_frame]
 return prog,blocks

def make_model():
 model.noise_blocks=paper_blocks
 # schedule() gap classification must be disabled since there are no idle channels.
 model.schedule=lambda text:(None, [[] for _ in model.parse(text)], [])
 q=(BASE/'rm_frame12.qasm').read_text()
 m=Model(q,DATA,p=1e-3)
 return m

def make_ed(m,basis):
 mm=copy.copy(m)
 # Add the three destructive syndrome projectors for the chosen tomography basis.
 gens=m.gen[:3] if basis=='X' else [m.gen[i]*m.gen[i+3] for i in range(3)]
 mm.proj_m=m.proj_m+[m.pull(g) for g in gens]
 mm.proj_v=m.proj_v+[None]*3
 eng=Engine(mm)
 fs=[]
 for f in m.faults:
  d=f['d']|sum(comm(f['x'],f['z'],g[0],g[1])<<(len(m.proj_m)+i) for i,g in enumerate(mm.proj_m[-3:]))
  logical=((f['e']>>6)^(f['e']>>(8 if basis=='X' else 7))^(0 if basis=='X' else f['e']>>9))&1
  fs.append((f['chan'],f['p']/1e-3,f['s'],d,logical))
 return eng,fs

if __name__=='__main__':
 m=make_model();print('paper channels',len(m.chans),collections.Counter(c['name'] for c in m.chans),flush=True)
 for b in 'XY':
  e,fs=make_ed(m,b);print(b,'rank',e.r,'faults',len(fs),'groups',len(set((s,d,z) for _,_,s,d,z in fs)),flush=True)
  print('zero',e.table(0,0)[0],e.table(0,0)[1][e.keys.index((b,0,0))],flush=True)

def enumerate_orders(e,fs,max_order=3):
 import functools
 chs=len(e.m.chans);clmask=(1<<15)-1
 grouped={}
 for ch,w,s,d,z in fs:
  key=(s,d,z)
  grouped.setdefault(key,np.zeros(chs))[ch]+=w
 keys=list(grouped);W=np.array(list(grouped.values()));tot=W.sum(axis=1);dot=W@W.T
 bysource=collections.defaultdict(list)
 for k,(s,d,z) in enumerate(keys):bysource[d&clmask].append(k)
 basis='X' if e.keys.index(('X',0,0))==0 else 'X'
 # Caller sets selected basis.
 Q=e.Qs[(e.paper_basis,0,0)]
 @functools.lru_cache(None)
 def metric(s,d):
  if d&clmask:return 0.,0.
  a=e.phi(s)
  for k,pm in enumerate(e.projs):
   sg=1-2*(int(e.v[k])^((d>>k)&1))
   a=(a+sg*e.apply(a,pm))/2
  A=float(np.vdot(a,a).real)
  E=e.expect(a,Q)
  if e.paper_basis=='Y':E=-E
  return A,E
 sums=np.zeros((max_order+1,2));sums[0]=metric(0,0)
 started=time.time();ng=len(keys)
 for a,(sa,da,za) in enumerate(keys):
  A,E=metric(sa,da);sums[1]+=tot[a]*np.array([A,(-1)**za*E])
  for b in range(a,ng):
   sb,db,zb=keys[b];s=sa^sb;d=da^db;z=za^zb
   if not d&clmask:
    w=(tot[a]*tot[b]-dot[a,b])/(2 if a==b else 1)
    A,E=metric(s,d);sums[2]+=w*np.array([A,(-1)**z*E])
   if max_order<3:continue
   for c in bysource[d&clmask]:
    if c<b:continue
    sc,dc,zc=keys[c]
    w=(tot[a]*tot[b]*tot[c]-dot[a,b]*tot[c]-dot[a,c]*tot[b]-dot[b,c]*tot[a]+2*np.dot(W[a]*W[b],W[c]))/(6 if a==b==c else 2 if a==b or b==c else 1)
    if abs(w)<1e-14:continue
    A,E=metric(s^sc,d^dc);sums[3]+=w*np.array([A,(-1)**(z^zc)*E])
  if a%100==0: print(e.paper_basis,'group',a,'/',ng,'seconds',time.time()-started,'cache',metric.cache_info(),flush=True)
 return sums

if __name__=='__main__':
 out={}
 for b in 'XY':
  e,fs=make_ed(m,b);e.paper_basis=b
  sums=enumerate_orders(e,fs,3);out[b]=sums.tolist();print('orders',b,sums.tolist(),flush=True)
  (BASE/'paper_orders.json').write_text(json.dumps(out,indent=2)+'\n')
 x,y=np.array(out['X']),np.array(out['Y']);A=(x[:,0]+y[:,0])/2;Q=(x[:,0]+y[:,0])/4-(x[:,1]+y[:,1])/(2*np.sqrt(2))
 p=1e-3;weights=np.array([p**w*(1-p)**(150-w) for w in range(4)])
 out['accepted_fault_weight']=A.tolist();out['loss_fault_weight']=Q.tolist();out['acceptance_through_fault3']=float(A@weights);out['loss_through_fault3']=float(Q@weights/(A@weights));out['coefficient_cubic']=float(Q[3]);out['missing_probability_w4plus']=float(1-sum(math.comb(150,w)*weights[w] for w in range(4)))
 (BASE/'paper_orders.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)

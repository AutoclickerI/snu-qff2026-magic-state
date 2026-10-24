"""Validated extension of reviewer3's Walsh frontend to five diagonal projectors.

The contraction/noise/decoder code is unchanged. The endpoint partition is now
checked against its actual diagonal-projector rank (including redundant projectors) rather than fixed at 4.
Finite-channel exhaustive validation precedes all full candidate contractions.
"""
from common import *
import ast,itertools,functools,multiprocessing as mp
os.environ['QUANTUMN_REPO']=str(ROOT)
sys.path.insert(0,str(H/'audit'));import fresh_exact_walsh as W
src=(H/'audit/fresh_exact_walsh.py').read_text();node=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef)and n.name=='prepare');frag=ast.get_source_segment(src,node)
frag=frag.replace('assert len(active)==4 and nr==15','''assert nr==15 and eng.r==5 and len(active) in (4,5)
    assert all(c==1 for x,z,c in eng.projs)
    pivots={}
    for i in active:
        z=eng.projs[i][1]
        while z:
            k=z.bit_length()-1
            if k in pivots:z^=pivots[k]
            else:pivots[k]=z;break
    projector_rank=len(pivots)''')
frag=frag.replace('assert all(len(v)==2 for v in where)','''assert all(len(v) in (0,1 << (eng.r-projector_rank)) for v in where)
    assert sum(bool(len(v)) for v in where)==(1 << projector_rank)
    assert sorted(int(i) for v in where for i in v)==list(range(eng.N))''')
ns=W.__dict__.copy();exec(compile(frag,str(H/'allorders5.py')+':prepare','exec'),ns);prepare=ns['prepare']

def finite_validation(prepared,variant=0):
 m,e,groups,nd,ks,psi,where,elim=prepared;active=ks[:-len(m.rots)]
 candidates=[c for c,fs in groups.items()if m.chans[c]['name']=='DEPOLARIZE2' and any(f['d']&(1<<active[-1])for f in fs)]
 ca=candidates[variant%len(candidates)]
 ids=[c for c,ch in enumerate(m.chans)if ch['name']=='DEPOLARIZE1' and c in groups];cb=sorted(ids,key=lambda c:m.chans[c]['p'],reverse=True)[variant%min(4,len(ids))]
 ids=[c for c,fs in groups.items()if c not in(ca,cb)and any(f['s']for f in fs)and m.chans[c]['name']=='DEPOLARIZE2'];cc=ids[variant%len(ids)];chosen=[ca,cb,cc]
 events=[[dict(p=1-m.chans[c]['p'],s=0,d=0,e=0)]+groups[c]for c in chosen];ea=en=0.;cache={}
 for fs in itertools.product(*events):
  p=math.prod(f['p']for f in fs);s=d=z=0
  for f in fs:s^=f['s'];d^=f['d'];z^=f['e']
  if(s,d)not in cache:cache[s,d]=e.ntable(s,d)
  aa,nn=cache[s,d];ea+=p*aa;en+=p*(0 if nn is None else nn[z])
 vals=[];kernels={}
 for key in[None]+e.keys:
  qpm=None if key is None else e.Qs[key]
  if qpm not in kernels:kernels[qpm]=W.kernel(e,ks,psi,where,key)
  mask=0 if key is None else W.emask_for(key);factors=[W.channel_factor(m,groups[c],nd,mask)for c in chosen]+[kernels[qpm]];vals.append(W.contract(factors,elim['order']))
 aa=vals[0];nn=(aa-sum(w*b*v for w,b,v in zip(e.W,e.beta,vals[1:])))/2
 out=dict(channels=chosen,events=math.prod(map(len,events)),acceptance=aa,numerator=nn,brute_acceptance=ea,brute_numerator=en,error_A=abs(aa-ea),error_N=abs(nn-en));assert out['error_A']<1e-12 and out['error_N']<1e-12,out;return out
G=None
def term(key):
 m,e,groups,nd,ks,psi,where,elim=G;st=time.monotonic();mask=0 if key is None else W.emask_for(key);factors=[W.channel_factor(m,fs,nd,mask)for fs in groups.values()]+[W.kernel(e,ks,psi,where,key)];return dict(key=key,value=W.contract(factors,elim['order']),seconds=time.monotonic()-st)

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=1);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 global G
 for stem in map(Path,a.stems):
  start=time.monotonic();G=prepare(stem);m,e,groups,nd,ks,psi,where,elim=G
  validations=[finite_validation(G,i)for i in range(2)];print('validated',stem,validations,flush=True)
  out=dict(stem=str(stem),sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),projectors=len(ks)-len(m.rots),rank=e.r,width=elim['width'],validation=validations)
  if not a.validate_only:
   keys=[None]+e.keys
   if a.procs==1:res=list(map(term,keys))
   else:
    with mp.get_context('fork').Pool(a.procs)as pool:res=pool.map(term,keys,chunksize=1)
   A=res[0]['value'];obs=sum(w*b*r['value']for w,b,r in zip(e.W,e.beta,res[1:]));out.update(acceptance=A,loss=(A-obs)/(2*A),terms=res,seconds=time.monotonic()-start)
  dest=H/(stem.name+('.ao5_validation.json'if a.validate_only else'.ao5.json'));dest.write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k not in('terms','validation')}),flush=True)
if __name__=='__main__':main()

"""Rank-three correlated BC resource with literal seven-bit final checks."""
import os,sys,json,argparse,time,collections,itertools
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
import fresh_sat as S
import ft
B,C,ROWS=ft.B,ft.C,ft.ROWS

def span(vs):
 out={0}
 for x in vs:out|={y^x for y in list(out)}
 return out

def verify(d,clean=False):
 xs={q:1<<q for q in d['pivots']}
 for layer in d['ops']:
  for u,v in layer:
   assert v in S.nb(u)
   for q,x in xs.items():
    if x>>u&1:xs[q]^=1<<v
 gs=[sum(1<<blk[i] for blk in (B,C) for i in row) for row in ROWS]
 target_ok=span(xs.values())==span(gs)
 bad=[];res=collections.Counter()
 for src in ft.sources(d,d['cells']):
  e=ft.propagate(d['ops'],src)
  diff=[(b in e) != (c in e) for b,c in zip(B,C)];sb=ft.sig(e,B)
  if not any(diff):
   res[sb]+=1
   if sb and (clean or ft.dangerous(sb)):bad.append(src)
 return dict(target_ok=target_ok,bad=bad,residues=dict(res),cx=sum(map(len,d['ops'])))

class Model(S.Model):
 def __init__(self,D,cap,seed,clean=False):
  self.clean=clean
  super().__init__(D,cap,seed)
 def cut(self,src):
  if src in self.added:return
  self.added.add(src);t,qs=src;hs=list(self.h[t][qs[0]]);guard=[]
  if len(qs)==2:
   hs=[self.xor(a,b) for a,b in zip(hs,self.h[t][qs[1]])];guard=[-self.sel[t-1][qs]]
  for sb in range(1,16 if self.clean else 9):
   self.add(guard+hs[4:]+[(-z if sb>>i&1 else z) for i,z in enumerate(hs[:4])])

def run(a):
 t=time.monotonic();m=Model(a.depth,a.cap,a.seed,a.clean);nc=0;found=0
 if a.hint:m.warm(json.loads(Path(a.hint).read_text()))
 # Every boundary single is a physical fault or conservative idle opportunity.
 if a.eager:
  for k in range(a.depth+1):
   for q in m.cells:m.cut((k,(q,)))
 status='UNKNOWN'
 while time.monotonic()-t<a.seconds:
  m.s.conf_budget(5000);ok=m.s.solve_limited()
  if ok is False:status='UNSAT';break
  if ok is None:continue
  nc+=1;d=m.candidate();v=verify(d,a.clean)
  assert v['target_ok'],v
  print(json.dumps(dict(model=nc,seconds=time.monotonic()-t,**v)),flush=True)
  if not v['bad']:
   found+=1;d.update(verification=v,clean=a.clean,seed=a.seed)
   stem=H/f'corr_d{a.depth}_k{a.cap}_s{a.seed}_{found:03d}'
   stem.with_suffix('.prep.json').write_text(json.dumps(d,indent=2)+'\n')
   with (H/'REPORT.md').open('a') as f:f.write(f'\nNative correlated resource `{stem.name}`: '+json.dumps(v)+'; complete circuit price pending.\n')
   if found>=a.count:status='SAT';break
   m.add([-z for ss in m.sel for z in ss.values() if z in set(m.s.get_model())])
  else:
   for src in v['bad']:m.cut(src)
   m.warm(d)
 r=dict(vars(a),status=status,models=nc,found=found,seconds=time.monotonic()-t,cuts=len(m.added),stats=m.s.accum_stats())
 (H/f'synth_d{a.depth}_k{a.cap}_s{a.seed}.receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--depth',type=int,required=True);p.add_argument('--cap',type=int,required=True);p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=180);p.add_argument('--count',type=int,default=2);p.add_argument('--clean',action='store_true');p.add_argument('--eager',action='store_true');p.add_argument('--hint');run(p.parse_args())

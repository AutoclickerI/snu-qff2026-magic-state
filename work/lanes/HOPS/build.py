import os,sys,json,re,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work/lanes/TREP2'),str(ROOT/'work/lanes/TREP2/inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
BASE=ROOT/'work/lanes/MAIN/v20'
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28]
def read(stem=BASE):
 text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());h,r,tail=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
 return h,u,ts,tail,meta

def save(name,h,u,ts,tail,meta):
 # The requested native layers, rather than QASM line order, specify chronology.
 text=S.emit(h,u,ts,tail);hh,rr,tt=S.qasm_ops(text);nu=S.fold_units(rr);nt=native_times(text,nu)
 order=sorted(range(len(u)),key=lambda i:(ts[i],i));assert [u[i].lines for i in order]==[x.lines for x in nu]
 assert [S.compress(ts)[i] for i in order]==nt,(name,'native timing mismatch')
 for x in nu:
  if x.name=='CX':
   a,b=x.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1,(name,x.lines)
 pre=set(meta.get('prefix_unit_indices',[]));meta=copy.deepcopy(meta);meta['prefix_unit_indices']=[j for j,i in enumerate(order)if i in pre]
 def last(c,v):return max(t for x,t in zip(nu,nt)if x.lines==[f'cx q[{c}],q[{v}];'])
 first=[last(c,v)for c,v in list(zip(meta['data_qubits'],A))+list(zip(B,C))]
 meta.update(source='MAIN/v20',variant=name,R=min(first),round_range=[min(first),max(first)],native_depth=max(nt)+1,CX=sum(x.name=='CX'for x in nu),data_hops=meta.get('data_hops',6),block_teleports=meta.get('block_teleports',0))
 stem=OUT/name;stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 stem.with_suffix('.schedule.json').write_text(json.dumps([dict(i=i,t=t,lines=x.lines,prefix=i in meta['prefix_unit_indices'])for i,(x,t)in enumerate(zip(nu,nt))],indent=1)+'\n')
 print(name,meta['R'],meta['CX'],flush=True)
 return stem

def variants():
 for mask in range(8):
  h,u,ts,tail,meta=read()
  for j,(src,dst)in enumerate([(4,10),(15,22),(8,21)]):
   if mask>>j&1:
    ix=next(i for i,x in enumerate(u)if x.lines==[f'tdg q[{src}];']);u[ix]=S.Unit([f'tdg q[{dst}];'],[]);ts[ix]=44
  meta['late_tdg_mask']=mask;save(f'tdg_{mask}',h,u,ts,tail,meta)
 for mode in ['m15','reuse9','m15_reuse9']:
  h,u,ts,tail,meta=read();drop=set()
  if 'm15' in mode:
   ix=next(i for i,x in enumerate(u)if x.lines==['reset q[15];']);u[ix]=S.Unit(['measure q[15] -> c[47];'],[]);h=[re.sub(r'creg c\[\d+\]','creg c[48]',s)for s in h];tail+=['// DETECTOR c[47]']
  if 'reuse9' in mode:
   ix=next(i for i,x in enumerate(u)if x.lines==['h q[9];','measure q[9] -> c[9];']);u[ix]=S.Unit(u[ix].lines+['h q[9];'],[])
   ix=next(i for i,x in enumerate(u)if x.lines==['reset q[9];']);drop.add(ix)
   pairs=[(next(i for i,x in enumerate(u)if i>110 and x.lines==[f'cx q[{a}],q[{b}];']),a,b) for a,b in [(8,9),(9,8)]]
   for ix,a,b in pairs:u[ix]=S.Unit([f'cx q[{b}],q[{a}];'],[])
  nu=[x for i,x in enumerate(u)if i not in drop];nt=[t for i,t in enumerate(ts)if i not in drop];pre=set(meta['prefix_unit_indices']);meta['prefix_unit_indices']=[j for j,i in enumerate(i for i in range(len(u))if i not in drop)if i in pre]
  save(mode,h,nu,nt,tail,meta)
if __name__=='__main__':variants()

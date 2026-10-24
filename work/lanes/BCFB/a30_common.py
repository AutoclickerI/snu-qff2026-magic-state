import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;ROOT=H.parents[2];D=H/'a30'
sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
import xtim
xtim.cache_dir=str(D/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(D/'.xtim_cache')
import schedule as S
from util import native_times
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];DATA=[0,20,7,10,3,22,21]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
BITS=re.compile(r'c\[(\d+)\]')
def bit(u):return int(BITS.search(next(l for l in u.lines if l.startswith('measure')))[1])
def edge(u):return tuple(map(int,re.findall(r'q\[(\d+)\]',u.lines[0])))
def source():
 p=D/'inputs/v30f';text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text());h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us);R=md['R']
 want={1:(43,'RX'),14:(41,'RESET'),8:(41,'MEASURE'),9:(40,'RX'),2:(42,'RX'),16:(44,'MEASURE'),15:(41,'RX')}
 init={q:next(i for i,(u,t) in enumerate(zip(us,ts)) if u.qs==(q,) and (t,u.name)==w) for q,w in want.items()}
 owned={i for i,u in enumerate(us) if ts[i]<R and set(u.qs)<=set(A) and all(i>=init[q] for q in u.qs)}
 assert len(owned)==21 and sum(us[i].name=='CX' for i in owned)==11
 oldbits={bit(us[i]) for i in owned if us[i].name in ('MX','MEASURE')};clean=[]
 for l in tail:
  bs=set(map(int,BITS.findall(l)))
  if bs&oldbits:assert l.startswith('// DETECTOR') and len(bs)==1
  else:clean.append(l)
 return text,md,h,us,ts,tail,init,owned,clean

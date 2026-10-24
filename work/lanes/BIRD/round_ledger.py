import os,sys,json,collections,re
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
os.environ['XTIM_TWIRL_CACHE_DIR']=str(OUT/'.xtim_cache')
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path[:0]=[str(OUT),str(ROOT/'work/lanes/TREP2')]
from audit import provenance,exact2,model,R,S,evaluate
from fast_third import third_order
text,meta,u,t,reg=provenance();orig=model.noise_blocks
model.noise_blocks=R.patch(text,u,reg,lambda r:r=='round')
ev=exact2.Eval(text,meta['data_qubits']);model.noise_blocks=orig
r=exact2.run(ev,1,keep_thr=0,third=True)
d=set(meta['data_qubits']);a=R.A_CELLS;b={6,26,13,11,4,23,27};c={12,25,19,17,5,29,28}
def label(i):
 ch=ev.m.chans[int(ev.fch[i])];lab=ev.chan_label(int(ev.fch[i]));qs=set(lab['qubits'])
 if ch['gap'] is not None and qs<=d:return 'terminal_idle'
 if ch['kind']=='gate2' and qs&d:return 'data_check_CX'
 if ch['kind']=='gate2' and qs&b and qs&c:return 'BC_check_CX'
 return 'readout_other'
sums=collections.defaultdict(float)
for val,i,j,_,_ in r['big']:sums[' x '.join(sorted([label(i),label(j)]))]+=float(val)
row=dict(second=r['loss2'],pair_sums=dict(sums),net_cubic=third_order(ev,1)[0]+r['t3bc'])
(OUT/'round_ledger.json').write_text(json.dumps(row,indent=2));print(json.dumps(row,indent=2))

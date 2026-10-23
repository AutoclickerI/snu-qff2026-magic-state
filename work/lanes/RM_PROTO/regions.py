import sys,os,json,multiprocessing as mp,warnings
sys.dont_write_bytecode=True
from score import *
from model import Model
from tprep.noise import noise_blocks
G={}
def region_worker(arg):
 name,shots,seed=arg;info=G[name]
 with warnings.catch_warnings():
  warnings.simplefilter('ignore')
  return tc._sample(xtim.Circuit(info['noisy']+'\n'+info['plan'].tail),shots,seed,info['plan'])
def main3():
 stem=Path(sys.argv[1]);shots=int(sys.argv[2]) if len(sys.argv)>2 else 100000000;procs=int(sys.argv[3]) if len(sys.argv)>3 else 4
 q=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];ev=exact2.Eval(q,data);m=ev.m
 final={d:[i for i,ins in enumerate(m.prog) if d in ins.qubits][-2:] for d in data}
 mask=np.array([any(d in ch['qubits'] and ch['ins'] in final[d] and ch['when']=='after' for d in data) for ch in m.chans])
 frame,post=declarations(m.text);plan=tc.Plan(data,frame,post,count_measurements(m.text));prog,blocks=noise_blocks(m.text,1e-3,STANDARD)
 out={'definition':'noise at final two data CX operations (entire two-qubit channels), and data idles starting at either; all other noise rest','shots':shots,'seed':0,'tail_channels':[dict(channel=int(i),**ev.chan_label(i)) for i in np.flatnonzero(mask)]}
 orig=ev.fp.copy()
 for name,select in [('tail',mask),('rest',~mask)]:
  ev.fp=orig*select[ev.fch];rr=exact2.run(ev,procs=procs);out[name+'_exact2']={k:float(rr[k]) for k in ['loss1','loss2','loss','A1','acc2']}
  channels={(ch['blk'],ch['jl'],ch['grp']):select[i] for i,ch in enumerate(m.chans)}
  lines=[]
  for ii,block in enumerate(blocks):
   for jl,line in enumerate(block):
    if '(' not in line or line.split('(')[0] not in ['DEPOLARIZE1','DEPOLARIZE2','X_ERROR','Z_ERROR']:
     lines.append(line);continue
    head,rest=line.split(')',1);name2,ps=head.split('(');qs=rest.split();arity=2 if name2=='DEPOLARIZE2' else 1
    for grp in range(len(qs)//arity):
     keep=channels.get((ii,jl,grp),False)
     lines.append(f'{name2}({ps if keep else "0"}) '+ ' '.join(qs[grp*arity:(grp+1)*arity]))
  G[name]={'noisy':'\n'.join(lines),'plan':plan}
  jobs=[(name,min(1000000,shots-i),i//1000000) for i in range(0,shots,1000000)]
  with mp.get_context('fork').Pool(procs) as pool:rs=pool.map(region_worker,jobs)
  ac=sum(r['acceptance']*job[1] for r,job in zip(rs,jobs));loss=sum(r['score']*r['acceptance']*job[1] for r,job in zip(rs,jobs))/ac
  sem=sum((r['sem']*r['acceptance']*job[1])**2 for r,job in zip(rs,jobs))**.5/ac
  out[name]={'loss':loss,'sem':sem,'acceptance':ac/shots};print(name,out[name],'2nd',out[name+'_exact2'],flush=True)
  stem.with_name(stem.name+'_regions').with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main3()

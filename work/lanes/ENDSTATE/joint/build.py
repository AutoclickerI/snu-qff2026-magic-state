"""Emit a complete circuit from a fixed region, real resource, and routed schedule."""
import os,sys,json,re,hashlib,argparse,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;P=H.parent;ROOT=H.parents[3]
from timing import schedule
from synth_resource import configure,F,endpoint

def build(path,name,seed=0,measured=True,a_prep=None,hop_t=False,row_override=None,require_clean=True):
 prep=json.loads(Path(path).read_text());row=json.loads((H/'labelled_regions.json').read_text())[prep['row_index']]
 if row_override is not None:row=json.loads(json.dumps(row_override))
 if hop_t:
  row['prefix']='v30f_hopT'
 if a_prep:
  ap=json.loads(Path(a_prep).read_text());row['a_prep']=dict(ap,ops=[edge for layer in ap['ops']for edge in layer])
 configure(row['final']['b'],row['final']['c']);v=F.verify(prep,clean=require_clean);assert v['target_ok']and not v['bad'];v['policy']='clean'if require_clean else'correctable-single diagnostic';endpoint(prep,prep['B'],prep['C']);t=schedule(row,len(prep['ops']),seed,20);assert 'R'in t,t;R=t['R'];pref=json.loads((P/(row['prefix']+'.prefix.json')).read_text());mp={int(k):v for k,v in row['mapping'].items()};ops=[]
 oldbits=sorted({int(b)for o in pref['ops']for l in o['lines']for b in re.findall(r'c\[(\d+)\]',l)});bm={b:i for i,b in enumerate(oldbits)};bit=len(bm)
 def rename(l):
  l=re.sub(r'q\[(\d+)\]',lambda m:f'q[{mp[int(m[1])]}]',l);return re.sub(r'c\[(\d+)\]',lambda m:f'c[{bm[int(m[1])]}]',l)
 det=[{bm[int(b)]for b in re.findall(r'c\[(\d+)\]',l)}for l in pref['detectors']]
 def add(time,name,qs,region,bit=None,**kw):
  q=qs[0]
  if name in('RESET','RX'):lines=[f'reset q[{q}];']+([f'h q[{q}];']if name=='RX'else[])
  elif name=='CX':lines=[f'cx q[{q}],q[{qs[1]}];']
  elif name in('MEASURE','MX'):lines=([f'h q[{q}];']if name=='MX'else[])+[f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];']if name=='MX'and kw.get('reuse')else[])
  else:lines=[f'{name.lower()} q[{q}];']
  ops.append(dict(t=int(time),name=name,qs=qs,lines=lines,region=region,tag=region,bit=bit,**kw))
 for o in pref['ops']:ops.append(dict(t=o['asap'],name=o['name'],qs=[mp[q]for q in o['qs']],lines=[rename(l)for l in o['lines']],region='prefix',tag='prefix'))
 if hop_t:
  for q in row['final']['d']:add(R-1,'TDG',[q],'prefix')
 for i,path in enumerate(t['paths']):
  for j,(u,w)in enumerate(zip(path,path[1:])):
   tt=t['hop_times'][i][j];add(tt-1,'RESET',[w],'data_hops');add(tt,'CX',[u,w],'data_hops');add(tt+1,'CX',[w,u],'data_hops');add(tt+2,'MEASURE',[u],'data_hops',bit=bit);det.append({bit});bit+=1
 for q,tt in t['a_init'].items():
  q=int(q);add(tt,'RX'if q in row['a_prep']['pivots']else'RESET',[q],'A')
 for (u,w),tt in zip(row['a_prep']['ops'],t['a_times']):add(tt,'CX',[u,w],'A')
 for q in row['region']:
  if q in prep['pivots']and measured:add(t['bc_init'],'MX',[q],'BC',bit=bit,reuse=True,init_frame=True);bit+=1
  else:add(t['bc_init'],'RX'if q in prep['pivots']else'RESET',[q],'BC')
 for j,layer in enumerate(prep['ops']):
  for u,w in layer:add(t['bc_init']+1+j,'CX',[u,w],'BC')
 reads={}
 for i in range(7):
  d,a,b,c=(row['final'][k][i]for k in'dabc');add(R,'CX',[d,a],'round');add(R,'CX',[b,c],'round');add(R+1,'CX',[b,d],'round')
  for k,q,tt,axis in [('a',a,R+1,'MEASURE'),('b',b,R+2,'MX'),('c',c,R+1,'MEASURE')]:add(tt,axis,[q],'round',bit=bit,read=True);reads[k,i]=bit;bit+=1
 ops.sort(key=lambda o:o['t']);frames={q:[set(),set()]for q in range(36)};corr={}
 for o in ops:
  qs=o['qs'];n=o['name']
  if o.get('init_frame'):frames[qs[0]]=[set(),{o['bit']}]
  elif n in('RESET','RX'):frames[qs[0]]=[set(),set()]
  elif n=='CX':u,w=qs;frames[w][0]^=frames[u][0];frames[u][1]^=frames[w][1]
  elif o.get('read'):corr[o['bit']]=frames[qs[0]][n=='MX'].copy()
  elif n=='H':frames[qs[0]].reverse()
  elif n in('T','TDG'):assert not any(frames[qs[0]])
 for k in'ab':
  for g in F.ROWS:
   ds={reads[k,i]for i in g}
   for i in g:ds^=corr[reads[k,i]]
   det.append(ds)
 for i in range(7):det.append({reads['c',i]}^corr[reads['c',i]])
 assert all(not any(frames[q])for q in row['final']['d'])
 times=sorted({o['t']for o in ops});compress={v:i for i,v in enumerate(times)};used=sorted({q for o in ops for q in o['qs']});lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];'];bar='barrier '+','.join(f'q[{q}]'for q in used)+';'
 for time in times:
  layer=[o for o in ops if o['t']==time];busy=[q for o in layer for q in o['qs']];assert len(busy)==len(set(busy)),(time,layer)
  for o in layer:
   if o['name']=='CX':u,w=o['qs'];assert abs(u//6-w//6)+abs(u%6-w%6)==1
   lines+=o['lines'];o['t']=compress[time]
  lines.append(bar)
 lines+=['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(ds))for ds in det]
 text='\n'.join(lines)+'\n';meta=dict(data_qubits=row['final']['d'],R=compress[R],R_model=R,cx=sum(o['name']=='CX'for o in ops),native_depth=len(times),resource_depth=len(prep['ops']),resource_cx=sum(map(len,prep['ops'])),resource_cells=row['region'],B=row['final']['b'],C=row['final']['c'],A=row['final']['a'],region_row=prep['row_index'],prefix=row['prefix'],prefix_embedding=row['embedding'],data_hops=t['data_hops'],measured_pivots=measured,resource_verification=v,source_resource=str(path),schedule=t)
 stem=H/name;stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2));stem.with_suffix('.plan.json').write_text(json.dumps(dict(h=lines[:4],ops=ops,tail=lines[-len(det):],meta=meta),indent=1));print(json.dumps(dict(name=name,R=meta['R'],cx=meta['cx'],resource_cx=meta['resource_cx'],data_hops=meta['data_hops'])),flush=True);return stem
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('prep');p.add_argument('name');p.add_argument('--seed',type=int,default=0);p.add_argument('--reset-pivots',action='store_true');p.add_argument('--a-prep');a=p.parse_args();build(a.prep,a.name,a.seed,not a.reset_pivots,a.a_prep)

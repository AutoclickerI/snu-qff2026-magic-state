from native import *
import hashlib
from ortools.sat.python import cp_model

def extract(name):
 head,ops,tail=read(ROOT/'work/lanes/MAIN'/name)
 seed=set()
 for i,o in enumerate(ops):
  bits=set(map(int,re.findall(r'c\[(\d+)\]',' '.join(o['lines']))))
  if o['name']=='TDG' or bits & (set(range(14))|({91}if name=='v29c'else set())):seed.add(i)
 prev={};pred={}
 for i,o in enumerate(ops):
  pred[i]=[prev[q]for q in o['qs']if q in prev]if o['name']not in('RESET','RX')else[]
  for q in o['qs']:prev[q]=i
 todo=list(seed);picked=set(seed)
 while todo:
  for j in pred[todo.pop()]:
   if j not in picked:picked.add(j);todo.append(j)
 pre=[dict(o)for i,o in enumerate(ops)if i in picked]
 bits={int(b)for o in pre for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))}
 det=[l for l in tail if l.startswith('// DETECTOR')and set(map(int,re.findall(r'c\[(\d+)\]',l)))<=bits]
 data=[0,20,7,10,3,16,8]if name=='v29c'else PD
 # Last gate on an output must be its terminal T dagger.
 for q in data:assert [o for o in pre if q in o['qs']][-1]['name']=='TDG',(name,q)
 # Derive ASAP under the actual per-wire order. Prefix gate topology is unchanged.
 avail={q:0 for q in range(36)}
 for o in pre:
  t=max(avail[q]for q in o['qs']);o['asap']=t
  for q in o['qs']:avail[q]=t+1
 per=collections.defaultdict(list)
 for i,o in enumerate(pre):
  for q in o['qs']:per[q].append(i)
 intervals=[]
 for q,seq in per.items():
  start=seq[0]
  for j,i in enumerate(seq):
   last=j+1==len(seq);resetnext=not last and pre[seq[j+1]]['name']in('RESET','RX')
   if last or resetnext:
    intervals.append(dict(cell=q,start_index=start,end_index=i,as_written=[pre[start]['t'],pre[i]['t']+1],asap=[pre[start]['asap'],pre[i]['asap']+1],output=q in data and last))
    if not last:start=seq[j+1]
 cells=sorted(per);emb=[]
 for sym in range(8):
  xy=[[(q//6,q%6),(q//6,-q%6),(-q//6,q%6),(-q//6,-q%6)]for q in []] # transformations below use explicit coordinates
  xy=[]
  for q in cells:
   r,c=divmod(q,6);xy.append([(r,c),(r,-c),(-r,c),(-r,-c),(c,r),(c,-r),(-c,r),(-c,-r)][sym])
  mr=min(r for r,c in xy);mc=min(c for r,c in xy);hh=max(r for r,c in xy)-mr+1;ww=max(c for r,c in xy)-mc+1
  for dr in range(7-hh):
   for dc in range(7-ww):emb.append(dict(sym=sym,row=dr,col=dc,mapping={q:(r-mr+dr)*6+c-mc+dc for q,(r,c)in zip(cells,xy)}))
 out=dict(name=name,sha256=hashlib.sha256((ROOT/'work/lanes/MAIN'/(name+'.qasm')).read_bytes()).hexdigest(),head=head,ops=pre,detectors=det,data_qubits=data,cells=cells,embeddings=emb,intervals=intervals,last_data_native={q:pre[per[q][-1]]['t']for q in data},last_data_asap={q:pre[per[q][-1]]['asap']for q in data},release_native={q:pre[seq[-1]]['t']+1 for q,seq in per.items()if q not in data},release_asap={q:pre[seq[-1]]['asap']+1 for q,seq in per.items()if q not in data},native_depth=max(o['t']for o in pre)+1,asap_depth=max(o['asap']for o in pre)+1,cx=sum(o['name']=='CX'for o in pre),note='backward quantum causal cone of terminal TDG gates and cultivation record bits 0..13 (and v29c bit91); reset cuts predecessor; every detector on retained records is kept; output labels track fused prefix transfers')
 (H/(name+'.prefix.json')).write_text(json.dumps(out,indent=2));print(json.dumps({k:out[k]for k in('name','data_qubits','cells','cx','native_depth','asap_depth','last_data_native','last_data_asap','release_native','release_asap')}),flush=True)
 return out
if __name__=='__main__':
 for name in ['v23h_c2c9','v29c']:extract(name)

import sys,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent

def metrics(stem):
 p=json.loads(Path(stem).with_suffix('.plan.json').read_text());m=p['meta'];ops=p['ops'];R=m['R'];busy=collections.defaultdict(set)
 for o in ops:
  for q in o['qs']:busy[q].add(o['t'])
 starts={};expo={};life=[]
 for block in ('A','B','C'):
  ex=0;starts[block]={}
  for q in m[block]:
   tags=('A',)if block=='A'else('BC',)
   own=[o for o in ops if q in o['qs']and o['region']in tags]
   first=min(o['t']for o in own);init=[o for o in own if o['name']in('RESET','RX')or o.get('init_frame')]
   if init:start=min(o['t']for o in init)
   else:
    prev=[o for o in ops if q in o['qs']and o['t']<first and o['name']in('MEASURE','MX')]
    assert prev,(stem,q);start=max(o['t']for o in prev)
   starts[block][q]=start;idle=sum(t not in busy[q]for t in range(start+1,R));ex+=idle;life.append(dict(block=block,cell=q,start=start,first_round_use=R,idle_before_round=idle))
  expo[block]=ex
 pref=json.loads((H.parent/(m['prefix']+'.prefix.json')).read_text());all48=[]
 for ei,emb in enumerate(pref['embeddings']):
  mapping={int(k):v for k,v in emb['mapping'].items()};source=[mapping[q]for q in pref['data_qubits']];dist=[abs(a//6-b//6)+abs(a%6-b%6)for a,b in zip(source,m['data_qubits'])];all48.append(dict(embedding=ei,distances=dist,total=sum(dist),max=max(dist)))
 out=dict(R=R,data_hops=m['data_hops'],hop_cx=2*m['data_hops'],block_measured_teleports=0,ancilla_idle_steps=expo,total_ancilla_idle_steps=sum(expo.values()),cells_and_start_steps=life,data_manhattan_to_fixed_endstate_all48=all48,notes='Manhattan distances for other embeddings are lower bounds, not collision-free routes. Native R and idle counts are measured from the emitted schedule; all 48 are listed against this fixed end-state. Main enumeration uses whole-grid symmetry to quotient to six translation classes.')
 Path(stem).with_suffix('.metrics.json').write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
 for s in sys.argv[1:]:print(Path(s).name,metrics(s)['total_ancilla_idle_steps'])

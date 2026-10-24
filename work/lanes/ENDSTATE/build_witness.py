import os,sys,json,itertools,collections,argparse
sys.dont_write_bytecode=True
from pathlib import Path
from library import rowkey
H=Path(__file__).resolve().parent
L=json.loads((H/'library_input.json').read_text());ENC=json.loads((H/'library_encoders.json').read_text())
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]

def label(d):
 shapes={}
 for k,qs in d['initial'].items():
  row=next(r for r in L['embeddings']if set(r[1:])==set(qs));shapes[k]=(row[0],row[1:])
 candidates=[];seen=set()
 for p in itertools.permutations(range(7)):
  key=rowkey([sum(1<<p[i]for i in g)for g in GENS])
  if key in seen:continue
  seen.add(key);blocks={}
  for k,(sid,native)in shapes.items():
   qs=[d['initial'][k][i]for i in p];perm=[native.index(q)for q in qs];cid=L['targets'].index(rowkey([sum(1<<perm[i]for i in g)for g in GENS]));b=ENC[sid][cid]
   piv=[native[j]for j in b['pivots']];ops=[[native[u],native[v]]for u,v in b['ops']]
   if k=='a':ops=[[v,u]for u,v in ops];piv=[q for q in native if q not in piv]
   blocks[k]=dict(cx=b['cx'],pivots=piv,ops=ops,native=native,shape=sid,code_class=cid)
  candidates.append(dict(permutation=list(p),max_cx=max(x['cx']for x in blocks.values()),total_cx=sum(x['cx']for x in blocks.values()),blocks=blocks))
 candidates.sort(key=lambda c:(c['max_cx'],c['total_cx']))
 out=dict(d,label_candidates=candidates)
 c=candidates[0];p=c['permutation'];out.update(initial={k:[qs[i]for i in p]for k,qs in d['initial'].items()},final={k:[qs[i]for i in p]for k,qs in d['final'].items()},blocks=c['blocks'],label_permutation=p,prep_cx=c['total_cx'],max_prep_cx=c['max_cx'])
 return out

def emit(d,name):
 bit=0;ops=[];det=[];frames={q:[set(),set()]for q in range(36)};read={};events=[]
 def reset(q,plus=False):
  ops.append(dict(name='RX'if plus else'R',qs=[q]));frames[q]=[set(),set()]
 def cx(u,v):
  assert abs(u//6-v//6)+abs(u%6-v%6)==1
  ops.append(dict(name='CX',qs=[u,v]));frames[v][0]^=frames[u][0];frames[u][1]^=frames[v][1]
 def measure(q,x=False):
  nonlocal bit
  ops.append(dict(name='MX'if x else'M',qs=[q],bit=bit));b=bit;bit+=1;return b
 occupied=set(d['final']['d']);moves={}
 for k in d['order']:
  b=d['blocks'][k];init=d['initial'][k];end=d['final'][k];assert not occupied&set(init)
  for q in init:reset(q,q in b['pivots'])
  for u,v in b['ops']:cx(u,v)
  occupied|=set(init);left={i for i in range(7)if init[i]!=end[i]};moves[k]=len(left)
  while left:
   ready=[i for i in sorted(left)if end[i]not in occupied];assert ready,(k,left,occupied)
   for i in ready:
    u,v=init[i],end[i];reset(v,k=='a');cx(v,u)if k=='a'else cx(u,v);rec=measure(u,k!='a');axis=0 if k=='a'else 1
    frames[v][axis]^=frames[u][axis]^{rec};frames[u]=[set(),set()];occupied.remove(u);occupied.add(v);left.remove(i)
 # Round: D->A and B->C, then B->D. A/C measured Z, B measured X.
 for i in range(7):cx(d['final']['d'][i],d['final']['a'][i]);cx(d['final']['b'][i],d['final']['c'][i])
 for i in range(7):cx(d['final']['b'][i],d['final']['d'][i])
 corrections={}
 for k in 'abc':
  for i,q in enumerate(d['final'][k]):
   b=measure(q,k=='b');read[k,i]=b;corrections[b]=frames[q][1 if k=='b'else 0].copy()
 for k in 'abc':
  for g in GENS+([list(range(7))]if k=='c'else[]):
   bs={read[k,i]for i in g}
   for i in g:bs^=corrections[read[k,i]]
   det.append(sorted(bs))
 assert all(not any(frames[q])for q in d['final']['d'])
 lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];','// Fragment assumes encoded data on metadata data_qubits.']
 for o in ops:
  n=o['name'];q=o['qs'][0]
  if n in('R','RX'):lines.append(f'reset q[{q}];');lines.extend([f'h q[{q}];']if n=='RX'else[])
  elif n=='CX':lines.append(f'cx q[{q}],q[{o["qs"][1]}];')
  else:
   if n=='MX':lines.append(f'h q[{q}];')
   lines.append(f'measure q[{q}] -> c[{o["bit"]}];')
 for bs in det:lines.append('// DETECTOR '+' '.join(f'c[{b}]'for b in bs))
 d.update(data_qubits=d['final']['d'],ops=ops,detectors=det,block_moves=moves,prep_plus_transfer_cx=d['prep_cx']+sum(moves.values()),fragment_cx=sum(o['name']=='CX'for o in ops),fragment_kind='encoded data input, preparation and final round; not a complete submission')
 (H/(name+'.qasm')).write_text('\n'.join(lines)+'\n');(H/(name+'.json')).write_text(json.dumps(d,indent=2));return d
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('name');a=p.parse_args();d=emit(label(json.loads(Path(a.source).read_text())),a.name);print(json.dumps({k:d[k]for k in('initial','final','order','prep_cx','max_prep_cx','block_moves','prep_plus_transfer_cx','fragment_cx')}))

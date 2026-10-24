from core import *
import copy,argparse

def apply_frames(units,dets):
 frames={q:[set(),set()] for q in range(36)};corr={}
 for u in sorted(enumerate(units),key=lambda p:(p[1]['t'],p[0])):
  u=u[1];s=u['stmts'][0];qq=u['qs']
  if 'tele' in u:
   src,dst,bit,kind=u['tele'];frames[dst]=copy.deepcopy(frames[src]);frames[dst][0 if kind=='A' else 1]^={bit};frames[src]=[set(),set()];continue
  if u.get('tele_m'):continue
  if 'mxinit' in u:frames[qq[0]]=[set(),{u['mxinit']}];continue
  if s.startswith('reset'):frames[qq[0]]=[set(),set()];continue
  if s.startswith('cx'):
   c,t=qq;frames[t][0]^=frames[c][0];frames[c][1]^=frames[t][1];continue
  ms=[x for x in u['stmts'] if x.startswith('measure')]
  if ms:
   bit=int(re.findall(r'c\[(\d+)\]',ms[0])[0]);axis=1 if s.startswith('h ') else 0;corr[bit]=frames[qq[0]][axis].copy()
  elif s.startswith('h '):frames[qq[0]].reverse()
 out=[]
 for d in dets:
  bits=set(map(int,re.findall(r'c\[(\d+)\]',d)));extra=set()
  for b in bits:extra^=corr.get(b,set())
  bits^=extra;out.append('// DETECTOR '+' '.join(f'c[{x}]' for x in sorted(bits)))
 return out,frames

def mx_variant(source,name,pivots=None):
 units,dets=parse_source(Path(str(source)+'.qasm'));enc=encoders();pivs={q for u in enc if u['tag']=='BC' and u['stmts'][0].startswith('reset') and len(u['stmts'])==2 for q in u['qs']}
 if pivots is not None:pivs&=set(pivots)
 bit=47
 for q in pivs:
  prev=[u for u in units if u['region']=='pre' and q in u['qs']]
  if prev and prev[-1]['stmts'][0].startswith('h ') and prev[-1]['stmts'][-1].startswith('measure'):prev[-1]['stmts'].append(f'h q[{q}];')
 for u in units:
  if u['region']=='prep' and u['qs'][0] in pivs and u['stmts'][0].startswith('reset') and len(u['stmts'])==2:
   q=u['qs'][0];u['stmts']=[f'h q[{q}];',f'measure q[{q}] -> c[{bit}];',f'h q[{q}];'];u['mxinit']=bit;bit+=1
 dets,frames=apply_frames(units,dets);assert all(not any(frames[q]) for q in D),frames
 emit(units,dets,D,HERE/name,dict(mx_pivots=sorted(pivs)))
 print(name,'mx_pivots',sorted(pivs),flush=True)

def build_route(path,name):
 h=json.loads(Path(path).read_text());init={int(q):v for q,v in h['init'].items()};tokens={int(q):v for q,v in h['tokens'].items()};R=h['R'];us,dets=parse_source();pre=[u for u in us if u['region']=='pre'];rnd=[u for u in us if u['region']=='round'];enc,ready=stage_prep(init);n=47
 perm=h.get('perm',{'a':list(range(7)),'b':list(range(7))})
 # Each finished wire is available to route at its first CX; ALAP encoder against these deadlines.
 deadline={q:next((t for t,mv in zip(tokens[q]['times'],tokens[q]['moves']) if mv),R) for q in A+B+C}
 for u in reversed(enc):
  u['t']=min(deadline[q] for q in u['qs'])-1
  for q in u['qs']:deadline[q]=u['t']
 for u in enc:
  u['qs']=[init[q] for q in u['qs']];u['stmts']=[QRE.sub(lambda m:f'q[{init[int(m.group(1))]}]',s) for s in u['stmts']]
  u['region']='prep'
 moves=[];initial=set(q for u in pre for q in u['qs'])|set(init[q] for q in A+B+C)
 seen=set(initial);newdets=[]
 for q,v in tokens.items():
  for src,dst,t,mv in zip(v['pos'],v['pos'][1:],v['times'],v['moves']):
   if not mv:continue
   kind='D' if q in D else ('A' if q in A else 'BC')
   prep=[f'reset q[{dst}];']+([f'h q[{dst}];'] if kind=='A' else [])
   # Reuse the source's first-use measurement recipe on never-used data destinations.
   if kind=='D' and dst not in seen:
    prep=[f'measure q[{dst}] -> c[{n}];'];newdets.append(f'// DETECTOR c[{n}]');n+=1
   moves.append(dict(stmts=prep,qs=[dst],t=t-1,region='move'))
   if kind=='D':
    moves.extend([dict(stmts=[f'cx q[{src}],q[{dst}];'],qs=[src,dst],t=t,region='move'),dict(stmts=[f'cx q[{dst}],q[{src}];'],qs=[dst,src],t=t+1,region='move')])
   else:
    cx=(dst,src) if kind=='A' else (src,dst)
    moves.append(dict(stmts=[f'cx q[{cx[0]}],q[{cx[1]}];'],qs=list(cx),t=t,tele=(src,dst,n,kind),region='move'))
    moves.append(dict(stmts=([f'h q[{src}];'] if kind=='BC' else [])+[f'measure q[{src}] -> c[{n}];'],qs=[src],t=t+1,tele_m=True,region='move'));n+=1
   seen.add(dst)
 final={q:v['pos'][-1] for q,v in tokens.items()}
 for u in rnd:
  if len(u['qs'])==2 and any(q in D for q in u['qs']):
   di=next(D.index(q) for q in u['qs'] if q in D); mp={A[di]:A[perm['a'][di]], B[di]:B[perm['b'][di]]};u['qs']=[mp.get(q,q) for q in u['qs']];u['stmts']=[QRE.sub(lambda m:f'q[{mp.get(int(m.group(1)),int(m.group(1)))}]',s) for s in u['stmts']]
  u['t']+=R-50;u['qs']=[final[q] for q in u['qs']];u['stmts']=[QRE.sub(lambda m:f'q[{final[int(m.group(1))]}]',s) for s in u['stmts']]
 # Source data-destination init records are replaced, but keep every BC and prefix record.
 dets=[d for d in dets if d not in ('// DETECTOR c[43]','// DETECTOR c[45]','// DETECTOR c[46]')]+newdets
 units=pre+enc+moves+rnd;dets,frames=apply_frames(units,dets);data=[final[q] for q in D];assert all(not any(frames[q]) for q in data),frames
 # Occupancy and one-gate-per-site audit against the constructed native units.
 busy={}
 for u in units:
  for q in u['qs']:
   assert (u['t'],q) not in busy,(u,busy.get((u['t'],q)))
   busy[u['t'],q]=u
 emit(units,dets,data,HERE/name,dict(route=str(path),R=R,init=init,final=final,moves=sum(sum(v['moves']) for v in tokens.values()),block_moves=sum(sum(v['moves']) for q,v in tokens.items() if q not in D),data_hops=sum(sum(v['moves']) for q,v in tokens.items() if q in D)))
 (HERE/(name+'.units.json')).write_text(json.dumps(units,indent=1));print(name,'R',R,'data',data,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--route');p.add_argument('--name',default='routed');p.add_argument('--mx',action='store_true');a=p.parse_args()
 if a.route:build_route(a.route,a.name)
 if a.mx:mx_variant(ROOT/'work/lanes/MAIN/spec/v17a','mx_init')

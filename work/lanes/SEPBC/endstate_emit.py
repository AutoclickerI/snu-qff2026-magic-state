"""Attach an ENDSTATE native fragment to a real cultivation prefix.

Usage: .venv/bin/python work/lanes/SEPBC/endstate_emit.py ENDSTATE.json
       --out work/lanes/SEPBC/es_name --choice 0 --prefix v23

Input contract: ENDSTATE's ops=[{name,qs,bit?}], detectors=[bit lists],
initial/final role arrays, and blocks[k].ops/pivots. Explicit per-op region
tags are retained. Gate order on each physical wire is preserved; supplied
fragment times are retimed. Native operations and detector XORs are authoritative,
so additional block moves/helpers need no new frame implementation.
"""
from common import *
import argparse,collections,random,itertools
PD=[0,20,7,4,3,15,8]
NB={q:[v for v in range(36)if abs(q//6-v//6)+abs(q%6-v%6)==1]for q in range(36)}
def transform(q,sym=0,row=0,col=0):
 r,c=divmod(q,6);r,c=[(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][sym]
 return 6*(r+row)+c+col
def autos():
 return [[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]for a in range(1,8)for b in range(1,8)for c in range(1,8)if len({a,b,c,a^b,a^c,b^c,a^b^c})==7]
def prefix(kind='v23'):
 name={'v23':'v23h_c2c9','v29':'v29c'}[kind]
 source=json.loads((H/'inputs'/(name+'.prefix.json')).read_text())
 ops=[dict(lines=o['lines'][:],t=o['asap'],tag='prefix',source_i=o['id'])for o in source['ops']]
 ops.sort(key=lambda o:o['t'])
 tail=source['detectors']
 if tail and not isinstance(tail[0],str):tail=['// DETECTOR '+' '.join(f'c[{b}]'for b in row)for row in tail]
 return ops,tail,source['data_qubits'][:]
def choices(d,kind='v23'):
 pre,tail,src=prefix(kind);out=[]
 used={q for o in d['ops']for q in o['qs']}|set(d.get('input_data_qubits',d['final']['d']))
 placements=[]
 for sym in range(8):
  transformed=[transform(q,sym)for q in used];rs=[q//6 for q in transformed];cs=[q%6 for q in transformed]
  for er in range(-min(rs),6-max(rs)):
   for ec in range(-min(cs),6-max(cs)):placements.append((sym,er,ec))
 for pr in range(3):
  for pc in range(2):
   ss=[transform(q,0,pr,pc)for q in src]
   for sym,er,ec in placements:
    end=[transform(q,sym,er,ec)for q in d.get('input_data_qubits',d['final']['d'])]
    for ai,p in enumerate(autos()):
     goals=[end[j]for j in p];dist=[abs(a//6-b//6)+abs(a%6-b%6)for a,b in zip(ss,goals)]
     out.append(dict(prefix_row=pr,prefix_col=pc,sym=sym,end_row=er,end_col=ec,auto=ai,permutation=p,source=ss,goals=goals,manhattan=sum(dist),max_manhattan=max(dist)))
 return sorted(out,key=lambda z:(z['manhattan'],z['max_manhattan'],z['prefix_row'],z['prefix_col'],z['sym'],z['auto']))
def route(source,goals,seed=0):
 rng=random.Random(seed);pos=list(source);paths=[[q]for q in pos];events=[];done=set();guard=0
 while pos!=goals:
  guard+=1
  if guard>100:raise ValueError('routing did not converge')
  eligible=[i for i in range(7)if pos[i]!=goals[i]and goals[i]not in set(pos)-{pos[i]}];rng.shuffle(eligible)
  progressed=False
  for i in eligible:
   blocked=set(pos)-{pos[i]};todo=collections.deque([pos[i]]);prev={pos[i]:None}
   while todo and goals[i]not in prev:
    q=todo.popleft();vs=NB[q][:];rng.shuffle(vs)
    for v in vs:
     if v not in blocked and v not in prev:prev[v]=q;todo.append(v)
   if goals[i]not in prev:continue
   rev=[goals[i]]
   while rev[-1]!=pos[i]:rev.append(prev[rev[-1]])
   for v in reversed(rev[:-1]):events.append((i,pos[i],v));paths[i].append(v);pos[i]=v
   progressed=True;break
  if not progressed:
   moves=[(i,v)for i,q in enumerate(pos)for v in NB[q]if v not in pos and v not in goals]
   if not moves:raise ValueError('no routing vacancy')
   i,v=rng.choice(moves);events.append((i,pos[i],v));paths[i].append(v);pos[i]=v
 return paths,events
def fragment(d,sym,bit_offset,row=0,col=0):
 data=set(d.get('input_data_qubits',d['final']['d']));raw=d['ops'];tagged=all('region'in o for o in raw)
 round_start=next(i for i,o in enumerate(raw)if o['region']=='round')if tagged else next(i for i,o in enumerate(raw)if o['name']=='CX'and set(o['qs'])&data)
 enc={};cursor=0
 if not all('region'in o for o in raw):
  for k in d.get('order',['a','b','c']):
   for edge in d['blocks'][k]['ops']:
    matches=[j for j in range(cursor,round_start)if raw[j]['name']=='CX'and raw[j]['qs']==edge]
    if not matches:raise ValueError('Interleaved/helper-assisted fragments must tag each native operation with region: encoder_a/b/c, block_teleport, or round.')
    j=matches[0];enc[j]='encoder_'+k;cursor=j+1
 out=[]
 for i,o in enumerate(raw):
  n=o['name'];qs=[transform(q,sym,row,col)for q in o['qs']];q=qs[0]
  if n in('R','RESET','RX'):lines=[f'reset q[{q}];']+([f'h q[{q}];']if n=='RX'else[])
  elif n=='CX':lines=[f'cx q[{qs[0]}],q[{qs[1]}];']
  elif n in('M','MEASURE','MX'):lines=([f'h q[{q}];']if n=='MX'else[])+[f'measure q[{q}] -> c[{o["bit"]+bit_offset}];']
  elif n in('H','S','S_DAG','X','Y','Z'):lines=[f'{"sdg"if n=="S_DAG"else n.lower()} q[{q}];']
  else:raise ValueError(('unsupported native fragment operation',o))
  tag=o.get('region',enc.get(i,'round'if i>=round_start else'block_teleport'))
  if i<round_start and n in('R','RX','RESET'):
   nxt=next((j for j in range(i+1,len(raw))if o['qs'][0]in raw[j]['qs']),None)
   if nxt in enc:tag=enc[nxt]
  item=dict(lines=lines,t=i,tag=tag,fragment_i=i,fragment_name=n)
  if 'round_offset'in o:item['round_offset']=int(o['round_offset'])
  elif tag=='round'and't'in o and'R'in d:item['round_offset']=int(o['t'])-int(d['R'])
  out.append(item)
 tail=['// DETECTOR '+' '.join(f'c[{b+bit_offset}]'for b in row)for row in d['detectors']]
 return out,tail,round_start
def build(d,ch,name,kind='v23',route_seed=0,seconds=30,workers=1,emit=True):
 if d.get('input_data_qubits',d['final']['d'])!=d['final']['d']:
  raise ValueError('Fragment data movement requires an explicit data-lifetime adapter; block moves and helper reuse are supported.')
 pre,tail,src=prefix(kind);mp={q:transform(q,0,ch['prefix_row'],ch['prefix_col'])for q in range(36)}
 for o in pre:o['lines']=rename(o['lines'],mp)
 src=ch['source'];goals=ch['goals'];paths,events=route(src,goals,route_seed)
 n=max(int(b)for o in pre for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])))+1
 frag,ftail,rstart=fragment(d,ch['sym'],n,ch.get('end_row',0),ch.get('end_col',0));n+=max(o.get('bit',-1)for o in d['ops'])+1
 m=cp_model.CpModel();R=m.NewIntVar(max(o['t']for o in pre)+1,160,'R');tv=[m.NewIntVar(0,162,f'f{i}')for i in range(len(frag))];pt=[m.NewIntVar(0,159,f'p{i}')for i in range(len(pre))];byq=collections.defaultdict(list);preq=collections.defaultdict(list)
 for i,o in enumerate(pre):
  m.Add(pt[i]<R);m.AddHint(pt[i],o['t'])
  for q in unit(o).qs:preq[q].append(i)
 for seq in preq.values():
  for a,b in zip(seq,seq[1:]):m.Add(pt[b]>pt[a])
 for i,o in enumerate(frag):
  for q in unit(o).qs:byq[q].append(i)
 for seq in byq.values():
  for a,b in zip(seq,seq[1:]):m.Add(tv[b]>tv[a])
 final={k:[transform(q,ch['sym'],ch.get('end_row',0),ch.get('end_col',0))for q in vs]for k,vs in d['final'].items()};data_in=[transform(q,ch['sym'],ch.get('end_row',0),ch.get('end_col',0))for q in d.get('input_data_qubits',d['final']['d'])]
 da=set(zip(final['d'],final['a']));bc=set(zip(final['b'],final['c']));bd=set(zip(final['b'],final['d']))
 for i,o in enumerate(frag):
  u=unit(o)
  if o['tag']=='round'and'round_offset'in o:m.Add(tv[i]==R+o['round_offset'])
  elif o['tag']!='round':m.Add(tv[i]<R)
  elif u.name=='CX':
   edge=tuple(map(int,S.QRE.findall(u.lines[0])))
   if edge in da|bc:m.Add(tv[i]==R)
   elif edge in bd:m.Add(tv[i]==R+1)
   else:raise ValueError(('noncanonical round edge; provide explicit timing adapter',edge))
  elif u.name in('MX','MEASURE'):m.Add(tv[i]==R+(2 if u.qs[0]in final['b']else 1))
  else:m.Add(tv[i]<=R+2)
 end=m.NewIntVar(0,163,'circuit_end');m.AddMaxEquality(end,[R+3]+[t+1 for t in tv])
 lives=collections.defaultdict(list);foreign=collections.defaultdict(list);release={q:pt[seq[-1]]+1 for q,seq in preq.items()};first={};restore={};prefix_start={}
 for q,seq in preq.items():
  if unit(pre[seq[0]]).name not in('RESET','RX'):
   restore[q]=m.NewBoolVar(f'restore_prefix{q}');m.Add(pt[seq[0]]>=restore[q]);prefix_start[q]=pt[seq[0]]-restore[q]
  else:prefix_start[q]=pt[seq[0]]
 def occ(q,s,e,label,is_foreign=False):
  a=m.NewIntVar(0,163,label+'start');b=m.NewIntVar(0,163,label+'end');m.Add(a==s);m.Add(b==e)
  z=m.NewIntVar(0,163,label+'duration');m.Add(z==b-a);lives[q].append(m.NewIntervalVar(a,z,b,label))
  if is_foreign:foreign[q].append((s,e))
 for q,seq in preq.items():
  starts=[0]+[k for k in range(1,len(seq))if unit(pre[seq[k]]).name in('RESET','RX')]
  for j,k in enumerate(starts):
   stop=starts[j+1]if j+1<len(starts)else len(seq);ss=prefix_start[q]if j==0 else pt[seq[k]]
   if q in src and j==len(starts)-1:first[q]=ss
   else:occ(q,ss,pt[seq[stop-1]]+1,f'prefix{q}_{j}')
 for q,seq in byq.items():
  if q in data_in:
   # Tagged fragments may borrow a final data cell for preparation before
   # the prefix state arrives. Its preparation lifetime ends before the
   # first round operation; the routed-data interval owns the rest.
   first_round=next(k for k,i in enumerate(seq)if frag[i]['tag']=='round')
   if any(frag[i]['tag']!='round' for i in seq[first_round:]):
    raise ValueError(('data-cell operation after its first round use must be tagged round',q))
   seq=seq[:first_round]
   if not seq:continue
  starts=[k for k,i in enumerate(seq)if unit(frag[i]).name in('RESET','RX')]
  assert starts and starts[0]==0,('fragment wire lacks initialization',q)
  for j,k in enumerate(starts):
   stop=starts[j+1]if j+1<len(starts)else len(seq);last=seq[stop-1];a=seq[k]
   occ(q,tv[a],tv[last]+1,f'fragment{q}_{j}',True)
 hops=[];path_times=[]
 for i,path in enumerate(paths):
  ts=[m.NewIntVar(1,155,f'd{i}hop{j}')for j in range(len(path)-1)];path_times.append(ts)
  for j,(u,v)in enumerate(zip(path,path[1:])):
   t=ts[j];m.Add(t>=release[src[i]] if j==0 else t>=ts[j-1]+2);m.Add(t+2<R+1)
   hops.extend([dict(lines=[f'reset q[{v}];'],tag='data_hops',time_expr=t-1),dict(lines=[f'cx q[{u}],q[{v}];'],tag='data_hops',time_expr=t),dict(lines=[f'cx q[{v}],q[{u}];'],tag='data_hops',time_expr=t+1),dict(lines=[f'measure q[{u}] -> c[{n}];'],tag='data_hops',time_expr=t+2)]);tail.append(f'// DETECTOR c[{n}]');n+=1
  if ts:m.Add(ts[-1]+2<=R)
  else:m.Add(R>=release[src[i]])
  ready=ts[-1]+2 if ts else release[src[i]]
  for j,o in enumerate(frag):
   if o['tag']=='round'and path[-1]in unit(o).qs:m.Add(tv[j]>=ready)
  for j,q in enumerate(path):occ(q,first[src[i]]if j==0 else ts[j-1]-1,end if j==len(path)-1 else ts[j]+3,f'data{i}_{j}',j>0)
 for q,ivs in lives.items():m.AddNoOverlap(ivs)
 # A first-use measurement/CX expects a virgin |0>. If another component
 # borrows that cell earlier, restore it with a real, noisy reset one tick
 # before the first prefix use. Explicit prefix resets already restore it.
 for q,z in restore.items():
  for j,(ss,ee)in enumerate(foreign[q]):
   before=m.NewBoolVar(f'before_prefix{q}_{j}');m.Add(ee<=prefix_start[q]).OnlyEnforceIf(before);m.Add(ee>=prefix_start[q]+1).OnlyEnforceIf(before.Not());m.Add(z>=before)
 # A guaranteed serialized route gives useful precedence hints, without fixing
 # that serialization: the solver can overlap routes and fragment preparations.
 hint_time=max(o['t']for o in pre)+2;cursor=[0]*7
 for i,u,v in events:m.AddHint(path_times[i][cursor[i]],hint_time);cursor[i]+=1;hint_time+=3
 s=cp_model.CpSolver();s.parameters.num_workers=workers;s.parameters.max_time_in_seconds=seconds;s.parameters.cp_model_presolve=False;m.Minimize(R);status=s.Solve(m)
 rec=dict(status=s.StatusName(status),seconds=s.WallTime(),bound=s.BestObjectiveBound(),choice=ch,route_seed=route_seed,data_paths=paths)
 if status not in(cp_model.FEASIBLE,cp_model.OPTIMAL):return None,rec
 first_solver=s;rr=s.Value(R);m.Add(R==rr);m.ClearHints()
 for v in pt+tv+[R]+list(restore.values())+[t for ts in path_times for t in ts]:m.AddHint(v,s.Value(v))
 terminal={seq[-1]for seq in byq.values()if unit(frag[seq[-1]]).name in('MX','MEASURE')};pterminal={seq[-1]for q,seq in preq.items()if q not in src and unit(pre[seq[-1]]).name in('MX','MEASURE')};m.Maximize(sum((-1 if i in terminal else 1)*t for i,t in enumerate(tv))+sum((-1 if i in pterminal else 1)*t for i,t in enumerate(pt))+sum(t for ts in path_times for t in ts)-100*sum(restore.values()))
 s=cp_model.CpSolver();s.parameters.num_workers=workers;s.parameters.max_time_in_seconds=seconds;s.parameters.cp_model_presolve=False;status=s.Solve(m);rec['tie_break']=s.StatusName(status)
 if status not in(cp_model.FEASIBLE,cp_model.OPTIMAL):s=first_solver
 ops=copy.deepcopy(pre)
 for i,o in enumerate(ops):o['t']=s.Value(pt[i])
 restoration_cells=[q for q,z in restore.items()if s.Value(z)]
 for q in restoration_cells:ops.append(dict(lines=[f'reset q[{q}];'],t=s.Value(pt[preq[q][0]])-1,tag='prefix',prefix_restore=True))
 for i,o in enumerate(frag):o['t']=s.Value(tv[i]);ops.append(o)
 for o in hops:o['t']=s.Value(o.pop('time_expr'));ops.append(o)
 times=sorted({o['t']for o in ops});rt=times.index(s.Value(R))
 for i,o in enumerate(ops):o['t']=times.index(o['t']);o['id']=i
 outdata=[final['d'][j]for j in ch['permutation']]
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];'],ops=ops,tail=tail+ftail,meta=dict(data_qubits=outdata,R=rt,R_model=s.Value(R),source_endstate=d.get('source_file'),prefix=kind,choice=ch,data_paths=paths,data_hops=sum(len(p)-1 for p in paths),block_teleports=sum(d.get('block_moves',{}).values()),encoders={k:b['cx']for k,b in d['blocks'].items()},schedule=rec,joint_prefix_lifetimes=True,prefix_restore_cells=restoration_cells))
 rec.update(R=rt,R_model=s.Value(R),cx=sum(unit(o).name=='CX'for o in ops),idle_objective=s.ObjectiveValue())
 if not emit:return c,rec
 c,ret=schedule(c,mode='alap',fixed_round=True,seconds=seconds)
 if c is None:raise ValueError(('full-circuit ALAP scheduling failed',ret))
 rec['alap_schedule']=ret
 (H/name).parent.mkdir(parents=True,exist_ok=True)
 stem=save(c,name);rec['stem']=str(stem);return stem,rec
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('endstate');p.add_argument('--out',required=True);p.add_argument('--prefix',choices=['v23','v29'],default='v23');p.add_argument('--choice',type=int,default=0);p.add_argument('--route-seed',type=int,default=0);p.add_argument('--seconds',type=float,default=30);p.add_argument('--workers',type=int,default=1);p.add_argument('--list-choices',action='store_true');a=p.parse_args();d=json.loads(Path(a.endstate).read_text());d['source_file']=str(Path(a.endstate).resolve());chs=choices(d,a.prefix)
 if a.list_choices:print(json.dumps(chs[:64],indent=2));return
 out=Path(a.out);name=str(out.resolve())if out.parent!=Path('.')else a.out
 stem,rec=build(d,chs[a.choice],name,a.prefix,a.route_seed,a.seconds,a.workers)
 if stem:
  try:rec['screen']=score(stem)
  except Exception as e:rec['error']=repr(e)
 (H/(name+'.build.json')).write_text(json.dumps(rec,indent=2));append_result(Path(name).name,rec,'ENDSTATE attached to the real prefix with coherent data hops and full cell-lifetime scheduling.');print(json.dumps(rec),flush=True)
if __name__=='__main__':main()

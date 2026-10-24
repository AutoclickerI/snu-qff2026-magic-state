"""Complete reverse port: v36a cultivation/guards into the compact B/C region."""
from context76 import *
import argparse,collections
from route_snapshot import route
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=4);p.add_argument('--drop-guards',default='');p.add_argument('--route-seed',type=int,default=0);p.add_argument('--transport-tdg',action='store_true');p.add_argument('--base',default='base38');p.add_argument('--shift',type=int,default=6);p.add_argument('--drop-blue',action='store_true');p.add_argument('--commute',action='store_true');a=p.parse_args();drop=set(map(int,a.drop_guards.split(',')))if a.drop_guards else set();src=read(H/'p76/control_v36a');base=json.loads((OUT/(a.base+'.plan.json')).read_text());ops=src['ops'];PD=[0,20,7,10,3,16,8];guard_records=set(range(273,278))-drop
pred={};last={};seeds=[]
for i,o in enumerate(ops):
 u=unit(o);pred[i]=[]if u.name in('RESET','RX')else[last[q]for q in u.qs if q in last]
 for q in u.qs:last[q]=i
 bs=set(map(int,re.findall(r'c\[(\d+)\]',' '.join(o['lines']))))
 if u.name=='TDG'or bs&((set(range(14))|(set()if a.drop_blue else{64,67}))|guard_records):seeds.append(i)
selected=set(seeds);todo=seeds[:]
while todo:
 for j in pred[todo.pop()]:
  if j not in selected:selected.add(j);todo.append(j)
# Dropped guard operations are identified from the authoritative v36a metadata.
guard_ops=src['meta']['wait_guards'];guard_by_record={}
for b in range(273,278):
 end=next(o for o in guard_ops if any(f'-> c[{b}];'in l for l in o['lines']));q=unit(end).qs[0];start=max(o['t']for o in guard_ops if q in unit(o).qs and unit(o).name in('RESET','RX')and o['t']<end['t']);guard_by_record[b]={(o['t'],tuple(o['lines']))for o in guard_ops if start<=o['t']<=end['t']and q in unit(o).qs}
for b in drop:
 selected={i for i in selected if(ops[i]['t'],tuple(ops[i]['lines']))not in guard_by_record[b]}
if a.drop_blue:
 for bit in [64,67]:
  end=next(o for o in ops if any(f'-> c[{bit}];'in l for l in o['lines']));q=unit(end).qs[0];start=max(o['t']for o in ops if q in unit(o).qs and unit(o).name in('RESET','RX')and o['t']<end['t'])
  selected={i for i in selected if not(start<=ops[i]['t']<=end['t'] and q in unit(ops[i]).qs)}
pre=[copy.deepcopy(ops[i])for i in sorted(selected)];prefix_bits=sorted({int(b)for o in pre for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))});pb={b:i for i,b in enumerate(prefix_bits)};tail=[]
for line in src['tail']:
 if line.startswith('// DETECTOR'):
  bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))
  if bs<=set(prefix_bits):tail.append('// DETECTOR '+' '.join(f'c[{pb[b]}]'for b in sorted(bs)))
mp={q:q+a.shift for q in range(36-a.shift)}
assert all(q in mp and mp[q]<36 for o in pre for q in unit(o).qs)
def rbits(lines,bm):return[re.sub(r'c\[(\d+)\]',lambda z:f'c[{bm[int(z[1])]}]',l)for l in lines]
for o in pre:o['lines']=rbits(rename(o['lines'],mp),pb);o['tag']='prefix_guard'
if a.transport_tdg:pre=[o for o in pre if unit(o).name!='TDG']
initial=[mp[q]for q in PD];D=base['meta']['data_qubits'];A=base['meta']['A'];B=base['meta']['B'];C=base['meta']['C'];paths,events=route(initial,D,set(B+C),a.route_seed);program=pre[:];bit=len(prefix_bits)
def add(lines,tag,offset=None):
 o=dict(lines=lines,tag=tag)
 if offset is not None:o['round_offset']=offset
 program.append(o);return o
for i,u,v in events:
 add([f'reset q[{v}];'],'data_hops');add([f'cx q[{u}],q[{v}];'],'data_hops');add([f'cx q[{v}],q[{u}];'],'data_hops');add([f'measure q[{u}] -> c[{bit}];'],'data_hops');tail.append(f'// DETECTOR c[{bit}]');bit+=1
if a.transport_tdg:
 for q in D:add([f'tdg q[{q}];'],'prefix_guard')
ap=[o for o in base['ops']if o.get('tag')=='A'and unit(o).name=='CX'];piv=[]
for q in A:
 first=min((o for o in base['ops']if o.get('tag')=='A' and q in unit(o).qs),key=lambda o:o['t']);before=[o for o in base['ops']if q in unit(o).qs and o['t']<first['t']];init=first if unit(first).name in('RX','RESET')else max(before,key=lambda o:o['t'])
 if unit(init).name in('RX','MX'):piv.append(q)
for q in A:add([f'reset q[{q}];']+([f'h q[{q}];']if q in piv else[]),'A')
for o in ap:add(o['lines'][:],'A')
suffix=[o for o in base['ops']if o.get('tag')in('BC','round')];sb=sorted({int(b)for o in suffix for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))});bm={b:bit+i for i,b in enumerate(sb)};bit+=len(sb)
for o in suffix:
 if o.get('tag')=='BC':add(rbits(o['lines'],bm),'BC')
for o in suffix:
 if o.get('tag')=='round':add(rbits(o['lines'],bm),'round',o['t']-base['meta']['R'])
for line in base['tail']:
 if line.startswith('// DETECTOR'):
  bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))
  if bs<=set(sb):tail.append('// DETECTOR '+' '.join(f'c[{bm[b]}]'for b in sorted(bs)))
m=cp_model.CpModel();R=m.NewIntVar(28,65,'round');ts=[m.NewIntVar(0,67,'op'+str(i))for i in range(len(program))];prev={}
for i,o in enumerate(program):
 for q in unit(o).qs:
  if q in prev and not a.commute:m.Add(ts[i]>ts[prev[q]])
  prev[q]=i
 m.Add(ts[i]<=R+2)
 if'round_offset'in o:m.Add(ts[i]==R+o['round_offset'])
if a.commute:commuting_precedence(m,program,ts)
s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=30;m.Minimize(R);st=s.Solve(m);rec=dict(status=s.StatusName(st),paths=paths,initial_data=initial,drop_guards=sorted(drop),transport_tdg=a.transport_tdg,drop_blue=a.drop_blue,base=a.base,prefix_ops=len(pre),prefix_cx=sum(unit(o).name=='CX'for o in pre),stats=s.ResponseStats())
if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):
 r=s.Value(R);m.Add(R==r);terminal=set()
 for q in range(36):
  seq=[i for i,o in enumerate(program)if q in unit(o).qs]
  for j,i in enumerate(seq):
   if unit(program[i]).name in('MX','MEASURE')and(j+1==len(seq)or unit(program[seq[j+1]]).name in('RESET','RX')):terminal.add(i)
 m.Minimize(sum((1 if i in terminal else-1)*t for i,t in enumerate(ts)));st=s.Solve(m);assert st in(cp_model.OPTIMAL,cp_model.FEASIBLE)
 for i,o in enumerate(program):o['t']=s.Value(ts[i]);o['id']=i
 compact={t:i for i,t in enumerate(sorted({o['t']for o in program}))};c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];'],ops=program,tail=tail,meta=dict(data_qubits=D,A=A,B=B,C=C,R=compact[r],source='v36a prefix/guards reverse port into compact B/C region',paths=paths,guard_records=sorted(guard_records),prefix_output=initial,round_model=r))
 try:stem=save(c,'p76/'+a.out);rec.update(rank(stem,a.workers));rec['R']=compact[r]
 except Exception as e:rec['error']=repr(e)
(OUT/(a.out+'.receipt.json')).write_text(json.dumps(rec,indent=2));append_result(a.out,rec,'Complete reverse-port control with v36a cultivation and selected guards, compact B/C region, native data routes and A9. Decoder synthesis is the next stage; this control is not an eligible decoder-retaining finalist.');print(json.dumps(rec),flush=True)

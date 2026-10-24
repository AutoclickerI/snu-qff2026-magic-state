"""Full-circuit native per-wire scheduling, preserving consecutive B verification.

The topological input includes region provenance. ALAP is applied to both the
prefix and preparations. Native schedule is reconstructed and checked on output.
"""
from co_design import *

def schedule_build(ops,dets,data,out,workers=2,details=None):
 # ops: list of {lines, region}. Input is a valid topological ordering.
 units=[S.Unit(o['lines'],[]) for o in ops]
 m=cp_model.CpModel();H=len(units)+3;ts=[m.NewIntVar(0,H,f't{i}') for i in range(len(units))];R=m.NewIntVar(0,H,'R');RA=m.NewIntVar(0,H,'RA');m.Add(RA<=R)
 per={}
 for i,u in enumerate(units):
  for q in u.qs:per.setdefault(q,[]).append(i)
  if ops[i]['region']=='round':m.Add(ts[i]==R+ops[i]['round_offset'])
  elif ops[i]['region']=='round_a':m.Add(ts[i]==RA+ops[i]['round_offset'])
  else:m.Add(ts[i]<=R+2 if u.name in ('MX','MEASURE') else ts[i]<R)
 for seq in per.values():
  for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i])
 terminal=set()
 for seq in per.values():
  for at,i in enumerate(seq):
   if units[i].name in ('MX','MEASURE') and (at+1==len(seq) or units[seq[at+1]].name in ('RESET','RX')):terminal.add(i)
 s=cp_model.CpSolver();s.parameters.num_workers=workers;s.parameters.max_time_in_seconds=60;s.parameters.cp_model_presolve=False
 m.Minimize(R);st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE),s.StatusName(st)
 r=s.Value(R);m.Add(R==r);m.Maximize(sum(t for i,t in enumerate(ts) if i not in terminal));st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE)
 # Preserve ALAP gates/preparations, then remove unnecessary waits before a
 # terminal measurement. A teleport source may be measured during the round.
 for i,t in enumerate(ts):
  if i not in terminal:m.Add(t==s.Value(t))
 m.Minimize(sum(ts[i] for i in terminal));st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE)
 times=[s.Value(t) for t in ts];bits=max(int(b) for o in ops for line in o['lines'] for b in re.findall(r'c\[(\d+)\]',line))+1
 head=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bits}];']
 txt=S.emit(head,units,times,dets);h,raw,tail=S.qasm_ops(txt);native_units=S.fold_units(raw);nt=native_times(txt,native_units)
 ordered=sorted(range(len(units)),key=lambda i:(times[i],i));ct={t:i for i,t in enumerate(sorted(set(times)))}
 assert [units[i].lines for i in ordered]==[u.lines for u in native_units]
 assert [ct[times[i]] for i in ordered]==nt
 native=[dict(ops[i],t=t,qs=list(u.qs),name=u.name) for i,t,u in zip(ordered,nt,native_units)]
 out=Path(out);out.with_suffix('.qasm').write_text(txt)
 meta=dict(data_qubits=data,R_native=min(u['t'] for u in native if u['region']=='round'),native_depth=max(nt)+1,cx=sum(u['name']=='CX' for u in native),schedule_status=s.StatusName(st),units_file=out.with_suffix('.units.json').name,**(details or {}))
 meta['R_A_native']=min((u['t'] for u in native if u['region']=='round_a'),default=meta['R_native'])
 out.with_suffix('.json').write_text(json.dumps(meta,indent=1));out.with_suffix('.units.json').write_text(json.dumps(native,indent=1));print(meta,flush=True)
 return meta

def build_l2(out,workers):
 pre,dets=prefix();ops=[]
 for u in pre:
  lines=list(u.lines)
  if u.name=='MX' and not lines[-1].startswith('h '):lines.append(f'h q[{u.qs[0]}];')
  ops.append(dict(lines=lines,region='pre'))
 source=(ROOT/'work/candidates/st_L2_v0.qasm').read_text();suffix=source[source.index('// region moves'):]
 reg=None;raw=[];regions=[]
 for line in suffix.splitlines():
  if line.startswith('// region'):reg=line.split()[-1]
  if S.OP_RE.match(line):raw.append(line);regions.append(reg)
 su=S.fold_units(raw);rcx=0
 for u in su:
  region=regions[u.raw_indices[0]];o=dict(lines=u.lines,region=region)
  if region=='round':
   # First 14 CX are D->A and B->C; the remaining seven B->D.
   if u.name=='CX':o['round_offset']=0 if rcx<14 else 1;rcx+=1
   else:o['round_offset']=2 if u.name=='MX' else 1
  ops.append(o)
 for line in suffix.splitlines():
  if line.startswith('// DETECTOR') and max(map(int,re.findall(r'c\[(\d+)\]',line)))>=14:dets.append(line)
 return schedule_build(ops,dets,[6,32,7,5,9,35,8],out,workers,dict(data_hops=10,block_moves=0,source='encoder19 prefix + independently prepared L2 blocks'))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',default='l2_alap');p.add_argument('--workers',type=int,default=2);a=p.parse_args();build_l2(HERE/a.out,a.workers)

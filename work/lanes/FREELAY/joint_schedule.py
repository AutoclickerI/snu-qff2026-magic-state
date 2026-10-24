"""Retained joint-prep option: solve full native timing and known-state hop reuse."""
from co_design import *
import copy

def main(a):
 txt=(HERE/'inputs/encoder19.qasm').read_text();h,r,tail=S.qasm_ops(txt);us=S.fold_units(r);old=native_times(txt,us)
 units=[dict(lines=u.lines.copy(),qs=u.qs,name=u.name,pre=t<=29,round=t>=47,offset=t-47) for u,t in zip(us,old)]
 if a.reuse:
  for src,dst in [(4,10)]+([(8,9)] if a.reuse==2 else []):
   ix=next(i for i,u in enumerate(units) if not u['pre'] and u['lines']==[f'reset q[{dst}];'])
   units.pop(ix)
   last=next(u for u in reversed(units) if u['pre'] and dst in u['qs'])
   assert last['name']=='MX';last['lines'].append(f'h q[{dst}];')
   fw=next(u for u in units if not u['pre'] and u['lines']==[f'cx q[{src}],q[{dst}];'])
   bw=next(u for u in units if not u['pre'] and u['lines']==[f'cx q[{dst}],q[{src}];'])
   fw['lines'],bw['lines']=bw['lines'],fw['lines']
 if a.exact_a:
  init={q:max(i for i,u in enumerate(units) if not u['pre'] and not u['round'] and u['qs']==(q,) and u['name'] in ('RESET','RX')) for q in AC}
  ai={i for i,u in enumerate(units) if not u['pre'] and not u['round'] and all(q in AC and i>=init[q] for q in u['qs'])}
  units=[u for i,u in enumerate(units) if i not in ai]
  p=json.loads((HERE/'inputs/prepA_L5_exact.json').read_text());new=[]
  for q in AC:
   ls=[f'reset q[{q}];']+([f'h q[{q}];'] if q in p['pivots'] else [])
   new.append(dict(lines=ls,qs=(q,),name='RX' if q in p['pivots'] else 'RESET',pre=False,round=False,offset=0))
  for L in p['ops']:
   for u,v in L:new.append(dict(lines=[f'cx q[{u}],q[{v}];'],qs=(u,v),name='CX',pre=False,round=False,offset=0))
  first=next(i for i,u in enumerate(units) if u['round']);units[first:first]=new
 m=cp_model.CpModel();ts=[m.NewIntVar(0,70,f't{i}') for i in range(len(units))];R=m.NewIntVar(29,65,'R')
 per={}
 for i,u in enumerate(units):
  for q in u['qs']:per.setdefault(q,[]).append(i)
  if u['round']:m.Add(ts[i]==R+u['offset'])
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i])
 # Explicitly force all preparation operations before round; wire order also implies this.
 for i,u in enumerate(units):
  if not u['round']:m.Add(ts[i]<R)
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=30
 m.Minimize(R);st=s.Solve(m);assert st in (cp_model.FEASIBLE,cp_model.OPTIMAL)
 bestR=s.Value(R);m.Add(R==bestR)
 if a.mode=='alap':obj=-sum(ts)
 elif a.mode=='prefix':obj=-100*sum(ts[i] for i,u in enumerate(units) if u['pre'])-sum(ts)
 else:
  terms=[]
  for q,seq in per.items():
   for i,j in zip(seq,seq[1:]):
    if units[j]['name'] not in ('RESET','RX'):
     terms.append((a.data_weight if q in D0 else 1)*(ts[j]-ts[i]-1))
  obj=sum(terms)
 m.Minimize(obj);st=s.Solve(m);assert st in (cp_model.FEASIBLE,cp_model.OPTIMAL)
 times=[s.Value(t) for t in ts];su=[S.Unit(u['lines'],[]) for u in units];out=S.emit(h,su,times,tail)
 hh,rr,tt=S.qasm_ops(out);nu=S.fold_units(rr);nt=native_times(out,nu)
 intended=[(t,u['lines']) for t,u in sorted(zip(times,units),key=lambda z:z[0])]
 actual=[(t,u.lines) for t,u in zip(nt,nu)]
 assert intended==actual,(intended,actual)
 data=[0,20,7,10,3,22,21];preend=max(t for t,u in zip(times,units) if u['pre'])
 path=HERE/a.out;path.with_suffix('.qasm').write_text(out)
 meta=dict(data_qubits=data,R=bestR,pre_end=preend,native_depth=max(nt)+1,cx=sum(u.name=='CX' for u in nu),args=vars(a),status=s.StatusName(st),proxy=s.ObjectiveValue(),bound=s.BestObjectiveBound(),
  prefix_unit_indices=[j for j,(_,u) in enumerate(sorted(zip(times,units),key=lambda z:z[0])) if u['pre']])
 path.with_suffix('.json').write_text(json.dumps(meta,indent=1));print(json.dumps(meta),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--reuse',type=int,default=1);p.add_argument('--exact-a',action='store_true');p.add_argument('--mode',choices=['alap','prefix','idle'],default='alap');p.add_argument('--data-weight',type=int,default=8);p.add_argument('--workers',type=int,default=2);main(p.parse_args())

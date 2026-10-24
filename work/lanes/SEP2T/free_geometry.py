"""Free final geometry with A encoded in place and separate early B/C blocks."""
from co_design import *

def main(a):
 m=cp_model.CpModel();ini={};fin={};ds=[];bs=[];em=json.loads((HERE/'inputs/l5_11.embeddings.json').read_text());free=set(range(36))-P0
 em=[e for e in em if set(e)<=free]
 if a.automorphisms:
  em=list({tuple(e[j] for j in p) for e in em for p in automorphisms()})
 for k in 'dabc':
  fin[k]=[m.NewIntVar(0,35,f'{k}f{i}') for i in range(7)]
  if k=='d':
   for i,q in enumerate(D0):
    d=m.NewIntVar(0,a.dhops,f'd{i}');m.AddAllowedAssignments([fin[k][i],d],[(v,abs(q//6-v//6)+abs(q%6-v%6)) for v in range(36) if abs(q//6-v//6)+abs(q%6-v%6)<=a.dhops]);ds.append(d)
  elif k=='a':
   ini[k]=fin[k]
   p=template(a.option,k)
   for u,v in {tuple(sorted(e)) for L in p['ops'] for e in L}:m.AddAllowedAssignments([fin[k][u],fin[k][v]],EDGES)
  else:
   ini[k]=[m.NewIntVar(0,35,f'{k}i{i}') for i in range(7)];m.AddAllowedAssignments(ini[k],em)
   for i in range(7):
    d=m.NewIntVar(0,a.bhops,f'{k}dist{i}');m.AddAllowedAssignments([ini[k][i],fin[k][i],d],[(u,v,abs(u//6-v//6)+abs(u%6-v%6)) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)<=a.bhops]);bs.append(d)
 m.AddAllDifferent(sum(fin.values(),[]));m.AddAllDifferent(ini['b']+ini['c']+fin['d'])
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([fin[k][i],fin[l][i]],EDGES)
 m.Minimize(5*sum(ds)+sum(bs));s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed
 out=HERE/a.out
 def result(cb):return dict(initial={k:[cb.Value(v) for v in vv] for k,vv in ini.items()},final={k:[cb.Value(v) for v in vv] for k,vv in fin.items()},cost=cb.ObjectiveValue(),args=vars(a),data_distance=sum(cb.Value(d) for d in ds),block_distance=sum(cb.Value(d) for d in bs))
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   x=result(self);out.with_suffix('.json').write_text(json.dumps(x,indent=1));Path(str(out)+f'_{int(self.ObjectiveValue())}.json').write_text(json.dumps(x,indent=1));print('incumbent',x['cost'],x['data_distance'],x['block_distance'],self.WallTime(),flush=True)
 st=s.Solve(m,CB());receipt=dict(status=s.StatusName(st),result='TIMEOUT' if st==cp_model.UNKNOWN else s.StatusName(st),stats=s.ResponseStats(),args=vars(a));out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=1));print(receipt,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=2);p.add_argument('--seconds',type=float,default=180);p.add_argument('--dhops',type=int,default=3);p.add_argument('--bhops',type=int,default=6);p.add_argument('--option',default='l5_11');p.add_argument('--automorphisms',action='store_true');p.add_argument('--seed',type=int,default=0);main(p.parse_args())

"""Three independently connected blocks; data may move and need not connect."""
from common import *
import argparse
EDGES=[(a,b)for a in range(36)for b in range(36)if abs(a//6-b//6)+abs(a%6-b%6)==1]
PD=[0,20,7,4,3,15,8]
P={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=300);p.add_argument('--workers',type=int,default=2);p.add_argument('--maxhop',type=int,default=4);p.add_argument('--a-connect',action='store_true');p.add_argument('--tag',default='static');a=p.parse_args()
 m=cp_model.CpModel();x={};pos={};mem={}
 for k in 'dabc':
  for i in range(7):
   xs=[m.NewBoolVar(f'{k}{i}_{q}')for q in range(36)]
   x[k,i]=xs;m.AddExactlyOne(xs);pos[k,i]=m.NewIntVar(0,35,f'p{k}{i}');m.Add(pos[k,i]==sum(q*z for q,z in enumerate(xs)))
  for q in range(36):mem[k,q]=sum(x[k,i][q]for i in range(7))
 for q in range(36):m.Add(sum(mem[k,q]for k in 'dabc')<=1)
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([pos[k,i],pos[l,i]],EDGES)
 for k in ('abc'if a.a_connect else'bc'):
  flow={e:m.NewIntVar(0,7,f'f{k}{e}')for e in EDGES}
  for (u,v),z in flow.items():m.Add(z<=7*mem[k,u]);m.Add(z<=7*mem[k,v])
  for q in range(36):m.Add(sum(flow[u,v]-flow[v,u]for u,v in EDGES if u==q)==7*x[k,0][q]-mem[k,q])
 hop=[]
 for i,q in enumerate(PD):
  ds=[abs(q//6-v//6)+abs(q%6-v%6)for v in range(36)];h=sum(d*z for d,z in zip(ds,x['d',i]));m.Add(h<=a.maxhop);hop.append(h)
 m.Minimize(1000*sum(hop)+sum(mem[k,q]for k in'bc'for q in P))
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False
 st=s.Solve(m);r=dict(status=s.StatusName(st),seconds=s.WallTime(),bound=s.BestObjectiveBound(),args=vars(a),stats=s.ResponseStats())
 if st in(cp_model.FEASIBLE,cp_model.OPTIMAL):r.update(layout={k:[s.Value(pos[k,i])for i in range(7)]for k in'dabc'},hops=sum(s.Value(h)for h in hop),objective=s.ObjectiveValue())
 (H/(a.tag+'.json')).write_text(json.dumps(r,indent=2));append_result(a.tag,r,'Static connected B/C regions with free data and A endpoints; does not yet assert short encoders or timed routability.');print(json.dumps(r),flush=True)
if __name__=='__main__':main()

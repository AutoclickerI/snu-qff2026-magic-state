"""Legally reorder commuting CXs, then minimize round start and price full circuits."""
from critical import *
from ortools.sat.python import cp_model
import argparse
A_START={1:43,2:42,8:41,9:40,14:41,15:41,16:44}
def annotate(c):
 R=c['meta']['R'];before=[o for o in c['ops']if o['t']<R];init={};astart={}
 for q in B+C:
  seq=[o for o in before if q in unit(o).qs];resets=[o for o in seq if unit(o).name in('RESET','RX')]
  init[q]=(resets[-1]if resets else seq[0])['t']
 for q in A:
  seq=[o for o in before if q in unit(o).qs]
  if q in(8,16):
   bit={8:54,16:55}[q];start=next(o for o in seq if f'measure q[{q}] -> c[{bit}];'in o['lines'])
  else:start=[o for o in seq if unit(o).name in('RESET','RX')][-1]
  astart[q]=start['t']
 for o in c['ops']:
  u=unit(o);o['origin_t']=o['t'];qs=set(u.qs)
  if o['t']>=R:tag='round'
  elif qs<=set(B+C) and all(o['t']>=init[q]for q in qs):tag='encoder_bc'
  elif qs<=set(A) and all(o['t']>=astart[q]for q in qs):tag='encoder_a'
  elif u.name in('CX','MEASURE','RESET')and o['t']>=32 and qs&{9,15,16,21,22}:tag='data_hops'
  else:tag='prefix'
  o['tag']=tag
 return c

def solve(c,cut=27,seconds=60,workers=1,seed=0,fixR=None,phases=False):
 c=copy.deepcopy(c);ops=c['ops'];us=[unit(o)for o in ops];n=len(ops);R0=c['meta']['R'];m=cp_model.CpModel();R=m.NewIntVar(0,R0,'R');tv=[m.NewIntVar(0,R0+2,f't{i}')for i in range(n)]
 byq=collections.defaultdict(list);pred=[[]for _ in ops]
 for j,u in enumerate(us):
  m.AddHint(tv[j],ops[j]['t'])
  for q in u.qs:byq[q].append(j)
  if ops[j]['t']>=R0:m.Add(tv[j]==R+ops[j]['t']-R0)
  else:m.Add(tv[j]<R)
  for i in range(j):
   if not set(us[i].qs)&set(u.qs):continue
   commute=False
   if us[i].name==u.name=='CX'and cut<=ops[i]['t']<R0 and cut<=ops[j]['t']<R0:
    ac,at=map(int,S.QRE.findall(us[i].lines[0]));bc,bt=map(int,S.QRE.findall(u.lines[0]));commute=ac!=bt and bc!=at
   if phases and cut<=ops[i]['t']<R0 and cut<=ops[j]['t']<R0:
    for a,b in [(us[i],u),(u,us[i])]:
     if a.name=='CX'and b.name in('T','TDG','S','SDG','Z','X'):
      control,target=map(int,S.QRE.findall(a.lines[0]));commute|=b.qs[0]==(target if b.name=='X'else control)
    if us[i].name in('T','TDG','S','SDG','Z')and u.name in('T','TDG','S','SDG','Z'):commute=True
   if not commute:m.Add(tv[j]>tv[i]);pred[j].append(i)
 for q,seq in byq.items():m.AddAllDifferent([tv[i]for i in seq])
 if fixR is not None:m.Add(R==fixR)
 m.Minimize(R);s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;s.parameters.random_seed=seed;st=s.Solve(m)
 rec=dict(status=s.StatusName(st),bound=s.BestObjectiveBound(),seconds=s.WallTime(),cut=cut,seed=seed,commuting_phases=phases)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,rec
 best=s;rr=s.Value(R);rec['R']=rr;m.Add(R==rr);m.ClearHints()
 for t in tv:m.AddHint(t,s.Value(t))
 m.AddHint(R,rr)
 terminal=set()
 for q,seq in byq.items():
  for k,i in enumerate(seq):
   if us[i].name in('MEASURE','MX')and(k+1==len(seq)or us[seq[k+1]].name in('RESET','RX')):terminal.add(i)
 m.Maximize(sum((-1 if i in terminal else 1)*t for i,t in enumerate(tv)))
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;s.parameters.random_seed=seed;st=s.Solve(m);rec['alap_status']=s.StatusName(st)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):s=best
 for i,o in enumerate(ops):o['t']=s.Value(tv[i])
 c['meta']['R']=rr;c['meta']['commuting_retime']=rec
 return c,rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cut',type=int,default=27);p.add_argument('--seconds',type=float,default=60);p.add_argument('--workers',type=int,default=1);p.add_argument('--seed',type=int,default=0);p.add_argument('--name',required=True);a=p.parse_args();c=annotate(read(H/'inputs/v30f'));d,r=solve(c,a.cut,a.seconds,a.workers,a.seed)
 if d:
  st=save(d,'v30/'+a.name)
  try:r['screen']=score(st)
  except Exception as e:r['score_error']=repr(e)
 (V/(a.name+'.build.json')).write_text(json.dumps(r,indent=2));append_result(a.name,r,'Commuting CX reorder with shared-cell capacity; noiseless identities only, full noise repriced.');print(json.dumps(r),flush=True)

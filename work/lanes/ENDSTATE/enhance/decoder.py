"""Enumerate native <=3-CX A decoders, logical-X and stabilizer-X flags."""
from common import *
import itertools,collections
from ortools.sat.python import cp_model

def span(gs):
 s={0}
 for g in gs:s|={x^g for x in list(s)}
 return s

def options(A):
 edges=[(u,v)for u in range(7)for v in range(7)if abs(A[u]//6-A[v]//6)+abs(A[u]%6-A[v]%6)==1];stab=span([sum(1<<i for i in g)for g in SUPPORTS]);logical={127^g for g in stab};seen=set();out=[]
 for n in (1,2,3):
  for seq in itertools.product(edges,repeat=n):
   if any(a==b for a,b in zip(seq,seq[1:])):continue
   matrix=[]
   for root in range(7):
    x=1<<root
    for u,v in reversed(seq):
     if x>>u&1:x^=1<<v
    matrix.append(x)
   for root,x in enumerate(matrix):
    if x not in logical|stab or not x:continue
    if x.bit_count()<3:continue
    key=(tuple(matrix),root)
    if key in seen:continue
    seen.add(key);out.append(dict(edges=[[A[u],A[v]]for u,v in seq],root=A[root],support=[A[i]for i in range(7)if x>>i&1],support_labels=[i for i in range(7)if x>>i&1],kind='logical_X'if x in logical else'stabilizer_X',cx=n))
 return out

def build(base,opt,name,late_bd=True,late_da=True):
 p=copy.deepcopy(base);A=p['meta']['A'];reads={o['qs'][0]:o for o in p['ops']if o['region']=='round'and o['name']=='MEASURE'and o['qs'][0]in A};assert set(reads)==set(A);bits={q:int(re.search(r'c\[(\d+)\]',o['lines'][0])[1])for q,o in reads.items()};dets=[set(map(int,re.findall(r'c\[(\d+)\]',l)))for l in p['tail']]
 for u,v in opt['edges']:
  for d in dets:
   if bits[v]in d:d.symmetric_difference_update({bits[u]})
 assert all(bits[opt['root']]not in d for d in dets);dets.append({bits[opt['root']]});p['tail']=['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(d))for d in dets]
 ops=[o for o in sorted(p['ops'],key=lambda o:o['t'])if o not in reads.values()];oldend=max(o['t']for o in p['ops']);R=p['meta']['R']
 for j,(u,v)in enumerate(opt['edges']):ops.append(dict(t=R+j,name='CX',qs=[u,v],lines=[f'cx q[{u}],q[{v}];'],region='A_decoder'))
 for q,o in reads.items():
  o=copy.deepcopy(o)
  if q==opt['root']:o.update(name='MX',lines=[f'h q[{q}];',f'measure q[{q}] -> c[{bits[q]}];'])
  ops.append(o)
 m=cp_model.CpModel();end=m.NewIntVar(0,oldend+3,'end');ts=[m.NewIntVar(0,oldend+3,f't{i}')for i in range(len(ops))];last={}
 for i,o in enumerate(ops):
  m.Add(ts[i]<=end)
  for q in o['qs']:
   if q in last:m.Add(ts[i]>ts[last[q]])
   last[q]=i
  if late_bd and o['region']=='round':
   if o['name']=='CX'and o['qs'][0]in p['meta']['B']and o['qs'][1]in p['meta']['data_qubits']:m.Add(ts[i]==end-1)
   if o['name']=='MX'and o['qs'][0]in p['meta']['B']:m.Add(ts[i]==end)
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;m.Minimize(end);status=s.Solve(m);assert status==cp_model.OPTIMAL;best=s.Value(end)
 if best>oldend+1:return None
 m.Add(end==best);dev=[]
 if late_da:
  da=[ts[i]for i,o in enumerate(ops)if o['region']=='round'and o['name']=='CX'and o['qs'][0]in p['meta']['data_qubits']and o['qs'][1]in A]
  assert len(da)==7;m.Maximize(sum(da));status=s.Solve(m);assert status==cp_model.OPTIMAL;m.Add(sum(da)==s.Value(sum(da)))
 for i,o in enumerate(ops):
  d=m.NewIntVar(0,oldend+3,f'd{i}');m.AddAbsEquality(d,ts[i]-o['t']);dev.append(d)
 m.Minimize(sum(dev));status=s.Solve(m);assert status==cp_model.OPTIMAL
 for o,t in zip(ops,ts):o['t']=s.Value(t)
 p['ops']=ops;p['meta']['A_decoder']=dict(opt,minimum_native_end=best,prior_native_end=oldend,late_BD=late_bd,late_DA=late_da,old_readout_bits=bits,flag_record=bits[opt['root']],proof='Backward X propagation belongs to A X-stabilizer group; X on CX targets commutes with transversal D->A. All old Z-detector rows are conjugated and avoid the X-read root.')
 return save(p,name)

if __name__=='__main__':
 base=load(P/'joint/region2_k56_A2_safe_dest');opts=options(base['meta']['A']);out=[]
 for i,opt in enumerate(opts):
  s=build(base,opt,f'a_ports_{i:03d}')
  if s is not None:out.append(dict(stem=s.name,option=opt))
 (H/'decoder_ports_candidates.json').write_text(json.dumps(out,indent=2));(H/'decoder_ports_scope.json').write_text(json.dumps(dict(all_sequences=len(opts),scheduled=len(out),CX_cap=3,end_extension_cap=1,late_BD=True,late_DA=True,original_A=base['meta']['A']),indent=2));print('decoder options',len(opts),'scheduled',len(out),collections.Counter((o['option']['cx'],o['option']['kind'])for o in out),flush=True)

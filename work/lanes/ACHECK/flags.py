from common import *
sys.path[:0]=[str(ROOT/'work/lanes/FLAG'),str(ROOT/'work/lanes/DR')]
from flag_search import build_flagged_layers
from flag_scorer import score_flagged
from synth import check,HAM_POS
from variants import retime

def search():
 cs=json.loads((HERE/'encoder_candidates.json').read_text());rows=[]
 for ci,c in enumerate(cs):
  for f,q in [(13,14),(17,16)]:
   for t1 in range(len(c['ops'])):
    for t2 in range(t1+1,len(c['ops'])+1):
     layers,flags=build_flagged_layers(c['ops'],[dict(cell=f,q=q,t1=t1,t2=t2)])
     # A + flag must end in the same tensor-product CSS state; checking only
     # propagated fault signatures would miss a noiselessly random flag.
     vec=[{p} for p in c['pivots']+[f]]
     for L in layers:
      for a,b in L:
       for v in vec:
        if a in v:v.symmetric_difference_update({b})
     span={frozenset()}
     for v in vec:span|={frozenset(set(w)^v) for w in list(span)}
     want=[{A[i] for i in g} for g in HAM_POS]+[set(A),{f}]
     if any(frozenset(w) not in span for w in want):continue
     z=score_flagged(layers,c['pivots'],A,A+[f],flags)
     if z['danger']>=c.get('danger',1):continue
     row=dict(z);row.update(encoder=ci,flags=flags,ops=layers,pivots=c['pivots'],base_danger=c.get('danger'));rows.append(row)
 rows.sort(key=lambda x:(x['danger'],len(x['ops'])))
 (HERE/'flag_search.json').write_text(json.dumps(rows,indent=1));print('flags',len(rows),flush=True)
 # Keep best per (flag cell, depth, danger) rather than duplicate windows.
 keep=[];seen=set()
 for row in rows:
  key=(row['flags'][0]['cell'],len(row['ops']),row['danger'])
  if key not in seen:seen.add(key);keep.append(row)
 for k,row in enumerate(keep[:24]):build(k,row)

def build(k,c):
 h,us,tail,ts,meta,init,ai=base();f=c['flags'][0]['cell'];q=c['flags'][0]['q']
 before=[i for i,t in enumerate(ts) if t<45 and i not in ai];after=[i for i,t in enumerate(ts) if t>=45]
 # Encoder and flag must precede the borrowed B/C cell's initialization.
 cut=next(j for j,i in enumerate(before) if f in us[i].qs and i not in set(meta['prefix_unit_indices']))
 # Move all non-prefix operations to a suffix list; per-qubit dependencies
 # place A after its data hops, flag before BC. General DAG handles this.
 au=[unit([f'reset q[{v}];']+([f'h q[{v}];'] if v in c['pivots'] else [])) for v in A]
 au+=[unit([f'reset q[{f}];',f'h q[{f}];'])]
 au += [unit([f'cx q[{u}],q[{v}];']) for L in c['ops'] for u,v in L]
 au += [unit([f'h q[{f}];',f'measure q[{f}] -> c[100];'])]
 uu=[us[i] for i in before]+au+[us[i] for i in after];old=[ts[i] for i in before]+[40]*len(au)+[ts[i] for i in after]
 # Reorder borrowed wire alone: prefix uses, flag uses, BC uses. Other
 # per-qubit orders remain base then A then round.
 from ortools.sat.python import cp_model
 m=cp_model.CpModel();tv=[m.NewIntVar(0,100,f't{i}') for i in range(len(uu))];R=m.NewIntVar(40,98,'R')
 per={}
 for i,u in enumerate(uu):
  for v in u.qs:per.setdefault(v,[]).append(i)
  if i>=len(before)+len(au):m.Add(tv[i]==R+old[i]-45)
  else:m.Add(tv[i]<R)
 seq=per[f];prefix=[j for j in seq if j<len(before) and before[j] in set(meta['prefix_unit_indices'])]
 flag=[j for j in seq if len(before)<=j<len(before)+len(au)]
 rest=[j for j in seq if j not in prefix+flag];per[f]=prefix+flag+rest
 for seq in per.values():
  for i,j in zip(seq,seq[1:]):m.Add(tv[j]>tv[i])
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=10;m.Minimize(R);st=s.Solve(m)
 if st not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return
 m.Add(R==s.Value(R));m.Maximize(sum(tv));st=s.Solve(m)
 times=[s.Value(t) for t in tv]
 emit(f'flag_{k:02}',uu,times,tail+['// DETECTOR c[100]'],dict(R=s.Value(R),method='A encoder flag, borrowed BC cell',flag=c))

if __name__=='__main__':search()

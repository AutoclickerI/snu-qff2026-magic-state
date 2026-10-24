import sys,json,copy,re,collections
from pathlib import Path
sys.path.insert(0,'work/lanes/FRESH');import common
from ortools.sat.python import cp_model
H=Path('work/lanes/FRESH')
def main():
 base='work/lanes/FRESH/corr_d11_k57_s35_002_v23h_c2c9_w0_fast';prefstem='work/lanes/TREP2/joint21_compact_reuse10_alap_two_moves';
 bc=common.read(base);pc=common.read(prefstem);pmeta=json.load(open(prefstem+'.json'));pidx=set(pmeta['prefix_unit_indices']);pops=pc['ops'];
 # candidate prefix via ladder subsequence
 ladder=json.load(open('work/lanes/SEPBC/inputs/ladder_f00.json'))['units'];want=[tuple(x['lines']) for x in ladder if x.get('tag')=='prefix'];order=sorted(range(len(bc['ops'])),key=lambda i:(bc['ops'][i]['t'],i));pi=[];j=0
 for i in order:
  if j<len(want) and tuple(bc['ops'][i]['lines'])==want[j]:pi.append(i);j+=1
 assert j==len(want)
 suf=[i for i in order if i not in set(pi)];R0=45
 rounds=[i for i in suf if bc['ops'][i]['t']>=R0];prep=[i for i in suf if i not in rounds]
 # Use compact prefix ops, candidate suffix operations/detectors.
 ops=[]
 for i in sorted(pidx):
  o=copy.deepcopy(pops[i]);o['kind']='prefix';ops.append(o)
 for i in prep:
  o=copy.deepcopy(bc['ops'][i]);o['kind']='prep';ops.append(o)
 for i in rounds:
  o=copy.deepcopy(bc['ops'][i]);o['kind']='round';ops.append(o)
 m=cp_model.CpModel();R=m.NewIntVar(33,R0,'R');tv=[m.NewIntVar(0,100,f't{i}') for i in range(len(ops))]
 for i,o in enumerate(ops):
  if o['kind']=='prefix':m.Add(tv[i]==o['t'])
  elif o['kind']=='round':m.Add(tv[i]==R+o['t']-R0)
  else:m.Add(tv[i]<R)
 by=collections.defaultdict(list)
 # explicit logical order: prefix -> prep -> round on each wire.
 for i,o in enumerate(ops):
  for q in common.unit(o).qs:by[q].append(i)
 for seq in by.values():
  for a,b in zip(seq,seq[1:]):m.Add(tv[b]>tv[a])
 m.Minimize(R);s=cp_model.CpSolver();s.parameters.max_time_in_seconds=60;s.parameters.num_search_workers=1;st=s.Solve(m);print('solve',s.StatusName(st),s.WallTime(),flush=True)
 if st not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return
 best=s.Value(R);m.Add(R==best);m.Maximize(sum(tv[i] for i in range(len(ops)) if ops[i]['kind']=='prep'));st=s.Solve(m);print('tie',best,s.StatusName(st),s.WallTime(),flush=True)
 for i,o in enumerate(ops):o['t']=s.Value(tv[i]);o['id']=i
 # Tail: compact prefix detectors then candidate suffix detectors (14 prefix dets).
 td=[x for x in pc['tail'] if x.startswith('// DETECTOR')];bd=[x for x in bc['tail'] if x.startswith('// DETECTOR')];tail=td[:14]+bd[14:]
 h=copy.deepcopy(bc['h']);meta=copy.deepcopy(bc['meta']);meta.update(R=best,prefix=prefstem,hybrid_prefix=True,native_depth=max(o['t'] for o in ops)+1,cx=sum(common.unit(o).name=='CX' for o in ops))
 c=dict(h=h,ops=ops,tail=tail,meta=meta)
 out=common.save(c,'hybrid_v23corr_compact');print(out,common.score(out),flush=True)
if __name__=='__main__':main()

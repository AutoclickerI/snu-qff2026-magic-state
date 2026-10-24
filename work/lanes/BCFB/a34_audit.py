from a34_prep import *
from collections import Counter

def audit(stem):
 stem=stem.resolve()
 source=read(D/'inputs/v34m');target=read(stem)
 before=Counter((t,tuple(u.lines)) for u,t in zip(source[3],source[4]));after=Counter((t,tuple(u.lines)) for u,t in zip(target[3],target[4]));removed=list((before-after).elements());added=list((after-before).elements())
 def qs(row):return set(map(int,re.findall(r'q\[(\d+)\]',' '.join(row[1]))))
 external_removed=[r for r in removed if not qs(r)<=set(A)];external_added=[r for r in added if not qs(r)<=set(A)]
 # All retained instructions outside the preparation's actual ownership span
 # are compared, with detector bit re-expression listed separately.
 oldtail=set(source[5]);newtail=set(target[5]);text=stem.with_suffix('.qasm').read_text()
 out=dict(stem=str(stem.relative_to(H)),qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),CX=sum(u.name=='CX' for u in target[3]),native_depth=max(target[4])+1,nearest_neighbor=all(abs(q[0]//6-q[1]//6)+abs(q[0]%6-q[1]%6)==1 for u in target[3] if u.name=='CX' for q in [list(map(int,re.findall(r'q\[(\d+)\]',u.lines[0]))) ]),native_schedule_matches=S.source_times(text,target[3])==target[4],layer_disjoint=S.feasible(target[4],target[3],*S.build_dag(target[3])),outside_A_native_operations_identical=not external_removed and not external_added,removed=removed,added=added,external_removed=external_removed,external_added=external_added,detectors_removed=sorted(oldtail-newtail),detectors_added=sorted(newtail-oldtail))
 Path(str(stem)+'.audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if not isinstance(v,list)}));return out
if __name__=='__main__':
 for s in sys.argv[1:]:audit(Path(s))

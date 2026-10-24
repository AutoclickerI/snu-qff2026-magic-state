from a35_prep import *
from collections import Counter

def audit(stem):
 stem=stem.resolve();s=read(stem);base=read(D/'inputs/v35b');old=Counter((t,tuple(u.lines)) for u,t in zip(base[3],base[4]));new=Counter((t,tuple(u.lines)) for u,t in zip(s[3],s[4]));text=s[0]
 nearest=all(abs(q[0]//6-q[1]//6)+abs(q[0]%6-q[1]%6)==1 for u in s[3] if u.name=='CX' for q in [list(map(int,re.findall(r'q\[(\d+)\]',u.lines[0])))])
 output=dict(stem=str(stem.relative_to(H)),qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),CX=sum(u.name=='CX' for u in s[3]),native_depth=max(s[4])+1,nearest_neighbor=nearest,native_schedule_matches=S.source_times(text,s[3])==s[4],layer_disjoint=S.feasible(s[4],s[3],*S.build_dag(s[3])),removed=list((old-new).elements()),added=list((new-old).elements()),detectors_removed=sorted(set(base[5])-set(s[5])),detectors_added=sorted(set(s[5])-set(base[5])))
 assert nearest and output['native_schedule_matches'] and output['layer_disjoint'];Path(str(stem)+'.audit.json').write_text(json.dumps(output,indent=2));print(stem.name,output['CX'],output['native_depth'],output['qasm_sha256'])
if __name__=='__main__':
 for s in sys.argv[1:]:audit(Path(s))

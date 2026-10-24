from a35_prep import *
from collections import Counter

def counters(source):
 s=read(source);return Counter((t,tuple(u.lines)) for u,t in zip(s[3],s[4])),Counter(s[5])
def patch(source,target,outside=False):
 a,ad=counters(source);b,bd=counters(target);rem=a-b;add=b-a;rd=ad-bd;nd=bd-ad
 if outside:
  protected_bits=set()
  def owned(k):
   t,lines=k;qs=set(map(int,re.findall(r'q\[(\d+)\]',' '.join(lines))))
   inside=qs<=set(A) and all(t>RELEASE[q] for q in qs)
   if inside:
    protected_bits.update(map(int,re.findall(r'c\[(\d+)\]',' '.join(lines))))
   return inside
  rem=Counter({k:n for k,n in rem.items() if not owned(k)});add=Counter({k:n for k,n in add.items() if not owned(k)})
  rd=Counter({l:n for l,n in rd.items() if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&protected_bits});nd=Counter({l:n for l,n in nd.items() if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&protected_bits})
 return dict(source=str(source),target=str(target),outside_A_only=outside,remove=[[t,list(ls)] for t,ls in rem.elements()],add=[[t,list(ls)] for t,ls in add.elements()],remove_detectors=list(rd.elements()),add_detectors=list(nd.elements()))
def apply(stem,p):
 s=read(stem);cc,dd=counters(stem)
 for t,ls in p['remove']:
  k=(t,tuple(ls))
  if not cc[k]:raise ValueError('native patch conflict '+str(k))
  cc[k]-=1
 for t,ls in p['add']:cc[t,tuple(ls)]+=1
 for d in p['remove_detectors']:
  if dd[d]:dd[d]-=1
 for d in p['add_detectors']:dd[d]+=1
 uu=[];tt=[]
 for (t,ls),n in cc.items():
  for _ in range(n):uu.append(U(list(ls)));tt.append(t)
 body,md=finish(uu,tt,list(dd.elements()),dict(kind='A_plus_guard_patch',A_source=str(stem.relative_to(H)),delay=s[1].get('R',44)-44,parent_options=s[1].get('options'),patch=p))
 # Every detector must reference a retained measurement record.
 bits={int(x) for u in uu for l in u.lines for x in re.findall(r'c\[(\d+)\]',l)}
 assert all(set(map(int,re.findall(r'c\[(\d+)\]',l)))<=bits for l in dd.elements()),'dangling detector record'
 return body,md
if __name__=='__main__':
 patches={}
 patches['drop_x20_guard']=patch(D/'inputs/v35a',ROOT/'work/lanes/ST2/v35/fasttrack/guard_274_off')
 for tag,path in [('guard_gain','focused/q7x_q10z_q7Z_mx1'),('headroom','zebra/g00_ecc15c15da6170'),('balanced','zebra/g03_b21170e18b01f2')]:
  patches[tag]=patch(D/'inputs/v35b',ROOT/'work/lanes/ST2/pop35b'/path,True)
 (D/'guard_patches.json').write_text(json.dumps(patches,indent=2));stems=[]
 for tag,p in patches.items():
  s,m=apply(D/'inputs/v35b',p);stem=D/'candidates'/('control_'+tag);stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));stems.append(str(stem.relative_to(H)))
 (D/'guard_controls.json').write_text(json.dumps(stems,indent=2));print([(k,len(v['remove']),len(v['add'])) for k,v in patches.items()],flush=True)

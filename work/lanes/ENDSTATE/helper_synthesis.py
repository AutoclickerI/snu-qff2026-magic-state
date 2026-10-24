from native import *
from library import rowkey
import subprocess,itertools
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def key8(rr):
 rr=list(rr)
 for i in range(3):
  j=min(range(i,3),key=lambda j:(rr[j]&-rr[j]).bit_length());rr[i],rr[j]=rr[j],rr[i];bit=rr[i]&-rr[i]
  for j in range(3):
   if j!=i and rr[j]&bit:rr[j]^=rr[i]
 return rr[0]|rr[1]<<8|rr[2]<<16

def run(source,name):
 d=json.loads(Path(source).read_text());seen=set();perms=[]
 for p in itertools.permutations(range(7)):
  key=rowkey([sum(1<<p[i]for i in g)for g in GENS])
  if key not in seen:seen.add(key);perms.append(p)
 candidates=[dict(permutation=list(p),blocks={})for p in perms]
 for k in'abc':
  cells=d['final'][k]+([d['helpers'][k]]if k in'bc'else[]);n=len(cells);edges=[(i,j)for i in range(n)for j in range(n)if abs(cells[i]//6-cells[j]//6)+abs(cells[i]%6-cells[j]%6)==1];targets=[];variants=[]
  for pi,p in enumerate(perms):
   for hcol in(range(8)if k in'bc'else[0]):
    rr=[sum(1<<p[i]for i in g)|(((hcol>>j)&1)<<7)for j,g in enumerate(GENS)];targets.append(key8(rr));variants.append((pi,hcol))
  request=f'{n} {len(edges)} {len(targets)}\n'+' '.join(str(i)for e in edges for i in e)+'\n'+' '.join(map(str,targets))+'\n';res=subprocess.run([str(H/'synth_one')],input=request,text=True,capture_output=True,check=True);enc=json.loads(res.stdout)
  for (pi,hcol),e in zip(variants,enc):
   if e is None:continue
   piv=[cells[i]for i in e['pivots']];ops=[[cells[u],cells[v]]for u,v in e['ops']]
   if k=='a':piv=[q for q in cells if q not in piv];ops=[[v,u]for u,v in ops]
   p=perms[pi];lab=[d['final'][k][i]for i in p];helper=None
   if k in'bc':helper=dict(cell=cells[7],measure='MX',frame_label=hcol-1 if hcol else None)
   z=dict(cx=e['cx'],ops=ops,pivots=piv,helpers=[]if helper is None else[helper],cells=cells)
   old=candidates[pi]['blocks'].get(k)
   if old is None or (z['cx'],hcol!=0)<(old['cx'],old['helpers'][0]['frame_label'] is not None if old['helpers']else False):candidates[pi]['blocks'][k]=z
 for x in candidates:x.update(max_cx=max(z['cx']for z in x['blocks'].values()),cx=sum(z['cx']for z in x['blocks'].values()))
 candidates.sort(key=lambda x:(x['max_cx'],x['cx']));best=candidates[0];p=best['permutation'];out=dict(d,final={k:[qs[i]for i in p]for k,qs in d['final'].items()},blocks=best['blocks'],label_permutation=list(p),prep_cx=best['cx'],max_prep_cx=best['max_cx'],all_label_candidates=candidates)
 out['initial']={k:out['final'][k]for k in'abc'};(H/(name+'.json')).write_text(json.dumps(out,indent=2));print({k:out[k]for k in('final','helpers','prep_cx','max_prep_cx')})
if __name__=='__main__':run(*sys.argv[1:])

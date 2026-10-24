from core import *
from collections import Counter,defaultdict

def regions(c):
 # HOPS provides trustworthy prefix identities. Match repeated operations by
 # occurrence number, independent of global schedule order.
 ref=read(ROOT/'work/lanes/HOPS/hop_early');pre=set(ref['meta']['prefix_unit_indices']);count=Counter();keys=set()
 for i,u in enumerate(ref['u']):
  key=tuple(u.lines);count[key]+=1
  if i in pre:keys.add((key,count[key]))
 count=Counter();pu=[]
 for i,u in enumerate(c['u']):
  key=tuple(u.lines);count[key]+=1
  if (key,count[key])in keys or u.name in ('T','TDG'):pu.append(i)
 c['meta']['prefix_unit_indices']=pu;c['meta']['pre_data']=[0,20,7,4,3,15,8]
 # regions.unit_regions reads original metadata for pre_data; carry a stem.
 sys.path.insert(0,str(OUT/'inputs'));import regions as R
 md=dict(c['meta'],_stem=c['source']);return R,R.unit_regions(c['u'],c['t'],md)

def main(stem):
 c=read(stem);text=textof(c);R,reg=regions(c);ev=exact2.Eval(text,D);sy=setup_syndromes(ev);pairs=[(a,b)for a in range(len(sy))for b in range(a,len(sy))if sy[a]==sy[b]]
 exact2.G.update(ev=ev,third=True,SA=float(ev.fp@ev.a_single),Pch=np.bincount(ev.fch,weights=ev.fp),pairs=pairs)
 p2,aa,sens,big,bc=exact2._pair_chunk((0,len(pairs),1e-15));tri,big3=fast_third.third_order(ev,1)
 qmap=S.native_qasm_index(text);rawmap={j:i for i,u in enumerate(c['u'])for j in u.raw_indices}
 def region(fi):
  ch=ev.m.chans[ev.fch[fi]];lab=ev.m.labels[ev.m.prog[ch['ins']].line_no-1];m=re.match(r'instruction (\d+)',lab)
  return reg[rawmap[qmap[int(m[1])]]]if m else 'other'
 sums=defaultdict(float);sums3=defaultdict(float)
 for val,i,j,_,_ in big:sums[' x '.join(sorted([region(i),region(j)]))]+=val
 for val,i,j,k in big3:sums3[' x '.join(sorted([region(i),region(j),region(k)]))]+=val
 row=dict(source=stem,second=p2,third=tri+bc,total=p2+tri+bc,weight3=tri,pair_times_others=bc,pair_regions=dict(sums),thresholded_triple_regions=dict(sums3),pair_threshold=1e-15,triple_threshold=3e-13,prefix_units=c['meta']['prefix_unit_indices'])
 row['pairs']=[dict(value=x[0],faults=[ev.fault_label(j)for j in x[1:3]],regions=[region(j)for j in x[1:3]])for x in sorted(big,reverse=True)[:100]]
 row['triples']=[dict(value=x[0],faults=[ev.fault_label(j)for j in x[1:]],regions=[region(j)for j in x[1:]])for x in sorted(big3,reverse=True)[:100]]
 (OUT/(Path(stem).name+'.attribution.json')).write_text(json.dumps(row,indent=2));print(json.dumps({k:v for k,v in row.items()if k not in ('pairs','triples','prefix_units')}),flush=True)
if __name__=='__main__':main(sys.argv[1])

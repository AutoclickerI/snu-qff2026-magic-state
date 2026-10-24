"""Complete unordered pair/triple region sums, without top-fault truncation."""
from core import *
import inspect,multiprocessing as mp,collections
import model

LABELS=['injection','stabilizer','T_layers','check1','check2','internal_idle','A','BC','hop','round','other']
def label_channels(ev,c):
 raw_to_unit={j:i for i,u in enumerate(c['u'])for j in u.raw_indices}
 qmap=S.native_qasm_index(ev.qasm);reg=[];tokens=set(PD);seen={}
 for i,(u,t,tag) in enumerate(zip(c['u'],c['t'],c['tags'])):
  if tag!='suffix':g=tag
  elif t>=c['meta']['R']:g='round'
  elif u.name=='CX' and len(set(u.qs)&tokens)==1:
   g='hop';pair=frozenset(u.qs);seen[pair]=seen.get(pair,0)+1
   if seen[pair]==2:tokens^=set(u.qs)
  elif set(u.qs)<=set(A):g='A'
  elif set(u.qs)<=set(B+C):g='BC'
  else:g='other'
  reg.append(g)
 out=[];detail=[]
 for i,ch in enumerate(ev.m.chans):
  lab=ev.m.labels[ev.m.prog[ch['ins']].line_no-1];mt=re.match(r'instruction (\d+)',lab)
  ui=raw_to_unit[qmap[int(mt.group(1))]] if mt and int(mt.group(1))in qmap else None
  g=reg[ui] if ui is not None else 'other'
  if ch['gap'] is not None and g in LABELS[:5]:g='internal_idle'
  out.append(LABELS.index(g));detail.append(dict(channel=i,component=g,unit=ui,**ev.chan_label(i)))
 return np.array(out),detail

def grouped(ev,labels,procs):
 K=len(LABELS);fl=labels[ev.fch];ng=len(ev.gkeys)
 exact2.G.update(ev=ev,third=True,SA=float(ev.fp@ev.a_single),Pch=np.bincount(ev.fch,weights=ev.fp),presyn_fl=fl,presyn_K=K)
 pairs=[(a,b)for a in range(ng)for b in range(a,ng)];exact2.G['pairs']=pairs
 src=inspect.getsource(exact2._pair_chunk)
 src=src.replace('t3bc = 0.0','t3bc = 0.0\n    bins = np.zeros(G["presyn_K"]**2)\n    bc_bins = bins.copy()')
 src=src.replace('if G.get("third"):', 'codes = G["presyn_fl"][ia][:,None]*G["presyn_K"]+G["presyn_fl"][ib][None,:]\n        bins += np.bincount(codes.ravel(),weights=c.ravel(),minlength=len(bins))\n        if G.get("third"):')
 src=src.replace('t3bc += float((pp * nij * cross * coefm).sum())','weighted=pp*nij*cross*coefm\n            t3bc += float(weighted.sum())\n            bc_bins += np.bincount(codes.ravel(),weights=weighted.ravel(),minlength=len(bins))')
 src=src.replace('return pair_sum, Asum, sens, big, t3bc','return pair_sum, Asum, sens, big, t3bc, bins, bc_bins')
 exec(compile(src,__file__+':pairs','exec'),exact2.__dict__)
 chunk=max(1,len(pairs)//(procs*8));jobs=[(i,min(i+chunk,len(pairs)),1e-12)for i in range(0,len(pairs),chunk)]
 with mp.get_context('fork').Pool(procs)as pool:parts=pool.map(exact2._pair_chunk,jobs)
 pair=sum(x[0]for x in parts);bc=sum(x[4]for x in parts);pbin=sum(x[5]for x in parts);bcbin=sum(x[6]for x in parts);big2=sorted([v for x in parts for v in x[3]],reverse=True)[:100]
 src=inspect.getsource(fast_third.SLOW_CHUNK)
 src=src.replace('big = []','big = []\n    bins = np.zeros(G["presyn_K"]**3)')
 src=src.replace('cs = np.arange(gb, len(ev.gkeys))','cs = _presyn_live_cs(ga,gb)\n        if len(cs)==0:continue')
 src=src.replace('tot += t','tot += t\n                if t>1e-20:\n                    fl=G["presyn_fl"];K=G["presyn_K"]\n                    codes=fl[ia[sl]][:,None,None]*K*K+fl[ib][None,:,None]*K+fl[ic][None,None,:]\n                    bins += np.bincount(codes.ravel(),weights=val.ravel(),minlength=len(bins))')
 src=src.replace('return tot, big','return tot, big, bins')
 exact2.__dict__['_presyn_live_cs']=fast_third.live_cs
 exec(compile(src,__file__+':triples','exec'),exact2.__dict__)
 fast_third.FAST_CHUNK=exact2._triple_chunk
 def collect(ev,procs):
  jobs=[(a,b)for a in range(ng)for b in range(a,ng)];chunk=max(1,len(jobs)//(procs*16));chunks=[jobs[i:i+chunk]for i in range(0,len(jobs),chunk)]
  with mp.get_context('fork').Pool(procs)as pool:parts=pool.map(exact2._triple_chunk,chunks,chunksize=1)
  return sum(x[0]for x in parts),sorted([v for x in parts for v in x[1]],reverse=True)[:100],sum(x[2]for x in parts)
 fast_third.SLOW_THIRD=collect
 tri,big3,tbin=fast_third.third_order(ev,procs)
 def table(bins,n,region=False):
  d=collections.defaultdict(float)
  for idx,val in enumerate(bins):
   if abs(val)<1e-20:continue
   qs=[]
   for _ in range(n):
    q=LABELS[idx%K];idx//=K
    qs.append('pre' if region and q in LABELS[:6] else q)
   d[' x '.join(sorted(qs))]+=float(val)
  return dict(sorted(d.items(),key=lambda x:-abs(x[1])))
 assert abs(sum(pbin)-pair)<1e-14
 assert abs(sum(tbin)-tri)<1e-14
 return dict(second=pair,weight3=tri,pair_times_others=bc,third=tri+bc,total=pair+tri+bc,
  pairs_component=table(pbin,2),triples_component=table(tbin,3),normalization_component=table(bcbin,2),pairs_region=table(pbin,2,True),triples_region=table(tbin,3,True),normalization_region=table(bcbin,2,True),
  top_pairs=[dict(value=x[0],faults=[ev.fault_label(j)for j in x[1:3]])for x in big2],top_triples=[dict(value=x[0],faults=[ev.fault_label(j)for j in x[1:]])for x in big3])

if __name__=='__main__':
 c=provenance(read(BASE));stem=save(c,'base','v22h_c2c9 control with reconstructed provenance')
 c=read(stem);c['tags']=c['meta']['component_tags'];ev=exact2.Eval(textof(c),D)
 labels,detail=label_channels(ev,c);row=grouped(ev,labels,int(sys.argv[1])if len(sys.argv)>1 else 8)
 row.update(channels=detail,c1=float(ev.fp@ev.n_single),exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))),unit_provenance=[dict(i=i,time=t,component=tag,lines=u.lines)for i,(u,t,tag)in enumerate(zip(c['u'],c['t'],c['tags']))])
 (OUT/'decomposition.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k not in ('channels','unit_provenance','top_pairs','top_triples')}),flush=True)

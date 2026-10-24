"""Exact fixed-order cubic objective compiled once, including zero-length gaps."""
from core import *
from quadratic_search import Quadratic
import collections,random,argparse

class Cubic:
 def __init__(self,base):
  self.base=base;self.q=Quadratic(textof(base),D,base['u'],base['h'],base['tail']);ev=self.q.ev;self.ev=ev
  ng=len(ev.gkeys);nc=len(ev.m.chans);masks=[0];coefs=[1.]
  for (T,a,b),coef in zip(ev.e.keys,ev.e.W*ev.e.beta):
   masks.append(a|(b<<3)|(1<<6)|((1<<8)if T=='X'else((1<<7)|(1<<9))));coefs.append(-coef)
  self.K=len(masks);self.MC=np.zeros((ng,nc,self.K));frac=ev.fp/self.q.p0[ev.fch]
  chars=1-2*(np.bitwise_count(ev.fe[:,None]&np.array(masks)[None,:])%2).astype(float)
  cs=[]
  for g,ix in enumerate(ev.gmem):np.add.at(self.MC[g],ev.fch[ix],frac[ix,None]*chars[ix]);cs.append(set(ev.fch[ix]))
  cgroups=collections.defaultdict(set)
  for g,chans in enumerate(cs):
   for c in chans:cgroups[c].add(g)
  opairs=sorted({tuple(sorted((a,b)))for gs in cgroups.values()for a in gs for b in gs});oi={p:i+1 for i,p in enumerate(opairs)}
  self.nop=len(opairs)+1;self.oc=[];self.oi=[];self.ov=[]
  for (a,b),i in oi.items():
   for c in cs[a]&cs[b]:self.oc.append(c);self.oi.append(i);self.ov.append(self.MC[a,c]*self.MC[b,c])
  self.oc=np.array(self.oc,dtype=int);self.oi=np.array(self.oi,dtype=int);self.ov=np.array(self.ov)
  sy=setup_syndromes(ev);groups=collections.defaultdict(list)
  for g,s in enumerate(sy):groups[s].append(g)
  cache={};coefs=np.array(coefs)
  def coeff(s,d):
   if (s,d)not in cache:
    v=ev.e.table(s,d);cache[s,d]=None if v is None else .5*np.array([v[0],*v[1]])*coefs
   return cache[s,d]
  pa=[];pb=[];po=[];pc=[];ta=[];tb=[];tc=[];tab=[];tac=[];tbc=[];tcoef=[];same3=np.zeros(nc)
  for a in range(ng):
   sa,da=ev.gkeys[a]
   for b in groups[sy[a]]:
    if b<a:continue
    sb,db=ev.gkeys[b];v=coeff(sa^sb,da^db)
    if v is None:continue
    pa.append(a);pb.append(b);po.append(oi.get((a,b),0));pc.append(v/(2 if a==b else 1))
   for b in range(a,ng):
    sb,db=ev.gkeys[b]
    for c in groups.get(sy[a]^sy[b],()):
     if c<b:continue
     sc,dc=ev.gkeys[c];v=coeff(sa^sb^sc,da^db^dc)
     if v is None:continue
     v=v/(6 if a==c else (2 if a==b or b==c else 1))
     ta.append(a);tb.append(b);tc.append(c);tab.append(oi.get((a,b),0));tac.append(oi.get((a,c),0));tbc.append(oi.get((b,c),0));tcoef.append(v)
     for ch in cs[a]&cs[b]&cs[c]:same3[ch]+=2*float(v@(self.MC[a,ch]*self.MC[b,ch]*self.MC[c,ch]))
  self.pa=np.array(pa);self.pb=np.array(pb);self.po=np.array(po);self.pc=np.array(pc)
  self.ta=np.array(ta);self.tb=np.array(tb);self.tc=np.array(tc);self.tab=np.array(tab);self.tac=np.array(tac);self.tbc=np.array(tbc);self.tcoef=np.array(tcoef);self.same3=same3
  # Flatten channels last for BLAS GEMV; no repeated group-table work.
  self.Mflat=np.ascontiguousarray(self.MC.transpose(0,2,1).reshape(ng*self.K,nc));self.ng=ng
 def score(self,times):
  p=self.q.probabilities(times);p2=p*p;p3=p2*p
  M=(self.Mflat@p).reshape(self.ng,self.K);MW=(self.Mflat@p2).reshape(self.ng,self.K)
  cross=np.zeros((self.nop,self.K));cw=np.zeros_like(cross)
  np.add.at(cross,self.oi,self.ov*p2[self.oc,None]);np.add.at(cw,self.oi,self.ov*p3[self.oc,None])
  W=M[self.pa]*M[self.pb]-cross[self.po];second=float(np.sum(self.pc*W))
  a1=float(p@self.q.alin);sa=float(p.sum()-a1)
  bc=float(np.sum(self.pc*(-sa*W+MW[self.pa]*M[self.pb]+M[self.pa]*MW[self.pb]-2*cw[self.po])))
  V=M[self.ta]*M[self.tb]*M[self.tc]-cross[self.tab]*M[self.tc]-cross[self.tac]*M[self.tb]-cross[self.tbc]*M[self.ta]
  t3a=float(np.sum(self.tcoef*V)+p3@self.same3)
  return dict(c1=float(p@self.q.nlin),second=second,third=t3a+bc,total=second+t3a+bc,exp_minus_A1=math.exp(-a1),A1=a1)

def shift(ts,i,delta,pred,succ,horizon):
 nt=ts[:];nt[i]+=delta;todo=[i]
 while todo:
  k=todo.pop()
  if nt[k]<0 or nt[k]>horizon:return None
  for j in(succ[k]if delta>0 else pred[k]):
   lim=nt[k]+(1 if delta>0 else -1)
   if (delta>0 and nt[j]<lim)or(delta<0 and nt[j]>lim):nt[j]=lim;todo.append(j)
 return S.compress(nt)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--steps',type=int,default=6000);ap.add_argument('--label',default='temporal');a=ap.parse_args();base=read(a.stem);start=time.monotonic();q=Cubic(base);print('compiled',time.monotonic()-start,len(q.ta),flush=True)
 pred,succ=S.build_dag(base['u']);rng=random.Random(10404);ts=base['t'];checks=[]
 trials=[ts]
 for i,d in [(53,1),(24,-1),(150,-1),(220,-1)]:
  t=shift(ts,i,d,pred,succ,max(ts)+2)
  if t is not None:trials.append(t)
 for t in trials:
  c=clone(base);c['t']=t;c=normalize(c);v=q.score(t);ref=score(textof(c));err=max(abs(v[k]-ref[k])for k in ['second','third','total']);assert err<1e-14,(v,ref,err);checks.append(dict(predicted=v,reference=ref,error=err))
 (OUT/(a.label+'.validation.json')).write_text(json.dumps(checks,indent=2));print('validated',flush=True)
 cur=q.score(ts);best=cur;bestts=ts[:];seen=set();accepted=0;trace=[];tick=time.monotonic()
 for step in range(a.steps):
  i=rng.randrange(len(ts));delta=rng.choice([-3,-2,-1,1,2,3]);nt=shift(ts,i,delta,pred,succ,max(base['t'])+2)
  if nt is None or tuple(nt)in seen:continue
  seen.add(tuple(nt));v=q.score(nt)
  if v['exp_minus_A1']<.505:continue
  temperature=2e-8*(1-step/a.steps)**2;diff=v['total']-cur['total']
  if diff<=0 or rng.random()<math.exp(-diff/max(temperature,1e-16)):ts,cur=nt,v;accepted+=1
  if v['total']<best['total']-1e-12:
   best=v;bestts=nt[:];trace.append(dict(step=step,**v));print('best',step,v,flush=True)
 c=clone(base);c['t']=bestts;c=normalize(c);ref=score(textof(c));assert max(abs(best[k]-ref[k])for k in ['second','third','total'])<1e-14
 desc=dict(family='timing',move='exact_cubic_lns',steps=a.steps,accepted=accepted,unique=len(seen),source=a.stem,parent_total=base['meta']['lns_result']['total']);row=dict(desc=desc,**ref,stem=a.label+'_best');save(row['stem'],textof(c),c['meta'],row)
 (OUT/(a.label+'.jsonl')).write_text(json.dumps(row)+'\n');(OUT/(a.label+'.trace.json')).write_text(json.dumps(trace,indent=2));report();print('DONE',time.monotonic()-tick,row,flush=True)
if __name__=='__main__':main()

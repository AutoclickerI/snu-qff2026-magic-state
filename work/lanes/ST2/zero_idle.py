"""Analysis-only zero-probability channels at currently zero-width waits.
The judge and on-disk exact2 model are untouched. Nonzero channels stay identical.
"""
import directed as d
exact2=d.C.exact2
import model as em,collections

def evaluate(text,data):
 original_schedule=em.schedule;original_blocks=em.noise_blocks
 def schedule(txt):
  prog,steps,gaps=original_schedule(txt);per=collections.defaultdict(list)
  for i,ss in enumerate(steps):
   for qs,t in ss:
    for q in qs:per[q].append((i,t))
  for q,seq in per.items():
   for (i,t),(j,u)in zip(seq,seq[1:]):
    if u==t+1 and prog[j].name not in('R','RZ','RX'):gaps.append((i,q,t+1,0))
  return prog,steps,sorted(gaps)
 def blocks(txt,p,noise):
  prog,out=original_blocks(txt,p,noise);_,_,old=original_schedule(txt);_,_,new=schedule(txt);oldcounts=collections.Counter(i for i,q,t,n in old);group=collections.defaultdict(list)
  for i,q,t,n in new:group[i].append((q,n))
  for i,rows in group.items():
   if oldcounts[i]:out[i]=out[i][:-oldcounts[i]]
   out[i]+=[f'DEPOLARIZE1({.75*(1-(1-4*p*noise.idle/3)**n)}) {q}'for q,n in rows]
  return prog,out
 em.schedule=schedule;em.noise_blocks=blocks
 try:ev=exact2.Eval(text,data)
 finally:em.schedule=original_schedule;em.noise_blocks=original_blocks
 assert max(abs(ev.n_single[ev.fp==0]),default=0)<1e-12,'A new idle interval would allow first-order loss'
 return ev

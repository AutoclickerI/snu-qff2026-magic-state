"""Known-state readouts and measured-Z initialization, full-circuit priced."""
from common import *
import echo_search as es

def candidates(c):
 ops=c['ops'];R=c['meta']['R'];bit=1+max([int(b)for o in ops for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))]+[-1]);per={q:[i for i,o in enumerate(ops)if q in unit(o).qs]for q in range(36)}
 def emitted(d,lines,t,desc,parity):
  d['h']=[re.sub(r'creg c\[\d+\];',f'creg c[{bit+1}];',l)for l in d['h']];d['tail'].append('// DETECTOR '+' '.join(f'c[{b}]'for b in parity));d['meta']['watches']=d['meta'].get('watches',[])+[desc];return d,desc
 for q,seq in per.items():
  for j,i in enumerate(seq):
   o=ops[i];u=unit(o)
   if o['t']>R:continue
   if u.name=='RESET'and(j==0 or unit(ops[seq[j-1]]).name=='MEASURE'):
    d=copy.deepcopy(c);d['ops'][i]['lines']=[f'measure q[{q}] -> c[{bit}];'];d['ops'][i]['tag']='measured_Z_init';desc=dict(family='measured_Z_init',q=q,time=o['t'],bit=bit)
    # Ideal acceptance is separately checked; the new outcome must be zero.
    yield emitted(d,d['ops'][i]['lines'],o['t'],desc,[bit])
   if j+1==len(seq)or u.name not in('RESET','RX','MEASURE','MX'):continue
   nxt=ops[seq[j+1]]
   if unit(nxt).name in('RESET','RX'):continue
   end=min(nxt['t']-1,R-1)
   if end<=o['t']:continue
   axis='X'if u.name in('RX','MX')else'Z';prevbits=list(map(int,re.findall(r'c\[(\d+)\]',' '.join(o['lines']))))
   for t in sorted({o['t']+1,end}):
    lines=([f'h q[{q}];']if axis=='X'else[])+[f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];']if axis=='X'else[]);d=copy.deepcopy(c);d['ops'].append(dict(t=t,lines=lines,tag='known_state_watch'));desc=dict(family='known_state_watch',q=q,axis=axis,time=t,bit=bit,previous_bits=prevbits)
    yield emitted(d,lines,t,desc,[bit]+prevbits)
es.candidates=candidates
if __name__=='__main__':es.main()

"""Native terminal Z-readout instruments within the existing final layer."""
from common import *
import echo_search as es

def candidates(c):
 R=c['meta'].get('R_BC',c['meta']['R']);ops=c['ops'];reads={unit(o).qs[0]:i for i,o in enumerate(ops)if unit(o).name=='MEASURE'and o['t']==R+1};allterminal={unit(o).qs[0]for o in ops if unit(o).name in('MEASURE','MX')and o['t']>=R+1};bit=1+max(int(b)for o in ops for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])));bits={q:int(re.search(r'c\[(\d+)\]',ops[i]['lines'][0])[1])for q,i in reads.items()}
 for q,i in reads.items():
  for h in range(36):
   if abs(q//6-h//6)+abs(q%6-h%6)!=1:continue
   if h in reads:
    d=copy.deepcopy(c);j=reads[h];d['ops'][i]['t']=d['ops'][j]['t']=R+2;d['ops'].append(dict(t=R+1,lines=[f'cx q[{q}],q[{h}];'],tag='terminal_instrument'));tail=[]
    for line in d['tail']:
     if line.startswith('// DETECTOR'):
      row=set(map(int,re.findall(r'c\[(\d+)\]',line)))
      if bits[h]in row:row.symmetric_difference_update({bits[q]})
      line='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(row))
     tail.append(line)
    d['tail']=tail;desc=dict(family='terminal_CX',edge=[q,h],time=R+1);d['meta']['terminal_edits']=d['meta'].get('terminal_edits',[])+[desc];yield d,desc
   elif h not in allterminal and h not in c['meta']['data_qubits']:
    hs=[o for o in ops if h in unit(o).qs]
    if hs and max(o['t']for o in hs)>R:continue
    prev=max(hs,key=lambda o:o['t'])if hs else None
    variants=[]
    if prev is None or prev['t']<R:variants.append(('reset',[]))
    if prev is not None and unit(prev).name in('RESET','MEASURE'):variants.append(('reuse',list(map(int,re.findall(r'c\[(\d+)\]',' '.join(prev['lines']))))))
    for policy,past in variants:
     d=copy.deepcopy(c);d['ops'][i]['t']=R+2
     if policy=='reset':d['ops'].append(dict(t=R,lines=[f'reset q[{h}];'],tag='terminal_init'))
     d['ops'].extend([dict(t=R+1,lines=[f'cx q[{q}],q[{h}];'],tag='terminal_instrument'),dict(t=R+2,lines=[f'measure q[{h}] -> c[{bit}];'],tag='terminal_read')]);d['tail'].append('// DETECTOR '+' '.join(f'c[{b}]'for b in[bit,bits[q]]+past));d['h']=[re.sub(r'creg c\[\d+\];',f'creg c[{bit+1}];',l)for l in d['h']];desc=dict(family='terminal_copy',edge=[q,h],policy=policy,previous_bits=past,bit=bit,time=R+1);d['meta']['terminal_edits']=d['meta'].get('terminal_edits',[])+[desc];yield d,desc
es.candidates=candidates
if __name__=='__main__':es.main()

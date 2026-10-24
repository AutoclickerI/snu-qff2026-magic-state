"""Known X/Z states of independent CSS preparations, including record frames."""
from common import *
import collections
def in_span(v,rows):
 bs={}
 for r in rows:
  while r:
   p=r.bit_length()-1
   if p not in bs:bs[p]=r;break
   r^=bs[p]
 while v:
  p=v.bit_length()-1
  if p not in bs:return False
  v^=bs[p]
 return True
def opportunities(c):
 ops=c['ops'];R=c['meta']['R'];out=[]
 for block,qs in [('a',A),('bc',B+C)]:
  init={q:max(i for i,o in enumerate(ops)if o['t']<R and unit(o).qs==(q,)and unit(o).name in('RX','RESET','MX','MEASURE'))for q in qs}
  vals={};frames={};n=0
  for t in range(R):
   busy=set()
   for i,o in enumerate(ops):
    if o['t']!=t:continue
    u=unit(o);busy|=set(u.qs)
    for q in u.qs:
     if init.get(q)==i:
      plus=u.name in('RX','MX');vals[q]=(1<<n)if plus else 0;n+=int(plus);frames[q]=[set(),set()]
      if u.name in('MX','MEASURE'):frames[q][1 if plus else 0]={int(re.findall(r'c\[(\d+)\]',' '.join(u.lines))[0])}
    if u.name=='CX'and set(u.qs)<=vals.keys():
     a,b=map(int,S.QRE.findall(u.lines[0]));vals[b]^=vals[a];frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
   for q in vals.keys()-busy:
    if t<=ops[init[q]]['t']or not any(o['t']>t and q in unit(o).qs for o in ops):continue
    if vals[q]==0:out.append(dict(q=q,t=t,axis='Z',correction=sorted(frames[q][0]),block=block))
    if vals[q]and not in_span(vals[q],[v for k,v in vals.items()if k!=q]):out.append(dict(q=q,t=t,axis='X',correction=sorted(frames[q][1]),block=block))
 return out
def insert(c,check):
 c=copy.deepcopy(c);b=max(int(x)for o in c['ops']for x in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])))+1;q=check['q'];x=check['axis']=='X'
 c['ops'].append(dict(lines=([f'h q[{q}];']if x else[])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];']if x else[]),t=check['t'],id=10000+b,tag='known_state_check'))
 c['tail'].append('// DETECTOR '+' '.join(f'c[{v}]'for v in sorted({b}^set(check['correction']))));c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{b+1}]',line)for line in c['h']];c['meta']['known_state_checks']=c['meta'].get('known_state_checks',[])+[check]
 return c
if __name__=='__main__':
 c=read(H/'inputs/v29c');op=opportunities(c);(H/'sepbc_v29c_opportunities.json').write_text(json.dumps(op,indent=2));print('opportunities',op,flush=True)
 rows=[]
 for ch in op:
  name=f"sepbc_v29c_{ch['axis'].lower()}{ch['q']}_t{ch['t']}"
  try:
   stem=save(insert(c,ch),name);r=score(stem);append_result(name,r,'Exact known-state check with symbolic preparation record frame.');rows.append(dict(name=name,check=ch,score=r));print(name,r,flush=True)
  except Exception as e:append_result(name,dict(error=repr(e)),'Known-state builder failure; no physical closure.');print(name,repr(e),flush=True)
 (H/'sepbc_v29c_known_results.json').write_text(json.dumps(rows,indent=2))

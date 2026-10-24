from core import *
import argparse

def build(name,pairs=((4,10),(8,9)),reuse15=False,reuse6=False):
 us,dets=parse_source();pre=[u for u in us if u['region']=='pre'];prep=[u for u in us if u['region']=='prep'];rnd=[u for u in us if u['region']=='round'];drop=set()
 for src,dst in pairs:
  inds=[i for i,u in enumerate(prep) if u['qs']==[src,dst]];i=inds[0];j=next(j for j in range(i+1,len(prep)) if prep[j]['qs']==[dst,src]);reset=next(k for k in reversed(range(i)) if prep[k]['qs']==[dst] and prep[k]['stmts'][0].startswith('reset'))
  drop.add(reset)
  for k,qq in [(i,[dst,src]),(j,[src,dst])]:prep[k]['qs']=qq;prep[k]['stmts']=[f'cx q[{qq[0]}],q[{qq[1]}];']
  u=next(u for u in reversed(pre) if dst in u['qs']);assert u['stmts'][0].startswith('h ') and u['stmts'][-1].startswith('measure');u['stmts'].append(f'h q[{dst}];')
 if reuse15:
  i=next(i for i,u in enumerate(prep) if u['qs']==[16,15]);k=next(k for k in range(i+1,len(prep)) if prep[k]['qs']==[15] and prep[k]['stmts'][0].startswith('reset'));drop.add(k)
 if reuse6:
  k=next(k for k,u in enumerate(prep) if u['qs']==[6] and u['stmts'][0].startswith('reset'));drop.add(k);u=next(u for u in reversed(pre) if 6 in u['qs']);u['stmts'].append('h q[6];')
 prep=[u for i,u in enumerate(prep) if i not in drop]
 release={}
 for u in pre:
  for q in u['qs']:release[q]=max(release.get(q,0),u['t']+1)
 end=release.copy()
 for u in prep:
  st=max(end.get(q,0) for q in u['qs'])
  for q in u['qs']:end[q]=st+1
 R=max(end.values());last={q:R for q in range(36)}
 for u in reversed(prep):
  u['t']=min(last[q] for q in u['qs'])-1
  for q in u['qs']:last[q]=u['t']
 for u in rnd:u['t']+=R-50
 emit(pre+prep+rnd,dets,D,HERE/name,dict(R=R,reuse_pairs=pairs,reuse15=reuse15,reuse6=reuse6))
 print(name,'R',R,flush=True)
if __name__=='__main__':
 build('reuse10',[(4,10)]);build('reuse9_10');build('reuse9_10_15',reuse15=True);build('reuse9_10_15_6',reuse15=True,reuse6=True)

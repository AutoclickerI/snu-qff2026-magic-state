from core import *
import argparse
EDGES=[(1,2),(14,15),(8,14),(8,9),(9,15),(2,8),(15,16),(28,29),(16,17),(19,25)]
def toggle(tail,subs):
 out=[]
 for line in tail:
  if line.startswith('// DETECTOR'):
   bs=set(map(int,re.findall(r'c\[(\d+)\]',line)));ex=set()
   for b in bs:
    if b in subs:ex^={subs[b]}
   line='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs^ex))
  out.append(line)
 return out

def matchings(i=0,used=frozenset(),pairs=()):
 if i==len(EDGES):yield pairs;return
 yield from matchings(i+1,used,pairs)
 a,b=EDGES[i]
 if a not in used and b not in used:
  for edge in [(a,b),(b,a)]:yield from matchings(i+1,used|{a,b},pairs+(edge,))

def moves(base):
 c=clone(base);R=c['meta']['R'];last={u.qs[0]:(i,int(re.findall(r'c\[(\d+)\]',u.lines[0])[0]))for i,u in enumerate(c['u'])if u.name=='MEASURE'and c['t'][i]>=R+1}
 removed=set();subs={}
 readout=[i for i,u in enumerate(c['u'])if u.name=='CX'and c['t'][i]>=R+1 and all(q in last for q in u.qs)]
 for i in sorted(readout,key=lambda i:c['t'][i],reverse=True):
  a,b=map(int,S.QRE.findall(c['u'][i].lines[0]));removed.add(i)
  ia,ba=last[a];ib,bb=last[b];c['tail']=toggle(c['tail'],{bb:ba});c['t'][ia]=c['t'][ib]=R+1
 c['u']=[u for i,u in enumerate(c['u'])if i not in removed];c['t']=[t for i,t in enumerate(c['t'])if i not in removed]
 last={u.qs[0]:(i,int(re.findall(r'c\[(\d+)\]',u.lines[0])[0]))for i,u in enumerate(c['u'])if u.name=='MEASURE'and c['t'][i]>=R+1}
 for pairs in matchings():
  d=clone(c);subs={}
  for a,b in pairs:
   ia,ba=last[a];ib,bb=last[b];d['t'][ia]=d['t'][ib]=R+2;subs[bb]=ba;d['u'].append(Unit([f'cx q[{a}],q[{b}];']));d['t'].append(R+1)
  d['tail']=toggle(d['tail'],subs)
  yield d,dict(family='readout',move='all_directed_matchings',pairs=pairs,parent_total=base['meta']['lns_result']['total'],local_track=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--label',default='matchings');a=ap.parse_args();batch(list(moves(read(a.stem))),a.label,a.workers)

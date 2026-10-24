"""Independent finite enumeration of stationary connected B/C star layouts.

Each B vertex needs distinct data and C neighbours, leaving degree <=2
within B. A connected seven-vertex B is therefore a path: the grid is
bipartite, so it cannot be a seven-cycle. Enumerate every such path, every
C matching, every D matching, then an A matching. No encoder assumptions.
"""
import os,sys,json,time,itertools
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
WIDTH=int(sys.argv[1])if len(sys.argv)>1 else 6
NB={q:[v for v in range(WIDTH*WIDTH)if abs(q//WIDTH-v//WIDTH)+abs(q%WIDTH-v%WIDTH)==1]for q in range(WIDTH*WIDTH)}
def connected(ss):
 seen={next(iter(ss))};todo=list(seen)
 while todo:
  q=todo.pop()
  for v in NB[q]:
   if v in ss and v not in seen:seen.add(v);todo.append(v)
 return len(seen)==len(ss)
def amatch(ds,blocked):
 dom={q:[v for v in NB[q]if v not in blocked]for q in ds}
 if any(not x for x in dom.values()):return None
 order=sorted(ds,key=lambda q:len(dom[q]))
 def rec(i,used,out):
  if i==7:return out.copy()
  for v in dom[order[i]]:
   if v not in used:
    ans=rec(i+1,used|{v},out+[v])
    if ans:return ans
  return None
 return rec(0,set(),[])
def main():
 st=time.monotonic();sets=set();counts=dict(paths=0,B_sets=0,C_assignments=0,C_connected=0,D_matchings=0,A_matchings=0);examples=[]
 def path(p):
  if examples:return
  if len(p)==7:
   if p[0]>p[-1]:return
   counts['paths']+=1;bb=frozenset(p)
   if bb in sets:return
   sets.add(bb)
   # Reject induced chords and vertices without two exterior neighbours.
   dom={q:[v for v in NB[q]if v not in bb]for q in bb}
   if any(len(vs)<2 for vs in dom.values()):return
   counts['B_sets']+=1;order=sorted(bb,key=lambda q:len(dom[q]))
   for cs in itertools.product(*(dom[q]for q in order)):
    cc=set(cs)
    if len(cc)!=7:continue
    counts['C_assignments']+=1
    if not connected(cc):continue
    counts['C_connected']+=1
    ddomain=[[v for v in dom[q]if v not in cc]for q in order]
    for ds in itertools.product(*ddomain):
     dd=set(ds)
     if len(dd)!=7:continue
     counts['D_matchings']+=1;aa=amatch(ds,set(bb)|cc|dd)
     if aa:
      counts['A_matchings']+=1;examples.append(dict(b=order,c=cs,d=ds,a=aa));return
   return
  for v in NB[p[-1]]:
   if v in p or len(NB[v])<3:continue
   # All nonterminal B vertices require two internal + two external neighbours.
   if len(p)>1 and len(NB[p[-1]])<4:continue
   path(p+[v])
 for q in range(WIDTH*WIDTH):
  if len(NB[q])>=3:path([q])
 r=dict(width=WIDTH,counts=counts,examples=examples[:4],seconds=time.monotonic()-st,scope=f'All {WIDTH}x{WIDTH} layouts with connected seven-cell B and C, seven distinct A/D/B/C roles, and NN A-D, D-B, B-C matchings; data/A need not connect. Time-dependent endpoint reuse and disconnected helper-assisted encoders excluded.')
 (H/('static_certificate.json'if WIDTH==6 else f'static_certificate_{WIDTH}.json')).write_text(json.dumps(r,indent=2))
 with(H/'REPORT.md').open('a')as f:f.write('\nIndependent stationary-layout enumeration: '+json.dumps(r)+'\n')
 print(json.dumps(r),flush=True)
if __name__=='__main__':main()

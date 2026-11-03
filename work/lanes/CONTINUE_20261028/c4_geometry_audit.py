"""Enumerate 7 disjoint 2x2 tiles and static cat-to-tile matchings."""
import itertools,json
from pathlib import Path
H=Path(__file__).resolve().parent
def neighbors(q):
 r,c=divmod(q,6);return {6*x+y for x,y in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=x<6 and 0<=y<6}
def connected(s):
 seen={next(iter(s))}
 while True:
  new=seen|{v for u in seen for v in neighbors(u)&s}
  if new==seen:return seen==s
  seen=new
def match(tiles,cats):
 options=[[(c,d) for c in sorted(cats) for d in sorted(tile) if c in neighbors(d)] for tile in tiles]
 order=sorted(range(7),key=lambda i:len(options[i]));out={}
 def go(k,used):
  if k==7:return True
  i=order[k]
  for c,d in options[i]:
   if c in used:continue
   out[i]=(c,d)
   if go(k+1,used|{c}):return True
  return False
 return dict(out) if go(0,set()) else None
tiles=[{6*r+c,6*r+c+1,6*(r+1)+c,6*(r+1)+c+1} for r in range(5) for c in range(5)]
count=perfect=connected_perfect=0;witness=connected_witness=None
for comb in itertools.combinations(range(25),7):
 selected=[tiles[i] for i in comb];used=set()
 for tile in selected:
  if used&tile:break
  used|=tile
 else:
  count+=1;free=set(range(36))-used;found=None;foundconn=None
  for cats in itertools.combinations(sorted(free),7):
   cats=set(cats);m=match(selected,cats)
   if m is not None:
    found=(cats,m)
    if connected(cats):foundconn=(cats,m);break
  if found:
   perfect+=1
   if witness is None:witness=dict(tiles=[sorted(t) for t in selected],cats=sorted(found[0]),assignment=found[1])
  if foundconn:
   connected_perfect+=1
   if connected_witness is None:connected_witness=dict(tiles=[sorted(t) for t in selected],cats=sorted(foundconn[0]),assignment=foundconn[1])
result=dict(packings=count,with_seven_distinct_adjacent_cats=perfect,
 with_connected_seven_cats_and_matching=connected_perfect,matching_witness=witness,
 connected_witness=connected_witness,
 scope='Static 2x2 tiles; each tile may choose any corner D and an adjacent internal K; no data/cat movement. Seven cat cells must be distinct. Connected-cat test assumes no extra bus.')
(H/'c4_geometry_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

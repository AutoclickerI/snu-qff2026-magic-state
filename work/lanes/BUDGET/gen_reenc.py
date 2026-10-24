import itertools,json,subprocess
from pathlib import Path
base='work/lanes/R1/v16_release_drop'
out=Path('work/lanes/BUDGET/reenc_scan');out.mkdir(exist_ok=True)
# all possible adjacent Z-readout edges in the final Z measurement block
edges=[(1,2),(14,15),(8,14),(8,9),(9,15),(2,8),(15,16),(28,29),(16,17),(19,25)]
# all matchings, with both directions per edge. Empty is included.
match=[]
def rec(i,used,chosen):
 if i==len(edges): match.append(list(chosen)); return
 rec(i+1,used,chosen)
 a,b=edges[i]
 if a not in used and b not in used:
  rec(i+1,used|{a,b},chosen+[(a,b)])
rec(0,set(),[])
sets=[]
for es in match:
 for bits in range(1<<len(es)):
  sets.append([(b,a) if bits>>j&1 else (a,b) for j,(a,b) in enumerate(es)])
# stable names and emit
for k,pairs in enumerate(sets):
 spec=','.join(f'{u}:{v}' for u,v in pairs)
 stem=out/f'r{k:04d}'
 if pairs: subprocess.run(['/home/jihoon/competitions/quantumn/.venv/bin/python','work/lanes/BUDGET/reenc_fixed.py',base,str(stem),spec],check=True,stdout=subprocess.DEVNULL)
 else:
  Path(str(stem)+'.qasm').write_text(Path(base+'.qasm').read_text());Path(str(stem)+'.json').write_text(Path(base+'.json').read_text())
json.dump({'edges':edges,'sets':[{"id":k,"pairs":p} for k,p in enumerate(sets)]},open(out/'manifest.json','w'),indent=2)
print('matchings',len(match),'sets',len(sets))

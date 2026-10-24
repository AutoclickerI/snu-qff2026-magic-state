"""Reuse ST1's measured local instrument; no duplicate instrument synthesis."""
from common import *
from instruments import build,EDGES
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args()
base=read(a.stem);ip=json.loads((ROOT/'work/lanes/ST1/instrument15_best.json').read_text())['st1_instrument'];gates=[EDGES.index(tuple(e)) for e in ip['gates']]
for mode in ['near','alap']:
 c,rec=build(base,gates,ip['contract'],mode)
 if c:
  # Instrument uses fresh classical bit91; extend the header explicitly.
  c['h']=[re.sub(r'creg c\[\d+\]', 'creg c[512]',s) for s in c['h']]
  stem=save(c,Path(a.stem).stem+'_i15_'+mode);r=score(stem)
  append_result(stem.name,r,'Rank-three BC plus imported ST1 q15 instrument; '+json.dumps(rec));print(stem,r,flush=True)

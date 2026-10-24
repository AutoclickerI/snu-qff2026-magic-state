from common import *
from instruments import build,EDGES
base=read(H/'boundary_endpoint_5_s712_00601_r0');p=json.loads((H/'instrument15_best.json').read_text())['st1_instrument'];gates=[EDGES.index(tuple(e))for e in p['gates']]
for mode in ['near','alap']:
 c,rec=build(base,gates,p['contract'],mode)
 if c:
  stem=save(c,'combined_endpoint_instrument15_'+mode);r=score(stem);append_result(stem.name,r,'q4 exchange + exact timing feedback + reduced-C endpoint5 + synthesized q15 boundary instrument');print(stem,r,flush=True)

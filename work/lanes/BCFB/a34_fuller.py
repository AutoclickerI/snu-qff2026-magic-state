from a34_search import *
from a34_dedup import physical_key
source=read(D/'candidates/encoders_00004');groups={};counts=collections.Counter()
for ops in algebra(5):
 zs=[zf(z,ops) for z in Z0];flags=[i for i in range(7) if not any(z>>i&1 for z in zs)]
 if len(flags)<2:continue
 counts['two_flags']+=1
 for end in range(47,53):
  try:text,md=decoder(ops,end=end,source=source)
  except (ValueError,AssertionError):continue
  o=md['options'];key=str(sorted(o['flag_X_supports']));v=(end,md['CX'],o['schedule'])
  if key not in groups or v<groups[key][0]:groups[key]=(v,text,md)
  break
ss=[]
for v,text,md in groups.values():
 md['base']='encoders_00004';stem=D/'candidates'/f'fuller_{len(ss):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));ss.append(str(stem.relative_to(H)))
(D/'fuller.json').write_text(json.dumps(dict(counts=counts,stems=ss),indent=2));print('fuller',counts,len(ss))

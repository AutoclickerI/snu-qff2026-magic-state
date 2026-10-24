from a35_guard_patches import *
from a35_funding import reset_checks
ss=[];src=D/'candidates/refine_002'
# Restore native resets for the two cheap internal checks, or trade the shortest
# guard for stronger A checks. Every composition is separately priced.
for bits in [[544],[540],[544,540]]:
 s,m=reset_checks(src,bits);name='swap_checks_'+'_'.join(map(str,bits));stem=D/'candidates'/name;stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));ss.append(str(stem.relative_to(H)))
for q,bit in [(16,542),(13,543)]:
 s=read(src);uu=[];tt=[];removed=[]
 # Remove exactly the added closed echo and its post-readout reset; retain a
 # same-basis initialization where its state is subsequently required.
 for u,t in zip(s[3],s[4]):
  drop=(q==16 and ((u.name=='CX' and u.qs==(10,16) and t in (20,21)) or (u.qs==(16,) and t in (19,22))))
  if drop:removed.append((t,u.lines));continue
  uu.append(u);tt.append(t)
 if not removed:continue
 ta=[l for l in s[5] if l!=f'// DETECTOR c[{bit}]'];body,md=finish(uu,tt,ta,dict(kind='budget_guard_swap',source='refine_002',delay=1,removed=removed));stem=D/'candidates'/f'swap_guard{bit}';stem.with_suffix('.qasm').write_text(body);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));ss.append(str(stem.relative_to(H)))
(D/'budget_swap.json').write_text(json.dumps(ss,indent=2));print('budget swaps',len(ss),flush=True)

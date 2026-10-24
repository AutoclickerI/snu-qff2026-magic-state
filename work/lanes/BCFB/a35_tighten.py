from a35_guard_patches import *
from a35_funding import reset_checks
ss=[]
def save(name,s,m):
 stem=D/'candidates'/name;stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));ss.append(str(stem.relative_to(H)))
# Reconsider the cheap acceptance trades individually near the binding budget.
for base,bitslist in [('f0_headroom',[ [181,182,188,186,187,b] for b in [271,185,183,184,3] ]),('f0_guard_gain',[ [181,182,188,186,187,185,183,184,b] for b in [271,3] ])]:
 for j,bits in enumerate(bitslist):s,m=reset_checks(D/'candidates'/base,bits);save(f'tight_{base}_{j}',s,m)
# An explicit single extra readout on the A-only winner, at earliest valid time.
source=D/'candidates/enc_00060';s=read(source)
for t in [37,38,39]:
 uu=list(s[3]);tt=list(s[4]);ta=list(s[5]);uu.append(U(['measure q[16] -> c[650];']));tt.append(t);ta.append('// DETECTOR c[650]')
 try:body,m=finish(uu,tt,ta,dict(kind='same_depth_A_plus_early16',source=str(source.relative_to(H)),time=t))
 except AssertionError:continue
 save(f'tight_Aonly_early16_{t}',body,m)
(D/'tighten.json').write_text(json.dumps(ss,indent=2));print('tighten',len(ss),flush=True)

from pathlib import Path
import json,sys
src=Path('work/lanes/LNS2/review_barrier_v25k')
q=src.with_suffix('.qasm').read_text().splitlines();m=json.loads(src.with_suffix('.json').read_text())
for k,bit in enumerate([230,231,232,233]):
 out=Path('work/lanes/LNS2')/f'review_drop{k}_v25k'
 lines=[l for l in q if l != f'// DETECTOR c[{[23,22,26,27][k]}] c[{bit}]']
 out.with_suffix('.qasm').write_text('\n'.join(lines)+'\n'); mm=dict(m);mm['method']=f'reviewer3 item1 copy4 drop equality {k}';mm['reviewer_drop']=k;out.with_suffix('.json').write_text(json.dumps(mm,indent=2)+'\n')
# all equality drop, useful control
out=Path('work/lanes/LNS2/review_dropall_v25k'); lines=[l for l in q if not any(l==f'// DETECTOR c[{a}] c[{b}]' for a,b in zip([23,22,26,27],[230,231,232,233]))];out.with_suffix('.qasm').write_text('\n'.join(lines)+'\n');mm=dict(m);mm['method']='reviewer3 item1 copy4 drop all equality';out.with_suffix('.json').write_text(json.dumps(mm,indent=2)+'\n')

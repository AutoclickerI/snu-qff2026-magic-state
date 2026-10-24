from core import *
import tprep
for stem in [str(BASE),str(OUT/'choices_6123b801f1'),str(OUT/'combo2_ebb6db5cde')]:
 c=read(stem)
 for n in [1000,10000]:
  start=time.monotonic();r=tprep.check(textof(c),D,shots=n,seed=0)
  row=dict(stem=stem,shots=n,seconds=time.monotonic()-start,passed=r.passed,acc=r.acceptance)
  with (OUT/'runtime.jsonl').open('a')as f:f.write(json.dumps(row)+'\n')
  print(row,flush=True)

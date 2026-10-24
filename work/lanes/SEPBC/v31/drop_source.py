from near_A import *
base=json.loads((V/'full_timing_0.plan.json').read_text())
for bits,c14 in [([54],False),([54],True),([54,56],False),([54,57],False),([54,56,57],False)]:
 name='release_'+('_'.join(map(str,bits)))+('_x14'if c14 else'')
 try:
  c=variant(base,False,c14)
  for b in bits:
   found=[o for o in c['ops']if re.search(rf' -> c\[{b}\];',' '.join(o['lines']))];assert len(found)==1,(b,found);c['ops'].remove(found[0]);uses=[l for l in c['tail']if re.search(rf'c\[{b}\]',l)];assert uses==[f'// DETECTOR c[{b}]'],uses;c['tail'].remove(uses[0])
  out,rec=solve(c,27,15,1)
  if out:
   # Use the proven minimum R, then minimize changes to the existing timings.
   out,r=near(c,rec['R']);rec['near']=r;st=save(out,'v31/'+name);rec['screen']=score(st)
  (V/(name+'.build.json')).write_text(json.dumps(rec,indent=2));append_result(name,rec,'Remove selected source-zero readouts in the physical circuit; remaining reset/preparation is priced, full ideal and single-fault checks retained.');print(name,json.dumps(rec),flush=True)
 except Exception as e:print(name,repr(e),flush=True)

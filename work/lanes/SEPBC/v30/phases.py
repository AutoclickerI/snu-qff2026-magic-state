from retime import *
for cut,name in [(27,'phase_tail'),(0,'phase_all')]:
 c=annotate(read(H/'inputs/v30f'));out,r=solve(c,cut,30,2,phases=True)
 if out:
  st=save(out,'v30/'+name)
  try:r['screen']=score(st)
  except Exception as e:r['score_error']=repr(e)
 (V/(name+'.build.json')).write_text(json.dumps(r,indent=2));append_result(name,r,'Legal diagonal-phase/CX-control commutations in addition to CX/CX, with physical cell capacity.');print(name,json.dumps(r),flush=True)

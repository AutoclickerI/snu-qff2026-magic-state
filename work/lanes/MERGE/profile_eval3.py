from pass3 import *
if __name__=='__main__':
 rows=[]
 for ln in (R/sys.argv[1]).read_text().splitlines():
  try:r=json.loads(ln)
  except json.JSONDecodeError:continue
  if 'loss'in r and 'evaluator_basis'in r:rows.append(r)
 old=max(rows,key=lambda r:r['seconds']);st=Path(old['stem']);E.configure(Path(old['evaluator_basis']),12);sw=E.sw;times={}
 with contextlib.redirect_stdout(io.StringIO()):
  t=time.monotonic();m,eng,groups,nd,ks,psi,where,de=sw.prepare(st,True);times['prepare']=time.monotonic()-t
  t=time.monotonic();compiled,elim=sw.compile_best(m,eng,groups,nd,ks);times['compile']=time.monotonic()-t
  sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
  t=time.monotonic();rr=[sw._row(k)for k in [None]+eng.keys[:72]];times['contract']=time.monotonic()-t
 A=rr[0]['value'];obs=sum(w*b*r['value']for w,b,r in zip(eng.W,eng.beta,rr[1:]));loss=(A-obs)/(2*A)
 assert abs(loss-old['loss'])<1e-13
 out=dict(stem=str(st),sha256=old['sha256'],seconds=times,width=elim['width'],loss=loss,acceptance=A,previous_seconds=old['seconds'])
 dump(R/'eval_profile.json',out);print(json.dumps(out),flush=True)

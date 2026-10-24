from common import *
import redesign as R,tprep
variants=['cats13+m20to21+release20','cats13+m15to16+release15','cats13+m20to21+m15to16+release20+release15']
rows=[]
for variant in variants:
 try:
  pre,tail=R.prefix(variant,keep_tdg=True);pred,succ=S.build_dag(pre);ts=[]
  for ps in pred:ts.append(max([ts[j]+1 for j in ps]+[0]))
  txt=S.emit(['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];'],pre,ts,tail);rep=tprep.check(txt,R.PD,p=0,shots=1000,seed=0)
  row=dict(variant=variant,passed=rep.passed,score=float(rep.score)if rep.score is not None else None,report=str(rep),data=R.PD[:],cx=sum(u.name=='CX'for u in pre),depth=max(ts)+1,physical_cells=sorted({q for u in pre for q in u.qs}))
  if not rep.passed:raise AssertionError(row)
  stem=H/('prefix_'+variant.replace('+','_'));stem.with_suffix('.qasm').write_text(txt);stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=R.PD,**row),indent=2))
 except Exception as e:row=dict(variant=variant,error=repr(e))
 rows.append(row);print(json.dumps(row),flush=True);(H/'prefix_release_validation.json').write_text(json.dumps(rows,indent=2));append_result('prefix:'+variant,row,'Noiseless cultivation-only target/check verification. No noise-performance claim.')

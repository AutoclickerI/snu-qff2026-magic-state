from common import *
import redesign as rd,tprep
variant='cats13+m20to26+release20';pre,tail=rd.prefix(variant,keep_tdg=True);pred,_=S.build_dag(pre);ts=[]
for ps in pred:ts.append(max([ts[j]+1 for j in ps]+[0]))
txt=S.emit(['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];'],pre,ts,tail);r=tprep.check(txt,rd.PD,p=0,shots=1000,seed=0);assert r.passed,str(r);x=dict(variant=variant,passed=r.passed,data=rd.PD,depth=max(ts)+1,cx=sum(u.name=='CX'for u in pre),report=str(r));(H/'prefix_release26_validation.json').write_text(json.dumps(x,indent=2));append_result('prefix_release26',x,'Ideal full-prefix judge verification; data20 relocated to26 before its final cultivation interaction, source20 released and reset only for the late cat transfer.');print(json.dumps(x))

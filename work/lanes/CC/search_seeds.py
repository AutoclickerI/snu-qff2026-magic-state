from search_cc import base,N,cm,data,Eval,run,tprep,transpile
from pathlib import Path
import json
# candidate initial patch from the first screen, and several compact/line patches.
patches=[[0,1,2,6,7,8,12],[7,8,9,13,14,15,16],[3,4,5,9,10,11,15],[20,21,22,26,27,28,32],[2,8,14,20,26,27,28]]
out=[]
for ds in patches:
 for seed in range(30):
  rest=[p for p in range(N) if p not in ds]; phys=ds+[10,11]+[p for p in rest if p not in (10,11)]
  try:
   tr=transpile(base(),basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'],coupling_map=cm,initial_layout=phys,layout_method='sabre',routing_method='sabre',optimization_level=1,seed_transpiler=seed)
   dp=list(tr.layout.final_index_layout()[:7]);txt=tprep.submission_text(tr,postselect=[(0,[tr.clbits[0]]),(0,[tr.clbits[1]])]);ev=Eval(txt,dp);rr=run(ev,procs=1)
   out.append((rr['loss'],rr['loss1'],rr['A1'],tr.count_ops().get('cx',0),tr.depth(),seed,ds,dp,txt));
   if len(out)==1 or rr['loss']<min(x[0] for x in out[:-1]): print('BEST',out[-1][:8],flush=True)
  except Exception as e: print('err',ds,seed,e,flush=True)
out.sort(key=lambda x:x[0]);
for x in out[:20]:print('TOP',x[:8])
b=out[0];Path('work/lanes/CC/cc_hm_best.qasm').write_text(b[8]);json.dump({'data_qubits':b[7],'loss2':b[0],'loss1':b[1],'A1':b[2],'cx':b[3],'depth':b[4],'seed':b[5],'initial':b[6]},open('work/lanes/CC/cc_hm_best.json','w'),indent=2)
json.dump([dict(loss=x[0],loss1=x[1],A1=x[2],cx=x[3],depth=x[4],seed=x[5],initial=x[6],data=x[7]) for x in out],open('work/lanes/CC/search_seeds.json','w'),indent=2)

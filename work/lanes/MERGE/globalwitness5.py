from pass5 import *
from judge5 import verify
hist=json.loads((R/'wide_history.json').read_text());cur=hist[1]['price'];es=json.loads((R/'wide_r3_menu.json').read_text());flip=M.mk(fam='rev',a=25,b=24,t=37)
E.configure(R/('basis_'+cur['sha256']+'.json'),12)
common=[dict(id='trade:363:detector',fam='trade',bit=363,mode='detector'),dict(id='trade:358:detector',fam='trade',bit=358,mode='detector')]
undo=es['ejectr2:herald:RESET25@32:v1']
cheap=[es[i]for i in ['shift:RX11@10>11','mi:RESET12@11','mi:RX21@14']]
cases=[('undo_q25',Path(cur['stem']),[flip]+common+[undo]),('keep_q25',Path(cur['stem']),[flip]+common+cheap),('fast',H/'cand/merge5_live_1c4b23e89b48',[flip]+common)]
rows=[]
for name,base,edits in cases:
 try:
  c,txt=apply(M.read(base),edits);st=E.write_stem(txt,c['meta']['data_qubits']);r=price(st,dict(kind='GLOBAL funded witness',name=name,base=str(base),edits=[e['id']for e in edits]),cur['loss']);r.update(name=name,edits=[e['id']for e in edits]);rows.append(r)
  if feasible(r)and r['loss']<TAU-3e-8:
   dest=H/'cand'/f'merge5_global_{name}_{r["sha256"][:12]}';shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),dict(r,status='exact finalist; judge pending'))
   j=verify(st);r['judge_1e6']=j;dump(dest.with_suffix('.json'),dict(r,status='finalist'if j['gates_ok']and j['speed_ok']else'judge rejected'))
   print(json.dumps(dict(event='candidate_published',stem=str(dest),loss=r['loss'],acceptance=r['acceptance'],gates_ok=j['gates_ok'],speed_ok=j['speed_ok'],judge_ratio=j.get('ratio'))),flush=True)
 except Exception as ex:
  r=dict(name=name,invalid=repr(ex),edits=[e['id']for e in edits]);rows.append(r);print(json.dumps(r),flush=True)
 dump(R/'global_witness_outcome.json',rows)
print(json.dumps(dict(event='global_witness_complete',prices=[dict(name=r['name'],loss=r.get('loss'),A=r.get('acceptance'),error=r.get('invalid',r.get('error')))for r in rows])),flush=True)

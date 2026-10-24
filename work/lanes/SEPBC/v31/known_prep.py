from build import *
from known_states import opportunities,insert
base=json.loads((V/'A44_feedback_2.plan.json').read_text());br=json.loads((V/'A44_feedback_2.screen.json').read_text());opts=opportunities(base);rows=[]
(V/'known_prep_opportunities.json').write_text(json.dumps(opts,indent=2));print('opportunities',opts,flush=True)
for j,ch in enumerate(opts):
 name=f'prepcheck_{j}_{ch["axis"]}{ch["q"]}_t{ch["t"]}'
 try:
  st=save(insert(base,ch),'v31/'+name);r=score(st);cost=math.log(br['exp_minus_A1']/r['exp_minus_A1']);row=dict(stem=name,check=ch,screen=r,gain=br['total']-r.get('total',1),acceptance_cost_A1=cost);rows.append(row);append_result(name,row,'CSS-known single-qubit state with explicit symbolic measurement frame; idle-slot detector addition on R44.');print(name,row,flush=True)
 except Exception as e:rows.append(dict(stem=name,check=ch,error=repr(e)));print(name,repr(e),flush=True)
(V/'known_prep_scan.json').write_text(json.dumps(rows,indent=2))
st=save(edit(base,'mz19'),'v31/A44_feedback_mz19');print('mz19',score(st),flush=True)
valid=[r for r in rows if r.get('gain',0)>1e-12 and r['screen']['exp_minus_A1']>=.5002]
if valid:
 # Reprice the best per-cell check together, including q19's known-zero init.
 d=base;chosen=[]
 for q in sorted({r['check']['q']for r in valid}):
  r=min((r for r in valid if r['check']['q']==q),key=lambda r:r['screen']['total']);d=insert(d,r['check']);chosen.append(r['stem'])
 st=save(d,'v31/A44_checked');r=score(st);print('joint',r,chosen,flush=True)
 st=save(edit(d,'mz19'),'v31/A44_checked_mz19');print('joint_mz19',score(st),flush=True)

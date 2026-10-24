from assemble_layers import *
from mutations import with_round
rows=[]
for source in ['layer_26_R44_m2','layer26_timing_0']:
 for reuse in [False,True]:
  c=with_round(json.loads((V/(source+'.plan.json')).read_text()),43)
  if reuse:
   candidates=[o for o in c['ops']if o.get('tag')=='prefix'and o['t']>=27 and o['lines']==['reset q[2];','h q[2];']];assert len(candidates)==1;c['ops'].remove(candidates[0])
  name=source+('_reuse_R43'if reuse else'_fixed_R43');d,r=fit(c,10,cut=0,phases=True);row=dict(stem=name,schedule=r)
  if d:
   try:st,z=write(d,name,'R43 re-test with the new12-CX A encoder and A2 now prepared in Z. Retain every source check; pre-blue X reuse is tested only with an explicit speed gate.');row['screen']=z
   except Exception as e:row['error']=repr(e);print(name,repr(e),flush=True)
  else:print(name,r,flush=True)
  rows.append(row);(V/'final_encoder_R43.json').write_text(json.dumps(rows,indent=2))

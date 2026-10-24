from assemble_layers import *
for source in ['layer_26_R44_m2','layer26_timing_0']:
 for qs in [(16,),(14,),(14,16)]:
  c=json.loads((V/(source+'.plan.json')).read_text());b=bit(c);new=[]
  for q in qs:
   rx=next(o for o in c['ops']if o.get('tag')=='encoder_a'and o['lines']==[f'reset q[{q}];',f'h q[{q}];']);first=min(o['t']for o in c['ops']if o.get('tag')=='encoder_a'and unit(o).name=='CX'and q in unit(o).qs)
   rx['t']=min(rx['t'],first-2);i=c['ops'].index(rx);new.append((i+1,dict(lines=[f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];'],t=first-1,tag='encoder_a')));c['tail'].append(f'// DETECTOR c[{b}]');b+=1
  for i,o in sorted(new,reverse=True):c['ops'].insert(i,o)
  R=c['meta']['R']
  for o in c['ops']:
   if o.get('tag')in('round','decoder'):o['offset']=o['t']-R
  name=source+'_check'+'_'.join(map(str,qs));d,r=fit(c,5,cut=0,phases=True)
  if d:
   try:write(d,name,'Add native known-X input verification on the new encoder pivots; all source checks and decoder retained. Any earlier prefix release needed for the new check is legally rescheduled and fully repriced.')
   except Exception as e:print(name,repr(e),flush=True)
  else:print(name,r,flush=True)

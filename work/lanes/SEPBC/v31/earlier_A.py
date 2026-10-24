"""Reverse A input orientation to remove its binding q15 X-reset/recheck delay."""
from build import *
sys.path.insert(0,str(H/'v30'));from retime import solve

def variant(base,check8,check14):
 c=copy.deepcopy(base);R=c['meta']['R'];ops=c['ops'];old_A=[o for o in ops if o.get('tag')=='encoder_a'and unit(o).name=='CX'];assert len(old_A)==11,len(old_A)
 # New pivots are1,2,8,14. q9 and q15 instead reuse source-zero MZs56/57.
 for q in [9,15]:
  o=[o for o in ops if o['t']<R and unit(o).qs==(q,)and unit(o).name=='RX'][-1];ops.remove(o)
 old59=next(o for o in ops if 'measure q[9] -> c[59];'in o['lines']);ops.remove(old59);c['tail']=[l for l in c['tail']if l!='// DETECTOR c[59]']
 o=[o for o in ops if o['t']<R and unit(o).qs==(14,)and unit(o).name=='RESET'][-1];o['lines']=['reset q[14];','h q[14];']
 b=bit(c);m8=next(o for o in ops if 'measure q[8] -> c[54];'in o['lines']);new_init=[dict(lines=['reset q[8];','h q[8];'],t=m8['t']+1,tag='encoder_a')]
 if check8:new_init.append(dict(lines=['h q[8];',f'measure q[8] -> c[{b}];','h q[8];'],t=m8['t']+2,tag='encoder_a'));c['tail'].append(f'// DETECTOR c[{b}]');b+=1
 if check14:new_init.append(dict(lines=['h q[14];',f'measure q[14] -> c[{b}];','h q[14];'],t=o['t']+1,tag='encoder_a'));c['tail'].append(f'// DETECTOR c[{b}]');b+=1
 gates=[[(8,9),(14,15)],[(14,8),(15,16)],[(2,8)],[(1,2),(8,14)],[(2,8),(14,15)],[(1,2),(8,14)]]
 new=[dict(lines=[f'cx q[{u}],q[{v}];'],t=R-6+j,tag='encoder_a')for j,layer in enumerate(gates)for u,v in layer]
 rest=[o for o in ops if o not in old_A];c['ops']=[o for o in rest if o['t']<R]+new_init+new+[o for o in rest if o['t']>=R]
 # Every initializer follows prefix use and precedes the replacement encoder.
 # Native-list dependency order is authoritative; stored times only seed search.
 for i,o in enumerate(c['ops']):o['id']=i
 c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{b}]',l)for l in c['h']]
 return c
if __name__=='__main__':
 base=json.loads((H/'v30/sensitivity_tail.plan.json').read_text())
 for c8,c14 in [(False,False),(True,False),(True,True)]:
  name=f'A_late_{int(c8)}{int(c14)}'
  try:
   c=variant(base,c8,c14);d,r=solve(c,27,15,1)
   if d:
    st=save(d,'v31/'+name);r['screen']=score(st)
   st=V/name;st.with_suffix('.build.json').write_text(json.dumps(r,indent=2));append_result(name,r,'A pivots changed from1,2,9,15 to1,2,8,14; q9/q15 reuse their source-zero measurements; exact-correct encoder, full circuit priced.');print(name,json.dumps(r),flush=True)
  except Exception as e:print(name,repr(e),flush=True)

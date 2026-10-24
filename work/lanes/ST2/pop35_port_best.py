"""Build direct Z-window crossover seeds and import measured external winners."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop35_support as v,pop35_moves as m
out=v.OUT/'focused';out.mkdir(exist_ok=True);jobs=[];seen=set()
def put(name,c,desc):
 try:
  c=v.d.normalize(c);fp=v.d.digest(c)
  if fp in seen:return
  seen.add(fp);p=out/name;v.d.save(c,p);jobs.append(dict(stem=str(p.relative_to(v.H)),description=dict(desc,budget_screen=True)))
 except Exception as e:print('BUILD_REJECT',name,repr(e))
for name,stem in [('base',v.OUT/'base'),('timing',v.OUT/'seed0/FRESH_feedback_i008_t04'),('q7x',v.OUT/'zebra/g00_ecc15c15da6170'),('q7x_q10z',v.OUT/'zebra/g01_f5d93c77813b4b')]:
 if not stem.with_suffix('.qasm').exists():continue
 c=v.C.read(stem)
 for g in m.guards(c):
  if g['q']==7 and g['h']==13 and g['times'][0]>=25:c=m.drop(c,g);break
 # Replace existing reset at25 by the post-echo reset; a FRESH-timed reset
 # at33 is already at the required site.
 for i,(u,t)in enumerate(zip(c['u'],c['t'])):
  if u.qs==(13,)and u.name=='RESET'and t==25:c['t'][i]=33
 b=v.C.bit(c)
 for t,ls in [(26,['reset q[13];','h q[13];']),(27,['cx q[13],q[7];']),(31,['cx q[13],q[7];']),(32,['h q[13];',f'measure q[13] -> c[{b}];','h q[13];'])]:c['u'].append(v.C.Unit(ls));c['t'].append(t)
 c['tail'].append(f'// DETECTOR c[{b}]');put(name+'_q7Z',c,dict(family='q7_Z_crossover',parent=str(stem.relative_to(v.H))))
 # Incorporate the successful measured-X initialization at q1 t7.
 try:
  x=v.C.clone(c);i=next(i for i,(u,t)in enumerate(zip(x['u'],x['t']))if u.qs==(1,)and u.name=='RX'and t==7);b=v.C.bit(x);x['u'][i]=v.C.Unit(['h q[1];',f'measure q[1] -> c[{b}];','h q[1];']);x['tail'].append(f'// DETECTOR c[{b}]');put(name+'_q7Z_mx1',x,dict(family='measured_crossover',parent=name+'_q7Z',move='q1_RX_to_checked_MX_at7'))
 except StopIteration:pass
# Import the complete measured WAITPROT winner as another population seed.
for source in ['combo_fund_fold15_released7Z','combo_st2_fund_parity_released7Z','combo_st2_fund_released7Z']:
 p=v.ROOT/'work/lanes/WAITPROT/v35'/source
 if p.with_suffix('.qasm').exists():put('WAIT_'+source,v.C.read(p),dict(family='WAITPROT_full_seed',source=str(p.relative_to(v.ROOT))))
(out/'jobs.json').write_text(json.dumps(jobs,indent=2));print('BUILT',len(jobs))

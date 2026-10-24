"""Resolve failed borrowed-cell/reuse recipes and price acceptance trades."""
from core import *
from build import reordered
def main():
 jobs=[]
 def emit(c,name,change,**sched):
  c=placement(c,**sched);stem=save(c,name,change);jobs.append(dict(stem=str(stem),change=change))
 # The previous flag used q13 after B had already started on it. Reserve the
 # complete borrowed lifetime before allowing suffix preparation on that cell.
 c=read(OUT/'flag_14_13_112');c['tags']=c['meta']['component_tags']
 c=reordered(c,[i for i,t in enumerate(c['tags'])if t!='suffix']+[i for i,t in enumerate(c['tags'])if t=='suffix'])
 emit(c,'flag14_reserved','late cat14 flag on q13, borrowed-cell lifetime reserved before BC initialization')
 # A bare cat parity has random individual MX outcomes. q10 must be reset
 # before its |+>-state data hop; retaining the measured sign was incorrect.
 for mask in (4,5,6):
  for mode in('x','z'):
   c=read(OUT/f'cat_{mask}_{mode}_0_0');c['tags']=c['meta']['component_tags']
   seq=[i for i,u in enumerate(c['u'])if u.qs==(10,)and c['tags'][i]!='suffix'and u.name in ('MX','MEASURE')]
   last=seq[-1]
   for i in seq:
    if c['u'][i].name=='MX':c['u'][i]=Unit(c['u'][i].lines[:2])
   add(c,last+1,['reset q[10];','h q[10];'])
   emit(c,f'cat_{mask}_{mode}_postreset10','cat parity check with reset after the last native MX/M of random-sign q10 before its data hop')
 # Preserve promising checks while trading pre-stage internal exposure for
 # acceptance. These are complete physical schedules, no noise is removed.
 for nm in ['partial_x_enc25_rigid','partial_x_enc24_resource11_rigid']+[f'form_{s}'for s in ['f00_0','f02_0','f04_0','f06_0','f09_0','f11_0','f13_0','f15_0','f17_0','f19_0','f21_0','f23_0','f24_0','f26_0','f28_0','f30_0']]:
  c=read(OUT/nm);c['tags']=c['meta']['component_tags']
  emit(c,nm+'_trade',nm+' with minimum prefix live-gap exposure to recover acceptance',compact=True,rigid=True)
 (OUT/'trade_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')
if __name__=='__main__':main()

from core import *
from build import insert_block,reordered
from partial_checks import tile
from qcirc import Circ
def cat_tile(mask,mode,measure_init=False):
 p=tile(mask,mode);us=S.fold_units(S.qasm_ops(p.text())[1]);pairs=[(1,2),(13,14),(9,10)];remove=set();tail=[]
 for k,(a,b)in enumerate(pairs):
  if not(mask>>k&1):continue
  ix=[i for i,u in enumerate(us)if u.lines==[f'cx q[{a}],q[{b}];']];assert len(ix)==2
  remove.add(ix[-1]);ma=next(i for i,u in enumerate(us)if u.last_is_measure and u.qs==(a,));mb=next(i for i,u in enumerate(us)if u.last_is_measure and u.qs==(b,))
  ba=int(re.findall(r'c\[(\d+)\]',us[ma].lines[-1])[0]);bb=int(re.findall(r'c\[(\d+)\]',us[mb].lines[-1])[0])
  if mode=='x':us[mb]=Unit([f'h q[{b}];',f'measure q[{b}] -> c[{bb}];'])
  else:us[ma]=Unit([f'measure q[{a}] -> c[{ba}];'])
  tail.append(f'// DETECTOR c[{ba}] c[{bb}]')
  if measure_init:
   ir=next(i for i,u in enumerate(us)if u.name=='RESET'and u.qs==(b,));us[ir]=Unit([f'measure q[{b}] -> c[{100+k}];']);tail.append(f'// DETECTOR c[{100+k}]')
 raw='\n'.join(l for i,u in enumerate(us)if i not in remove for l in u.lines)
 class Text:
  def text(self):return 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[256];\n'+raw+'\n'+'\n'.join(tail)+'\n'
 return Text()
def main():
 base=provenance(read(BASE));jobs=[]
 def emit(c,nm,change,**opts):
  try:
   c=placement(c,**opts);stem=save(c,nm,change);jobs.append(dict(stem=str(stem),change=change))
  except Exception as e:print(nm,'BUILD ERROR',e,flush=True)
 # Budget recovery for full blue XZ and the extra HXY: compact scheduling is
 # an actual circuit change whose fidelity cost is included.
 for nm in ['partial_1_x_129','partial_1_xz_129','extra_hxy_77_0','extra_stab_77_z']:
  c=read(OUT/nm);c['tags']=c['meta']['component_tags']
  for rigid in(False,True):emit(copy.deepcopy(c),nm+'_compact'+str(int(rigid)),nm+' compact live-gap schedule to recover acceptance',compact=True,rigid=rigid)
 for mask in (1,2,4,3,5,6):
  for mode in('x','z'):
   for mi in(False,True):
    if mask!=1 and mi:continue
    p=cat_tile(mask,mode,mi);c=insert_block(base,p,129)
    if mask&4:
     inds=[i for i,u in enumerate(c['u'])if u.name=='MX'and u.qs==(10,)and c['tags'][i]!='suffix']
     for i in inds:c['u'][i]=Unit(c['u'][i].lines[:2]+(['h q[10];']if i==inds[-1]else[]))
     if mode=='z':add(c,inds[-1]+1,['reset q[10];','h q[10];'])
    for compact in(False,True):emit(copy.deepcopy(c),f'cat_{mask}_{mode}_{int(mi)}_{int(compact)}',f'tile {mask} {mode} check: omit unbell, parity of both readouts; M-init={mi}; compact={compact}',compact=compact)
 # Transplant 21/24/25 encoders into the promising single-tile check networks.
 for enc in ('enc25_rigid','enc24_resource11_rigid','enc21_joint_d7_rigid'):
  c=read(OUT/enc);c['tags']=c['meta']['component_tags'];ref=provenance(read(BASE));old=read(OUT/'partial_1_x_129');old['tags']=old['meta']['component_tags']
  nu=[u for u,tag in zip(c['u'],c['tags'])if tag=='injection']
  rem=[i for i,tag in enumerate(old['tags'])if tag not in ('injection',) and not(old['u'][i].name=='T'and old['u'][i].qs==(7,)and old['t'][i]<10)]
  # Source new encoder tags include its injection T, the old source had a
  # distinct T_layers tag. Exact correctness guards the full replacement.
  v=reordered(old,rem);v['u']=nu+v['u'];v['t']=[0]*len(nu)+v['t'];v['tags']=['injection']*len(nu)+v['tags']
  if enc.startswith('enc25')or enc.startswith('enc24'):
   v['tail']=[x for x in v['tail']if not any(re.fullmatch(r'// DETECTOR c\['+str(b)+r'\]',x.strip())for b in(39,40,41))]
   bits={int(b)for u in nu for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)};v['tail'] += [f'// DETECTOR c[{b}]'for b in bits]
  emit(v,'partial_x_'+enc,'single blue X stabilizer check plus '+enc,rigid=True)
 (OUT/'refine_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')
if __name__=='__main__':main()

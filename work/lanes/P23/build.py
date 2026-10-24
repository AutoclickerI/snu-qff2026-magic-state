from core import *
import cultiv_port
from qcirc import Circ

def reordered(c,indices):
 c=copy.deepcopy(c);c['u']=[c['u'][i]for i in indices];c['t']=[c['t'][i]for i in indices];c['tags']=[c['tags'][i]for i in indices];c.pop('origin',None);return c
def insert_block(c,new,where):
 pre=[i for i,tag in enumerate(c['tags'])if tag!='suffix'];suf=[i for i,tag in enumerate(c['tags'])if tag=='suffix']
 before=[i for i in pre if c['origin'][i]<where];after=[i for i in pre if i not in before]
 h,r,det=S.qasm_ops(new.text());nu=S.fold_units(r)
 c=reordered(c,before+after+suf);idx=len(before)
 c['u'][idx:idx]=nu;c['tags'][idx:idx]=['check_extra']*len(nu);c['t'][idx:idx]=[c['t'][max(0,idx-1)]]*len(nu)
 c['tail']+=det;return c
def cat_block():
 p=Circ();p.nbits=64;cultiv_port.run_chunk(p,cultiv_port.extract_chunk('make_chunk_d3_double_cat_check',cultiv_port.UP+'_cultivation_stage.py'),s_to='Tswap');return p
def cycle_block(zfirst=True):
 p=Circ();p.nbits=64;cultiv_port.superdense_cycle(p,z_first=zfirst);return p

def main():
 base=provenance(read(BASE));manifest=[]
 def emit(c,name,change,**sched):
  try:
   if sched:c=placement(c,**sched)
   stem=save(c,name,change);manifest.append(dict(stem=str(stem),change=change));print('built',name,c['meta']['R'],c['meta']['cx'],flush=True)
  except Exception as e:manifest.append(dict(name=name,change=change,build_error=str(e)));print('BUILD FAIL',name,e,flush=True)
 emit(copy.deepcopy(base),'base','unaltered v22h_c2c9 control')
 for rigid in (False,True):
  for w in (1,4,16):
   emit(copy.deepcopy(base),f'compact_{"rigid"if rigid else"free"}_w{w}',f'CP-SAT minimize weighted pre-stage internal live gaps; data weight {w}; rigid suffix {rigid}',compact=True,rigid=rigid,weights={q:w for q in PD})
 for where in (77,129):
  c=insert_block(base,cat_block(),where)
  # Preserve q10's |+> for its existing one-step-saving hop when the extra
  # block becomes its last measurement before that hop.
  if where==129:
   inds=[i for i,u in enumerate(c['u'])if u.name=='MX'and u.qs==(10,)and c['tags'][i]!='suffix']
   for i in inds:
    c['u'][i]=Unit(c['u'][i].lines[:2]+([f'h q[10];']if i==inds[-1]else[]))
  for compact in (False,True):emit(copy.deepcopy(c),f'extra_hxy_{where}_{int(compact)}',f'add full 22-CX H_XY cultivation check at prefix boundary {where}',compact=compact)
 for where in (77,129):
  for zfirst in (True,False):
   c=insert_block(base,cycle_block(zfirst),where)
   if where==129:
    inds=[i for i,u in enumerate(c['u'])if u.name in('MX','MEASURE')and u.qs==(10,)and c['tags'][i]!='suffix']
    # Superdense ends q10 in Z; reset it to |+> for the retained hop.
    last=inds[-1];add(c,last+1,['reset q[10];','h q[10];'])
    for i in inds:
     if c['u'][i].name=='MX':c['u'][i]=Unit(c['u'][i].lines[:2])
   emit(c,f'extra_stab_{where}_{"z"if zfirst else"x"}',f'extra full colour-code stabilizer round at boundary {where}, z_first={zfirst}',mode='alap')
 # Deterministic preparation checks: each verifies the freshly prepared state.
 check_sites=[i for i,u in enumerate(base['u'])if base['tags'][i]!='suffix'and u.name=='RX']
 for group in [[i]for i in check_sites]+[[i for i in check_sites if base['tags'][i]=='check1'],check_sites]:
  c=copy.deepcopy(base)
  for b,i in enumerate(sorted(group,reverse=True)):
   q=c['u'][i].qs[0];bit=64+b;add(c,i+1,[f'h q[{q}];',f'measure q[{q}] -> c[{bit}];',f'h q[{q}];']);c['tail'].append(f'// DETECTOR c[{bit}]')
  name='mx_'+('_'.join(str(base['origin'][i])for i in group)if len(group)<4 else f'group{len(group)}')
  emit(c,name,'MX check after pre-stage RX at reference units '+str([base['origin'][i]for i in group]),mode='alap')
 for i,u in enumerate(base['u']):
  if base['tags'][i]!='suffix'and u.name=='RESET':
   c=copy.deepcopy(base);q=u.qs[0];c['u'][i]=Unit([f'measure q[{q}] -> c[64];']);c['tail'].append('// DETECTOR c[64]')
   emit(c,f'minit_{base["origin"][i]}',f'replace prefix reset on {q} by postselected Z measurement',mode='alap')
 # Paired flags around single cat-to-data couplings; flag ideal cancellation
 # is verified by the judge, including flags through intervening cat gates.
 for cat,flag in [(6,12),(10,11),(14,13)]:
  couplings=[i for i,u in enumerate(base['u'])if base['tags'][i]in('check1','check2')and u.name=='CX'and int(S.QRE.findall(u.lines[0])[0])==cat]
  for i in couplings:
   c=copy.deepcopy(base);ri=base['origin'][i]
   # Put the flag prep after its last existing use, before the selected CX.
   # On q13 this follows injection readout; q11/q12 block preps follow later.
   after=[[f'cx q[{cat}],q[{flag}];'],[f'measure q[{flag}] -> c[64];']]
   for lines in reversed(after):add(c,i+1,lines)
   for lines in reversed([[f'reset q[{flag}];'],[f'cx q[{cat}],q[{flag}];']]):add(c,i,lines)
   c['tail'].append('// DETECTOR c[64]')
   emit(c,f'flag_{cat}_{flag}_{ri}',f'Z-read flag {flag} catches X on cat {cat} around reference CX {ri}',mode='alap')
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()

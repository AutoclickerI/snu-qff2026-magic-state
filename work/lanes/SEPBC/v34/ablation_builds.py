from design import *
from mutations import with_round
from assemble_layers import fit
base=getbase(0)
for name in ['decoder0','reuseblue_0_R43']:
 c=json.loads((V/(name+'.plan.json')).read_text());c=remove_decoder(c)
 # The two A readouts can return to the ordinary R+1 readout layer.
 for o in c['ops']:
  if o['t']>=c['meta']['R']and any(f'measure q[{q}] -> c[{b}];'in o['lines']for q,b in[(8,16),(9,17)]):o['t']=c['meta']['R']+1
 write(c,name+'_no_decoder','Matched decoder ablation, keeping early D->A couplings and restoring their original Z readout detector basis. All source checks unchanged.')
for b in [60,180,272]:
 c=copy.deepcopy(base);o=next(o for o in c['ops']if any(f'-> c[{b}];'in l for l in o['lines']));assert o.get('tag')=='encoder_a';c['ops'].remove(o);c['tail'].remove(f'// DETECTOR c[{b}]');name=f'no_prepcheck_{b}';write(fix(c),name,'Remove an A-input X verification, not a data-source zero check. Full source detectors and A logical-X decoder flag retained.')

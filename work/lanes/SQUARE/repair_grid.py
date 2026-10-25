import sys,json
from build_rounds import H
from synthesize_grid import build

name=sys.argv[1]
m=json.loads((H/'builds'/name).with_suffix('.json').read_text())
if 'resource' in m:r=m['resource']
else:r=dict(seed=m['seed'],pivots=m['initial_plus'],ops=m.get('preparation_sequence',[(a,b) for t,a,b in m['preparation_ops']]),checks=[],
            flag=m['flag'],support=m['logical_z_verification'],prep_cx=m['prep_cx'])
layout='layout_compact.json' if name.startswith('grid_compact') else 'layout_joint.json'
out=[build(r,tag=name+'_alap',layout=layout,alap=True),build(r,tag=name+'_guards',layout=layout,guards=True),
     build(r,tag=name+'_both',layout=layout,alap=True,guards=True)]
(H/'repair_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out),flush=True)

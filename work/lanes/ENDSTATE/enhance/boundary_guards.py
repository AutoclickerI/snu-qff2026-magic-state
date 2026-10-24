from common import *
from guards import echo_options,apply
p=load(H/'matrix_R38_pack03');actions=[a for a in echo_options(p)if a.get('next_measured_pivot')];names=[]
for i,a in enumerate(actions):
 a['id']=f'mb{i:03d}';z=apply(p,[a]);z['meta']['MB_boundary_parent']='matrix_R38_pack03';s=save(z,f'boundary_{i:03d}');names.append(s.name)
(H/'boundary.queue.json').write_text(json.dumps(names));(H/'boundary.actions.json').write_text(json.dumps(actions,indent=2));print('measured-pivot boundary actions',len(actions),flush=True)

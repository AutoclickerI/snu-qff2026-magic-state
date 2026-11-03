from spidercss.cat_at_origin import cat_at_origin
from spidercss.utils import load_qecc
from spidercss.resource_targets import ReuseTarget
v=load_qecc('7_1_3');print('LOADED',v)
for target in [ReuseTarget.DEPTH,ReuseTarget.QUBITS]:
 c=cat_at_origin(v[1],v[5],basis='Z',reuse_target=target,analyze_hook_errors=True)
 print('TARGET',target,'\n',c,flush=True)

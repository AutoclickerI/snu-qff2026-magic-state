from pass3 import *
from judge3 import one
import socket
if __name__=='__main__':
 rows=[]
 for n in ['G3','G3_prefix_resets','bc3_7','bc3_sources_all','seed3_0','G3_prefix_resets','G3','bc3_sources_all','bc3_7','seed3_0']:
  r=one(C/n);r.update(stem=str(C/n),host=socket.gethostname());rows.append(r);dump(R/'runtime_controls_hippo.json',rows);print(json.dumps(r),flush=True)

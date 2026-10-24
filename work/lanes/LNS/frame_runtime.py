"""Existing detector parity is zero on accepted shots; test equivalent frames."""
from core import *
import tprep,concurrent.futures
def one(axis):
 c=read(OUT/'bc_port_229898d242');assert '// DETECTOR c[7]'in c['tail'];assert not any('FRAME_'in l for l in c['tail'])
 if axis!='auto':c['tail'] += [f'// FRAME_{p}(0)'+(' c[7]'if p in axis else '')for p in ['X','Z']]
 t=time.monotonic();r=tprep.check(textof(c),D,shots=10000,seed=0);elapsed=time.monotonic()-t
 return dict(axis=axis,seconds=elapsed,passed=r.passed,acc=r.acceptance,source='bc_port_229898d242',shots=10000)
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(2)as pool:rows=list(pool.map(one,['auto','X','Z','XZ']))
 (OUT/'frame_runtime.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)

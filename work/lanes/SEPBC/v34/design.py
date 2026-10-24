from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'v31')]
from common import *
from build import fix,bit,parity
import wide_moments
V=H/'v34'
def write(c,name,why=''):
 st=save(c,'v34/'+name);ev=exact2.Eval(st.with_suffix('.qasm').read_text(),c['meta']['data_qubits']);c1=float(ev.fp@ev.n_single)
 r=wide_moments.evaluate(ev)if abs(c1)<1e-12 else dict(c1=c1,invalid_cubic=True,exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))))
 r['sha256']=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest();st.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));append_result(name,r,why);print(name,json.dumps(r),flush=True);return st,r
def getbase(k=0):
 old=json.loads((H/f'v31/guard5_timing_{k}.plan.json').read_text());c=read(V/'inputs'/f'guard5_timing_{k}_a_decode');pool={}
 for o in old['ops']:pool.setdefault(tuple(o['lines']),[]).append(o)
 for o in c['ops']:
  found=pool.get(tuple(o['lines']),[])
  if found:o['tag']=found.pop(0).get('tag','prefix')
  elif o['t']>=c['meta']['R']:o['tag']='decoder'if unit(o).name=='CX'else'round'
  else:o['tag']='prefix'
 c['meta'].update(source=f'FRESH/guard5_timing_{k}_a_decode',R=44);return c
def remove_decoder(c):
 c=copy.deepcopy(c);R=c['meta']['R'];ops=c['ops']
 for edge in [(8,9),(9,15)]:
  o=max((o for o in ops if o['lines']==[f'cx q[{edge[0]}],q[{edge[1]}];']),key=lambda o:o['t']);assert o['t']>=R;ops.remove(o)
 mx=next(o for o in ops if 'measure q[8] -> c[16];'in o['lines']and o['t']>=R);mx['lines']=['measure q[8] -> c[16];']
 c['tail'].remove('// DETECTOR c[16]');parity(c,17,16);parity(c,20,17)
 return fix(c)
if __name__=='__main__':
 for k in [0,1]:write(getbase(k),'decoder'+str(k),'FRESH decoder port rebased verbatim in native operations. No new decoder claim; independent local price.')

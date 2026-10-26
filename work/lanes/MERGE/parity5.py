"""Price nonzero residual XOR parities, distinct from adding several detectors."""
from pass5 import *

def run(which,workers):
 if which=='base':current=json.loads((R/'baseline.json').read_text());menuf=R/'wide_r1_menu.json'
 else:
  hist=json.loads((R/'wide_history.json').read_text());current=hist[-1]['price'];menuf=R/f'wide_r{hist[-1]["round"]+1}_menu.json'
 st=Path(current['stem']);es=json.loads(menuf.read_text());c=M.read(st);gap=H5.detgap(st.with_suffix('.qasm').read_text());dims=gap['extra'];xs=[]
 for mask in range(1,1<<len(dims)):
  bits=set()
  for k,d in enumerate(dims):
   if mask>>k&1:bits.symmetric_difference_update(d)
  bits=sorted(bits);i='xor:'+','.join(map(str,bits));es[i]=dict(id=i,fam='detparity',bits=bits);xs.append(i)
 p=R/f'xor_{which}_menu.json';dump(p,es);E.configure(R/('basis_'+sha(C/'base')+'.json'),12)
 rows=batch(st,p,[[i]for i in xs],f'xor_{which}',workers,current['loss'])
 dump(R/f'xor_{which}_summary.json',dict(base=current,dimensions=dims,priced=len(rows),rows=rows))
 print(json.dumps(dict(event='xor_scan_complete',base=which,directions=len(dims),prices=len(rows),best=choose(rows,current))),flush=True)
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]))

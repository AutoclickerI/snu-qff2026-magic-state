import json
import sys
from pathlib import Path
from evaluate import *

def decomposed():
    text=(HERE/'base.qasm').read_text(); meta=json.loads((HERE/'base.json').read_text())
    model.noise_blocks=ablation(meta,'round')
    ev=exact2.Eval(text,meta['data_qubits']); fast_exact.prepare(ev)
    r=exact2.run(ev,1,keep_thr=0)
    data=set(meta['data_qubits']); pairs={}
    def label(f):
        ch=ev.chan_label(int(ev.fch[f])); qs=set(ch['qubits']); kind=ch['kind']; st=ch['steps']
        if kind=='idle' and qs&data: return 'data idle'
        if kind=='gate2' and qs&data: return 'data CX'
        if kind=='gate2': return 'B-C verification CX'
        if kind=='flip': return 'readout'
        return kind
    for v,i,j,*_ in r['big']:
        k=' x '.join(sorted((label(i),label(j)))); pairs[k]=pairs.get(k,0)+v
    model.noise_blocks=orig
    out={'base_round_pairs':pairs,'data':evaluate('base',True,('data',))}
    (HERE/'diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))

if __name__=='__main__': decomposed()

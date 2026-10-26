"""Seven concrete grid tiles; retain BOTH final native ticks, idealize the preceding state."""
import importlib,json,sys,time
from pathlib import Path
import tail_tests as tt
from tprep.qasm import to_stim
from tprep.exact import verify
from tprep.parse import declarations
from tprep.noise import schedule
import tprep

def main():
    start=time.perf_counter()
    tt.D=[1,7,13,19,25,31,10]
    helpers=[2,8,14,20,26,32,16]
    partners=[0,6,12,18,24,30,4]
    other=[3,9,15,21,27,33,22]
    enc=tt.sequential(tt.encoder())
    prep=tt.layer(tt.preps(helpers+partners+other))
    inverse=tt.layer(tt.cxs(tt.D,partners)+tt.cxs(helpers,other))
    last=tt.layer(tt.cxs(helpers,tt.D)+[f'measure q[{q}] -> c[{k}];' for k,q in enumerate(partners+other)])
    dets='\n'.join(f'// DETECTOR c[{k}]' for k in range(14))+'\n'
    prefix=enc+prep+inverse
    text=tt.HEADER+prefix+inverse+last+dets
    stem=tt.OUT/'experiments/seven_tiles'
    stem.with_suffix('.qasm').write_text(text)
    stem.with_suffix('.json').write_text(json.dumps({'data_qubits':tt.D})+'\n')
    st,errors=to_stim(text);assert not errors,errors
    raw=verify(st,tt.D);assert not raw['errors'],raw
    judge=tprep.check(text,tt.D,p=0,shots=64);assert judge.correct_ok,str(judge)
    ops,_=tt.qs.fa.parse_current(text);native,labels=tt.qs.fa.native_text(ops)
    _,steps,_=schedule(native);tail_line=len((tt.HEADER+prefix).splitlines())+1
    cut=min(steps[i][0][1] for i,o in enumerate(labels) if o.line>=tail_line)
    result=tt.price(text,stem,cut,tt.qs)
    result.update(raw=raw,judge=str(judge),data=tt.D,helpers=helpers,partners=partners+other,
                  seconds=time.perf_counter()-start,scope='Perfect prefix; every native noise channel in the final two ticks, including readout errors, retained')
    (tt.OUT/'experiments/seven_tiles_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()

"""Fix the pre-resource random classical source before data/byproduct fanout."""
import json,sys
from pathlib import Path
from joint import *

def baseline():
    ops,dets=f.parse_current(BASE.with_suffix('.qasm').read_text())
    o=next(o for o in ops if o.bit==366)
    assert (o.kind,o.qs,o.time)==('M',(1,),29)
    o.kind='R';o.bit=None
    dets=[r-{366} for r in dets if r-{366}]
    text=emit(ops,dets)
    return write_stem(text,D,HERE/'cand','v37j_source_zero'),text

if __name__=='__main__':
    stem,text=baseline()
    result={'baseline_stem':str(stem.relative_to(ROOT)),'baseline_raw':raw_check(text,D)}
    sol=json.loads((HERE/'sol/joint_first.json').read_text());sol['source_zero']=True
    st,txt=make(sol,'joint39_source_zero')
    result.update(joint_stem=str(st.relative_to(ROOT)),joint_raw=raw_check(txt,D))
    print(json.dumps(result,indent=2),flush=True)
    if '--price' in sys.argv:
        for name,s,r in [('baseline',stem,result['baseline_raw']),('joint',st,result['joint_raw'])]:
            if r['ok']:
                result[name+'_price']=price(s,1,use_cache=False)
                print(name,json.dumps(result[name+'_price']),flush=True)
    (HERE/'source_fix_result.json').write_text(json.dumps(result,indent=2)+'\n')

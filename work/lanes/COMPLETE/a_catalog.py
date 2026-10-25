"""Release-aware A resynthesis from EXENC's verified 20-encoder library.

The A state is rebuilt on its original physical cells after relocated source
records; correlated r3 is unchanged. Existing A-only gates/initializers and the
three identity A/data guard CXs are replaced, then native scheduling is solved.
"""
import os,sys,json,copy,re
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from build import H,lib,timing
A=[1,14,8,9,2,16,15];D=[0,20,7,10,3,22,21]
BITS={64,12,54,56,67,55,57}
AENC={(37,8,2),(38,2,1),(38,14,8),(39,1,2),(39,9,8),(40,8,2),(40,9,15),(41,8,9),(41,16,15),(42,9,8),(42,15,14),(43,14,8)}
INIT={(36,8),(36,2),(38,9),(38,16)}
GUARD={(40,20,14),(41,20,14),(40,22,16)}
def synth(base,name,enc):
    c=json.loads((H/'builds'/base).with_suffix('.plan.json').read_text());rel={};basis={}
    for o in c['ops']:
        if set(lib.bits_of(o))&BITS:
            q=lib.unit(o).qs[0];rel[q]=o['t'];basis[q]='X' if lib.unit(o).name=='MX' else 'Z'
    assert set(A)==set(rel),(base,rel)
    da={}
    for d,a in zip(D,A):
        line=f'cx q[{d}],q[{a}];'
        da[a]=max(o['t'] for o in c['ops'] if o['lines']==[line])
    rt=min(da.values());removed=[];keep=[]
    for o in c['ops']:
        u=lib.unit(o);qs=set(u.qs)
        nq=list(map(int,re.findall(r'q\[(\d+)\]',o['lines'][0])));nt=o.get('nominal_t',-1)
        hit=(o.get('stage')=='A_extra_init' or (o.get('stage') in ('A_rebind','round') and ((nt,*nq) in AENC|GUARD or u.name in ('RX','RESET') and (nt,nq[0]) in INIT)))
        if hit:removed.append(o)
        else:keep.append(dict(o,fixed=o['t']<=23))
    assert sum(lib.unit(o).name=='CX' and (o.get('nominal_t',-1),*map(int,re.findall(r'q\[(\d+)\]',o['lines'][0]))) in AENC for o in removed)==12
    prefix=[o for o in keep if o.get('nominal_t',-1)<43];tail=[o for o in keep if o.get('nominal_t',-1)>=43]
    first={q:min(i for i,layer in enumerate(enc['ops']) if any(q in e for e in layer)) for q in A}
    t0=rt-len(enc['ops'])
    prep=[]
    for q in A:
        desired='X' if q in enc['pivots'] else 'Z'
        if desired!=basis[q]:prep.append(dict(t=max(rel[q]+1,t0+first[q]-1),lines=[f'reset q[{q}];']+([f'h q[{q}];'] if desired=='X' else [])))
    # Gate order follows the exact state-synthesis witness; the CP solver moves
    # layers independently subject to each cell's actual release and exterior.
    for i,layer in enumerate(enc['ops']):
        for a,b in layer:prep.append(dict(t=t0+i,lines=[f'cx q[{a}],q[{b}];']))
    ops,info=timing(prefix+prep+tail,name,seconds=2)
    c['ops']=ops;c['meta']=dict(data_qubits=D,source=base+'; EXENC A replacement, release-aware timing',
      a_catalog=enc,a_release=rel,removed=removed,timing=info)
    st=lib.save(lib.fix(c),name);return st,info
if __name__=='__main__':
    encs=json.loads((H.parent/'EXENC/prepA_L5_exact_top.json').read_text());out={}
    for base in sys.argv[1:]:
        rows=[]
        for i,enc in enumerate(encs):
            try:
                st,info=synth(base,f'{base}_a{i:02}',enc)
                rows.append(dict(stem=st.name,depth=info['depth'],cx=enc['cx'],proxy=enc['danger']))
            except (AssertionError,ValueError) as e:rows.append(dict(index=i,error=str(e)[:250]))
        out[base]=sorted(rows,key=lambda r:(r.get('depth',999),r.get('proxy',999)))
        print(base,json.dumps(out[base][:3]),flush=True)
    (H/'a_catalog.json').write_text(json.dumps(out,indent=2)+'\n')

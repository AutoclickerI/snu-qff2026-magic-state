"""Exact, non-additive circuit counterfactuals for rebuilt block operation noise."""
import hashlib,json,sys
from pathlib import Path
from qedit import load,QRE
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'sparse'))
import region

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,A,DA,astarts,bc,R):
    stem=H/'builds'/name;c=load(str(stem));records={}
    acells=set(A);bcells={q for ss in bc['ops'] for a,b in ss for q in (a,b)}
    first={q:min(t+bc['T0'] for t,ss in enumerate(bc['ops']) for a,b in ss if q in (a,b)) for q in bcells}
    bstarts={}
    for q,t in first.items():
        opts=[tt for tt,ss in enumerate(c.segs[:t]) for g in ss if set(map(int,QRE.findall(g[0])))=={q} and ('measure' in ' '.join(g) or g[0].startswith('reset'))]
        bstarts[q]=max(opts)
    for key,cells,starts,ends in [('A',acells,astarts,DA),('BC',bcells,bstarts,{q:R for q in bcells})]:
        units=[]
        for t,ss in enumerate(c.segs):
            for g in ss:
                qs=tuple(map(int,QRE.findall(g[0])))
                if set(qs)<=cells and all(starts[q]<=t<ends[q] for q in qs):units.append([t,list(qs)])
        spec=dict(name=name+'_'+key+'_operations_perfect',units=units,gate_only=True)
        sp=H/'layouts'/f'{name}_{key}_perfect.json';sp.write_text(json.dumps(spec,indent=2)+'\n')
        out=region.run(stem,spec,1);out.update(qasm_sha256=sha(stem.with_suffix('.qasm')),spec_sha256=sha(sp),scope='selected operation noise only; idle channels retained; counterfactual differences overlap and are not additive')
        records[key]=out
    f=H/'diagnostics.json';allrec=json.loads(f.read_text()) if f.exists() else {};allrec[sha(stem.with_suffix('.qasm'))]=records;f.write_text(json.dumps(allrec,indent=2)+'\n')

if __name__=='__main__':
    origA=[1,14,8,9,2,16,15];origBC=json.loads((H.parent/'BFLAG/syn/r3.json').read_text())
    run('v36h',origA,{q:43 if q in [9,15] else 44 for q in origA},{1:37,14:37,8:36,9:38,2:36,16:38,15:39},origBC,44)
    for name,label,ae,be in [('r44_a0_h','r44_1','r44_a0',None),('r45_a0_h','r45_2','r45_2_a0','r45_2_bc_s3_reuse_clean'),('r46_a0_h','r46_2','r46_2_a0','r46_2_bc_s1')]:
        lay=json.loads((H/'layouts'/f'{label}.json').read_text());enc=json.loads((H/'enc'/f'{ae}.json').read_text());A=lay['A'];R=lay['R']
        if be:bc=json.loads((H/'enc'/f'{be}.json').read_text())
        else:
            bc=dict(origBC);mp={13:18,19:24};bc['ops']=[[[mp.get(a,a),mp.get(b,b)] for a,b in ss] for ss in origBC['ops']]
        run(name,A,{q:R-1 if i in lay['flagdata'] else R for i,q in enumerate(A)},{q:enc['init'][i][1] for i,q in enumerate(A)},bc,R)

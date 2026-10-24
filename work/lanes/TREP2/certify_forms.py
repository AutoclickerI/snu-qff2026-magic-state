"""Certify stored physical forms without rebuilding or overwriting circuits."""
import os,sys,json,itertools
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT))
import forms
from model import Basis,comm
from exact2 import Eval

if __name__=='__main__':
    fs={f['id']:f for f in json.loads((OUT/'inputs/enumeration.json').read_text())['forms']}
    for stem in sorted(OUT.glob('f*_parity.qasm')):
        meta=json.loads(stem.with_suffix('.json').read_text());form=fs[meta['form']];ops,_=forms.network(form,meta['search_seed']);byq={}
        for op,q,ax in ops:
            if op!='cx':byq.setdefault(q,[]).append(ax)
        ev=Eval(stem.read_text(),meta['data_qubits']);basis=Basis();images=[];observed=[]
        for x,z,c,theta,ii in ev.m.rots:
            q=ev.m.prog[ii].qubits[0];wanted=byq[q].pop(0);coord=basis.express(x)
            if coord is None:basis.add(x);images.append(wanted);coord=basis.express(x)
            actual=0
            for j,img in enumerate(images):
                if coord>>j&1:actual^=img
            assert actual==wanted
            observed.append(actual)
        assert sorted(observed)==form['support']and len(images)==5
        assert all(comm(x,z,v,w)==0 for x,z,*_ in ev.m.rots for v,w,*_ in ev.m.rots)
        c1=float(ev.fp@ev.n_single);assert abs(c1)<1e-12
        tids=[]
        for x,z,c,theta,ii in ev.m.rots:
            hits=[i for i,f in enumerate(ev.m.faults)if f['pauli']=='Z'and ev.m.chans[f['chan']]['ins']==ii and ev.m.chans[f['chan']]['when']=='after'and ev.m.chans[f['chan']]['kind']=='gate1']
            assert len(hits)==1; tids.append(hits[0])
        bad_pairs=[]
        for i,j in itertools.combinations(tids,2):
            aa,nn=ev.e.ntable(ev.fs[i]^ev.fs[j],ev.fd[i]^ev.fd[j]);loss=0 if nn is None else float(nn[ev.fe[i]^ev.fe[j]])
            if abs(loss)>1e-12:bad_pairs.append([i,j,loss])
        assert not bad_pairs
        result=dict(form=form['id'],reference_support=sorted(observed),native_basis_to_reference=images,commuting=True,c1=c1,full_single_fault_protection=True,physical_T_phase_singles_max_loss=float(max(abs(ev.n_single[i])for i in tids)),physical_T_phase_pairs_checked=len(tids)*(len(tids)-1)//2,physical_T_phase_bad_pairs=bad_pairs)
        stem.with_suffix('.phase.json').write_text(json.dumps(result,indent=2)+'\n');print(stem.stem,c1,flush=True)

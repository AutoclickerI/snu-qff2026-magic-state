"""Independent consistency checks on the parity enumeration and rescoring."""
from search import *
import hashlib

def main():
    out={}
    for name,stem in TARGETS.items():
        text=stem.with_suffix('.qasm').read_text()
        data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
        space=parity_space(text)
        (HERE/f'{name}_space.json').write_text(json.dumps(space,indent=2))
        z=np.load(HERE/f'{name}_hist.npz');ds,h=z['ds'],z['h'];pt=float(z['Ptotal'])
        lookup={int(d):i for i,d in enumerate(ds)}
        ev=Eval(text,data)
        errors=[]
        for kernel in ([1],[2,4],[1,4,8],[3,5], [8,16,32,64]):
            span=xor_span(kernel)
            vals=h[[lookup[d] for d in span if d in lookup]].sum(axis=0)
            a1=pt-vals[0];n1=vals[1];loss2=vals[4]-vals[2]+a1*n1
            r=run(rebind(ev,records_for(kernel,space['full_records'])),procs=1)
            err=max(abs(r['loss1']-n1),abs(r['loss2']-loss2),abs(r['A1']-a1))
            assert err<1e-12,(name,kernel,err)
            errors.append(dict(kernel=kernel,max_abs_difference=err))
        out[name]=dict(qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
                       full_dimension=space['full_rank'],frame=ev.m.frame,
                       max_nondeterministic_abs_expectation=space['max_random_abs'],checks=errors)
        print(name,json.dumps(out[name]),flush=True)
        (HERE/'audit.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':
    main()

"""Inventory physical Z axes in the original, common phase basis."""
import os,sys,json,re
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
from model import Model,Basis,masks,CLIFFORD,N_QUBITS
import stim

def inventory(text,data):
    m=Model(text,data);b=Basis()
    for x,z,*_ in m.rots:b.add(x)
    sim=stim.TableauSimulator();sim.set_num_qubits(m.n);wire=list(range(36));nxt=36;out=[]
    used=set()
    for ii,ins in enumerate(m.prog):
        name,qs=ins.name,ins.qubits
        if name in ('M','MX'):
            for q in qs:
                if name=='MX':sim.h(wire[q])
                sim.cx(wire[q],nxt);nxt+=1
                if name=='MX':sim.h(wire[q])
        elif name in ('R','RX'):
            for q in qs:
                wire[q]=nxt;nxt+=1
                if name=='RX':sim.h(wire[q])
        elif name in CLIFFORD:
            if name!='I':sim.do(stim.CircuitInstruction(name,[wire[q] for q in qs]))
        used.update(qs)
        if not qs:continue
        inv=sim.current_inverse_tableau()
        axes=[]
        for q in sorted(used):
            ps=stim.PauliString(m.n);ps[wire[q]]='Z';x,z,c=masks(inv(ps));coord=b.express(x)
            if coord and all((z&v).bit_count()%2==0 for v in b.vecs) and abs(c.imag)<1e-9:
                axes.append(dict(q=q,axis=coord,sign=round(c.real)))
        lab=m.labels[ins.line_no-1]
        out.append(dict(instruction=lab,name=name,qs=list(qs),axes=axes))
    return out

if __name__=='__main__':
    stem=OUT/'v17a';rows=inventory(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'])
    (OUT/'axis_inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('reachable',sorted({x['axis']for row in rows for x in row['axes']}))
    for row in rows:
        if row['name']in ('T','T_DAG','RX') and len(row['axes'])>=7:print(row)

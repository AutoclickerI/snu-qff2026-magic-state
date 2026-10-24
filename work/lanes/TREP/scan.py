"""State-aware CX deletion screen. Every retained circuit is checked by the exact judge model."""
import os,sys,json,re,concurrent.futures
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
from exact2 import Eval
SRC=ROOT/'work/lanes/MAIN/spec/v17a.qasm'
DATA=json.loads(SRC.with_suffix('.json').read_text())['data_qubits']

def job(args):
    i,text=args
    row={'line':i+1}
    try:
        e=Eval(text,DATA)
        row['c1']=float((e.fp*e.n_single).sum());row['valid']=True
        name=f'drop_{i+1:03d}'
        (OUT/(name+'.qasm')).write_text(text)
        (OUT/(name+'.json')).write_text(json.dumps({'data_qubits':DATA,'source':str(SRC),'drop_line':i+1})+'\n')
    except Exception as ex:row.update(valid=False,error=str(ex))
    return row

if __name__=='__main__':
    lines=SRC.read_text().splitlines(); end=next(i for i,s in enumerate(lines) if s=='reset q[10];' and i>180)
    jobs=[(i,'\n'.join(lines[:i]+lines[i+1:])+'\n') for i,s in enumerate(lines[:end]) if s.startswith('cx ')]
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
        rows=[]
        for row in pool.map(job,jobs):rows.append(row);print(json.dumps(row),flush=True)
    (OUT/'deletion_screen.json').write_text(json.dumps(rows,indent=2)+'\n')

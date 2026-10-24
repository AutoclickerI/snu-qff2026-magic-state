import argparse,json
from pathlib import Path
import early_merge
from run_synth import capacity
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def build(path,name,rule):
    p=json.loads(Path(path).read_text());capacity()
    text,data,R,end,status,wall=early_merge.build({'a':json.loads((ROOT/'work/lanes/DR/prepA_L5_s7307.json').read_text()),'bc':p},early_merge.LAYOUTS['L5'],early_merge.MOVES['L5'],workers=1)
    stem=HERE/name
    stem.with_suffix('.qasm').write_text(text)
    stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=data,rule=rule,depth=len(p['ops']),prep_cx=sum(map(len,p['ops'])),R=R,wait_steps=R-end,pre_end=end,solver=status,solver_wall=wall,prep=str(path)),indent=2))
    print(name,'R',R,'wait',R-end,'CX',sum(map(len,p['ops'])),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('prep');ap.add_argument('name');ap.add_argument('--rule',default='clean');a=ap.parse_args();build(a.prep,a.name,a.rule)

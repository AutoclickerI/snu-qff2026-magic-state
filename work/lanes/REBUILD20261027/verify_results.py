"""Reprice saved structural candidates with the unmodified pinned evaluator.

Abstract results are explicitly labeled and bypass adjacency only in an
isolated process-local context. They never enter the grid-valid price cache.
"""
import hashlib, importlib.metadata, json, os, sys, time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'work/tools'))
from qtools import price
from qtools.version import EVALUATOR_VERSION
from qtools.evaluator.frontend import parse_current
HERE=Path(__file__).resolve().parent

CASES={
 'baseline_v37j':('work/lanes/MAIN/v37j','grid'),
 'compact_rank5':('work/lanes/PREFIX20261027/cand/final_phase_random_1','grid'),
 'b_output_teleport':('work/lanes/FRAME20261027/cand/btele_fresh','frame'),
 'joint_flags_abstract':('work/lanes/NATIVE20261027/builds/abstract_joint_flags_R18_cat2time12_b53b04680ced76f0_d0_1_2_3_4_5_6','abstract'),
 'joint_flags_native':('work/lanes/NATIVE20261027/builds/native_joint_flags_seed612_76bdd20283aa9a22_d16_32_34_2_4_30_14','grid'),
}

def evaluate(name):
    rel,kind=CASES[name];stem=REPO/rel;text=stem.with_suffix('.qasm').read_text()
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops,_=parse_current(text)
    if kind=='frame':
        sys.path.insert(0,str(REPO/'work/lanes/FRAME20261027'))
        import frame_tools
        result=frame_tools.price(stem)
    elif kind=='abstract':
        from qtools.pricing import _calculate
        import tprep.qasm as jq
        old=jq.adjacent
        try:
            jq.adjacent=lambda a,b:a!=b
            result=_calculate(text.encode(),data,1,save_basis=False)
        finally:jq.adjacent=old
    else:result=price(stem,1,use_cache=False)
    return dict(name=name,stem=rel,scope=kind,grid_valid=kind!='abstract',
        qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),data_qubits=data,
        cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1,
        t_gates=sum(o.kind in ('T','TDG') for o in ops),evaluator_version=EVALUATOR_VERSION,
        source_commit='020cd0364b8f75d167ca203fd9e615ea100c9bf8',
        judge_commit='76fe47c0324f1c1f8b72a7d55af200e88043b522',
        dependencies={p:importlib.metadata.version(p) for p in ('numpy','scipy','stim','xtim','qiskit','ortools','numba','tprep')},
        result=result)

if __name__=='__main__':
    name=sys.argv[1]
    out=evaluate(name)
    target=HERE/'evidence'/('verified_'+name+'.json')
    target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

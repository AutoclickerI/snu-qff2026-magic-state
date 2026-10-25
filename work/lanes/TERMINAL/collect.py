"""Reviewable receipts keyed by QASM hash, with multiple noise scopes per hash."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    results={}
    for p in sorted((H/'builds').glob('*.qasm')):
        key=sha(p);r=results.setdefault(key,dict(qasm_sha256=key,files=[],assessments=[]))
        meta=json.loads(p.with_suffix('.json').read_text())
        r['files'].append(dict(qasm=str(p.relative_to(H)),metadata=str(p.with_suffix('.json').relative_to(H)),
                              metadata_sha256=sha(p.with_suffix('.json'))))
        receipt=H/'logs'/f'{p.stem}.receipt.json'
        if receipt.exists():
            price=json.loads(receipt.read_text());assert price['sha256']==key
            r['assessments'].append(dict(name=p.stem,kind='exact_all_orders_numerical',noise_scope=meta,
                L=price['loss'],A=price['acceptance'],single_fault_loss=price['single_fault_loss'],
                first_order='pass' if price['single_fault_loss']<1e-12 else 'fail',
                full_build=p.stem=='v37b',receipt=str(receipt.relative_to(H)),
                kernel_omission_bound=price['evaluator']['conditional_loss_kernel_omission_bound']))
    # b has the same relative schedule and every record as a: the same QASM
    # hash is the exact channel identity, not a separate numerical estimate.
    for r in results.values():
        aliases=[f['qasm'] for f in r['files'] if Path(f['qasm']).stem.startswith('b_')]
        if aliases:r['schedule_identity_b_equals_a']=aliases
    bounds=json.loads((H/'logs/wait_bounds.json').read_text());two=next(x for x in bounds if x['idle_ticks']==2)
    for name,scan in [('c_coherent','c_onehot'),('c_coherent_rccx','c_onehot_rccx'),('d_linear_frame','d_or_duplicate')]:
        p=H/'builds'/f'{name}.qasm';r=results[sha(p)];s=json.loads((H/'logs'/f'{scan}.scan.json').read_text())
        wb=next(x for x in bounds if x.get('witness')==scan)
        r['assessments'].append(dict(name=name,kind='mechanism_exclusion',L=None,A=1. if name.startswith('c_') else None,
            independent_wait_relaxation=wb,minimal_two_tick_relaxation=two,
            lookup_single_fault_scan=s,first_order='fail' if name.startswith('c_') else 'tail passes by lookup scan and external-fault partition; actual extraction not audited',
            actual_noisy_tail_A='not evaluated; exclusion independent of acceptance',
            grid='not advanced: wait lower bound exceeds gate',full_build=False))
    grid=json.loads((H/'logs/grid_test.json').read_text())
    for name in ('ab_checkedA_cut8','ab_checkedC_cut8'):
        r=results[sha(H/'builds'/f'{name}.qasm')]
        r['grid_tests']=grid;r['full_build']='none: all tested layouts infeasible, even under contact relaxation'
    (H/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    (H/'manifest.json').write_text(json.dumps(dict(files={str(p.relative_to(H)):sha(p) for p in sorted(H.rglob('*'))
        if p.is_file() and p.suffix in ('.py','.qasm','.json','.md') and p.name!='manifest.json' and '__pycache__' not in p.parts},
        computation_host='hippo',maximum_python_processes_in_lane=4,threads_per_worker=1,
        submissions=0,commits=0,pushes=0),indent=2)+'\n')
    print(json.dumps(dict(unique_qasms=len(results),files=sum(len(r['files']) for r in results.values()),
                         exact_prices=sum(sum(a['kind']=='exact_all_orders_numerical' for a in r['assessments']) for r in results.values()))))

if __name__=='__main__':main()

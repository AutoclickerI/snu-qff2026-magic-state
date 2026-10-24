"""Collect completed all-orders and official receipts without rerunning tests."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
names=['v32p_control','v32p_a_decode','v32p_a_decode_remove_z6','v32p_a_decode_remove_z26','v32p_a_decode_budget_c']
rows=[]
for name in names:
    meta=json.loads((HERE/(name+'.json')).read_text())
    result=json.loads((HERE/(name+'_canonical_sparse_result.json')).read_text())
    assert len(result['results'])==73
    meta['independent_all_orders']={k:result[k]for k in['loss','acceptance','conditional_loss_kernel_omission_bound']}
    meta['independent_all_orders']['scope']='Independent all73moments/allnoiseorders atSTANDARDp=.001; cutoffboundexcludesroundoff.'
    row=dict(name=name,loss=result['loss'],acceptance=result['acceptance'],CX=meta['CX'],depth=meta['native_depth'],
             qasm_sha256=hashlib.sha256((HERE/(name+'.qasm')).read_bytes()).hexdigest(),receipt=name+'_canonical_sparse_result.json')
    official=HERE/(name+'.official_1000000_0.json')
    if official.exists():
        off=json.loads(official.read_text())
        v={k:off[k]for k in['shots','seed','gates','check_seconds','official_commit']}
        v.update({k:off['report'][k]for k in['score','sem','acceptance','frame']})
        v['receipt']=official.name;row['official_1m']=v
        meta.update(official_class_tested=True,official_runtime_tested=True,official_format_tested=True,
                    official_correctness_tested=True,official_acceptance_tested=True,official_validation=v)
    (HERE/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
    rows.append(row)
source=json.loads((ROOT/'quantumn_review7/work/lanes/MAIN/sparse/v32p_canonical_sparse_result.json').read_text())
best=rows[-1];base=rows[0]
out=dict(source_commit='f843cb2a2a7e23e53cb2ba54b891d42943bfedfe',models=rows,
         recommended_candidate=best['name'],baseline_reproduced_exactly=base['loss']==source['loss'],
         loss_reduction_percent=100*(base['loss']-best['loss'])/base['loss'],
         improvement_over_previous_fast_percent=100*(4.9485457947061475e-5-best['loss'])/4.9485457947061475e-5,
         scope='Model ranking uses completedallorders; official1m isvalidity/runtimeonly. Thislane didnotrun1e8.')
(HERE/'results_summary.json').write_text(json.dumps(out,indent=2)+'\n')
target=dict(qasm='audit/review7_architecture/'+best['name']+'.qasm',data_qubits=[0,20,7,10,3,22,21],
            qasm_sha256=best['qasm_sha256'],requested_shots=1000000,requested_seed=0)
(HERE/'target.json').write_text(json.dumps(target,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k!='models'},indent=2))

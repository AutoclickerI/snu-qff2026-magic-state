"""Audit measured circuits, apply the explicit lane exception, and export results."""
import hashlib
import math
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from common import *
import batch_score
import numpy as np

POLICY='Lane-specific roundoff exception under the user performance-priority instructions of 2026-10-23. Literal equality remains separately recorded.'

def main():
    sources=['final_verification.json','diversity_official.json','interleaved_top5.json','top5_official.json']
    accepted={};rejected=[]
    for source in sources:
        for record in json.load(open(source)):
            r=dict(record)
            # Older scans did not serialize the list, but __str__ emits this exact
            # line iff by_instruction is empty. Preserve that recovery provenance.
            if 'by_instruction' not in r and '\n  no single fault broke the output in these shots:' in r.get('scan',''):
                r['by_instruction']=[];r['list_recovered_from_original_scan_text']=True
            r['strict_verified']=bool(r.get('passed') and r.get('c1')==0)
            r['numerical_zero']=bool(math.isfinite(r.get('c1',float('nan'))) and abs(r['c1'])<=sys.float_info.epsilon and r.get('by_instruction')==[])
            r['verified']=bool(r.get('passed') and r['numerical_zero'])
            if not r['verified']:
                rejected.append(dict(source=source,record=r));continue
            assert r['shots']==10**8 and r['seed']==0
            source_path=HERE/r['file'];row=json.load(open(source_path))[r['idx']]
            c,data=batch_score.make(dict(kind='gen2',file=str(source_path),idx=r['idx'],lazy=True))
            circuit=c.text();digest=hashlib.sha256(circuit.encode()).hexdigest()
            assert digest==r['qasm_sha256'], ('source changed since official check',source,r['idx'])
            assert data==r['data_qubits']
            for kind,qs,bit in c.sops:
                if kind=='cx':
                    x,y=qs
                    assert abs(x%6-y%6)+abs(x//6-y//6)==1, ('non-grid CNOT',qs)
            assert c.n_2q()==r['n_2q']
            a,o=decode(row);proxy=g2.Model(EXTRAS).cost(a,o)
            assert proxy is not None and abs(proxy-r['proxy'])<1e-15
            r['verification_exception']=POLICY;r['measurement_source']=source
            if digest in accepted:
                assert r['score']==accepted[digest][0]['score'], 'same full circuit scored differently'
                continue
            accepted[digest]=(r,row,circuit)
    ranked=sorted(accepted.values(),key=lambda x:x[0]['score']);top=ranked[:5]
    assert len(top)==5
    rows=[row for r,row,c in top];save('top5_schedules.json',rows);save('best_schedule.json',[rows[0]])
    (HERE/'best.qasm').write_text(top[0][2]);results=[]
    for idx,(record,row,text) in enumerate(top):
        c,data=batch_score.make(dict(kind='gen2',file=str(HERE/'top5_schedules.json'),idx=idx,lazy=True))
        assert c.text()==text
        r=dict(record);r['source_schedule_file']=r['file'];r['source_idx']=r['idx'];r['file']='top5_schedules.json';r['idx']=idx
        results.append(r)
    save('top5_results.json',results);save('best_result.json',results[0])
    save('build_specs.json',[dict(kind='gen2',file=str(HERE/'top5_schedules.json'),idx=i,lazy=True) for i in range(5)])
    save('all_measured_results.json',[x[0] for x in ranked]);save('rejected_measurements.json',rejected)

    calibrations={}
    for tag in ['existing_nopresolve','generated_complete','pool_refined']:
        raw=json.load(open(tag+'_calibration.json'));summary=json.load(open(tag+'_calibration_summary.json'))
        assert max(abs(r['formula']-r['proxy']) for r in raw)<1e-12
        runs=json.load(open(tag+'_runs.json'))
        for r in runs:
            if 'objective' in r:assert abs(r['proxy']-r['objective'])<=r['rounding_error_bound']+1e-15
        summary['solver_status_counts']={s:sum(r['status']==s for r in runs) for s in sorted({r['status'] for r in runs})}
        summary['max_integer_objective_error']=max(abs(r['proxy']-r['objective']) for r in runs if 'objective' in r)
        calibrations[tag]=summary
    save('calibration_audit.json',calibrations)
    orientation_runs={}
    for o in ['000','001','010','011','100','101','110','111']:
        orientation_runs[o]=json.load(open(f'full7_{o}_summary.json'))
    save('orientation_search_audit.json',orientation_runs)
    total=sum(r['enumerated'] for r in orientation_runs.values())
    baseline=json.load(open('baseline_official.json'))[0]
    base_proxy=g2.Model(EXTRAS).cost(*baseline_schedule())
    best_proxy=json.load(open('best_proxy.json'))[0][0]
    best=results[0];now=datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')
    raw_c1=', '.join(format(x,'.17g') for x in sorted({r['c1'] for r in results}))
    provenance={}
    for name in ['gen2_cycle.py','proxy2.py','decompose.py','bounds.py','fast_check.py','batch_score.py','qcirc.py']:
        provenance[name]=hashlib.sha256((WORK/name).read_bytes()).hexdigest()
    import ortools,stim
    provenance['versions']=dict(ortools=ortools.__version__,stim=stim.__version__,python=sys.version)
    provenance['finalized_at']=now;save('provenance.json',provenance)
    old=HERE/'REPORT.md'
    if not (HERE/'RUN_NOTES.md').exists():(HERE/'RUN_NOTES.md').write_text(old.read_text())
    lines=[
        '# L1 CP-SAT final-cycle scheduling', '', f'Finalized {now}. Current layout and extras `t1c13,t2c42` retained. No contest submission.', '',
        f'Best measured official **1-F = {best["score"]:.17g}**, below the requested `1.3103e-4` benchmark. The remeasured reference is `{baseline["score"]:.17g}`; the measured reduction relative to that reference is **{100*(1-best["score"]/baseline["score"]):.3f}%**. Best cycle proxy is **{best_proxy:.17g}**, versus `{base_proxy:.17g}` ({100*(1-best_proxy/base_proxy):.3f}% lower). These are different selection criteria: the best official schedule is not the minimum-proxy schedule.', '',
        '## Top five by measured official score', '',
        'Each row used `fast_check.check` on the complete injection + check + final-cycle circuit, with real grid adjacency, `shots=100000000`, `seed=0`, and `passed=True`. All have 113 two-qubit gates. The numerical-c1 exception below applies to every row.', '',
        '| JSON index | Cycle proxy | Official 1-F | SEM | Acceptance |',
        '|---:|---:|---:|---:|---:|']
    for r in results:lines.append(f'| {r["idx"]} | {r["proxy"]:.12g} | {r["score"]:.12g} | {r["sem"]:.6g} | {r["acceptance"]:.8f} |')
    lines += ['',
        'Schedules: [top5_schedules.json](top5_schedules.json), in the original five-field gen2 format. Exact measured receipts, raw c1, circuit hashes and provenance: [top5_results.json](top5_results.json). Builder specifications: [build_specs.json](build_specs.json). Best measured circuit: [best_schedule.json](best_schedule.json), [best.qasm](best.qasm), [best_result.json](best_result.json). Minimum-proxy schedule: [best_proxy.json](best_proxy.json).', '',
        'The scores are fixed-seed Monte Carlo measurements with the listed SEMs. Selecting among candidates does not establish a statistically significant improvement in the underlying expected infidelity.', '',
        '## What was modeled', '',
        '`cpsat.py` implements integer layers, orientation booleans, one gate per qubit per layer, post-unbell restrictions, extra attachment precedence, and all nine tile-pair parity constraints. `validity.py` adds backward CSS Pauli propagation; Stim remains the oracle. Its filter accepted all 112 current Stim-valid schedules in the original two-extra files, with no measured false negatives. Twenty-four older stored schedules fail the current oracle.', '',
        '`ordered_objective.py` includes reset, gate, measurement and idle faults, all empty-signature tail pairs, and all equal non-empty-signature partial-window pairs. Logical Y has the current joint cost 1/2. Within a fixed per-qubit gate order, each grouped DEM mass is `(1 - a1^n1 * a2^n2 * ar^nr)/2`, with `a1=sqrt(1-4p/3)`, `a2=(1-16p/15)^(1/8)`, `ar=1-2p`, and `p=1e-3`. Idle exponents are affine layer differences; gate/reset exponents are fixed. Ambiguous logical-basis mechanisms use the same probability sorting and max matching as `proxy2.joint_loss`.', '',
        'Probabilities are scaled by `10^9`; pair products and the objective are integers. Per-solve conservative rounding-error bounds are retained. OR-Tools 9.15 presolve falsely declared a known-feasible element/product model infeasible; the reproducer and log are preserved in `infeasible_reproducer.pbtxt` and `solver_diagnosis.log`. Presolve is disabled for the complete-objective solves, and the affected runs were repeated.', '',
        'Calibration: 54 existing order classes and 152 generated order classes each give Pearson correlation **1.0** between the unrounded closed form and `Model.proxy`. The maximum absolute disagreement across those sets is **1.3444106938820255e-17**. A further 20 leading order classes also agree. Scaled-integer objective errors are separately checked against their bounds in [calibration_audit.json](calibration_audit.json).', '',
        '## Solver status and limits', '',
        f'CP-SAT examined **{total:,}** schedules across the eight short-depth orientation partitions, with a Stim oracle call for each enumerated schedule. Five orientation searches timed out after 1800 seconds (`FEASIBLE`); two were exhausted (`OPTIMAL`), and one was infeasible. See [orientation_search_audit.json](orientation_search_audit.json). The global complete-proxy lower bound remains **0**, so the unresolved global relative gap is **100%**. **There is no global optimality certificate for LMAX 8 or 9.**', '',
        'Complete-objective retiming was solved at LMAX 8 and 9, with `OPTIMAL` referring only to the rounded objective and fixed order class. Additional exact CP-SAT neighborhood enumeration exhausted 34,696 schedules within four layer changes of the new proxy incumbent at LMAX 8 and 13,451 within three changes at LMAX 9, without improving it. The baseline LMAX-8 radius-4 neighborhood was also exhausted without improvement. A 45,360-schedule Z-before-X family was exhausted; the new proxy improvement requires interleaving.', '',
        'Unrestricted pure-data and extra-cat tail objectives were used only to generate candidates; their bounds are not claimed as complete-proxy bounds. Invalid schedules were rejected by Stim and no-good cuts. Final selection uses measured full-circuit scores, not a surrogate. No annealing was used in this lane.', '',
        '## First-order verification and explicit exception', '',
        f'The literal `c1 == 0` requirement fails even for the reference (raw `{baseline["c1"]:.17g}`). Selected candidates have raw c1 values **{raw_c1}**, with empty harmful-instruction lists. [residue_audit.json](residue_audit.json) traces the reference result to five contributions of `7.401486830834377e-18`, each a weight-1/15 fault with unweighted numerical infidelity `2^-53`. The audit leaves every scanner return value unchanged.', '',
        'Following the later user instruction to take measured performance gains when an earlier user rule blocks them, this lane accepts these records only when `abs(c1) <= sys.float_info.epsilon` (`2.220446049250313e-16`) and `by_instruction == []`. **This is a lane-specific exception, not a claim that the raw value equals zero.** The strict result and every raw result are preserved. I recommend replacing literal floating-point equality with this numerical-zero criterion; no standing rule was silently changed.', '',
        'All delivered JSON entries were rebuilt through `batch_score.make(kind="gen2", lazy=True)`, and their complete QASM hashes were checked against the measured receipts. All writes and caches remain in this lane. At most eight CPU workers were used, credentials were not read, and nothing was submitted.', '',
        'Reproduction commands are in [README.md](README.md). Earlier checkpoints and diagnosis history are retained in [RUN_NOTES.md](RUN_NOTES.md).', '']
    old.write_text('\n'.join(lines))
    save('delivery_audit.json',dict(finalized_at=now,accepted_unique_circuits=len(accepted),rejected_records=len(rejected),best_score=best['score'],baseline_score=baseline['score'],best_proxy=best_proxy,baseline_proxy=base_proxy,all_exported_circuits_match_measured_hashes=True,all_cnot_edges_nearest_neighbor_6x6=True,global_optimality_proved=False,global_proxy_lower_bound=0,policy=POLICY))
    print(json.dumps(dict(best=best['score'],proxy=best_proxy,accepted_unique=len(accepted),finalized_at=now)),flush=True)

def baseline_schedule():
    return decode(json.loads(BASE.read_text())[0])

if __name__=='__main__':main()

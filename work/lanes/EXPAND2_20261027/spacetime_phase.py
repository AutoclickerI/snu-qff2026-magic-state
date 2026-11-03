"""Generate two-pulse S identities on repeated B/C computational parities.

The pulses may occupy different clocks and different wires. A fixed ideal
computational parity acquires opposite quarter-turn phases at its two visits.
All generated circuits still require independent official raw-state replay;
the support certificate alone does not establish noisy performance.
"""
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
INVENTORY=ROOT/'work/lanes/END2_20261027/incumbent_b_affine_support_columns.json'


def main():
    inventory=json.loads(INVENTORY.read_text())
    module=json.loads((ROOT/inventory['b_module']).read_text())
    operations=module['candidates'][0]['operations']
    # After the last reset, the module contains only CX and Z measurements.
    # X-record phases already in the input are arbitrary; they do not change
    # its computational support. Later source couplings are covered by the
    # independent complete-circuit raw check before any noisy audit.
    start=1+max(o['time'] for o in operations if o['kind'] not in ('CX','M'))
    groups={}
    for snapshot in inventory['snapshots']:
        if not start<=snapshot['time']<=45:
            continue
        for q in snapshot['idle']:
            column=snapshot['raw_columns'][str(q)]
            if column:
                groups.setdefault(column,[]).append((snapshot['time'],q))
    candidates=[]
    for column,slots in sorted(groups.items()):
        for first,last in itertools.combinations(slots,2):
            if first[0]==last[0]:
                continue # Already included in the completed single-clock screen.
            for reverse in (False,True):
                kinds=('S','SDG') if reverse else ('SDG','S')
                name=f'spacetime_c{column}_t{first[0]}q{first[1]}_t{last[0]}q{last[1]}_r{int(reverse)}'
                candidates.append(dict(name=name,operations=[
                    dict(kind=kind,qs=[q],time=t)
                    for kind,(t,q) in zip(kinds,(first,last))],
                    fixed_record_contract=True,
                    proof=dict(raw_column=column,first_slot=list(first),last_slot=list(last),
                        support_source=str(INVENTORY),
                        phase_polynomial='-parity(column & u) + parity(column & u) == 0 mod 4',
                        scope='CX/MZ-only module after its last reset; complete literal-circuit raw replay is mandatory.'),
                    noise_scope='Real native S/Sdg pulses in active idle slots. All original operations, measurements, detectors and clocks retained.'))
    result=dict(base=inventory['full_stem'],baseline_sha256=inventory['full_qasm_sha256'],
        inventory_sha256=hashlib.sha256(INVENTORY.read_bytes()).hexdigest(),
        start=start,end=45,groups=groups,candidates=candidates,
        scope='All opposite-sign repeated nonzero support-column pairs at distinct clocks in the certified post-reset B/C interval; both signs retained. No same-clock pairs or zero columns.')
    path=HERE/'spacetime_phase_candidates.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(path=str(path),candidates=len(candidates),start=start,groups=groups)))


if __name__=='__main__':main()

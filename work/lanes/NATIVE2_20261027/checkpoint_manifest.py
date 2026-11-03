"""Select reproducible native architecture code, witnesses, and receipts."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
files=set(HERE.glob('*.py'))|{HERE/'REPORT.md'}
names=['linear_magic_d6_s2.json','linear_magic_d8_s1.json','linear_cat_d8_s1.json','hybrid_d10_m4_s1.json',
    'clifford_frontend_verification.json','prefix_release.json','prefix_product_states.json',
    'contracted105_product_states.json','a_factory_search.json','a_orientation.json','a_factory_contracted105.json',
    'old_b_module.json','old_a_instrument.json','old_b_instrument_module.json',
    'old_footprint_a_s1.json','compact_a_modes_instrument48.json','compact_a_weak_instrument48.json',
    'record_contract_control.json','record_contract_filtered_control.json','record_contract_modes_control.json',
    'discarded_mz_h_probe.json','a_measured.json','a_measured_pairs_fixed.json']
files.update(HERE/n for n in names)
files.update(HERE.glob('*.result.json'))
for pattern in ('*_module.json','dual_old_a_module*.json','q15_early39_*.json',
                '*.pairs.json','*probe_result.json'):
    files.update(HERE.glob(pattern))
files.update(p for p in (HERE/'boundary').glob('*') if p.suffix in ('.qasm','.json'))
prefixes=[
    'separate_w2_full_pcXZ_reuse_jit_linear_magic_d6_s2_d66d',
    'separate_w2_full_pcZ_reuse_jit_linear_magic_d6_s2_072a',
    'separate_w2_full_pcY_reuse_jit_linear_magic_d6_s2_1bd9',
    'separate_w2_full_pcZ_reuse_jit_linear_magic_d6_s2_phase4_b3f0',
    'separate_w2_full_pcZ_reuse_a0fb',
    'coherent_fresh_w2_flag1_eaed',
    'coherent_old_w1_flag1_b26b',
    'late_w1_two_ea30','late_w1_none_c5ea',
    'hybrid_early_flag5_5cb8','growth_flag13_c88b',
    'joint_end_separate_w2_full_pcZ_reuse_a0fb',
    'joint_end_separate_w2_full_pcZ_reuse_jit_linear_magic_d6_s2_072a',
    'separate_w2_full_pcZ_reuse_jit_linear_magic_d6_s2_partialX2_',
    'separate_w2_full_pcY_reuse_jit_linear_magic_d6_s2_partialZ2_',
    'separate_w3_full_pcZ_reuse_1933']
for prefix in prefixes:files.update(p for p in (HERE/'cand').glob(prefix+'*') if p.suffix in ('.qasm','.json'))
rows=[]
for p in sorted(files):
    assert p.is_file(),p
    data=p.read_bytes();rows.append(dict(path=str(p.relative_to(ROOT)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(HERE/'selected_files.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),manifest=str((HERE/'selected_files.json').relative_to(ROOT)))))

import json,hashlib
from pathlib import Path
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028'
groups={
 'report':['REPORT.md','publish_manifest.py'],
 'reproduction_code':['direct_parity.py','joint_search.py','joint_gauge.py','joint_pivot17.py','screen.py','singles.py','price.py','joint_remove.py','random_joint.py','price_joint.py','price_random.py','resource_pairs.py','resource_risk.py','resource_reset_heralds.py','resource_reset_late.py','reuse_reset17.py','construct_four.py','assemble_four.py','connected_bc.py','connected_module.py','connected_diagnostic.py','connected_faults.py','sym4_measured.py','sym4_module.py','seven_relaxed.py','seven_joint_module.py','six_joint_measured.py','six_joint_module.py','six_construct_css.py','five_joint_measured.py','five_joint_module.py','preserve_b_geometry.py','five_headroom.py','five_headroom_early.py','assemble_geometry.py','spider_graph.py','spider85_map.py','prefix_known_axes.json','six_source_release.json'],
 'solver_status':['sol/resynth_safe.json','sol/pivot17.json','sol/gauge102_safe.json','sol/gauge102_soft.json','sol/bridged_state_d32.json','sol/connected_state_d20.json','sol/connected_risk_d20.json','sol/sym4_measured_d22.json','sol/six_joint_d23.json','sol/six_joint_known_d23.json','sol/five_joint_d22.json','sol/five_joint_d24.json'],
 'ledgers':['direct_parity.receipt.json','screen.json','singles.json','joint.log','resource_pairs.json','resource_fault_pairs.json','resource_ablations.json','connected_state_d20_module.json','connected_state_d20_diagnostic_result.json','connected_state_d20_faults.json','connected_herald_module.json','connected_herald_diagnostic_result.json','preserve_b_geometry.json','spider_graph.json','spider85_map.json','five_partial_3d_compensated.diagnostic.json','five_early_partial_3d_compensated.diagnostic.json','lateherald_17_11_23.receipt.json'],
 'selected_circuits':[]}
for prefix in ['direct_parity_99ce73d2594d76fc','resynth_safe_ed3fedc445723242','pivot17_6d42b4bca21f650e','gauge102_safe_bc182b58aef1a5d1','gauge102_soft_debd2481fcaca113','lateherald_17_11_23_65cbd37412fd2af5']:
 for suffix in ('.qasm','.json'):
  paths=list((H/'cand').glob(prefix+'*'+suffix));assert len(paths)==1,(prefix,suffix,paths);groups['selected_circuits'].append(str(paths[0].relative_to(H)))
groups['selected_circuits'] += ['joint_0.qasm','joint_0.json','joint_0.exact.json']
groups['counterfactual_artifacts']=['five_partial_3d_compensated.qasm','five_partial_3d_compensated.json','five_early_partial_3d_compensated.qasm','five_early_partial_3d_compensated.json']
for suffix in ('.qasm','.json','.result.json'):
 paths=list((H/'geometry_cand').glob('six_measured_baseline_*'+suffix));paths=[p for p in paths if suffix!='.json' or not p.name.endswith('.result.json')];assert len(paths)==1,(suffix,paths);groups['selected_circuits'].append(str(paths[0].relative_to(H)))
entries=[]
for category,paths in groups.items():
 for name in paths:
  p=H/name;assert p.is_file(),p;b=p.read_bytes();entries.append({'category':category,'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
external=[]
for suffix in ('.qasm','.json','.result.json'):
 p=R/('work/lanes/SOTA_20261028/geometry_cand/seven_measured_baseline_cc15a1ad0db415a2_d11_22_28_1_2_25_13'+suffix);assert p.is_file();b=p.read_bytes();external.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
out={'scope':'Selected reproducible checkpoint; excludes bulk generated candidates and lock/cache files. Prior-lane code and pinned qtools/judge remain dependencies.','entries':entries,'external_complete_baseline':external}
(H/'publish_manifest.json').write_text(json.dumps(out,indent=2)+'\n');print('manifest entries',len(entries),'external baseline',len(external))

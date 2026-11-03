"""Create the selective lane publication manifest (does not publish)."""
import hashlib,json,glob
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
patterns=[
 'REPORT.md','REPRODUCE.md','HEADROOM.md','TELEPORT.md','make_manifest.py','teleport_probe.py','teleport/source_to_fresh_plus.qasm','teleport/source_to_fresh_plus.json','teleport/source_to_fresh_plus.result.json','gauge_frames.py','gauge_frames.json',
 'unmoved_six_headroom.py','seven_headroom.py','unmoved_six_headroom_results.json','seven_headroom_results.json','unmoved_six_*.release.json',
 'tile_route.py','tile_route_six.py','reflected_route.py','reflected_route_early.py','reflected_six.py','reflected_seven.py',
 'source_symmetries.py','source_symmetries.compact.json','geometry_labeled.py','geometry_labeled_sym4.json','geometry_labeled_sym0.json',
 'geometry_highsquare.py','geometry_highsquare_6.json','geometry_highsquare_7.json','geometry_both_borrow.py','geometry_both_borrow_6.json','geometry_both_borrow_7.json','geometry_both_borrow_6_opt.json','geometry_both_borrow_7_opt.json','geometry_connectedbc.py','geometry_connectedbc_4.json','fixed_d_helpers.py','fixed_d_helpers_result.json',
 'gao/build.py','gao/parallel.py','gao/retime.py','gao/gao_abstract_*.qasm','gao/gao_abstract_*.json','gao/tight_pairs.min.json','gao/late_pairs.min.json',
 'diagnostic/unmoved_six_original_tail41.qasm','diagnostic/unmoved_six_original_tail44.qasm','diagnostic/seven_original_tail44.qasm','diagnostic/seven_contracted_tail44.qasm','diagnostic/unmoved_six_*.json','diagnostic/seven_*.json',
 'tile_boundary/reflected_source_early_*.qasm','tile_boundary/reflected_source_early_*.json','tile_boundary/seven_source_*.qasm','tile_boundary/seven_source_*.json','tile_boundary/six_source_*.qasm','tile_boundary/six_source_*.json',
 'combine_z.py','zmax.py','temporal_zdynamic.py','combine_z_results.json','zmax_results.json','temporal_zdynamic_results.json',
 'cand/zech_3_4_2_22.qasm','cand/zech_3_4_2_22.json','cand/zmax_10_11_4_17.qasm','cand/zmax_10_11_4_17.json',
 'cand/combo_1_0_8_22_14_20_19_22_16_22_4_9_16_22_12_17.qasm','cand/combo_1_0_8_22_14_20_19_22_16_22_4_9_16_22_12_17.json']
files=sorted({Path(p) for pat in patterns for p in glob.glob(str(H/pat)) if Path(p).is_file()})
deps=[
 'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.qasm',
 'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.json',
 'work/lanes/PREFIX2_20261027/retimed/source_aligned_f4c43ebcb17bfa49_d6_20_19_10_2_22_16.qasm',
 'work/lanes/PREFIX2_20261027/retimed/source_aligned_f4c43ebcb17bfa49_d6_20_19_10_2_22_16.json',
 'work/lanes/PREFIX2_20261027/cand/dynamic11_schedule_e0_d1.qasm','work/lanes/PREFIX2_20261027/cand/dynamic11_schedule_e0_d1.json',
 'work/lanes/PREFIX2_20261027/pairs.py','work/lanes/FRAME20261027/frame_tools.py','work/lanes/STRATEGY_CROSS_20261027/reuse_final.py','work/lanes/STRATEGY_CROSS_20261027/cross.py','work/lanes/CAT3_20261027/multicat.py','work/lanes/PREFIX20261027/search_phase.py','work/lanes/T14/qcirc.py',
 'work/lanes/END2_20261027/joint.py','work/lanes/END2_20261027/partial_square.py','work/lanes/END2_20261027/partial_incumbent.py',
 'work/lanes/REBUILD20261027/record_contract.py','work/lanes/CAT3_20261027/smallcat.py','work/lanes/SOTA_20261028/tile_geometry.py',
 'work/tools/qtools/evaluator/frontend.py','work/tools/qtools/evaluator/sparse_walsh.py','work/tools/qtools/evaluator/judge_subset/noise.py','work/tools/qtools/version.py']
def entry(p):
 p=Path(p);assert p.is_file(),p;b=p.read_bytes();return dict(path=str(p.relative_to(R)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
out=dict(scope='Selective research handoff; no publication performed.',selected_files=[entry(p)for p in files],repository_dependencies=[entry(R/p)for p in deps],
 total_selected_bytes=sum(p.stat().st_size for p in files),python='3.12.14',numpy='2.3.5',stim='1.16.0',ortools='9.15.6755',qiskit='2.5.2',xtim='3.1.3+qff2',
 evaluator_version='94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f',
 primary_sources=[dict(url='https://arxiv.org/html/2603.05429v2',version='v2, 2026-09-29',license='arXiv perpetual non-exclusive license'),dict(url='https://arxiv.org/html/2609.12698v1',version='v1, 2026-09-11',license='arXiv perpetual non-exclusive license'),dict(url='https://github.com/IBM/gauging_clifford_measurement',license='Apache-2.0',usage='Read only; no third-party source included')],
 excluded=['virtual environments','downloaded third-party sources and PDFs','unselected bulk candidate circuits','intermediate scratch logs','manifest self-hash'],
 caveat='Dependency files are referenced by path and hash; include their existing repository context when reproducing this handoff.')
(H/'publish_manifest.json').write_text(json.dumps(out,indent=2)+'\n');print('selected',len(files),'bytes',out['total_selected_bytes'],'dependencies',len(deps))

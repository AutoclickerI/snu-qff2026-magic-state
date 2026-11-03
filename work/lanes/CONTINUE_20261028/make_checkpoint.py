"""Build a reviewable, hash-pinned continuation inventory; never publish or alter refs.

Regenerate after the continuation report and in-progress lanes are complete.
The inventory is deliberately not a self-hash and cannot approve its own export.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
LANES='JIT_RECEIVER GAO_QUOTIENT EARLY_BOUNDARY ARCHITECTURE_CONTINUE NATIVE_INSTRUMENT MEASURED_BC JOINT_A_ISOMETRY SOURCE_ISOMETRY NATIVE_CAT7 GAUGE_RECOVERY_AUDIT GAUGE_NATIVE_IDENTITY COHERENT_GAUGING GAUGE_SCHEDULE GAUGE_HEADROOM DIRECT_NATIVE DIRECT_CAT GAO_DIRECT'.split()
KNILL_LANES=['KNILL_HEADROOM','KNILL_RESOURCE']
FINAL_LANES=['C4_DIRECT','GAUGE_TREE_NOISE','C2_DIRECT','CAT_INSTRUMENT_AUDIT','CAT_TRANSFER_HERALD']
PRIOR='7cb6d35a735df2630582f7f90efe31105ccc298d'
MAIN='82657bf8e1de91f40e9137f5a517e6f4dacd7518'
ADDITIONAL_HELPERS=[
 'work/lanes/NATIVE2_20261027/incumbent_a_sx.py',
 'work/lanes/END2_20261027/b_phase_symmetries.py',
 'work/lanes/SOTA_SOURCE_20261028/boundary/flag_bell_precheck_86265e64234cb729_d6_20_19_10_2_22_16.qasm',
 'work/lanes/SOTA_SOURCE_20261028/boundary/flag_bell_precheck_86265e64234cb729_d6_20_19_10_2_22_16.json',
]
# The owner explicitly selected these two status documents for this checkpoint.
# Their previous SHA-256 values are in the historical 526-entry inventory, and
# their published blob IDs were verified against PRIOR. The after hashes pin
# exactly the reviewed versions; any subsequent edit requires fresh review.
STATUS_UPDATES={
 'docs/PLAN.md':dict(before_sha256='7332c2a5f50eff1781d7834f96b842cba02510fb881c4b8911ef98c33d724edf',
                     before_blob='cf4e618796f673980b2ca601f8173754bf691dd6',
                     after_sha256='1d96cfeb5be554009eda16bece04fbaacf4446016b5288111bab9e62b5e57551'),
 'docs/SOTA.md':dict(before_sha256='efcea5afa4024003d7f76770bb66c8ecc4c158ebfadec5f2fe8dd22a625c94f0',
                     before_blob='5cc9dbafd289f61dfac6140c6516a14b86f46cfc',
                     after_sha256='903f59ff609b29d618928a4fd86fbaaeda0948f7bbaf98dedbe5b6d2d36f844f'),
}
# These Git blob IDs were independently fetched from PRIOR's tree. They are
# references, not new payload. A mismatch must be reviewed, not overwritten.
PUBLISHED_DEPS={
 'work/lanes/EXPAND2_20261027/axis_echo.py':'aa9a6993f83908be73bb71c9b1c9a1f2382a4320',
 'work/lanes/EXPAND2_20261027/frontend_axis.py':'12bce4948261133bf7e6c0c18309274d784d604b',
 'work/lanes/FRAME20261027/frame_tools.py':'48106fe602e41326ffac8e7b86dc76e4336d3a8c',
 'work/lanes/REBUILD20261027/record_contract.py':'9d3f39eac32fd1e5a97944e2f282e5a253510dc9',
 'work/lanes/END2_20261027/joint.py':'e47efd649542a3560ee9126384cfa0c2764ab148',
 'work/lanes/END2_20261027/partial_incumbent.py':'d409926a1e1f485491dd74e20b0d3b4cb69df29e',
 'work/lanes/END2_20261027/partial_square.py':'9a77d3fa437bdf4287d30238aefc5b84dfca98f3',
 'work/lanes/END2_20261027/source_product_boundaries.py':'ab1b13aa2a828afd48e90d179448b3db9f8cc99b',
 'work/lanes/NATIVE2_20261027/boundary_product.py':'5c9dd0b0a730b4c7f7db6883476453a1da959ec6',
 'work/lanes/NATIVE2_20261027/measured_assemble.py':'ddd70b0d1947c8cc33923f27fe4a32053114661b',
 'work/lanes/NATIVE2_20261027/a_factory.py':'c309064f2a3b98626fea30fd67cc2f526e75d1fe',
 'work/lanes/NATIVE2_20261027/compact_a_logical_read_a_module.json':'d8fb9ea5c0ab3fd3fa2abc817e4e728c6eddecd1',
 'work/lanes/NATIVE2_20261027/old_b_module.json':'645d3af5e97f06e8773b3adb7e65701d615c126e',
 'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.qasm':'7c5e628807b019ed87f4269f6ccd5b736dff18f1',
 'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16.json':'83d1b63406c36f51fed653aeedfc3374a80cbc1d',
 'work/lanes/SOTA_DETECT_20261028/native_teleport/fixed_source.qasm':'75f7fc8698bcdfcf59079e19a3f0dcc1907ec881',
 'work/lanes/SOTA_SOURCE_20261028/gao/gao_abstract_retimed_late.qasm':'acd1e7c888b59cc91e6c91b5bab876e5f5268347',
 'work/lanes/SOTA_SOURCE_20261028/gao/gao_abstract_parallel.qasm':'1347daf928701eb8b0e0c29ba62395e18f391a25',
 'work/lanes/SOTA_RESOURCE_20261028/resource_pairs.py':'428efe06778abf3015c2937c1ce9868c7c40e00e',
 'work/lanes/SOTA_RESOURCE_20261028/resource_risk.py':'16fd0ca4436b92a67921cf1be3efdf21fefc0d97',
 'work/lanes/SOTA_RESOURCE_20261028/six_construct_css.py':'fc5ad0baefe2c26bd99387ae241be87f3eb3c21b',
 'work/lanes/SOTA_20261028/native_schedule.py':'892ac2de4e819097a9c7ec66776916c68314ff48',
 'work/lanes/CAT3_20261027/smallcat.py':'67050fd2f42f129edf17ffe87e3ce675db63a6dc',
 'work/lanes/NATIVE20261027/rebuild.py':'639e5cc61ff399b45c55492042918514e67726ef',
 'work/lanes/STRATEGY_CROSS_20261027/reuse_final.py':'2c4e0bd2f959fb99927a9377fbdb527ad875c142',
}
CAT_LEDGERS={'b_delay.json','b_delay_more.json','flag_b_delay.json','flag_b_delay_more.json',
 'one_round.json','enumeration.json','tree_prices.json','architecture_pairs.json',
 'architecture_pairs_delay17.json','optimized_flags.json','local_schedules.json',
 'partial_local.json','partial_prices.json','pair_participation.json','pairs_flagged.json','pairs_unflagged.json'}
CAT_EXAMPLES=('cat7_unflagged_','cat7_bdelay17_','cat7_flagged_','cat7_flag_bdelay23_',
 'cat7_bdelay16_','cat7_bdelay18_','cat7_one_r1_n3_d20_','cat7_opt_t11_m0_d21_','cat7_partial_')
LARGE_LEDGERS={'isometry_search.json','resource_ablations.json','search.json','shallow.json'}
EXCLUDED_DIRS={'__pycache__','compiler_deps','spidercss_src','.venv','vendor','cache','caches'}

def digest(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
                git_blob_sha1=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest())

def choose(lane):
    files=set();folder=ROOT/'work/lanes'/(lane+'_20261028')
    if not folder.is_dir():return files
    report_text='\n'.join(x.read_text(errors='replace') for x in folder.rglob('*.md'))
    cited_logs=set(re.findall(r'`([^`\n]+\.log)`',report_text))
    for p in folder.rglob('*'):
        if not p.is_file() or p.is_symlink() or set(p.parts)&EXCLUDED_DIRS:continue
        rel=p.relative_to(folder)
        split_paths={'GAUGE_SCHEDULE':{'search.json','shallow.json'},
                     'MEASURED_BC':{'resource_ablations.json'},'EARLY_BOUNDARY':{'isometry_search.json'}}
        if str(rel) in split_paths.get(lane,set()):continue
        if p.suffix in {'.py','.md'}:files.add(p);continue
        if p.suffix=='.log':
            if str(rel) in cited_logs and p.stat().st_size<=250000:files.add(p)
            continue
        if lane=='NATIVE_CAT7':
            if len(rel.parts)==1 and p.name in CAT_LEDGERS:files.add(p)
            elif len(rel.parts)==1 and (p.name in {'a_opt_t11_m0_d21.json','b_opt_t11_m0_d21.json'}
                or p.name.startswith('source_opt_t11_m0_d21_') and p.suffix in {'.qasm','.json'}):files.add(p)
            elif rel.parts[0]=='boundary' and p.name.startswith(CAT_EXAMPLES) and p.suffix in {'.qasm','.json'}:files.add(p)
            continue
        if p.suffix=='.qasm':files.add(p);continue
        if p.suffix=='.json' and (p.stat().st_size<=250000 or p.name in LARGE_LEDGERS):files.add(p)
    return files

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--include-knill',action='store_true',
        help='include both Knill lanes only after their owners confirm completion')
    ap.add_argument('--include-final-lanes',action='store_true',
        help='include final C4, gauge-tree, C2, CAT-instrument and CAT-transfer lanes after their owners confirm completion');args=ap.parse_args()
    files={Path(__file__)};lanes=[];missing=[]
    for lane in LANES + (KNILL_LANES if args.include_knill else []) + (FINAL_LANES if args.include_final_lanes else []):
        folder=ROOT/'work/lanes'/(lane+'_20261028')
        if not folder.is_dir():missing.append(str(folder.relative_to(ROOT)));continue
        if lane in KNILL_LANES+FINAL_LANES and not (folder/'REPORT.md').is_file():missing.append(str((folder/'REPORT.md').relative_to(ROOT)))
        chosen=choose(lane);files.update(chosen)
        lanes.append(dict(lane=folder.name,files=len(chosen),bytes=sum(x.stat().st_size for x in chosen)))
    for p in HERE.iterdir():
        if p.is_file() and not p.is_symlink() and p.name!='selected_manifest.json' and p.suffix in {'.py','.md','.json'}:
            files.add(p)
    if not (HERE/'REPORT.md').is_file():missing.append(str((HERE/'REPORT.md').relative_to(ROOT)))
    for path in ADDITIONAL_HELPERS:
        p=ROOT/path
        if not p.is_file():missing.append(path)
        else:files.add(p)
    for path in STATUS_UPDATES:
        p=ROOT/path
        if p.is_file():files.add(p)
        else:missing.append(path)
    deps=[];mismatches=[];advisories=[]
    for path,sha in PUBLISHED_DEPS.items():
        p=ROOT/path
        if not p.is_file():mismatches.append(dict(path=path,status='missing locally',published_blob=sha));continue
        row=digest(p);deps.append(dict(path=path,published_blob=sha,local_blob=row['git_blob_sha1'],matches=sha==row['git_blob_sha1']))
        if sha!=row['git_blob_sha1']:
            issue=dict(path=path,status='local differs',published_blob=sha,local_blob=row['git_blob_sha1'])
            evidence=HERE/'dependency_audit.json'
            if path.endswith('/boundary_product.py') and evidence.exists():
                audit=json.loads(evidence.read_text())
                if audit.get('identical') and audit.get('published_helper_git_blob')==sha and audit.get('local_helper_git_blob')==row['git_blob_sha1']:
                    issue['status']='scoped import paths verified against published version; see DEPENDENCY_AUDIT.md'
                    advisories.append(issue);continue
            mismatches.append(issue)
    rows=[digest(p) for p in sorted(files)]
    prior_inventory=ROOT/'work/lanes/SOTA_20261028/checkpoint_manifest.json'
    prior=json.loads(prior_inventory.read_text());prior_paths={r['path'] for r in prior['files']}
    overlap=sorted(prior_paths & {r['path'] for r in rows})
    previous_mismatches=[];status_updates=[];status_mismatches=[]
    for r in prior['files']:
        p=ROOT/r['path']
        if not p.is_file():previous_mismatches.append(dict(path=r['path'],status='missing'));continue
        a=digest(p)
        if r['path'] in STATUS_UPDATES:
            expected=STATUS_UPDATES[r['path']]
            status_updates.append(dict(path=r['path'],before_sha256=r['sha256'],before_blob=expected['before_blob'],
                                       after_sha256=a['sha256'],after_blob=a['git_blob_sha1']))
            if r['sha256']!=expected['before_sha256'] or a['sha256']!=expected['after_sha256']:
                status_mismatches.append(dict(path=r['path'],status='status-document before/after differs from reviewed hash'))
            continue
        if a['bytes']!=r['bytes'] or a['sha256']!=r['sha256']:
            previous_mismatches.append(dict(path=r['path'],status='hash mismatch'))
    if set(overlap)!=set(STATUS_UPDATES):status_mismatches.append(dict(status='prior overlap is not exactly the two selected status documents',paths=overlap))
    report=HERE/'REPORT.md'
    pending_patterns=[r'follow-up comparison[^.\n]*\bis testing\b',r'will be recorded here when complete',
                      r'while this test runs',r'\b(?:currently|still) (?:running|pending)\b']
    pending=[];consistency_warnings=[]
    if report.is_file():
        prose=report.read_text()
        for pat in pending_patterns:
            pending.extend(x.group(0) for x in re.finditer(pat,prose,re.I))
        if args.include_final_lanes:
            for marker in ('C4_DIRECT_20261028','GAUGE_TREE_NOISE_20261028','C2_DIRECT_20261028',
                           'CAT_INSTRUMENT_AUDIT_20261028','CAT_TRANSFER_HERALD_20261028'):
                if marker not in prose:consistency_warnings.append('Root report does not reference completed '+marker)
    manifest=dict(status='User-authorized continuation checkpoint for existing private draft PR #1; no new native SOTA.',
       scope='Selected continuation artifacts, two explicit status-document updates, and inventory itself; prior inventory remains historical.',
       base_head=PRIOR,main_head=MAIN,
       publication='After the earlier approval-review rejection, the user explicitly requested publication to the repository. Publish the verified selected tree to existing draft PR #1 using the expected-head lease. See PUBLICATION.md.',
       reproduction='See CONTINUE_20261028/REPORT.md and the individual lane reports; preserve native versus abstract and ideal-resource scope.',
       knill_lanes_requested=args.include_knill,
       final_lanes_requested=args.include_final_lanes,lanes=lanes,missing_required=missing,
       pending_report_markers=pending,report_consistency_warnings=consistency_warnings,
       published_dependencies=deps,dependency_mismatches=mismatches,dependency_advisories=advisories,
       prior_inventory=dict(path=str(prior_inventory.relative_to(ROOT)),sha256=digest(prior_inventory)['sha256'],
           entries=len(prior_paths),selected_overlap=overlap,unchanged_research_entries=len(prior_paths)-len(STATUS_UPDATES),
           local_mismatches=previous_mismatches,status_updates=status_updates,status_mismatches=status_mismatches),
       exclusions=['vendor/compiler environments','bytecode and cache','lock files','unreferenced logs',
                   'bulk CAT7 sweep candidate copies; retained cited witnesses and full summary ledgers',
                   'four unsplit large ledgers; full lossless records retained in indexed readable JSON parts'],
       files=rows,count=len(rows),total_bytes=sum(r['bytes'] for r in rows))
    (HERE/'selected_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('count','total_bytes','missing_required','dependency_mismatches','lanes')},indent=2))

if __name__=='__main__':main()

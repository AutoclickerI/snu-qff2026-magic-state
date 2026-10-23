"""Regenerate the lane report and complete score table from completed receipts."""
from search_v10 import *
import csv


def report(final=False):
    rows=[]
    for path in HERE.glob('*.json'):
        try:d=json.loads(path.read_text())
        except (ValueError,OSError):continue
        if not isinstance(d,dict) or 'official' not in d or d.get('mean') is None:continue
        if len(d.get('seeds',{}))!=3 or not d.get('passed'):continue
        d['label']=path.stem;rows.append(d)
    baseline=next(d for d in rows if d['label']=='v10_reference');b=baseline['mean'];s0=baseline['score']
    def family(d):
        n=d['label']
        if n=='v10_reference':return 'Baseline'
        if n.startswith('boundary_cm0'):return 'Per-qubit boundary deadlines'
        if n.startswith('boundary_cm1'):return 'Commuting boundary deadlines'
        if n.startswith('lns'):return 'Pre-cycle MC local/LNS search'
        if n.startswith('joint_deep'):return 'Pre-cycle + cycle prefix through layer 37'
        if n.startswith('joint'):return 'Pre-cycle + first three cycle layers'
        if n.startswith('cat_sign'):return 'Transversal T sign patterns'
        if n.startswith('cat_'):return 'Random double-cat trees'
        if n.startswith('enumcat'):return 'Enumerated shallow double-cat trees'
        if n.startswith('retain_cycle'):return 'Retain final-cycle X readouts'
        if n.startswith('combined'):return 'Boundary timing + retained X readouts'
        if n.startswith('bell0'):return 'Delay tile-0 Bell preparation'
        if n.startswith('grid_'):return 'Exhaustive boundary CX/readout moves'
        if n.startswith('nreset'):return 'Retain central cat X readout'
        if n.startswith('prune_cat_1'):return 'Remove leaf flag q1'
        if n.startswith('prune_cat_2'):return 'Remove leaf flag q2'
        if n.startswith('prune_cat_3'):return 'Remove both leaf flags'
        if n.startswith('prune_cat_4'):return 'Remove central cat readout'
        return d.get('family','Other')
    rows.sort(key=lambda d:d['mean'])
    with (HERE/'SCOREBOARD.csv').open('w') as f:
        fields=['label','family','seed_0','seed_1000','seed_2000','mean','delta_seed0_v10','delta_mean_v10','n_2q','holdout_mean','direct_tprep_passed','source']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for d in rows:w.writerow({'label':d['label'],'family':family(d),'seed_0':d['seeds']['0'],'seed_1000':d['seeds']['1000'],'seed_2000':d['seeds']['2000'],'mean':d['mean'],'delta_seed0_v10':d['score']-s0,'delta_mean_v10':d['mean']-b,'n_2q':d['n_2q'],'holdout_mean':d.get('holdout',{}).get('mean'),'direct_tprep_passed':d.get('direct_tprep',{}).get('passed'),'source':json.dumps(d['source'])})
    now=time.strftime('%Y-%m-%d %H:%M:%S KST',time.gmtime(time.time()+9*3600))
    lines=['# Lane L5: pre-cycle optimization against v10','',f'Updated {now}. '+('Final.' if final else 'Active; final due 23:00 KST.'),'',
        'G1 objective: minimize the official 100,000,000-shot mean over seeds 0, 1000, 2000. Eligibility is format, class, correctness and acceptance PASS. `fault_scan.c1` is diagnostic only. No submissions. All artifacts and caches stay in this lane. Numerical-library threads are capped at one; worker counts are chosen after host-capacity checks.',
        '',f'v10 baseline: seed 0 **{s0:.12g}**; three-seed mean **{b:.12g}**; 115 CX. Reconstructed QASM matches the submitted artifact byte for byte; fresh official evaluations reproduce seed 0 exactly.',
        '', '## Best completed candidate per change','',
        '| Change | Candidate | Seed 0 | Δ seed 0 vs v10 | Three-seed mean | Δ mean vs v10 | CX | Completed |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    groups={}
    for d in rows:groups.setdefault(family(d),[]).append(d)
    for fam,rr in groups.items():
        d=rr[0];n=d['label']
        lines.append(f'| {fam} | [{n}]({n}.qasm) | {d["score"]:.9g} | {d["score"]-s0:+.4g} | {d["mean"]:.9g} | {d["mean"]-b:+.4g} | {d["n_2q"]} | {len(rr)} |')
    lines+=['','Every row above has all four gates PASS at every official seed. [SCOREBOARD.csv](SCOREBOARD.csv) records each completed candidate, each seed, both deltas, and provenance. JSON files contain full gate receipts and exact schedules.','',
            '## Independent-seed evidence','',
            'Seeds 3000, 4000, 5000 were not used by the initial three-seed search. Selection among many MC candidates can bias the search mean downward; a lower search mean alone does not establish lower expected infidelity.','',
            '| Candidate | Search mean | Independent mean | Δ independent vs v10 |','|---|---:|---:|---:|']
    hb=baseline.get('holdout',{}).get('mean')
    for d in rows:
        h=d.get('holdout',{}).get('mean')
        if h is None:continue
        lines.append(f'| {d["label"]} | {d["mean"]:.9g} | {h:.9g} | {h-hb:+.4g} |')
    lines+=['','## Broader fresh-seed panel','', '| Candidate | Seeds 6000–17000 mean | Δ vs v10 on same panel |', '|---|---:|---:|']
    pb=baseline.get('validation_panel',{}).get('mean')
    for d in rows:
        pm=d.get('validation_panel',{}).get('mean')
        if pm is not None and pb is not None:lines.append(f'| {d["label"]} | {pm:.12g} | {pm-pb:+.6g} |')
    lines+=['','## Verified winners','']
    wins=[d for d in rows if d.get('winner_confirmed')]
    if not wins:lines+=['No independently confirmed winner yet. Lower three-seed candidates above are provisional while broader validation and direct sequential `tprep.check` are pending.']
    for d in wins:
        n=d['label'];lines.append(f'- [{n}.qasm]({n}.qasm), [{n}.json]({n}.json): seed 0 {d["score"]:.12g}; three-seed mean {d["mean"]:.12g}; Δ {d["mean"]-b:+.6g}; {d["n_2q"]} CX. Direct sequential `tprep.check`: PASS.')
    lines+=['','## Methods and decisions','',
        '- Boundary schedules use individual qubit deadlines while preserving the complete v10 cycle timing. A second family permits proven gate commutations across the boundary.',
        '- `lns.py` searches legal single-operation timing moves and larger schedule neighborhoods using all three official seeds at 1e8 shots each. `joint1` also moves the cycle preparation and first interaction layer; its later cycle gates remain fixed.',
        '- `cat_trees.py` replaces the double-cat contraction/expansion network with a grid spanning tree, choosing its root and leaf-ancilla flag directions. Injection and the final cycle stay fixed. All 60 generated trees passed the initial exact correctness/acceptance screen; final ranking uses full official MC.',
        '- Modified-noise diagnostics are isolated in `idle_windows.py`; they are not candidate scores. Removing double-cat-window idle gives mean 1.12874938e-4, first-check-window idle 1.21367855e-4, pre-cycle data idle 1.14044114e-4, and pre-cycle ancilla idle 1.19200626e-4. This motivated concentrating work on the double-cat stage.',
        '- Native h-measure-h readout retains the measured X state (organizer problem.md, section 1.2; tprep/qasm.py `_x_readouts`). Retaining final-cycle X ancillas removes their resets; this is scored with the unmodified official noise model. Retaining the central cat readout passes all four gates and scores 1.21522361e-4 over three seeds. It takes about 500 seconds per seed at six workers; the remaining 15 priority variants were stopped in favor of stronger, faster methods. The completed evidence is preserved.',
        '- Exhaustive enumeration found 776 spanning trees on the original cat footprint. Roots 8, 7, 9 and 14 yielded 85 distinct circuits at depth <=42; two reused exact-QASM receipts, and the other 83 are being scored.',
        '- Single-operation T/TDG timing moves are omitted from the next LNS run because shifting them through commuting gates and depolarizing idle slots often changes MC draws without changing the physical noisy channel. CX/readout moves remain in the search.',
        '- Earlier boundary seed-5 mean improvement did not repeat on independent seeds (independent mean 1.21570344e-4 versus v10 1.21137131e-4). Its expected-value gain is therefore unproven.',
        '', '## Earlier work','',
        'The v6 experiments remain in `results.jsonl` and their original QASM/JSON files. `pre_alap_ordered` scored 0.000128628417625 at seed 0 versus v6 0.000131030214099. ALAP is now in production and is not a new improvement against v10. The old report’s c1 eligibility requirement, eight-process restriction and seed-0-only ranking were removed.',
        '', '## Remaining verification','',
        'Official scoring of the running searches, independent-seed confirmation of finalists, and a direct sequential `tprep.check` for every declared winner. No contest submission is performed by this lane.']
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'candidates':len(rows),'best':rows[0]['label'],'mean':rows[0]['mean']}),flush=True)

if __name__=='__main__':report('--final' in sys.argv)

"""Write a self-contained checkpoint and a hashed, selected handoff manifest."""
import datetime, hashlib, json
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]


def main():
    selected = set(H.glob('*.py'))
    # Network descriptors and exact result ledgers are small enough to preserve
    # together; only selected full QASM candidates are included.
    selected.update(H.glob('*.json'))
    selected.discard(H / 'selected_files.json')
    winners = []
    for p in sorted(H.glob('*best.json')):
        row = json.loads(p.read_text())
        if 'stem' in row and 'loss' in row:
            winners.append(dict(family=p.stem.removesuffix('_best'), **row))
    for fname in ('targeted_results.json', 'wide_constructive_results.json',
                  'wide_layer_results.json', 'wide_pair_results.json', 'wide_early_results.json'):
        path = H / fname
        if not path.exists():
            continue
        vals = json.loads(path.read_text())
        vals = [v for v in vals if v.get('acceptance', 0) >= .5002 and 'loss' in v]
        if vals:
            winners.append(dict(family=path.stem.removesuffix('_results'), **min(vals, key=lambda r: r['loss'])))
    stems = {Path(r['stem']) for r in winners}
    stems.update([H / 'cand' / 'guarded_003_first0', H / 'cand' / 'wide_constructive_s0',
                  H.parent / 'PREFIX20261027/cand/final_phase_random_1'])
    for stem in stems:
        for suffix in ('.qasm', '.json'):
            if stem.with_suffix(suffix).exists():
                selected.add(stem.with_suffix(suffix))
    for name in ('synth.py', 'search_phase.py', 'REPORT.md', 'selected_files.json'):
        selected.add(H.parent / 'PREFIX20261027' / name)
    for name in ('qcirc.py', 't14a.qasm', 't14a.stage.json'):
        selected.add(H.parent / 'T14' / name)
    # qtools is an existing repository dependency, never a lane-local replacement.
    runtime = [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'work/tools/qtools').glob('*.py'))]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    snapshot = dict(timestamp_utc=now, status='prefix searches checkpointed; native B/C resource work active; no incumbent improvement',
                    evaluator_version='94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f',
                    incumbent_loss=3.58709500347e-5, acceptance_threshold=.5002,
                    families=sorted(winners, key=lambda r: r['loss']))
    (H / 'checkpoint_results.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    selected.add(H / 'checkpoint_results.json')
    lines = ['# PREFIX2_20261027 checkpoint', '',
             f'Checkpoint: {now}. Prefix searches are checkpointed; the lane is moving to native B/C resource synthesis. No candidate here beats the incumbent.', '',
             '## Measured candidates', '',
             'All losses below are the all-orders expectation at p=0.001. Acceptance must be at least 0.5002. '
             'The incumbent is L=3.58709500347e-5. The 15-T phase polynomial and the fifth detection coordinate '
             'are preserved. Additional flags use Clifford operations only.', '',
             '| Family | Full loss L | Acceptance A | Full CX | Native ticks | c1 audit | Candidate |',
             '|---|---:|---:|---:|---:|---|---|']
    for row in sorted(winners, key=lambda r: r['loss']):
        stem = Path(row['stem']); meta = json.loads(stem.with_suffix('.json').read_text())
        c1 = row.get('c1', 'not in family-best row')
        lines.append(f"| {row['family']} | {row['loss']:.12g} | {row['acceptance']:.10f} | "
                     f"{meta.get('cx', '?')} | {meta.get('native_depth', '?')} | {c1} | {stem.name} |")
    lines += ['', '## Findings that determine the next work', '',
              '1. The compact native 134-CX source/control has exact L=8.48960074708e-5, A=0.68901191635. '
              'Its accepted second-order loss coefficient is 70.0036111. Fault-pair attribution is in base_pairs.json.',
              '2. Bell-pair meters targeted at copied computational rows preserve raw validity and c1=0, '
              'but improve the compact source only to approximately 8.20e-5. These meters are physical, adjacent, '
              'and fully noisy; no ideal measurement is used in candidate circuits.',
              '3. A sixth Clifford flag with the original fifteen phase axes gives 8.08603222531e-5. '
              'Fresh flag periods and native reset scheduling improve this to 7.81576076591e-5, acceptance '
              '0.62986089791, at 153 CX and 38 native ticks. It is a measured improvement over the 134-CX '
              'redesign, not over the incumbent.',
              '4. Restricting every non-target intermediate parity to carry the sixth flag, then measuring that '
              'flag whenever it becomes a physical plus factor, removes the large pure-Z complementary-pair '
              'mechanism. The price is longer coherent arithmetic. The audited 154-CX example has second-order '
              'coefficient 84.3295833, dominated by X/Y histories and the terminal round. These facts do not prove '
              'all guarded constructions fail.',
              '5. Fifteen simultaneous phase cells are native and valid in the constructed witnesses, but '
              'preparing all fifteen rows creates long exposed complementary Z histories. The original wide '
              'example has second-order coefficient 181.4077778; its largest single grouped pair contributes '
              '73.6 p^2. Exact-kernel-weighted preparation improves that family to roughly 1.25e-4, still far worse '
              'than the incumbent. Early flag/herald readout and early transfers were tested separately.',
              '6. Replacing the terminal A ancilla by a jointly synthesized 11-CX, six-layer encoder with a '
              'two-CX logical-X decoder is native, raw-valid, and c1=0, but yields 8.99e-5 on its tested source. '
              'The three pure-Z parity-only version loses the logical-X check and is worse. The original '
              'terminal A structure remains the better measured choice for this source.',
              '7. Fresh-flag relocation was tested on nine and eleven source cells (three search seeds each, '
              '72 phase variants and eight scheduling controls). Once the sixth coordinate factorizes on a '
              'physical qubit, MX followed by reset removes it. A later RX can introduce an independent flag '
              'on any available zero cell. This keeps separate time-slice records without a coherent SWAP. '
              'dynamic_guard.py synthesizes these resets and native CX gates together, checks raw validity and '
              'singles, and ranks by the unchanged qtools all-orders evaluator. dynamic_schedule.py removes '
              'unused initial and discarded-state resets and tests individual wire release. Every scheduled '
              'control passed raw validity and had c1=0.',
              '8. The best fresh-flag candidate has exact second-order coefficient 57.9402777778, versus '
              '70.0036111111 for the original compact source. Its largest grouped accepted pair is now below '
              '1 p^2. The three largest terminal time-pair groups contribute 22.8666667, 4.2933333, and '
              '2.24 p^2; the largest source groups are X/Y propagation histories. Evidence: dynamic_pairs.json. '
              'Further changes require an identified physical mechanism; the next assignment is native B/C '
              'preparation for the independently developed rank-eight four-square ending.', '',
              '## Scope and controls', '',
              '- Every full candidate uses ordinary native gates. Raw checks require adjacency and the six final '
              'Steane stabilizers, ideal acceptance, and ideal logical fidelity. A c1 audit is a diagnostic only; '
              'the ranking is the full all-orders loss.',
              '- ideal_precheck.py is explicitly a counterfactual diagnostic. It inserts noiseless nonlocal checks '
              'while preserving original source-channel noise. Its outputs are not legal candidates. Both ideal '
              'X/Z prechecks before transfer lower the compact source to 5.44729e-5; this establishes that fixed '
              'source checks alone leave a substantial suffix contribution.',
              '- CP-SAT UNKNOWN and beam-search exhaustion are budget outcomes, not impossibility proofs. '
              'The failed scopes include the tested geometry, hard row restrictions, fixed 112-CX transfer/suffix, '
              'and bounded repair; none excludes a different native source or tail.',
              '- No submission, commit, push, qtools edit, or judge edit was made by this lane.', '',
              '## Reproduction and selected handoff', '',
              'Run from the repository root with `.venv/bin/python` and '
              '`PYTHONPATH=work/tools:upstream/snu-qff2026-problem`; set OMP/OPENBLAS/MKL thread counts to 1. '
              'Use `.venv/bin/python -m qtools price <stem> --processes 1`. '
              'The repository runtime qtools version recorded by the exact receipts is '
              '`94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.', '',
              '`selected_files.json` contains SHA-256 hashes for the generators, exact ledgers, network descriptors, '
              'chosen full QASM/JSON candidates, and exact old-prefix/T14 dependencies. `checkpoint_results.json` '
              'is the machine-readable family table at this timestamp. `reproduce_dynamic.py` rebuilt six '
              'representative family winners byte-for-byte; `reproduction.json` records their exact QASM hashes. '
              'Run `checkpoint.py` after new results to update this checkpoint. The full candidate metadata '
              'embeds its network descriptor.', '']
    (H / 'REPORT.md').write_text('\n'.join(lines))
    selected.add(H / 'REPORT.md')
    entries = []
    for path in sorted(selected):
        if not path.exists():
            continue
        raw = path.read_bytes()
        entries.append(dict(path=str(path.relative_to(ROOT)), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    manifest = dict(timestamp_utc=now, root=str(ROOT), files=entries, runtime_qtools_dependencies=runtime,
                    status='prefix checkpoint; next work is native B/C resource preparation')
    (H / 'selected_files.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(files=len(entries), bytes=sum(r['bytes'] for r in entries),
                          candidates=len(stems), report=str(H / 'REPORT.md'))))


if __name__ == '__main__':
    main()

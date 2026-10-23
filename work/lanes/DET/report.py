from search import *
import hashlib

def records_text(space,d):
    return ' XOR '.join(f'c[{space["record_clbits"][i]}]' for i in bits(d))

def change(space,kernel):
    if not kernel:
        return 'full declared span'
    if all(v.bit_count()==1 for v in kernel):
        return 'drop '+', '.join('`'+records_text(space,space['full_records'][bits(v)[0]])+'`' for v in kernel)
    return 'kernel span {'+', '.join(hex(v) for v in kernel)+'}'

def read_lines(path):
    return [json.loads(s) for s in path.read_text().splitlines()]

def main():
    mc=collections.defaultdict(list)
    for r in read_lines(HERE/'mc.jsonl'):
        mc[r['candidate']].append(r)
    checks={r['candidate']:r for r in read_lines(HERE/'checks.jsonl')}
    audit=json.loads((HERE/'audit.json').read_text())
    out=['# Detector lane report','',
        'At p = 10^-3, neither target has an undeclared independent deterministic parity. '
        'The full declared span remains best among the third-order finalists and the measured MC candidates. '
        'Dropping `c[3]` frees acceptance with a very small loss cost. '
        'For the present circuits, retain the full span to minimize loss; the `c[3]` variants provide acceptance headroom.',
        '',
        'All files are under `work/lanes/DET/`. No submission was made. All emitted QASM files passed '
        '`tprep.check(..., shots=10**6, seed=0)` for format, class, correctness, and acceptance. '
        'Monte Carlo below uses `work/fast_check.check`, 10^8 shots per seed, seeds 0, 1000, 2000, '
        '22 worker processes on hippo (23 including its parent), with BLAS/OpenMP threads capped at one. '
        'Zebra initially used eight workers plus the parent; a transient total-load spike to 50.27/64 '
        'was observed and the lane restarted with at most four workers. Completed checkpoints were retained.',
        '',
        '## Deterministic parity space and judge semantics','',
        '| Target | Measurement records | Declared lines | Declared rank | Full deterministic rank | Missing independent parities | Quotient representatives checked |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for name in TARGETS:
        s=json.loads((HERE/f'{name}_space.json').read_text())
        out.append(f'| {name} | {s["n_measurements"]} | {s["declared_count"]} | {s["declared_rank"]} | {s["full_rank"]} | {len(s["missing_records"])} | {s["quotient_checked"]} |')
    out += ['',
        'The proof uses the judge’s own `tprep.exact.run` deferred-measurement state, retaining all 15 T/T† rotations. '
        'First, row-reduce the already verified detector parities. Then enumerate every coset of their span in '
        'the full measurement-record parity space and evaluate the exact Pauli expectation. Multiplication '
        'by a declared deterministic parity preserves the absolute expectation, so one representative per coset '
        'is sufficient. Every nontrivial coset representative has expectation **0**, far from the judge’s '
        '`abs(abs(expectation)-1) <= 1e-9` criterion. This proves completeness, not merely completeness of a Clifford surrogate. '
        'See [v12_space.json](v12_space.json), [cand2_space.json](cand2_space.json), and [audit.json](audit.json).',
        '',
        'The QASM converter resolves classical bit names to measurement records and places each `DETECTOR` '
        'after its latest referenced measurement. A noiseless parity of either 0 or 1 is valid; the detector '
        'compares against that reference. `POSTSELECT(v)` compares the raw record parity to v, and can '
        'make an otherwise random detector conditionally deterministic. Both targets have no POSTSELECT '
        'and their actual auto frames are `X=(0,[])`, `Z=(0,[])`. No frame or postselection changes were made. '
        'Adding any parity within the existing deterministic span cannot change accepted shots. '
        'v12 has three duplicate `c[7]` declarations; [v12_dedup.qasm](v12_dedup.qasm) removes them while retaining rank 20.',
        'The duplicate-free v12 is bit-identical to the original in score, SEM, and acceptance at all three '
        '10^8-shot seeds. [emitted_audit.json](emitted_audit.json) independently confirms that all 20 emitted '
        'circuits declare exactly the intended subspaces; their quantum-operation text is unchanged.',
        '',
        'Primary implementation sources: [QASM conversion](../../../upstream/snu-qff2026-problem/tprep/qasm.py), '
        '[exact determinism check](../../../upstream/snu-qff2026-problem/tprep/exact.py), '
        '[frame, postselection and scoring](../../../upstream/snu-qff2026-problem/tprep/check.py).',
        '',
        '## Search and exact validation','',
        'The search reuses `exact2.Eval` fault signatures and `Engine` expectations. It accumulates joint '
        'detector-syndrome probability and logical-loss mass for every single fault and every unordered pair '
        'from distinct noise channels. A subspace then accepts a linear kernel in that joint syndrome space. '
        'This preserves the exact normalized first- and second-order coefficients, including single-loss '
        'normalization terms. The unchanged cases reproduce the supplied numbers. Ten independently rebound '
        '`exact2.run` evaluations agree with histogram rescoring to at most 3.4e-16 absolute.',
        '',
        'Enumerated: each generator removal; every coordinate removal set of size 2, 3, or 4; every subspace '
        'supported on at most four generator coordinates; and every one-dimensional relaxed syndrome kernel '
        'that has nonzero mass through second order, at any Hamming weight. Unlisted syndrome sectors have '
        'zero effect at these orders. Multi-start greedy search extends promising kernels. All reported '
        'fronts enforce first-order loss < 1e-14; finalists actually remain around 5e-19. '
        'There are no missing independent parities to add. This is exhaustive for the stated neighborhoods, '
        'not a claim of global optimality over all subspaces at all fault orders.',
        '',
        'Finalists use `exact2.run(third=True)` and `exact2.third_order`. A local acceleration rejects only '
        'detector outcomes outside the exact joint spectrum before calling the same loss engine; baseline '
        'weight-three terms agree with the original implementation within 5.5e-20. '
        'See [acceleration_audit.json](acceleration_audit.json). `exp(-A1)` is an acceptance estimate; '
        'judge MC acceptance is listed separately. “Through third” means the sum of orders one, two and three.',
        '']
    all_summary={}
    for name in TARGETS:
        space=json.loads((HERE/f'{name}_space.json').read_text())
        sr=json.loads((HERE/f'{name}_search.json').read_text())
        base=json.loads((HERE/f'{name}_baseline.json').read_text());base['kernel']=[]
        thirds=read_lines(HERE/f'{name}_third.jsonl')
        out += [f'## {name}','',
                f'The search retained {sr["unique_ft"]:,} distinct first-order-safe subspaces. '
                f'It represented {sr["hist_syndromes"]:,} syndrome sectors through second order. '
                f'Full counts and every single-generator result are in [{name}_search.json]({name}_search.json).',
                '',
                '| Change | Exact second | Through third | First order | exp(-A1) |',
                '|---|---:|---:|---:|---:|']
        for r in [base]+sorted(thirds,key=lambda r:r['total3']):
            out.append(f'| {change(space,r["kernel"])} | {r["loss2"]:.10e} | {r["total3"]:.10e} | {r["loss1"]:.3e} | {r["exp_acc"]:.9f} |')
        out += ['','### Through-third-order Pareto front among finalists','',
                '| Change | Through third | exp(-A1) |','|---|---:|---:|']
        bestacc=-1
        for r in sorted([base]+thirds,key=lambda r:r['total3']):
            if r['exp_acc']>bestacc+1e-12:
                out.append(f'| {change(space,r["kernel"])} | {r["total3"]:.10e} | {r["exp_acc"]:.9f} |')
                bestacc=r['exp_acc']
        out += ['','### Monte Carlo: 10^8 shots per seed','',
                '| Candidate | Seed 0 | Seed 1000 | Seed 2000 | 3-seed mean | Mean acceptance |',
                '|---|---:|---:|---:|---:|---:|']
        rows=[]
        for candidate,rs in mc.items():
            if not candidate.startswith(name+'_'):
                continue
            assert len(rs)==3 and {r['seed'] for r in rs}=={0,1000,2000}
            assert all(r['passed'] for r in rs)
            rs=sorted(rs,key=lambda r:r['seed'])
            mean=sum(r['score'] for r in rs)/3
            acc=sum(r['acceptance'] for r in rs)/3
            rows.append((mean,candidate,rs,acc))
        rows.sort()
        for mean,candidate,rs,acc in rows:
            out.append(f'| [{candidate}]({candidate}.qasm) | '+ ' | '.join(f'{r["score"]:.10e}' for r in rs)+f' | {mean:.10e} | {acc:.9f} |')
        out += ['',
                'The ordering above uses the three-seed mean; seed 0 is retained separately because it is '
                'the judge’s submission key. MC uncertainty per seed is about 1.1e-6 for v12 and 1.3e-6 '
                'for cand2. Small differences should not be described as proven improvements.',
                '',
                '### Loss/acceptance Pareto front through second order','',
                'These are the nondominated points among all searched first-order-safe subspaces, using '
                'exact second-order loss and exp(-A1). The search JSON gives the exact generator vectors. '
                'For a non-coordinate change, `kernel span {hex masks}` specifies the admitted full-detector '
                'syndromes; detector generators are its GF(2) orthogonal complement. Bit j refers to '
                '`full_records[j]` / `independent_clbits[j]` in the parity-space JSON.',
                '',
                '| Change | Detector rank | Exact second | exp(-A1) |',
                '|---|---:|---:|---:|']
        for r in sr['pareto']:
            out.append(f'| {change(space,r["kernel"])} | {r["rank"]} | {r["loss2"]:.10e} | {r["exp_acc"]:.9f} |')
        out += ['','### MC Pareto front among measured candidates','',
                '| Candidate | 3-seed mean | Mean acceptance |','|---|---:|---:|']
        best_acc=-1
        for mean,candidate,rs,acc in rows:
            if acc>best_acc+1e-9:
                out.append(f'| [{candidate}]({candidate}.qasm) | {mean:.10e} | {acc:.9f} |')
                best_acc=acc
        out += ['']
        all_summary[name]=dict(mc=[dict(mean=m,candidate=c,acceptance=a) for m,c,rs,a in rows],
                               best_third=min([base]+thirds,key=lambda r:r['total3']))
    out += ['## Artifact and verification inventory','',
            '| Circuit | 10^6-shot check | Acceptance |', '|---|---|---:|']
    for p in sorted(HERE.glob('*.qasm')):
        assert p.stem in checks,p
        r=checks[p.stem]
        assert r['passed']
        # Quantum operations are byte-for-byte identical after stripping declarations.
        meta=json.loads(p.with_suffix('.json').read_text())
        original=(ROOT/meta['detector_source']).with_suffix('.qasm').read_text()
        strip=lambda s:'\n'.join(x for x in s.splitlines() if not re.match(r'\s*//\s*DETECTOR\b',x))
        assert strip(p.read_text())==strip(original),p
        out.append(f'| [{p.stem}]({p.name}) ([metadata]({p.stem}.json)) | PASS all four gates | {r["acceptance"]:.6f} |')
    out += ['',
            'Checked: source hashes, full noiseless parity-space completeness with T rotations, empty frames, '
            'baseline exact coefficients, cached rescoring against direct `exact2`, final third-order terms, '
            'unchanged quantum operations, all emitted circuit gates at 10^6 shots, and the listed three-seed '
            '10^8-shot MC results. Inferred: acceptance headroom may help another circuit variant; that must '
            'be re-evaluated after changing quantum operations. Unverified: global optimality outside the '
            'enumerated neighborhoods, and all higher-order coefficients beyond the MC measurements.',
            '',
            'Reproduction: run `analyze.py`, `search.py`, `audit.py`, `accelerate.py`, `third_screen.py`, '
            '`validate.py <candidate stems>` / `validate.py mc <candidate stems>`, then `report.py`, using '
            'the repository venv, cwd `work/lanes/DET/`, `PYTHONDONTWRITEBYTECODE=1`, and all three BLAS/OpenMP '
            'thread variables set to 1. `validate.py mc` is configured for hippo’s 22 workers. '
            'The original exact evaluator and judge were not modified.',
            '']
    (HERE/'REPORT.md').write_text('\n'.join(out))
    (HERE/'summary.json').write_text(json.dumps(all_summary,indent=2))
    print(json.dumps(all_summary,indent=2))

if __name__=='__main__':
    main()

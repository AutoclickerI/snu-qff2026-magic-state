"""Assemble the reviewable report directly from completed experiment receipts."""
import json
import re
from pathlib import Path
HERE=Path(__file__).resolve().parent

def read(n,suffix='third'):
    return json.loads((HERE/f'{n}.{suffix}.json').read_text())
def fmt(x):return f'{x:.6e}'

descriptions=[
('base','Reference: A→Z readout, verified B→data, B→X readout','28'),
('crossAC','Winner: seven Aᵢ→Cᵢ at R+1; all reads R+2','28'),
('acmask022','Smaller recoding: Aᵢ→Cᵢ for i={1,2,4}','28'),
('ac53','Grid-compatible recoding: A₅→C₃','28'),
('earlyA','A at32 before T†33; B34; end35','28'),
('earlyA_sync','Early A and all reads at35','28'),
('sync_read','Delay A/C reads to the common last step','28'),
('reverse','B first, then independently verified A; Z check last','28'),
('derived_mix064','Best nontrivial mixed order with c1=0; full derived parity span','28'),
('C_after','Verify B after its data coupling; adds a step','28'),
('dummyR','Final zero-control CX; reused A reset the prior step','28'),
('dummy_checked','Final zero-control CX; noisy transversal partner verification','35'),
('reuseC','Use Z-measured C codeword as final CX controls','28'),
('hybridPZ4','Parallel flagged Z checks then verified Steane X check','27'),
('hybridPX4','Steane Z check then parallel flagged X checks','20'),
('derived_overlap246','Best overlap total; flagged Z checks at27–33, complete parity span','27'),
('knill','Verified encoded Bell resource; Bell-measure source, retain O','28'),
('repeatX','One extra verified partial X round; last read41','28'),
('repeatZ_verified','One extra verified partial Z round; last read41','28'),
('double_full','Second complete round39–41; total-only gain','35'),
('onlyX','Remove final Z check (A)','21'),
('onlyZ','Remove final X coupling (diagnostic)','28'),
('post_A','Postselect A logical Z record; ideal acceptance 1/2','28'),
('post_B','Postselect B logical X record; ideal acceptance 1/2','28'),
]

def main():
    out=[]
    out.append('Best in ARCH’s grid-free search: **3.51317194e-5**, from a seven-CX readout recoding of A into C. '
        'The comparable marginal round cost is **3.10674038e-5**, below **3.14204114e-5**. '
        'This is a **0.995% total reduction**, mainly in cross terms. It does not remove a leading second-order round mechanism. '
        'The full seven-pair contact pattern cannot embed at either the unchanged prefix data positions or v17a’s data positions. '
        'The single-edge version that fits v17a was built and scored on the real grid; results are below.')
    out.append('**Baseline correction and score convention.** The supplied 3.14e-5 is **full minus round-noiseless**, '
        'not the score with pre-stage and block preparations noiseless. Reproducing both ablations gives: full **3.54847270e-5**; '
        'round-noiseless **4.06431563e-6**; only-round-noisy **2.87129381e-5**. '
        'Thus the isolated-round reference is 2.87129381e-5, and the marginal reference including cross terms is 3.14204114e-5. '
        'The winning circuit’s isolated round is **2.87112332e-5**: its reduction is only **1.70489e-9** through third order. '
        'These distinctions prevent a spurious large win from comparing different ablations. [Reproduction](base.third.json), '
        '[winner](crossAC.third.json), [upstream receipt](../MAIN/gf/abl_sep33_pre32.txt).')
    out.append('All grid-free results use STANDARD p=1e-3, the judge’s target/lookup decoder, and the full original R33 prefix. '
        '“Exact” here means the exact2 **first/second/third-order calculation**, not an all-orders fidelity. '
        'Third-order truncation has no new error bound; tiny differences, especially ac53, are not claimed as all-orders gains. '
        'Every scored circuit first passed tprep’s noiseless class/correctness check with **only adjacency bypassed**. '
        'For c1 p ≥1e-12, full-circuit third order is unavailable and the total is explicitly marked **1st+2nd**. '
        'Other c1 p values are rounding residues below 2e-18. exp(−A1) is a computed **acceptance approximation**, '
        'not measured acceptance; POSTSELECT requires multiplying by noiseless A0. Acceptance above 0.5 never changes rank.')
    out.append('**Ideas table.** Q is final-check footprint / distinct cells used over the complete circuit, not the fixed qreg declaration. '
        'CX is whole-circuit CX; the common prefix has 81. “Isolated” switches off prefix and preparation faults; '
        '“marginal” is full minus no-round and includes cross terms. For overlapping schedules, each inserted check operation '
        'and the waiting interval after its first contact belong to the round; original prefix gates remain in the prefix. '
        'Explicit operation labels and split idle intervals make the ablations disjoint. Link stems provide qasm, metadata and score JSON.')
    out.append('| Idea / mechanism | Q | CX | Round-only grid-free: isolated / marginal | Total with pre-stage | exp(−A1) | Files / diagnostic |\n'
               '|---|---:|---:|---:|---:|---:|---|')
    for n,desc,q in descriptions:
        d=read(n);m=json.loads((HERE/f'{n}.json').read_text());a=d['all'];bad=abs(a['c1'])>=1e-12
        diag=(f'c1 p={a["c1"]:.3e}; **1st+2nd**' if bad else 'c1=0')
        if a['A0']<.9:diag+=f'; A0={a["A0"]:.1f}; A≈{a["A0"]*a["expA"]:.4f}, fails'
        out.append(f'| {desc} | {q}/{m["used_qubits"]} | {m["cx"]} | {fmt(d["round"]["total"])} / {fmt(d["marginal_round"])} | '
                   f'{fmt(a["total"])} | {a["expA"]:.6f} | [{n}]({n}.qasm), [score]({n}.third.json); {diag} |')
    out.append('A second full round reduces the total to 3.52932122e-5, but **increases** the isolated round to 2.91640903e-5 '
        'and the marginal round to 3.25823362e-5. It therefore misses the joint architecture goal after correcting the baseline definition. '
        'The O-block teleport already tested by ST_TP remains closed: its fault graph is isomorphic to the old star round '
        '(3.2324e-5 with its older standalone preparation timing). The `knill` row above instead constructs and verifies an encoded Bell resource '
        'before Bell-measuring the source; it is a distinct mechanism, not a repricing of that O-block. '
        '[Prior teleport proof](../ST_TP/REPORT.md), [new construction](more.py).')
    out.append('**Search coverage and rejected mechanisms.** '
        'All 128 per-qubit A/B order masks were built. The original detector set is invalid for 126 mixed masks. '
        'I then derived the **entire deterministic record-parity span** from the exact non-Clifford state for all 128, '
        'rather than treating random old detectors as an architectural impossibility. All 128 derived mixed-order circuits are noiselessly correct; '
        'only masks 0 and 64 have c1=0, and mask64 scores 1.55751621e-4. '
        'The 28 choices of independent Z generators were also scheduled as flagged checks overlapping prefix steps27–33: '
        '12 have timing witnesses, 16 are infeasible in that scheduling model. After full parity derivation, nine of the 12 fail output correctness '
        'and three have c1 p ≥1.99667e-4. '
        '[Order manifest](more_manifest.json), [derived circuits](derived_manifest.json), [parity proof implementation](detectors.py), '
        '[overlap schedules](overlap_manifest.json).')
    out.append('The parallel hybrid screen used five different legal data orders for each asymmetry, selected across the 2,496 '
        'orders of the fixed six-step flagged-gadget template. The table gives the best measured representatives; this is **not** '
        'an exhaustive optimization of all flagged circuits. Both verified repeated partial-round types and a complete repeated round were priced. '
        'Readout recoding screened all 49 single A→C edges and all 127 nonempty diagonal subsets; 13 finalists received full third-order ablations. '
        'The single A₅→C₃ win is only 2.09231e-8 in total and has identical second order. '
        '[Readout screen](readout_manifest.json), [finalists](readout_finalists.json), [parallel hybrids](more.py), '
        '[repeat circuits](repeat_verified.py).')
    out.append('**Why the large tail gap remains.** Direct round faults decompose at second order as: data idle×idle **1.16666667e-5**, '
        'data CX×idle **1.12000000e-5**, data CX×CX **2.80000000e-6**, and all pairs involving B–C verification **3.17333333e-6**. '
        'Their sum is 2.88400000e-5. Keeping only the data-touching CXs and data idles reproduces the **2.56666667e-5** data-side floor. '
        'Late ancilla recoding leaves this leading term unchanged; it changes which earlier faults are masked by noisy records. '
        '[Exact pair decomposition](diagnostics.json).')
    out.append('A checked dummy control must itself be prepared and checked. Its last verification CX can leave an undetected X component on the control; '
        'the final CX then copies that component into data. Fresh reset controls and measured-C controls also carry preparation/readout noise. '
        'The two explicit constructions cost 4.65190e-5 and 4.81838e-5 total, respectively. '
        'Using B’s syndrome coupling in the circuit’s final step cannot yield a later B measurement in the same native step: '
        'the two operations share B. Omitting that measurement removes the Z-syndrome information; `onlyZ` diagnoses the resulting first-order failure. '
        'A one-qubit replacement for the final idle has the same depolarizing channel under STANDARD. '
        'These are causal/channel arguments for these designs, **not a proof excluding every architecture**. '
        'The quoted 1.116e-5 assumes ideal checked partners and removes earlier check noise; the LIT/AUDIT review does not establish a positive universal lower-bound theorem. '
        '[Boundary audit](../LIT/REPORT.md), [judge noise implementation](../../../upstream/snu-qff2026-problem/tprep/noise.py).')
    out.append('Postselecting either available logical readout bit halves ideal acceptance and leaves the entire computed infidelity unchanged. '
        'Deterministic C logical parity and the stabilizer parities are already included. '
        'The extra information is therefore either redundant or too expensive in acceptance in this family. '
        'A biased non-Clifford logical check is a different gadget; the earlier logical-H_XY/injection ablation bounds its tested source-only opportunity '
        'at about 1%, without claiming that a new noisy check is free. [Stored ablations](../MAIN/gf/abl_sep33_pre8.txt).')
    out.append('**Grid-fit table.** All coordinates are linear cells 6r+c. The resource lower bounds here are contact-graph proofs '
        'before considering encoder connectivity. The full seven-edge winner and all 12 tested diagonal-subset finalists are infeasible '
        'with either fixed prefix data or v17a data, even when A/B/C cells may be chosen freely. '
        'This does not prove infeasibility after new data moves or a longer routed schedule. '
        'Earliest R is measured for built schedules; no unbuilt routing delay is assigned an invented value.')
    out.append('| Winner / realization | Footprint | Partner cells and steps | Earliest R | Blocking constraint / result |\n'
               '|---|---|---|---|---|\n'
               '| Seven Aᵢ→Cᵢ, `crossAC` | 28 round qubits, 36 cells with prefix; 7 extra CX | Each Dᵢ needs adjacent Aᵢ,Bᵢ; Cᵢ adjacent to both. R: D→A,B→C; R+1: B→D,A→C; R+2: all reads | Grid-free33; no direct embedding at either fixed data layout | Seven disjoint unit squares required. D₀=0 forces square {0,1,6,7}, already containing D₂=7. [Proof](grid_fit.json) |\n'
               '| Diagonal subsets, best small mask22={1,2,4}; all 12 finalists | 28 round qubits, 36 cells; 3–7 extra CX | Same star partners; added Aᵢ–Cᵢ contacts only for selected i. Same three round steps | Grid-free33; no direct embedding for either fixed data layout | Full star-contact CP-SAT tests return INFEASIBLE for all24 cases; not merely encoder failure. [Witness model/results](mask_fit.json) |\n'
               '| Single A₅→C₃, `ac53` → `grid_ac` / `grid_ac_only` | Same 28-qubit L5 round; 6 existing data hops; no new cells or steps | A₅=16,C₃=17; data d₅=22 has A₅=16,B₅=23; d₃=10 has A₃=9,B₃=11,C₃=17. Added CX16→17 at51; A₅,C₃ read52 | **50 as built**, end52 | Fits and passes all judge gates. `grid_ac` retains C₂=19→C₁=25 recoding; `grid_ac_only` omits it. MC below |\n'
               '| Native recoding plus other A edges, `grid_ac_aa` | Same cells, +3 CX over grid_ac | Also14→8,9→15,1→2 at51; disjoint matching, read52 | **50 as built** | Fits, c1=0, measured acceptance above0.5; MC below |')
    out.append('The existing v17a sidecar says R47, but the judge’s **native schedule is R50, B→data51, final read52**. '
        'I verified this directly from the current QASM and used those times in all ARCH grid metadata/ablations; I did not edit MAIN. '
        'The generated `grid_v17a` reorders independent lines but has exactly the stored v17a second/third-order score '
        '(8.24541189e-5). It provides the same-order construction control for the new grid circuits. '
        '[Grid builder](grid.py), [control score](grid_v17a.third.json).')
    mc=HERE/'grid_mc.log'
    if mc.exists() and 'grid_ac_aa mean' in mc.read_text():
        log=mc.read_text(); vals={}
        for line in log.splitlines():
            mt=re.search(r'/(grid_\w+) (0|1000|2000) ([\d.e+-]+).* acc ([\d.]+)',line)
            if mt:
                n,seed,loss,acc=mt.groups();vals.setdefault(n,[]).append(dict(seed=int(seed),loss=float(loss),acceptance=float(acc)))
        (HERE/'grid_mc.json').write_text(json.dumps(vals,indent=2)+'\n')
        out.append('**Full-grid ranking, measured with 10^8 shots at each of seeds 0/1000/2000.** '
            'The runner is a byte-identical lane-local copy of the requested MAIN/spec/mc3.py: '
            '[hashes](mc3_sha256.txt), [raw log](grid_mc.log), [structured results](grid_mc.json). '
            'Each run passed the real adjacency/class/correctness/acceptance gates. The printed single-seed SEM is about1.1e-6; '
            'these three seeds establish the requested ranking, not a high-confidence resolution of sub-percent changes.')
        for n,rs in sorted(vals.items(),key=lambda x:sum(r['loss'] for r in x[1])/len(x[1])):
            assert sorted(r['seed'] for r in rs)==[0,1000,2000]
            out.append(f'- [{n}]({n}.qasm): mean **{fmt(sum(r["loss"] for r in rs)/3)}**; '
                f'seed0 **{fmt(next(r["loss"] for r in rs if r["seed"]==0))}**; '
                f'acceptance {min(r["acceptance"] for r in rs):.5f}–{max(r["acceptance"] for r in rs):.5f}; '
                f'{json.loads((HERE/(n+".json")).read_text())["cx"]} CX.')
    else:out.append('Full-grid MC is still running; this draft is not the completion report.')
    out.append('**Primary literature since2024.** These sources were checked online in this lane, alongside the requested LIT report. '
        'No paper number below is substituted for a judge score; no claim relies on memory.')
    out.append('- [Gidney, Shutty & Jones (2024), magic-state cultivation](https://arxiv.org/abs/2409.17595): '
        'the source of the current cultivation family, not an independent final-round candidate. Its larger-code/end-to-end and terminal-postselected benchmarks '
        'do not directly price this retained Steane output. The present exact prefix and final-round calculations are the relevant local measurements.')
    out.append('- [Daguerre & Kim (2024/2025), code switching](https://arxiv.org/abs/2410.07327): '
        'reported corrected logical infidelity **4.6e-5 ±1.6e-5**, acceptance **84%**, at p=1e-3 **excluding idle noise**; '
        'this is a retained-output benchmark but not STANDARD. The repository’s complete STANDARD implementation instead reports '
        '**9.02257e-5** grid-free mean ([DK receipt](../DK/REPORT.md)); it is not a new ARCH measurement.')
    out.append('- [Poór, Rodatz & Kissinger (2025/2026), low-overhead Steane extraction](https://arxiv.org/abs/2511.13700): '
        '**14 CNOTs** describes the primary extraction component; the dynamic protocol also uses an **11-CNOT** recovery component. '
        'The published cycle-error comparison is not postselected magic-state infidelity. Its fixed static STANDARD adaptations were already priced '
        'at **3.23500e-4** with separate ancillas in [SEARCH](../SEARCH/evaluations/summary.json), with ideal encoded input. '
        'The parallel hybrid rows above separately price the closer final-check alternatives.')
    out.append('- [Weilandt, Peham & Wille (2026), Steane-type state-preparation synthesis](https://arxiv.org/abs/2601.13313), '
        '[Strikis, Browne & Beverland (2026), syndrome-extraction optimization](https://arxiv.org/abs/2603.05481), and '
        '[Poór et al. (2026), SpiderCSS](https://arxiv.org/abs/2610.03714): useful primary methods for ancilla verification, '
        'residual-error-aware timing and fault-preserving CSS circuit rewrites. They supply no retained Steane-T/this-judge coefficient '
        'that can be inserted into the table. SpiderCSS is a new relevant source beyond the requested LIT set; '
        '[its full text and code link](https://arxiv.org/html/2610.03714v1) concern stabilizer/CSS-state preparation, not a free final magic-state detector.')
    out.append('- [Chan et al. (2026), cultivation hook faults](https://arxiv.org/abs/2609.17706): '
        'explains loss of the anticipated fault distance under true T propagation and gives flag repairs. Its pre-escape/terminal-check convention '
        'does not remove the retained-output tail or justify transferring a headline improvement factor. '
        '[Mehta et al. (2026), practical cultivation cost](https://arxiv.org/abs/2610.06828) explicitly distinguishes '
        'destructive final syndrome information from nondestructive usable-output evidence; its Caliper postselection is not a new constant-XOR gadget '
        'with a quoted score for this judge. These papers reinforce the boundary accounting used here.')
    out.append('**Verification and limits.** [evaluate.py](evaluate.py) uses the judge’s noiseless verification and the existing exact2 model. '
        '[fast_exact.py](fast_exact.py) removes zero-probability faults and joins only algebraically possible detector syndromes, '
        'while keeping exact2’s distinct-channel triple probabilities and normalization. It reproduces both stored sep33 and v17a '
        'second/third-order totals and baseline ablations. The full-span detector derivation exhausts the Pauli stabilizers of the exact sparse ideal state '
        'and checks every returned parity expectation. Every invalid or first-order-failing build is retained and labeled, not counted as a winner. '
        'The geometry certificates concern direct contacts with the two specified data placements; no optimality claim is made for unrestricted '
        'data relocation, longer routing, all possible flagged circuits, or all final-check architectures. '
        'All generated circuits, metadata, receipts, scripts and this report are in ARCH. No submission, commit, push, credential read, or sub-agent action was performed.')
    rendered='\n\n'.join(out)+'\n'
    rendered=re.sub(r'(?m)(\|)\n\n(?=\|)',r'\1\n',rendered)
    (HERE/'REPORT.md').write_text(rendered)
    summary={}
    for f in HERE.glob('*.third.json'):
        d=json.loads(f.read_text()); summary[d['name']]=d
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('wrote REPORT.md; third-order/diagnostic receipts',len(summary))

if __name__=='__main__':main()

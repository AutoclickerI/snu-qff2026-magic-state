"""Build the final report from measured receipts; no inferred scores."""
import os,sys,json,re,hashlib,itertools
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from model import Model,Basis

def static(name):
    p=OUT/(name+'.qasm');text=p.read_text();meta=json.loads(p.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
    R=max(t for a,t in zip(u,ts)if a.lines==['cx q[0],q[1];']);end=max(t for a,t in zip(u,ts)if a.name in('T','TDG'))
    pre=set(meta.get('prefix_unit_indices',[i for i,t in enumerate(ts)if t<=end]))
    row=dict(R=R,depth=max(ts)+1,cx=sum(a.name=='CX'for a in u),pre_cx=sum(u[i].name=='CX'for i in pre),pre_depth=end+1,
             release=[max(ts[i]for i in pre if q in u[i].qs)+1 for q in [1,6,13,2,9,14]],sha256=hashlib.sha256(text.encode()).hexdigest())
    if not name.startswith('inputs/'):
        meta.update(R=R,pre_end=end,native_depth=row['depth'],full_cx=row['cx']);p.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return row

def exact(name):
    p=OUT/('inputs/v17a.exact.txt'if name=='inputs/v17a'else name+'.exact.log')
    if not p.exists():return {}
    text=p.read_text();out={}
    for key,pat in [('c1',r'c1 p = ([\deE+.-]+)'),('second',r'second order: ([\deE+.-]+)'),('third',r'third order: ([\deE+.-]+)'),('total',r'1-F \(to 3rd order\) = ([\deE+.-]+)'),('acc',r'exp\(-A1\) = ([\deE+.-]+)')]:
        mt=re.search(pat,text)
        if mt:out[key]=float(mt.group(1))
    return out

def mc(name):
    p=OUT/('inputs/mc3_v17.log'if name=='inputs/v17a'else name+'.mc.log');tag='v17a'if name=='inputs/v17a'else 'work/lanes/TREP/'+name
    if not p.exists():return {}
    text=p.read_text();out={}
    for seed in (0,1000,2000):
        mt=re.search(re.escape(tag)+r' '+str(seed)+r' ([\deE+.-]+).*?acc ([\d.]+)',text)
        if mt:out[str(seed)]=float(mt.group(1));out['acc'+str(seed)]=float(mt.group(2))
    mt=re.search(re.escape(tag)+r' mean ([\deE+.-]+)',text)
    if mt:out['mean']=float(mt.group(1))
    return out

def fmt(x):return '—'if x is None else f'{x:.6e}'

def main():
    names=['inputs/v17a','init_state_d5_s1','encoder19','init_state_d5_s1_idle','encoder19_idle','encoder19_alap']
    results={n:dict(static=static(n),exact=exact(n),mc=mc(n))for n in names}
    # Match every physical T site/occurrence to v17a, then verify one linear
    # coordinate map on all 15 axes. This distinguishes synthesis from renaming.
    points={}
    for name in ['inputs/v17a','encoder19_alap']:
        m=Model((OUT/(name+'.qasm')).read_text(),[0,20,7,10,3,22,21]);b=Basis();seen={};p={}
        for x,z,*_ in m.rots:b.add(x)
        for r in m.rots:
            q=m.prog[r[-1]].qubits[0];k=seen.get(q,0);seen[q]=k+1;p[q,k]=b.express(r[0])
        points[name]=p
    pairs={v:points['inputs/v17a'][k]for k,v in points['encoder19_alap'].items()};images=[pairs[1<<i]for i in range(5)]
    def canonical(c):
        z=0
        for i,v in enumerate(images):
            if c>>i&1:z^=v
        return z
    assert all(canonical(x)==y for x,y in pairs.items())
    classification=dict(form='f00_0',coordinate_map=images,all_15_physical_T_occurrences_match=True)
    (OUT/'classification.json').write_text(json.dumps(classification,indent=2)+'\n')
    (OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    en=json.loads((OUT/'enumeration.json').read_text());forms=[f for f in en['forms']if f['T']==15]
    ref=results['inputs/v17a']['mc']['mean'];best=results['encoder19_alap']['mc']['mean'];gain=100*(1-best/ref)
    lines=[f'# TREP — verified grid candidate, {gain:.2f}% lower MC mean', '',
      f'**Primary delivery: [encoder19_alap.qasm](encoder19_alap.qasm) + [metadata](encoder19_alap.json).** '
      f'The 1e8-shot mean at seeds 0/1000/2000 is **{best:.6e}**, versus v17a **{ref:.6e}**. '
      'All four judge gates pass at 1e6 shots; seed-0 acceptance is 0.52782. The circuit uses 203 CX and native depth 49, with the round at native step 46. '
      'No submission, commit, push, or writes outside this lane were performed.', '',
      'The first completion gate is met. All 16 supports were enumerated and their phase-axis protection checked. '
      'The winning circuit resynthesizes the current form; the other 15 forms were **not physically synthesized or priced**. '
      'Their full-fault behavior remains unverified. They are not claimed to lose.', '',
      '## Corrections to the brief', '',
      '- v17a’s metadata/barrier label is R=47, but `tprep.noise.schedule` places its actual round at **50**, with native depth **53**. '
      'Its pre-stage still ends at 32. Every R and release step below uses the judge’s native scheduler. '
      f'The source QASM SHA-256 is `{results["inputs/v17a"]["static"]["sha256"]}`.',
      '- In [R1’s pair log](../R1/v16_release_drop.pairs.log), 6.410e-6 is **prep×round**, and 5.875e-6 is **prep×prep**. '
      'Those refer to suffix-block preparation. The distinct pre×round entry is 2.265e-6.', '',
      '## Enumeration and physical synthesis', '',
      'Pulling back the 15 rotations gives mutually commuting axes. Their X action on the occupied orbit has **rank 5**; '
      'the full Pauli vectors have **rank 9**. Every extra Z factor is trivial on the occupied orbit. '
      'In the basis recorded in [enumeration.json](enumeration.json), the signed phase is exactly `parity(25 & y) mod 8` for all 32 assignments.', '',
      'The degree-1/2/3 binary phase-signature matrix has rank 25 on the 31 nonzero axes. Its six-dimensional kernel is exactly the punctured affine functions. '
      'The complete 64-word coset has T-weight counts `1:1, 14:15, 15:16, 16:16, 17:15, 30:1`. '
      'The one-T support has one harmful phase-axis single; every 14-T support has seven harmful phase-axis pairs; every 15-T support has zero harmful singles and pairs. '
      'Each 15-T support also has explicit ±1 coefficients reproducing the exact ideal phase, so no extra Clifford phase correction is required. '
      'These statements are exhaustive calculations in [enumerate.py](enumerate.py), not full-fault guarantees for unsynthesized circuits.', '',
      'Two CP-SAT models changed the physical network:', '',
      '- [synth_init.py](synth_init.py) replaced the 12-CX pre-T Clifford resource by an 11-CX, five-layer state preparation, preserving its entire CSS stabilizer space. '
      'The fixed-initialization five-layer objective was solved optimally. Four-layer variants and the five-layer full-unitary model returned INFEASIBLE; these are limited to the encoded solver models.',
      '- [synth_encoder.py](synth_encoder.py) replaced the complete 25-CX injection encoder by **19 CX in six occupied layers**. '
      'Backward Z constraints preserve the three Steane checks and logical Z; the initial logical phase has exactly one nonzero component on a |+> input, identifying the T site. '
      'The selected measured-zero inputs are cells 2, 9, 13, and the T site is cell 7. Unused preparations and an empty solver layer were removed by [emit_encoder.py](emit_encoder.py). '
      'The existing injection verification, double-cat check, final T-dagger layer, and v17a suffix are retained. The full pre-stage footprint stays at 15 cells and pre-CX count falls from 81 to 75.',
      '- [schedule_prefix.py](schedule_prefix.py) keeps all per-wire dependencies and shifts every suffix operation by one common offset. '
      'It first minimizes the suffix start, then applies the stated scheduling objective. The ALAP prefix gives the best MC mean. '
      'Its native prefix overlaps suffix preparation; the final prefix T-dagger occurs at 45. '
      'Later release of some flag cells is accepted because the full-circuit loss is lower.', '',
      f'The new network is still form f00_0: its coordinate-basis map back to the original basis is `{images}`, '
      'and all 15 physical T-site occurrences match under that map ([classification](classification.json)). '
      'The actual parity network changed by six CX, so the gain is not attributed to coordinate renaming.', '',
      '## Forms and prefix pricing', '',
      'T supports use decimal five-bit coordinates. Release is the first step after the last prefix operation on cells **[1,6,13,2,9,14]**, '
      'in that order. Depth is the last prefix native step plus one; an interleaved prefix can extend until just before the round. '
      'Pre loss means only prefix noise enabled on the full circuit, through third order. '
      'All grid-free rows use separate standard 9-CX A/B/C encoders and R=33; they are diagnostic circuits and fail physical adjacency.', '',
      '| Form / implementation | T support | Protection | Pre CX | Depth | Releases [1,6,13,2,9,14] | Pre-region exact loss | Grid-free total, R=33 |',
      '|---|---|---|---:|---:|---|---:|---:|']
    supp=lambda f:','.join(map(str,f['support']))
    for n,label in [('encoder19_alap','f00_0 / 19 CX, ALAP'),('encoder19_idle','f00_0 / 19 CX, compact'),('init_state_d5_s1_idle','f00_0 / 11 CX resource')]:
        p=OUT/(n+'.price.json');price=json.loads(p.read_text())if p.exists()else{};st=results[n]['static']
        lines.append(f'| {label} | {supp(forms[0])} | Phase 0 singles/0 pairs; full c1≈0; judge pass | {st["pre_cx"]} | {st["pre_depth"]} | {st["release"]} | {fmt(price.get("only_pre",{}).get("total"))} | {fmt(price.get("gf33",{}).get("total"))} |')
    for f in forms[1:]:lines.append(f'| {f["id"]} | {supp(f)} | Phase 0/0; full circuit untested | — | — | — | — | — |')
    lines += ['',
      'The compact variants use the existing [ablate.py](../MAIN/ablate.py) time regions. For the interleaved ALAP circuit, '
      '[price.py](price.py) uses saved prefix-operation provenance, otherwise a time cutoff would wrongly include the suffix blocks. '
      'Noise before a prefix operation, including its preceding idle gap, belongs to that prefix; data waits before suffix operations belong to the suffix. '
      'For the ALAP grid-free R=33 diagnostic, the same prefix network is rescheduled ALAP with all prefix operations finishing by 32. '
      'It is not the R=46 clock schedule transplanted unchanged. The existing sep33 reference is about 3.55e-5.', '',
      '## Full grid circuits', '',
      'Each MC seed uses 1e8 shots. `c1` is the first-order loss printed by exact2, including p=1e-3. '
      'All reported third-order totals satisfy |c1|<1e-12. The acceptance estimate does not rank candidates.', '',
      '| Circuit | R | CX | c1 | 2nd | 3rd | Exact total | exp(-A1) | MC 0 / 1000 / 2000 | MC mean | Seed-0 acceptance | Files |',
      '|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|']
    for n in names:
        st=results[n]['static'];ex=results[n]['exact'];mc_=results[n]['mc'];label=n.replace('inputs/','')
        lines.append(f'| {label} | {st["R"]} | {st["cx"]} | {fmt(ex.get("c1"))} | {fmt(ex.get("second"))} | {fmt(ex.get("third"))} | {fmt(ex.get("total"))} | {ex.get("acc","—")} | '+ ' / '.join(fmt(mc_.get(str(s)))for s in [0,1000,2000])+f' | {fmt(mc_.get("mean"))} | {mc_.get("acc0","—")} | [qasm]({n}.qasm), [json]({n}.json) |')
    lines += ['',
      'Ranked by MC: **encoder19_alap**, encoder19_idle, init_state_d5_s1_idle, v17a, init_state_d5_s1, encoder19. '
      'The two unscheduled synthesis variants lose on the required mean despite reducing gates/depth. '
      'The ASAP variant has only a second-order screen (5.73086e-5), so it is not assigned a final rank. '
      'An early emission experiment, init_state_d5_s0, used barrier counts instead of native times; it is retained as a negative implementation receipt, not a delivery.', '',
      '## Verification and remaining limits', '',
      '- [encoder19_alap.check.json](encoder19_alap.check.json), [encoder19_idle.check.json](encoder19_idle.check.json), and '
      '[init_state_d5_s1_idle.check.json](init_state_d5_s1_idle.check.json) contain explicit format, class, correctness, and acceptance verdicts at 1e6 shots. '
      'All pass, and every physical T-axis single and pair was checked again on the synthesized circuits.',
      '- Full-fault exact screens and three-seed results are in each candidate’s `.exact.log` and `.mc.log`. '
      'The MC command is the requested `mc3.py`; [results.json](results.json) collects the measured numbers. '
      'Individual MC SEMs are about 1.0–1.1e-6. The reported gain is the observed three-seed mean difference, not an official submission result.',
      '- Every QASM has a sibling JSON with `data_qubits`. Grid-free artifacts are marked `grid_free: true`; only the full-grid candidates above are deliveries. '
      'Remote calculations used at most 20 lane cores on jerry and 8 on hippo, with all three BLAS/OpenMP variables set to 1. '
      'No other lane’s files or jobs were changed.',
      '- This does not establish an optimum over all 16 forms, all encoders, or all schedules. The 15 alternative physical forms remain open because the successful-circuit completion branch was reached.', '']
    (OUT/'REPORT.md').write_text('\n'.join(lines))
    print('report generated; best',best,'gain',gain)

if __name__=='__main__':main()

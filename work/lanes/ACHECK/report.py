from common import *
import hashlib
scores={p.name[:-11]:json.loads(p.read_text()) for p in HERE.glob('*.score.json')}
mechanism=json.loads((HERE/'mechanism.json').read_text());base_total=mechanism['total']
def fmt(x):return '—' if x is None else f'{x:.7g}'
def linked(name):return f'[{name}]({name}.qasm)'
parts=['# ACHECK\n', '**Completed: [best.qasm](best.qasm) and [best.json](best.json), sourced from `verify_2_9_15`.** The 3-seed 1e8-shot mean is **7.34312063185213e-5**, 2.57% below v19’s 7.536742492e-5. Seed-0 acceptance is **0.53238408**. The circuit passes all four judge checks at 1e6 shots, retains 203 CX and native round step 45, and satisfies the first completion branch.\n',
 'The winner retains the existing A encoder, reuses the already-postselected MX state of q1, replaces A’s q16 reset with a Z measurement and its detector, and adds deterministic MX checks immediately after RX initialization on q2, q9, and q15. The whole circuit is rescheduled ALAP with the native per-wire dependencies retained. Every extra measurement has an explicit detector; the existing output frame is unchanged.\n',
 'All loss numbers are 1−F at p=0.001. Exact totals include the isolated cubic increment and are used only for |c1 p| < 1e-12. exp(−A1) is an acceptance **estimate**. Every circuit in the fixes table was run through unmodified `tprep.check(..., shots=10**6, seed=0)`; its verdict and actual acceptance are retained. No submission, commit, push, credential access, or sub-agent was used.\n',
 'A’s loss decomposition, using the judge’s native schedule and channel provenance. Each ablation switches off just the named channels; differences overlap and must not be added. Pair terms below credit the full pair to a family whenever it participates (so within-A pairs appear in both families). The original 20-unit region contains 18 A encoder operations plus two data-hop initializations; this analysis separates those and includes A’s actual readout.\n',
 '| A fault family | Pair loss involving family | Largest pair partners (loss) | Cubic loss removed | Loss removed through third order | Share of full v19 loss |\n|---|---:|---|---:|---:|---:|']
for fam,title in [('A_CX','Encoder CX'),('A_init','Encoder initialization'),('A_idle','A idle after initialization'),('A_readout','A readout, including shared C→A re-encoding')]:
 pairs=[(k,v) for k,v in mechanism['pairs'].items() if fam in k.split(' × ')];pair=sum(v for k,v in pairs)
 biggest='; '.join(f'{next(x for x in k.split(" × ") if x!=fam) if any(x!=fam for x in k.split(" × ")) else fam}: {fmt(v)}' for k,v in sorted(pairs,key=lambda x:-x[1])[:4])
 delta=base_total-mechanism['ablations'][fam]['total'];cubic=mechanism['third']-mechanism['ablations'][fam]['third'];parts.append(f'| {title} | {fmt(pair)} | {biggest} | {fmt(cubic)} | {fmt(delta)} | {100*delta/base_total:.2f}% |')
delta=base_total-mechanism['ablations']['A_all']['total'];parts.append(f'| All four A families together | — | overlapping pairs and triples | {fmt(mechanism["third"]-mechanism["ablations"]["A_all"]["third"])} | {fmt(delta)} | {100*delta/base_total:.2f}% |\n')
parts.append('`pre_idle` includes data gaps ending at a prefix operation, especially the final T_DAG. `data_idle` denotes later data gaps owned by hops or the round. `A_readout` includes the joint two-qubit noise of C17→A16; it is not an attribution to A alone within that shared channel.\n')
parts += ['The leading pair is a Z/Y idle on data cell 10 at native steps 31–44 with a late A encoder fault (for example ZZ after CX 1→2 at step 44), contributing 3.0842914e-7 per listed Pauli pair. The analogous cell-0 idle at 30–43 pairs with the 8→14 / 14→15 branch. These form a logical Z from A’s weight-two Z class plus the missing data error. Leading positive weight-three sets include Z on A cell 9 during steps 40–44 with Z idles on data cells 3 and 0 (3.8094160e-8); pivot initialization plus two data idles also appears. Top triples are positive weight-three terms, **not** the normalized cubic contribution; the exact cubic term includes the pair-times-other-channel correction. Full labels, pair aggregation, and ablations: [mechanism.json](mechanism.json).\n',
 'Fixes. Extra CX and occupied cells are relative to v19; a borrowed B/C flag cell and the internal A15 checker add no physical cells. “3rd” is the isolated cubic increment. Native round step and one-million-shot acceptance expose timing and acceptance costs.\n',
 '| Method / circuit | Extra CX / cells | R | c1 p | 2nd | 3rd | Exact total | exp(−A1), estimate | Judge 1e6 / acceptance |\n|---|---:|---:|---:|---:|---:|---:|---:|---|']
names=['base','init_1','init_2','init_1_2','init_16','reuse_1_2_16','init_9','init_15','reuse_8','pivot_9','pivot_15','pivot_9_15','pivot_1_2_9_15','combo_9_15','combo_9_15_8','combo_9_15_14','combo_9_15_8_14','verify_9_15','verify_2_9_15','verify_1_2_9_15','enc_214','enc_000','flag_00','flag_05','flag_15','early_008','early_032','early_064','layout2_alap']
enc=sorted((k for k in scores if k.startswith('enc_') and 'total' in scores[k]),key=lambda k:scores[k]['total'])
names+=enc[:3]
internal=sorted((k for k in scores if k.startswith('internal_') and 'total' in scores[k]),key=lambda k:scores[k]['total']);names+=internal[:3]
usedbase=set(map(int,re.findall(r'q\[(\d+)\]',(HERE/'base.qasm').read_text())))
for name in dict.fromkeys(names):
 if name not in scores:continue
 sc=scores[name];md=json.loads((HERE/(name+'.json')).read_text());txt=(HERE/(name+'.qasm')).read_text();used=set(map(int,re.findall(r'q\[(\d+)\]',txt)))
 acc=sc.get('acceptance_1e6');verdict='PASS' if sc.get('judge_passed') else 'FAIL'
 desc={'base':'v19 control','init_1':'MX reuse q1','init_2':'MX reuse q2','init_1_2':'MX reuse q1/q2','init_16':'M-init q16','init_9':'RX→H q9','init_15':'RX→H q15','reuse_8':'R→H q8','layout2_alap':'new layout + 3-cell cat'}.get(name)
 if desc is None:desc=next((v for k,v in [('reuse_','combined reuse/init'),('pivot_','RX then MX'),('combo_','reuse + measured init'),('verify_','verified pivots + q16 M-init'),('enc_','in-situ encoder'),('flag_','borrowed-cell flag'),('early_','early A coupling'),('internal_','A15 logical-X check')] if name.startswith(k)),'candidate')
 parts.append(f'| {desc}: {linked(name)} | {md.get("cx",203)-203:+d} / {len(used)-len(usedbase):+d} | {md.get("R","—")} | '+ ' | '.join(fmt(sc.get(k)) for k in ['c1','second','third','total','exp_A1'])+f' | {verdict} / {fmt(acc)} |')
parts += ['\nAll detailed scores, including additional encoder and init variants, are in [scores.json](scores.json). `init_8`, `init_8_16`, and `init_1_2_8_16` fail noiseless detector determinism: the reused hop leaves q8 in |+⟩, so its proposed Z measure-init is random. The corrected H-based q8 variant is `reuse_8`, which passes and loses. These failures were not patched by dropping detectors.\n',
 'Finalists: 1e8 shots for each of seeds 0, 1000, 2000, using the judge’s unmodified chunk arithmetic through `fast_check.check`. Ranking uses only the three-seed mean and requires seed-0 acceptance ≥0.505 as the practical floor.\n',
 '| Circuit | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance | Files |\n|---|---:|---:|---:|---:|---:|---|']
mc=[]
for p in HERE.glob('*.mc.json'):
 if p.stem.startswith('best'):continue
 x=json.loads(p.read_text());name=p.name[:-8]
 if len(x.get('seeds',[]))!=3:continue
 mc.append((x['mean'],name,x))
for mean,name,x in sorted(mc):
 vals={s['seed']:s for s in x['seeds']};parts.append(f'| {name} | '+ ' | '.join(fmt(vals[s]['score']) for s in [0,1000,2000])+f' | {fmt(mean)} | {fmt(vals[0]["acceptance"])} | [QASM]({name}.qasm), [JSON]({name}.json), [MC]({name}.mc.json) |')
parts.append('| v19 reference | 7.5448361e-5 | 7.4562589e-5 | 7.6091324e-5 | 7.536742492e-5 | 0.53486914 | [QASM](base.qasm), [JSON](base.json), [FREELAY receipt](../FREELAY/joint_reuse2_alap.score.json) |')
parts += ['\nReference v19 mean supplied and reproduced in FREELAY: 7.536742492e-5, seeds 7.5448361e-5 / 7.4562589e-5 / 7.6091324e-5; seed-0 acceptance 0.53486914. Its identical QASM is retained as `base.qasm` and was separately checked at 1e6 here.\n',
 'Search boundaries and validation: 521 distinct retained EXENC/FLAG/SCHED encoder paths were built in v19’s full timing model and screened at second order; 33 diverse candidates were checked through third order. Second-order screening is not a final performance rank. All 168 GL(3,2) maps per encoder were tested on the fixed A cell set; only the original physical embeddings survived adjacency. The seven logical-X support geometries are in [automorphism_audit.json](automorphism_audit.json). The common-neighbor support {14,9,16} uses A’s own cell 15; 190 algebraically admissible prefixes were built with its three-CX check before it joins A, choosing the best round/time-sum schedule among all six check orders. Their minimum native R is 49 (maximum 54), with full-circuit shortlist prices in the fixes table. This is not a proof against arbitrary new placements or other dynamic encoders.\n',
 'The LAYOUT2 cat check was rebuilt with the 19-CX injection prefix and full ALAP scheduling. External flags borrow B/C cells before their preparation and thereby delay the round; their recorded acceptance fails. Early A was moved before final T_DAG where legal, with the native schedule verified; its increased unprotected data exposure outweighed the A idle saving. Logical-X checks on A remain valid in principle; these measurements close only the constructed schedules.\n',
 'The lane-local [fast_exact.py](fast_exact.py) only rejects fault signatures that flip an identity detector projector; all accepted tables and all pair/triple sums use the original exact2 code. Baseline total agrees with the original evaluator. On four architecture families, 1,800 random single/pair/triple table queries agreed exactly with the unmodified dense engine ([validation](fast_validation.json)); both `combo_9_15_8` and the delivered `verify_2_9_15` were cross-checked with the unmodified exact2 CLI; all reported printed terms match. The requested unmodified `MAIN/spec/mc3.py` was copied verbatim into this lane for owl and rerun on `best`; it reproduces the three seed scores ([receipt](best.mc3.log)). Every emitted native operation is compared with `tprep.noise.schedule`, including folded MX/RX operations.\n',
 'Runs used owl Docker quotas totaling at most 32 cores and zebra jobs with at most three workers, with OMP/BLAS/MKL threads fixed to one. MC jobs for `init_1_2`, `reuse_1_2_16`, and `combo_9_15_8` were stopped by explicit PID/container ID before a complete seed result, after selecting the verified-q2 implementation. Their means remain unmeasured, and no partial draw is used in ranking. `combo_9_15_8` has the slightly lower exact estimate 7.31860e-5, but direct q2 MX reuse made sampling much slower; the delivered reset-then-MX alternative has exact 7.32342e-5 and completed all three MC seeds. This is a screening decision, not a measured MC comparison between those two circuits. Artifacts and useful completed checks are retained. No claim of global optimality or of a statistically established true-mean improvement follows from three seeds alone.\n']
parts.append('Reproduction: with OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1, run the project `.venv/bin/python work/lanes/ACHECK/build_best.py`. The resulting `replay.qasm` is asserted byte-identical to `best.qasm`; `best.json` includes native prefix provenance, data_qubits, exact scores, all MC seeds, and the SHA-256. All lane processes were finished or explicitly stopped at handoff.\n')
(HERE/'scores.json').write_text(json.dumps(scores,indent=1));(HERE/'REPORT.md').write_text('\n'.join(parts))
if mc:
 passing=[(mean,name,x) for mean,name,x in mc if x['check_passed'] and x['seeds'][0]['acceptance']>=.505]
 if passing:
  mean,name,x=min(passing);txt=(HERE/(name+'.qasm')).read_text();md=json.loads((HERE/(name+'.json')).read_text())
  h,r,tail=S.qasm_ops(txt);us=S.fold_units(r);ts=native_times(txt,us);_,bu,_,_,bm,_,_=base()
  from collections import Counter
  def key(u):return tuple(u.lines[:-1] if u.name=='MX' and u.lines[-1].startswith('h ') else u.lines)
  counts=Counter(key(bu[i]) for i in bm['prefix_unit_indices']);indices=[]
  for i,u in enumerate(us):
   k=key(u)
   if counts[k]>0:counts[k]-=1;indices.append(i)
  assert not +counts,counts
  md.update(source_candidate=name,sha256=hashlib.sha256(txt.encode()).hexdigest(),MC=x,exact=scores[name],prefix_unit_indices=indices,pre_end=max(ts[i] for i in indices))
  (HERE/'best.qasm').write_text(txt);(HERE/'best.json').write_text(json.dumps(md,indent=1));(HERE/'best.check.log').write_text((HERE/(name+'.check.log')).read_text())
  print('best',name,mean,flush=True)

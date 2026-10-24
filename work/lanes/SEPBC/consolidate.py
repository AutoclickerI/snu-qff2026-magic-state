"""Consolidate completed receipts; retain two finalist circuit packages only."""
import os,sys,json,csv,hashlib,shutil,collections
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
SEP=5.71112722e-5;ABC=5.03262480e-5;V25=6.505010287762392e-5
BEST='zero_endpoint_blue_q5_t37';NONBLUE='zero_endpoint_q5_t34'
def read(p):return json.loads(p.read_text())
def main():
 rows=[]
 for p in sorted(H.glob('*.screen.json')):
  name=p.name.removesuffix('.screen.json');stem=H/name;s=read(p);ex=stem.with_suffix('.price.json')
  assert ex.exists(),('missing CLI verification',name)
  r=read(ex);m=read(stem.with_suffix('.json'));valid=abs(r['c1'])<1e-12
  if valid:assert abs(r['total']-s['total'])<1e-14,(name,r['total'],s['total'])
  row=dict(name=name,sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),c1=r['c1'],second=r['second'],third=r['third']if valid else None,total=r['total']if valid else None,exp_minus_A1=r['exp_minus_A1'],delta_sep=r['total']-SEP if valid else None,delta_ABC=r['total']-ABC if valid else None,R=m.get('R'),cx=m.get('cx',m.get('CX')),block_teleports=m.get('block_teleports',0),pair_classes=r['pair_classes'],examples=r['examples'],third_reused_from=r.get('third_reused_from'),categorical_key=r.get('categorical_key'))
  rows.append(row)
 fields=['name','sha256','c1','second','third','total','exp_minus_A1','delta_sep','delta_ABC','R','cx','block_teleports','third_reused_from','categorical_key']
 with(H/'built_variants.csv').open('w')as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k)for k in fields}for r in rows)
 (H/'measurements.jsonl').write_text(''.join(json.dumps(r)+'\n'for r in rows))
 index={r['name']:r for r in rows};b=index[BEST];nb=index[NONBLUE];ao=read((H/BEST).with_suffix('.allorders.json'));nao=read(H/'audit'/f'fresh_exact_walsh_{NONBLUE}_result.json');cert=read(H/'static_certificate.json');neg=read(H/'interleave_r45_k4_s3_w0.provenance_pairs.json')
 solvers={p.name:read(p)for p in H.glob('*.receipt*.json')};solvers.update({p.name:read(p)for p in H.glob('static_*.json')})
 for line in (H/'REPORT.md').read_text().splitlines():
  if line.startswith('- `unlabelled_') and ' Mechanism/scope:'in line:
   name,rest=line[3:].split('`: ',1);solvers[name]=json.loads(rest.split(' Mechanism/scope:',1)[0])
 (H/'solver_receipts.json').write_text(json.dumps(solvers,indent=2))
 for old,new in [(BEST,'best'),(NONBLUE,'nonblue')]:
  for suffix in ['.qasm','.json','.plan.json','.screen.json','.price.json','.exact.log','.exact.json','.speed.log','.mc.log','.allorders.log','.allorders.json','.allorders_general.validation.json']:
   src=H/(old+suffix)
   if src.exists():shutil.copy2(src,H/(new+suffix))
 shutil.copy2(H/'audit'/f'fresh_exact_walsh_{NONBLUE}_result.json',H/'nonblue.allorders.json')
 assert (H/'best.qasm').read_bytes()==(H/(BEST+'.qasm')).read_bytes()
 assert (H/'nonblue.qasm').read_bytes()==(H/(NONBLUE+'.qasm')).read_bytes()
 mechanism=lambda name:('Independent A encoder: extra live-state exposure and A/data fault pairs'if name.startswith('amb')else 'Separate B/C: 48 moves and long live-state exposure'if name.startswith('interleave')else 'Measured-helper BC: routing/fault correlations exceed saved CX cost'if name.startswith('mblns')else 'Transient known-zero measurement catches BC preparation faults'if name.startswith('zero')else 'Reset/init and readout control')
 selected=[BEST,NONBLUE,'zero_endpoint_q4_t42','zero_endpoint_q4_t41','interleave_r45_k4_s3_w0','amb_d8_c11_s2_000','mblns_s1_000_orig','control_original','mb_control']
 def table(names):
  text='| Variant | Second | Third increment | Total | exp(-A1) | Delta vs sepBC / ABC210 | Mechanism |\n|---|---:|---:|---:|---:|---:|---|\n'
  for name in names:
   r=index[name];fmt=lambda x:'—'if x is None else f'{x:.9e}'
   text+=f"| `{name}` | {fmt(r['second'])} | {fmt(r['third'])} | {fmt(r['total'])} | {r['exp_minus_A1']:.7f} | {fmt(r['delta_sep'])} / {fmt(r['delta_ABC'])} | {mechanism(name)} |\n"
  return text
 body=f'''Status: **COMPLETE — stopping gate reached.** `best` is grid-valid, passes the judge and runtime gates, and beats v25k through third order and at all orders. **The independent 9+9-CX B/C construction remains open.** The delivered improvement uses a measured joint preparation. No submission, commit, push, credentials access, or other-lane write.

Best grid circuit: [best.qasm](best.qasm) / [best.json](best.json), byte-identical to verified `{BEST}`. **213 CX**, native round boundary **R=48**, depth **51**. `c1={b['c1']:.12e}`; second **{b['second']:.12e}**, third increment **{b['third']:.12e}**, total **{b['total']:.12e}**; exp(-A1) **{b['exp_minus_A1']:.10f}**. This is **{(1-b['total']/V25)*100:.4f}%** below v25k's third-order 6.505010288e-5.

Validated all-orders **1-F = {ao['loss']:.12e}**, acceptance **{ao['acceptance']:.12f}**. v25k's independently inherited all-orders reference is 6.59136168224142e-5, so the gain is **2.1461%**. The inherited BCPOL parent is 6.476729894421287e-5; the new measurement improves it by **2.68246299e-7**. All-orders ranking resolves the small opposite fluctuation in the three-seed estimates; no seed-0 cherry-picking was used.

The unchanged 1e6-shot judge passes format, class, correctness and acceptance; seed-0 acceptance **0.514806**, zebra **2.8 s/1e6** (gate <=20 s). The byte-identical MAIN/spec/mc3.py driver, copied to inputs for the older tom mirror, passes its direct tprep.check and returns 1e8-shot seeds 0/1000/2000: **6.624655e-5 / 6.462748e-5 / 6.389037e-5**, mean **6.492147e-5**. Seed-0 acceptance at 1e8 is **0.51489**. [Exact receipt](best.exact.log), [speed](best.speed.log), [MC](best.mc.log), [all orders](best.allorders.json), [channel/sector validation](best.allorders_general.validation.json).

## What changed and what was reused

Reused BCPOL `cache_endpoint_5_902_02232` (rank-five joint endpoint), and its port of KNAP's blue XZ check and q19 RX speed repair. SEPBC adds **`measure q[5] -> c[264]` at native step37**, plus its detector, while q5 is noiselessly |0>. It fits an idle slot and changes no CX, native timing, or placement. The unchanged full judge proves the new detector deterministic. This is an internal preparation measurement, not a separate B or C encoder.

Matched parent-to-child exact gain: second **-1.866666666667e-7**, third **-7.618091165831e-8**, total **-2.628475783250e-7**. Every second-order change belongs to BC-preparation pairs. Largest removed pairs: X preparation flip at q11/t33 paired with XI on CX12→13/t45, IX on CX13→12/t46, or XX on CX12→13/t47. New post-measurement X/Y faults at q5/t37 give back part of that gain. [Complete pair difference](q5_pair_delta.json).

The non-blue port [nonblue.qasm](nonblue.qasm) has third-order **{nb['total']:.12e}**, all-orders **{nao['loss']:.12e}**, 201 CX, R45, exp(-A1) **{nb['exp_minus_A1']:.10f}**; the 1e6 judge passes at acceptance **0.544293**, **3.6 s/1e6 on zebra**. Adding the KNAP blue/speed-repair package yields the best above: third-order change **{b['total']-nb['total']:.12e}**. This is a package comparison, including its timing and initialization policy.

## Layout and move plan

| Role | Physical cells in logical-index order |
|---|---|
| data | 0, 20, 7, 10, 3, 22, 21 |
| A | 1, 14, 8, 9, 2, 16, 15 |
| B | 6, 26, 13, 11, 4, 23, 27 |
| C | 12, 25, 19, 17, 5, 29, 28 |

The inherited six two-CX data hops remain: logical d3, **4→10**; d5, **15→16→22**; d6, **8→9→15→21**. No new block teleport is added. A retains its grid encoder. The rank-five BC preparation plus verification uses **87 CX in 15 native layers**, finishes at48, and B couples to data at49. q5's added measurement is inside that preparation. The complete native operation plan is [best.plan.json](best.plan.json).

## Built variants and the LADDER shortfall

All losses in this table are through third order at STANDARD p=1e-3. The references ignore adjacency: sepBC **5.71112722e-5**, ABC210 **5.03262480e-5**. Deltas include interactions and cannot be added as independent taxes.

{table(selected)}
The best retains routing and the old A package, so its shortfall remains **{b['delta_sep']:.9e} / {b['delta_ABC']:.9e}** against the two LADDER rungs. Dominant second-order contributions: final round × round **2.884e-5**; BC-region pairs **6.81917e-6**; A-region × data-idle **4.32804e-6**; A-region × BC **2.49307e-6**. Net cubic is **1.351065e-5**. The top A/data pair is Z idle on q10/t35–47 with a late A-encoder CX fault at45. These region bins are physical-cell/time diagnostics, not an order-independent attribution of the reference gap. Exact fault labels are retained in [best.price.json](best.price.json).

The complete separate-block witness has **18 encoder CX + 48 measured teleports**, 185 total CX, R45. B=[6,26,13,11,4,28,27], C=[12,32,19,17,5,34,33], with A and data retained. It passes correctness and speed (**7.2 s/1e6**) but fails acceptance (**0.334859**, versus exp(-A1)=0.332370); exact 1-F **1.66268423558e-4**. Emitted-provenance pair sums: BC prep/moves × themselves **2.84595534e-5**, A prep × BC prep/moves **2.06536687e-5**, plus cubic **7.52021337e-5**. One dominant pair is q25's preparation X flip/t16 with X idle on q13/t19–30; another is Z idle on a C wire q32/t16–44 with a late A-encoder fault. This measured negative closes that exact routing witness only. [Provenance receipt](separate_provenance.json), [judge receipt](separate_speed.json).

Measured-helper searches used the eight spare cells, final X projections, and then intermediate MX+reset operations, with explicit frame derivation and single-X-fault cuts. LNS found a 67-CX preparation, but fewer CX did not rank better: its extra exposure and residual accepted fault pairs outweigh the savings. Independent A instruments on the seven A cells also failed to improve this baseline; cap10/depth6 is UNSAT, while larger time-limited cases remain open. Exact model bounds and timeouts are in [solver_receipts.json](solver_receipts.json).

## Static-layout result

There is **no stationary 6×6 placement with connected seven-cell B and C, all seven B–C pairs adjacent, and a distinct neighboring data cell for every B qubit**. A need not be connected; the independent enumeration reaches the contradiction before choosing A or a complete data matching. Each B vertex needs two external neighbors (C and data), so its degree within connected B is at most two; a seven-cycle is impossible on the bipartite grid, hence B is a path. Enumerating all such physical paths leaves **1584 oriented-canonical paths, 656 eligible B sets, 59,568 C assignments, and zero connected C assignments**. An independent unlabelled CP-SAT formulation is also INFEASIBLE. A 7×7 positive control finds a valid placement. [Certificate](static_certificate.json), [enumerator](static_certificate.py), [7×7 control](static_certificate_7.json).

This closes the stationary row-style version of approach (b), without a fourth connected-block assumption. It does **not** close moving blocks, helper-assisted disconnected final blocks, endpoint reuse, staggered data positions, or other joint instruments.

## Verified and inferred

- Verified: every listed completed circuit's native adjacency/timing; noiseless correctness in the EVAL frontend; exact2 pair/third-order sums; |c1| gates; full judge, seed-0 acceptance, zebra runtime, MC and all-orders results for the delivery; the static obstruction and positive control.
- The original four-projector reviewer evaluator was used unchanged in arithmetic for the non-blue candidate. The blue circuit has five active projectors and uses BCPOL's extension: complete physical-channel multiset equality, 1024 projector-sector checks (max error 3.33e-16), and all 4096 outcomes of three correlated channels with nonzero loss (numerator error 1.32e-16). It contracts at width26. It uses no boundary-response cache across changed exteriors.
- Exact2 CLI validation uses algebraically zero-acceptance pruning, with unchanged surviving arithmetic. The unmodified control's third-order output agrees at its printed precision; the pruned calculation and fast categorical contraction agree to <=5e-18 on that control. Equivalent circuits may reuse a completed third-order term only after exact equality of the complete reduced engine and every unrounded categorical noise channel; each retains its own physical pair/top analysis. {sum(bool(r['third_reused_from'])for r in rows)} receipts used that equivalence.
- Timing correction: v23h_c2c9 has four terminal T-dagger gates at **native step44**, not32. Measurements after32 alone do not guarantee the fast judge path. Actual runtimes, rather than that assumption, decide the gate.
- Inferred: live-state exposure is the general obstacle suggested by these routed witnesses. Only the stationary geometric obstruction is proved globally within its stated domain. SAT timeouts are not impossibility claims. The ideal 5.711e-5/5.033e-5 separate-encoder packages have not been realized.
- Build failures were repaired before physics conclusions: the remote mirror lacked a copied evaluator module; a redundant helper reset followed by MX changed native H folding; the cache seeder initially used a shared temporary filename between threads. These failures were not counted as circuit negatives. Cache writes now use process/thread-specific temporary files and atomic replacement; completed equal-key receipts were checked for numerical equality.
- The lane stops because the explicit below-v25k gate was reached, not because all approaches are closed. Local judge results are not an official submission; no server result is claimed.

All **{len(rows)} built variants** and exact measurements are also available in [built_variants.csv](built_variants.csv) and [measurements.jsonl](measurements.jsonl). Nonfinal circuit files are removed after consolidation; generators, solver receipts, and numerical evidence remain.

<details><summary>Complete built-variant table ({len(rows)} circuits)</summary>

{table(list(index))}
</details>
'''
 (H/'REPORT.md').write_text(body)
 manifest={name:{s:hashlib.sha256((H/(name+s)).read_bytes()).hexdigest()for s in('.qasm','.json')}for name in('best','nonblue')}
 (H/'finalist_manifest.json').write_text(json.dumps(dict(files=manifest,source_aliases={'best':BEST,'nonblue':NONBLUE},all_built=len(rows),max_screen_cli_discrepancy=max(abs(read(H/(r['name']+'.screen.json'))['total']-r['total'])for r in rows if r['total']is not None)),indent=2))
 print(json.dumps(dict(rows=len(rows),best=ao['loss'],manifest=manifest)),flush=True)
if __name__=='__main__':main()

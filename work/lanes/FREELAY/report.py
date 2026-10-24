"""Assemble the requested report from measured receipts and native schedules."""
from co_design import *
import hashlib, math

def main():
 # mc3 prints rounded scores, while evaluate.py saves full floats.
 p=HERE/'joint_reuse_alap.score.json';d=json.loads(p.read_text());log=(HERE/'joint_reuse_alap.mc.log').read_text()
 d['seeds']=[dict(seed=int(seed),score=float(score),acceptance=float(acc)) for seed,score,acc in re.findall(r'joint_reuse_alap (0|1000|2000) ([\deE.+-]+) ± [\deE.+-]+ acc ([\d.]+)',log)]
 if len(d['seeds'])==3:d['mean']=sum(x['score'] for x in d['seeds'])/3
 p.write_text(json.dumps(d,indent=1))
 fs=[];models=[];manifest=[]
 for q in sorted(HERE.glob('*.qasm')):
  meta=json.loads(q.with_suffix('.json').read_text());data=meta['data_qubits']
  score=q.with_suffix('.score.json');assert score.exists(),f'Unverified full circuit: {q}'
  sc=json.loads(score.read_text());check=q.with_suffix('.check.log').read_text()
  assert 'shots=1,000,000' in check and 'format:' in check
  txt=q.read_text();h,r,t=S.qasm_ops(txt);us=S.fold_units(r);nt=native_times(txt,us)
  planned=q.with_suffix('.units.json')
  if planned.exists():
   plan=sorted(json.loads(planned.read_text()),key=lambda u:u['t']);raw=[];rt=[]
   for u in plan:raw+=u['lines'];rt += [u['t']]*len(u['lines'])
   compressed={v:i for i,v in enumerate(sorted(set(rt)))};pu=S.fold_units(raw)
   expected=[(compressed[rt[u.raw_indices[0]]],u.lines) for u in pu]
   assert expected==[(tt,u.lines) for tt,u in zip(nt,us)],f'Native plan mismatch {q}'
  if 'solver' in meta:
   x=meta['solver'];perm=x.get('permutations',{k:list(range(7)) for k in 'abc'});tt=x['tokens'];ends={k:v['pos'][-1] for k,v in tt.items()}
   ra=[max(t for u,t in zip(us,nt) if u.lines[0]==f"cx q[{ends[f'd{i}']}],q[{ends[f'a{perm['a'][i]}']}];") for i in range(7)]
   rb=[max(t for u,t in zip(us,nt) if u.lines[0]==f"cx q[{ends[f'b{perm['b'][i]}']}],q[{ends[f'd{i}']}];") for i in range(7)]
   R=str(ra[0]) if len(set(ra))==1 else f'{min(ra)}–{max(ra)}';R+=f' / {max(rb)}'
  else:R=f"{meta['R']} / {meta['R']+1}"
  fs.append(dict(name=q.stem,meta=meta,score=sc,R=R,cx=sum(u.name=='CX' for u in us),depth=max(nt)+1))
  manifest.append(dict(file=q.name,sha256=hashlib.sha256(txt.encode()).hexdigest(),data_qubits=data,native_depth=max(nt)+1,judge_1e6=sc['judge_passed']))
 for p in sorted(HERE.glob('*.receipt.json')):
  x=json.loads(p.read_text());a=x['args'];name=a['out'];s=HERE/(name+'.solver.json');sol=json.loads(s.read_text()) if s.exists() else None
  q=next((r for r in fs if r['name']==name),None)
  moves=f"data ≤{a['dhops']}/wire; block ≤{a['bhops']}/wire"
  if sol:moves=f"{sum(sum(v['moves']) for k,v in sol['tokens'].items() if k[0]=='d')} data; {sum(sum(v['moves']) for k,v in sol['tokens'].items() if k[0]!='d')} block"
  option=('joint82 + ' if a.get('joint') else 'separate ')+a['option']
  if a.get('automorphisms'):option+='; GL(3,2) labels'
  if a.get('early_a'):option+='; early A'
  if a.get('fixed_endpoints'):option+='; fixed L5 endpoints'
  if a.get('alap_tie'):option+='; ALAP tie'
  status=x.get('result',x['status'])
  models.append([f'r{a["row"]}c{a["col"]}',option,moves,status,str(sol['proxy']) if sol else '—','yes' if q else 'no',fmt(q['score'].get('total')) if q else '—',f'[{name}]({p.name})'])
 winner=min((r for r in fs if 'mean' in r['score'] and r['score']['judge_passed']),key=lambda r:r['score']['mean'])
 w=winner['score'];name=winner['name'];gain=100*(1-w['mean']/7.636e-5)
 out=[f'# FREELAY — verified mean {w["mean"]:.9e}', '',
 f'**Delivery: [{name}.qasm]({name}.qasm) and [metadata]({name}.json).** Its three 1e8-shot MC scores have mean **{w["mean"]:.9e}**, a measured **{gain:.2f}%** below the requested v18 bar 7.636e-5. Seed-0 acceptance is **{w["seeds"][0]["acceptance"]:.8f}**. The full 1e6-shot judge passes format, class, correctness, and acceptance. This satisfies the first completion branch. It remains above the supplied leader score 5.727e-5.', '',
 'The winner retains the L5 cell sets and clean 82-CX joint B+C preparation. It reuses the prefix MX states on cells 10 and 9, whose records are already postselected, for the first data hops from 4 and 8. Each hop uses the |+⟩ transfer order CX destination→source, then CX source→destination. Full-circuit CP-SAT timing puts the native round at 45, versus the supplied v18 reference at 46. The 11-CX A encoder wins over the tested 12-CX lower-danger encoder. No submission, commit, push, credential access, sub-agent, or write outside FREELAY was performed.', '',
 'The separate-block target near 3.55e-5 was **not reached**. The successful delivery is a scheduling/reuse improvement in the joint-prep option, not a successful separate-encoder placement. The measured difference is modest relative to MC uncertainty (each winner seed has SEM about 1.04e-6); it is not an established true-mean optimum.', '',
 '## Models', '',
 'Times are native operations. [co_design.py](co_design.py) reserves complete live-state intervals, including destination resets and both source CX/measurement steps of a move. Prefix wire order is preserved and its end is free. Encoder wire dependencies precede moves, every final A/B partner is distinct, and B→C at R is immediately followed by B→data at R+1. Data moves use two CX; block moves use one CX plus measurement, with detector-frame XORs. The optional early-A branch frees A cells after readout. The optional GL(3,2) branch permits all 168 code-label automorphisms independently (joint B/C retain their paired labeling).', '',
 'The 48 legal isometry/translation embeddings reduce to **six** labeled translation classes under whole-board D4 symmetry. [geometry.json](geometry.json) records every mapping; [geometry.py](geometry.py) exhaustively verifies it. Small-block templates are EXENC/L5’s 11-CX six-layer witness and 12-CX nine-layer witness; B and C use the dual 11-CX encoder. The standard grid-free 9-CX graph has zero direct seven-cell grid embeddings. This closes that fixed-cell graph only, not dynamically routed 9-CX encoders or all possible small encoders.', '',
 'Initial occupancy searches used the stated integer exposure proxy. A four-build nonnegative calibration uses native prefix/data/block exposure features ([calibration.json](calibration.json)); data moves and teleports retain explicit exploratory priors because those four builds do not identify their coefficients. The first placement test exposed an identification failure: B/C exposure was constant in the calibration sample, received zero coefficient, and the optimizer introduced unpriced waits. All six `joint_cal` builds failed acceptance and their exact losses rose to 1.54–4.59e-4. These failed measurements are retained. `joint_safe` adds a lexicographic ALAP tie-break over preparation, prefix, and move times at the same primary proxy optimum. The fit is not validated for separate blocks. “OPTIMAL” below means optimal for the named bounded proxy model, never globally optimal infidelity. Placement-model horizons are R≤60. No UNKNOWN result is called UNSAT.', '',
 '| Embedding class | Block option | Moves | Solver status | Proxy objective | Built? | Exact total | Receipt |',
 '|---|---|---|---|---:|---|---:|---|',
 '| all six (48 embeddings) | standard 9-CX graph | no intra-encoder routing | INFEASIBLE (embedding enumeration) | — | no | — | [geometry](geometry.json) |']
 out+=['| '+' | '.join(row)+' |' for row in models]
 for r in fs:
  if 'solver' in r['meta']:continue
  mm=r['meta'];out.append('| r0c0, retained L5 | joint82 + '+('12-CX A' if mm['args']['exact_a'] else '11-CX A')+f'; reuse={mm["args"]["reuse"]}; {mm["args"]["mode"]} | 6 data; 0 block | {mm["status"]} | {mm["proxy"]} | yes | {fmt(r["score"].get("total"))} | [{r["name"]}]({r["name"]}.json) |')
 out+=['', 'The binding cut for the fixed-label, one-teleport models is the encoder-to-round geometry: an independent placement-only relaxation already returns INFEASIBLE at r0c0 ([receipt](geometry_h1_l5_11.json)), while two teleports admit a geometric witness ([receipt](geometry_h2_l5_11.json)). The full one-teleport time models prove infeasibility in each of the six classes for both tested A templates. These statements do not include the later code-label-permutation branch. Timed two-teleport searches, including calibrated and early-A variants, are reported at their actual termination status; their timeouts do not establish a physical obstruction.', '',
 '## Full circuits', '',
 'R lists A coupling / last B→data CX, measured from `tprep.noise.schedule`. “3rd” is the third-order increment. Exact totals are used only for |c1|<1e-12. exp(-A1) is an acceptance **estimate**. Every listed circuit received `tprep.check(..., shots=10**6, seed=0)`; only full MC finalists receive a final performance rank. MC seeds are 0 / 1000 / 2000 at 1e8 shots each.', '',
 '| Circuit | R native | CX | c1 | 2nd | 3rd | Exact total | exp(-A1), estimate | MC seeds | MC mean | Seed-0 acceptance, 1e8 | Judge 1e6 | Files |',
 '|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|']
 for r in sorted(fs,key=lambda r:r['score'].get('mean',r['score'].get('total',1))):
  s=r['score'];ss=s.get('seeds',[]);nm=r['name'];vals=[nm,r['R'],str(r['cx']),fmt(s.get('c1')),fmt(s.get('second')),fmt(s.get('third')),fmt(s.get('total')),fmt(s.get('exp_A1')),' / '.join(fmt(x['score']) for x in ss) or '—',fmt(s.get('mean')),f'{ss[0]["acceptance"]:.8f}' if ss else '—','PASS' if s['judge_passed'] else 'FAIL',f'[qasm]({nm}.qasm), [json]({nm}.json), [check]({nm}.check.log), [scores]({nm}.score.json)']
  out.append('| '+' | '.join(vals)+' |')
 out+=['', '## Verification and limits', '',
 '- Every generated QASM has sibling metadata with `data_qubits`. The emitter checks every native unit against its requested layer after removing empty global layers; the retained-joint scheduler checks exact native timing equality. [manifest.json](manifest.json) records delivered hashes and native depths.',
 '- Prefix operation provenance is preserved through rescheduling. Native MX folding is retained with `h; measure; h` when the measured physical cell is reused. Full judge correctness checks detector determinism and the actual output state.',
 '- The separate-block emitter implements teleport frames, but a successful separate-block full circuit was not established by the completed searches. Those frame paths remain unverified by a full judge build unless a separate candidate appears in the table above.',
 '- The 15 alternative phase-polynomial prefix forms, additional encoder families, more routing depth, and a general interleaving of encoder CXs with moves remain open. The model moves each wire only after its last encoder CX, and treats each prefix wire as busy from first to last prefix operation; it does not reuse gaps between prefix resets. Early A is tested after that data wire’s prefix operations, rather than commuting it through its final T-dagger.',
 '- All CPU work used zebra (≤8 lane cores) or sunfish (≤24), with BLAS/OpenMP fixed to one and explicit CP-SAT workers. Subprocess exits, not output-file creation, controlled sequencing. No active FREELAY job is intentionally left running at handoff.', '',
 'Reproduction: use the environment `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1` and the project `.venv/bin/python`. `joint_schedule.py --out joint_reuse2_alap --reuse 2 --mode alap` builds the delivery; `evaluate.py joint_reuse2_alap 8 --mc` runs the complete verification. The first finalist also uses the requested unchanged `MAIN/spec/mc3.py`; the second evaluator calls the same `fast_check.check` chunk implementation and seeds, saving full-precision receipts.', '']
 (HERE/'REPORT.md').write_text('\n'.join(out));(HERE/'manifest.json').write_text(json.dumps(manifest,indent=1))
 print('winner',name,w['mean'],'full circuits',len(fs),'models',len(models),flush=True)

def fmt(x):return '—' if x is None else f'{x:.7e}'
if __name__=='__main__':main()

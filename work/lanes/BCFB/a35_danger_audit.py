from a35_prep import *
import stim
records=[]
for dr in ['exenc','exenc14']:
 for l in (D/dr/'pareto_paths.jsonl').open():
  r=json.loads(l);e=r['circuit'];v=proxy(e['ops'],e['pivots'],A,A);assert v==e['danger_vector_units'];assert r['blind']==v[3]+v[4]+v[7] and r['detected']==sum(v)-r['blind']
  sim=stim.TableauSimulator();sim.reset(*A);sim.h(*e['pivots'])
  for layer in e['ops']:
   for a,b in layer:sim.cx(a,b)
  for basis,supps in [('X',[[0,2,4,6],[1,2,5,6],[3,4,5,6],list(range(7))]),('Z',[[0,2,4,6],[1,2,5,6],[3,4,5,6]])]:
   for supp in supps:
    ps=stim.PauliString(36)
    for i in supp:ps[A[i]]=basis
    assert sim.peek_observable_expectation(ps)==1
  records.append(dict(engine=dr,blind=r['blind'],detected=r['detected'],cx=r['cx'],depth=r['depth']))
 summary=dict(verified=len(records),checks='Every Pareto witness independently matches EXENC Python score, flag-conditioned split, and all six code stabilizers plus logical X in Stim.',by_engine=dict(collections.Counter(r['engine'] for r in records)),metrics={dr:sorted(set(tuple(r[k] for k in ['blind','detected','cx','depth']) for r in records if r['engine']==dr)) for dr in ['exenc','exenc14']})
(D/'pareto_independent_audit.json').write_text(json.dumps(summary,indent=2));print(summary['verified'],summary['by_engine'],flush=True)

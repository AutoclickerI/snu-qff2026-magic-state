from build import *
import wide_moments
c=json.loads((V/'guard5_timing_0.plan.json').read_text());r=c['meta']['R']
for delta in [1,2]:
 d=copy.deepcopy(c);name=f'round_delay_{r+delta}'
 for o in d['ops']:
  if o['t']>=r:o['t']+=delta
 # Empty global layers are compressed by the native emitter. Occupy each
 # extra layer with one independent final resource CX, making the added
 # round delay physically representable and keeping all gate counts fixed.
 last=[o for o in d['ops']if o['t']==r-1 and o.get('tag')=='encoder_bc'and unit(o).name=='CX']
 assert len(last)>=delta
 for j,o in enumerate(last[:delta]):o['t']=r+j
 d['meta']['R']=r+delta;st=save(d,'v31/'+name);z=wide_moments.evaluate(exact2.Eval(st.with_suffix('.qasm').read_text(),d['meta']['data_qubits']));st.with_suffix('.screen.json').write_text(json.dumps(z,indent=2));append_result(name,z,'Delay the whole round/readout, placing one independent terminal resource CX in each added native layer. Other prep/prefix operations are fixed. Measures a realizable later-round latency change with unchanged physical gate multiset, not an optimized later-R architecture.');print(name,z,flush=True)

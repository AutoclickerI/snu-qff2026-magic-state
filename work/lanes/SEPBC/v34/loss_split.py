"""Cubic channel-removal ablations, preserving the full detection predicate."""
from design import *
import wide_moments,collections
for name in sys.argv[1:]:
 st=V/name;c=json.loads(st.with_suffix('.plan.json').read_text());txt=st.with_suffix('.qasm').read_text();ev=wide_moments.prepare(exact2.Eval(txt,c['meta']['data_qubits']));R=c['meta']['R'];flat=[(l,o.get('tag','prefix'))for o in c['ops']for l in o['lines']];at=0;tags={}
 for li,line in enumerate(txt.splitlines(),1):
  s=line.strip()
  if not s or s.startswith(('//','barrier','OPENQASM','include','qreg','creg')):continue
  assert s==flat[at][0],(li,s,flat[at]);tags[li]=flat[at][1];at+=1
 regions=[]
 for j,ch in enumerate(ev.m.chans):
  label=ev.chan_label(j)
  regions.append(('pre_round_idle'if ch['gap'][1]+ch['gap'][2]<=R else'round')if ch['gap']is not None else tags[label['line']])
 fp=ev.fp.copy();rows=[]
 tests=[('all',lambda r:False),('no_pre_round_idle',lambda r:r=='pre_round_idle'),('no_BC_encoder',lambda r:r=='encoder_bc'),('no_A_encoder',lambda r:r=='encoder_a'),('no_encoder',lambda r:r.startswith('encoder')),('no_data_hops',lambda r:r=='data_hops'),('no_guard_noise',lambda r:r=='wait_guard'),('only_round',lambda r:r!='round'),('no_prefix',lambda r:r=='prefix')]
 for label,pred in tests:
  ev.fp=fp.copy();ev.fp[[i for i,ch in enumerate(ev.fch)if pred(regions[ch])]]=0
  row=mom.evaluate(ev);row['label']=label;rows.append(row);print(name,label,row['second'],row['third'],row['total'],flush=True)
 out=dict(stem=name,regions=dict(collections.Counter(regions)),rows=rows,note='Counterfactual channel removals are nonadditive. only_round second is the exact round x round pair component. Idle gaps crossing R are grouped with round. No block teleports exist in this family. Operation provenance is in plan.json; source-zero A preparation measurements retain their original source tags.')
 st.with_suffix('.ablation.json').write_text(json.dumps(out,indent=2))

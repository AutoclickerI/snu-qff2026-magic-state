"""Rebuild schedule metadata from native plans, without changing QASM or data order."""
from critical import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args();audit=[]
for f in sorted(V.glob('*.screen.json')):
 name=f.name.removesuffix('.screen.json');st=V/name;c=json.loads(st.with_suffix('.plan.json').read_text());ops=c['ops'];R=c['meta']['R'];before=[o for o in ops if o['t']<R];cuts={};acuts={}
 for q in B+C:
  seq=[o for o in before if q in unit(o).qs];resets=[o for o in seq if unit(o).name in('RESET','RX')];start=resets[-1]if resets else seq[0];assert len(unit(start).qs)==1,(name,q,start);cuts[q]=start['t']
 for q in A:
  seq=[o for o in before if q in unit(o).qs]
  if q in(8,16):
   bit={8:54,16:55}[q];start=next(o for o in seq if f'measure q[{q}] -> c[{bit}];'in o['lines'])
  else:start=[o for o in seq if unit(o).name in('RESET','RX')][-1]
  acuts[q]=start['t']
 changes=[]
 for o in before:
  qs=set(unit(o).qs);new=o['tag']
  if qs<=set(B+C)and all(o['t']>=cuts[q]for q in qs):new='encoder_bc'
  elif qs<=set(A)and all(o['t']>=acuts[q]for q in qs):new='encoder_a'
  if new!=o['tag']:changes.append(dict(lines=o['lines'],t=o['t'],old=o['tag'],new=new));o['tag']=new
 md=dict(data_qubits=c['meta']['data_qubits'],R=R,cx=sum(unit(o).name=='CX'for o in ops),native_depth=max(o['t']for o in ops)+1,
  source='MAIN/v30f'if name!='critical_comp29'else'COMP29/best at recorded source SHA',method=name,
  init_times={str(k):v for k,v in cuts.items()},A_init_times={str(k):v for k,v in acuts.items()},
  roles=dict(data=c['meta']['data_qubits'],A=A,B=B,C=C),
  resource_schedule=[dict(t=o['t'],lines=o['lines'])for o in ops if o['tag']=='encoder_bc'],
  resource_contract='Correlated rank-three B/C resource; native measured-initialization frames are specified by the QASM detector parities.',
  final_role_geometry_changed=False,
  construction_receipt=name+'.build.json',qasm_sha256=json.loads(f.read_text())['sha256'],input_source_qasm_sha256=(json.loads(st.with_suffix('.build.json').read_text()).get('source_sha256') or hashlib.sha256((H/'inputs/v30f.qasm').read_bytes()).hexdigest()))
 c['meta']=md
 if a.apply:
  st.with_suffix('.json').write_text(json.dumps(md,indent=2));st.with_suffix('.plan.json').write_text(json.dumps(c,indent=1))
 audit.append(dict(stem=name,region_changes=changes,old_init_times_replaced=a.apply,gate_program_unchanged=True))
(V/'metadata_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps([r for r in audit if r['region_changes']],indent=2))

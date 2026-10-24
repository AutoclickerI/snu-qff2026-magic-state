"""Refresh descriptive metadata from each emitted physical schedule."""
from build import *
rows=[]
for path in V.glob('*.plan.json'):
 name=path.name.removesuffix('.plan.json');st=V/name
 if name.startswith('round_hold_'):continue
 c=json.loads(path.read_text());md=c['meta'];R=md['R'];ops=c['ops'];actual=read(st)
 assert all(o['t']==p['t']and o['lines']==p['lines']for o,p in zip(ops,actual['ops'])),name
 roundop=[o for o in ops if o['lines']==['cx q[0],q[1];']]
 assert roundop[-1]['t']==R,(name,roundop[-1]['t'],R)
 md['source']='MAIN/v31s; COMP29/best mechanisms; EXENC reoriented A; WAITPROT storage-guard mechanism where present'
 md['method']='SEPBC v31 native schedule composition; exact recipe is the sibling plan.json'
 md['construction_receipt']=name+'.plan.json';md['qasm_sha256']=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest();md['input_source_qasm_sha256']=hashlib.sha256((H/'inputs/v31s.qasm').read_bytes()).hexdigest()
 bc=[o for o in ops if o.get('tag')=='encoder_bc'];aa=[o for o in ops if o.get('tag')=='encoder_a'];md['resource_schedule']=[dict(t=o['t'],lines=o['lines'])for o in bc];md['init_times']={q:min(o['t']for o in bc if int(q)in unit(o).qs)for q in map(str,B+C)if any(int(q)in unit(o).qs for o in bc)}
 md.pop('A_init_times',None);md['A_input_plan']={}
 for q in A:
  gates=[o for o in aa if unit(o).name=='CX'and q in unit(o).qs]
  if not gates:continue
  first=min(o['t']for o in gates);pre=[o for o in ops if o['t']<first and unit(o).qs==(q,)]
  if pre:md['A_input_plan'][q]=dict(last_single_qubit_operation_t=pre[-1]['t'],last_single_qubit_operation=pre[-1]['lines'],first_encoder_CX_t=first)
 md['wait_guards']=[dict(t=o['t'],lines=o['lines'])for o in ops if o.get('tag')=='wait_guard']
 md['cx']=sum(unit(o).name=='CX'for o in ops);md['native_depth']=max(o['t']for o in ops)+1
 st.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n');path.write_text(json.dumps(c,indent=1)+'\n');rows.append(dict(stem=name,R=R,cx=md['cx'],sha256=md['qasm_sha256']))
(V/'metadata_audit.json').write_text(json.dumps(rows,indent=2));print('audited',len(rows),'metadata files',flush=True)

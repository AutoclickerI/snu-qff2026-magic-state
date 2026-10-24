from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args();base=read(a.stem)
for family in ['teleport','coherent']:
 c=copy.deepcopy(base);ops=c['ops']
 def find(line):return next(o for o in ops if line in o['lines'])
 m9=find('measure q[9] -> c[9];');last=max((o for o in ops if o['lines']==['cx q[9],q[15];'] and o['t']<m9['t']),key=lambda o:o['t'])
 t=last['t'];tdg=find('tdg q[15];');m9=find('measure q[9] -> c[9];')
 init=find('measure q[16] -> c[43];');fw=find('cx q[15],q[16];');bw=find('cx q[16],q[15];')
 init['t']=t-6;fw['t']=t-5;bw['t']=t-4
 last['lines']=['cx q[15],q[16];'];last['t']=t+1 if family=='teleport'else t+2
 tdg['lines']=['tdg q[16];'];tdg['t']=last['t']+1
 m9['lines']=['h q[15];','measure q[15] -> c[9];'];m9['t']=last['t']+1
 watch=find('measure q[15] -> c[53];');watch['lines']=['reset q[15];'];watch['t']=max(watch['t'],m9['t']+1)
 c['tail']=[l for l in c['tail']if l!='// DETECTOR c[53]']
 ops.append(dict(id=1000,lines=['cx q[9],q[15];'],t=t))
 if family=='teleport':
  ops.append(dict(id=1001,lines=['h q[9];','measure q[9] -> c[90];','h q[9];'],t=t+1))
  c['tail']=[l+' c[90]'if re.search(r'c\[9\](?!\d)',l)else l for l in c['tail']]
 else:ops.append(dict(id=1001,lines=['cx q[15],q[9];'],t=t+1))
 # CP-SAT repair physical ordering, allowing retargeted prefix and reuse to shift.
 for o in ops:
  if o['lines']==['reset q[9];']:o['t']=max(o['t'],t+2)
 c['meta']['st1_change']='Early data15→16; cat9→15 '+family+'; retarget final cultivation CX and TDG; reset source after cat readout'
 for mode in ['near','alap']:
  d,rec=schedule(c,mode=mode)
  if d:
   name=Path(a.stem).name+'_early15_'+family+'_'+mode
   try:s=save(d,name);r=score(s);append_result(name,r,'Data moved before its last cultivation interaction; cat relocated to vacated source. '+json.dumps(rec));print(name,r,flush=True)
   except Exception as e:append_result(name,dict(error=str(e)),'Build failed; no physics conclusion');print(name,repr(e),flush=True)

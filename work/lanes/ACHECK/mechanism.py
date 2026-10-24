from common import *
import exact2,numpy as np
from collections import defaultdict

h,units,tail,times,meta,init,ai=base()
text=(HERE/'base.qasm').read_text();ev=exact2.Eval(text,D)
pre=set(meta['prefix_unit_indices']);qmap=S.native_qasm_index(text)
raw_to_unit={j:i for i,u in enumerate(units) for j in u.raw_indices}
def label(ch):
 ins=ev.m.prog[ch['ins']];lab=ev.m.labels[ins.line_no-1]
 mt=re.match(r'instruction (\d+)',lab)
 i=raw_to_unit.get(qmap.get(int(mt.group(1)))) if mt else None
 qs=set(ch['qubits']);t=times[i] if i is not None else 99
 if ch['gap'] is not None:
  q,first,n=ch['gap']
  if q in A and first>times[init[q]]:return 'A_idle'
  if i in pre:return 'pre_idle'
  if q in D or (i is not None and units[i].name=='CX' and not qs<=set(B+C)):
   return 'round_data_idle' if t>=45 else 'data_idle'
  return 'BC_idle' if qs<=set(B+C) else 'hop_idle'
 if i in ai:return 'A_init' if units[i].name in ('RX','RESET') else 'A_CX'
 if t>=46 and qs&set(A):return 'A_readout'
 if i in pre:return 'pre_gate'
 if t>=45:return 'round_gate'
 if qs<=set(B+C):return 'BC_gate'
 return 'hop_gate'

labels=[label(ch) for ch in ev.m.chans];fl=[labels[c] for c in ev.fch]
procs=int(sys.argv[1]) if len(sys.argv)>1 else 16
r=exact2.run(ev,procs,keep_thr=1e-18,third=True)
t3,big3=exact2.third_order(ev,procs)
pairs=defaultdict(float)
for val,i,j,*_ in r['big']:pairs[' × '.join(sorted([fl[i],fl[j]]))]+=val
out=dict(c1=r['loss1'],second=r['loss'],third=t3+r['t3bc'],total=r['loss']+t3+r['t3bc'],exp_A1=float(np.exp(-r['A1'])),pairs=dict(sorted(pairs.items(),key=lambda x:-x[1])),
 top_A_pairs=[dict(loss=v,families=[fl[i],fl[j]],faults=[ev.fault_label(i),ev.fault_label(j)]) for v,i,j,*_ in sorted(r['big'],reverse=True) if fl[i].startswith('A_') or fl[j].startswith('A_')][:80],
 top_A_triples=[dict(loss=v,families=[fl[i],fl[j],fl[k]],faults=[ev.fault_label(i),ev.fault_label(j),ev.fault_label(k)]) for v,i,j,k in sorted(big3,reverse=True) if any(fl[x].startswith('A_') for x in (i,j,k))][:80],
 channels=[dict(label=lab,**ev.chan_label(c)) for c,lab in enumerate(labels)],ablations={})
path=HERE/'mechanism.json'
def save():path.write_text(json.dumps(out,indent=1))
save();print('base',out['total'],flush=True)
fp=ev.fp.copy()
for family in ['A_init','A_CX','A_idle','A_readout','A_prep','A_all']:
 ev.fp=fp.copy()
 names={'A_init','A_CX'} if family=='A_prep' else ({'A_init','A_CX','A_idle','A_readout'} if family=='A_all' else {family})
 ev.fp[np.array([x in names for x in fl])]=0
 rr=exact2.run(ev,procs,keep_thr=1,third=True);tt,_=exact2.third_order(ev,procs)
 out['ablations'][family]=dict(second=rr['loss'],third=tt+rr['t3bc'],total=rr['loss']+tt+rr['t3bc'],exp_A1=float(np.exp(-rr['A1'])))
 save();print(family,out['ablations'][family],flush=True)

from common import *
from variants import retime
txt=(ROOT/'work/lanes/FREELAY/inputs/encoder19.qasm').read_text();h,r,tail=S.qasm_ops(txt);uu=S.fold_units(r);tt=native_times(txt,uu)
pre=[u for u,t in zip(uu,tt) if t<=29]
prebits={int(x) for u in pre for l in u.lines for x in re.findall(r'c\[(\d+)\]',l)}
pd=[l for l in tail if set(map(int,re.findall(r'c\[(\d+)\]',l)))<=prebits]
def remap(l):return re.sub(r'c\[(\d+)\]',lambda m:f'c[{int(m[1])+100 if int(m[1])>=14 else int(m[1])}]',l)
pre=[unit([remap(l) for l in u.lines]) for u in pre];pd=[remap(l) for l in pd]
for reuse in [False,True]:
 txt=(ROOT/'work/lanes/LAYOUT2/best.qasm').read_text();h,r,tail=S.qasm_ops(txt);uu=S.fold_units(r);tt=native_times(txt,uu)
 suffix=[u for u,t in zip(uu,tt) if t>=33];old=[t-54+45 for u,t in zip(uu,tt) if t>=33]
 det=pd+[l for l in tail if not set(map(int,re.findall(r'c\[(\d+)\]',l)))<=set(range(14))]
 units=copy.deepcopy(pre)+suffix;ts=[0]*len(pre)+old
 if reuse:
  # Use preceding deterministic MX on cell 13 as A's |+> pivot if available.
  pass
 rid={i for i,t in enumerate(ts) if t>=45}
 ts,R=retime(units,ts,rid)
 emit('layout2_alap',units,ts,det,dict(R=R,method='new A layout + logical-X cat, ALAP prefix',data_qubits=[7,25,19,16,15,17,8]))
 break

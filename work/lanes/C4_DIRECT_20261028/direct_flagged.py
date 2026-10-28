import os,sys,json,copy,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import smallcat as s
from joint import emit
F=s.f;tiles=[(4*i,4*i+1,4*i+2,4*i+3) for i in range(7)];out=[x[1] for x in tiles];meters=list(range(28,35));GEN=[{0,2,4,6},{1,2,5,6},{3,4,5,6}];ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]];piv={0,1,3}
ops=[];ds=[];bit=0
def op(k,q,t,b=None):ops.append(F.Op(k,tuple(q),t,b))
def logical_cx(a,b,t):
 for x,y in zip(tiles[a],tiles[b]):op('CX',(x,y),t)
def meterprep(t,plus):
 for i,q in enumerate(meters):op('RX' if ((i not in piv) if plus else (i in piv)) else 'R',(q,),t)
 for j,layer in enumerate(ENC):
  for a,b in layer:op('CX',(meters[b],meters[a]) if plus else(meters[a],meters[b]),t+1+j)
def meas(qs,t,k):
 global bit
 bits=[]
 for q in qs:op(k,(q,),t,bit);bits.append(bit);bit+=1
 return bits
for i,(h,d,l,k) in enumerate(tiles):
 op('RX',(h,),0);op('RX' if i in piv or i==2 else 'R',(d,),0);op('R',(l,),0);op('R',(k,),0)
 op('CX',(h,d),1);op('CX',(d,k),2);op('CX',(h,l),2)
h,d,_,_=tiles[2];op('CX',(h,d),3);op('T',(d,),4);op('CX',(h,d),5)
logical_cx(2,4,6);logical_cx(2,5,7)
for j,layer in enumerate(ENC):
 for a,b in layer:logical_cx(a,b,8+j)
# Outer Steane Z syndrome with an unencoded plus-L meter. Never measure logical Z.
meterprep(11,True)
for i,(h,d,l,k) in enumerate(tiles):op('CX',(h,meters[i]),15);op('CX',(d,meters[i]),16)
b=meas(meters,17,'M')
for S in GEN:ds.append({b[i] for i in S})
# Outer X syndrome, zero-L meter controls both X logical representatives.
meterprep(18,False)
for i,(h,d,l,k) in enumerate(tiles):op('CX',(meters[i],d),22);op('CX',(meters[i],k),23)
b=meas(meters,24,'MX')
for S in GEN:ds.append({b[i] for i in S})
# Logical T enters the two shared U-check rounds.
for h,d,l,k in tiles:op('CX',(h,d),25);op('T',(d,),26);op('CX',(h,d),27)
def cat(t):
 for i,q in enumerate(meters):op('RX' if i==0 else 'R',(q,),t)
 for j,layer in enumerate([[(0,1)],[(0,2),(1,3)],[(0,4),(1,5),(2,6)]]):
  for a,b in layer:op('CX',(meters[a],meters[b]),t+1+j)
 for a,b in ((1,2),(0,4)):op('CX',(meters[a],meters[b]),t+4)
 b=meas([meters[2],meters[4]],t+5,'M')
 for z in b:ds.append({z})
 for a,b in ((1,2),(0,4)):op('CX',(meters[a],meters[b]),t+6)
 for i,(h,d,l,k) in enumerate(tiles):op('CX',(meters[i],d),t+7);op('CX',(meters[i],k),t+8)
 b=meas(meters,t+9,'MX');ds.append(set(b))
cat(25);cat(35)
for h,d,l,k in tiles:op('CX',(h,d),44);op('TDG',(d,),45);op('CX',(h,d),46)
# Two clock tile inverse; K,L zero measurements are physical checks.
for h,d,l,k in tiles:op('CX',(d,k),47);op('CX',(h,l),47);op('CX',(h,d),48)
b=meas([q for h,d,l,k in tiles for q in (k,l)],48,'M')
for x in b:ds.append({x})
ops.sort(key=lambda o:(o.time,o.kind,o.qs));occ=set()
for o in ops:
 for q in o.qs:assert (o.time,q) not in occ,(o.time,q,o.kind);occ.add((o.time,q))
text=emit(ops,ds);stem=H/'direct_flagged';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':out,'abstract':True,'tiles':tiles,'flags':'two in-place cat parity checks per round','source':'direct 28-qubit concatenated C4/Steane'},indent=2)+'\n')
raw=s.ideal_contract_check(text,out);print('RAW',json.dumps(raw),flush=True)
r={'stem':str(stem),'raw':raw,'cx':sum(o.kind=='CX'for o in ops),'clocks':max(o.time for o in ops)+1,'T':sum(o.kind in ('T','TDG') for o in ops),'detectors':len(ds),'abstract':True}
if raw['ok']:
 s.f.DATA=out;a=s.record_contract.singles(s.f.make_model(*s.f.parse_current(text)));r['singles']=a;print('SINGLES',a['c1'],len(a['harmful_faults']),flush=True)
 (H/'direct_flagged.result.json').write_text(json.dumps(r,indent=2)+'\n')
 print('PRICE_START',flush=True);v=s.exact(stem);r['exact']=v;print('RESULT',v['loss'],v['acceptance'],flush=True)
(H/'direct_flagged.result.json').write_text(json.dumps(r,indent=2)+'\n')

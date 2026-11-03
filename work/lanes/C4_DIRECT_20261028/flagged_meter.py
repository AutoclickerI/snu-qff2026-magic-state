import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import smallcat as s
from joint import emit
F=s.f;tiles=[(4*i,4*i+1,4*i+2,4*i+3)for i in range(7)];out=[x[1]for x in tiles];meters=list(range(28,35));GEN=[{0,2,4,6},{1,2,5,6},{3,4,5,6}];ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]];piv={0,1,3};ops=[];ds=[];bit=0
def op(k,q,t,b=None):ops.append(F.Op(k,tuple(q),t,b))
def meas(qs,t,k):
 global bit
 b=[]
 for q in qs:op(k,(q,),t,bit);b.append(bit);bit+=1
 return b
for i,(h,d,l,k) in enumerate(tiles):
 for kind,q in [('RX',h),('RX' if i in piv or i==2 else 'R',d),('R',l),('R',k)]:op(kind,(q,),0)
 op('CX',(h,d),1);op('CX',(d,k),2);op('CX',(h,l),2)
h,d,_,_=tiles[2];op('CX',(h,d),3);op('T',(d,),4);op('CX',(h,d),5)
for t,a,b in [(6,2,4),(7,2,5)]:
 for x,y in zip(tiles[a],tiles[b]):op('CX',(x,y),t)
for j,layer in enumerate(ENC):
 for a,b in layer:
  for x,y in zip(tiles[a],tiles[b]):op('CX',(x,y),8+j)
# Serial three physical SpiderCSS flags on a single q35; this prepares an unencoded 0L outer-X meter.
seq=json.load(open(H/'spider_serial.json'))['operations'];perm=(0,1,4,2,5,6,3);mp={x:meters[j]for j,x in enumerate(perm)};mp.update({7:35,8:35,9:35})
for z in sorted(seq,key=lambda x:x['time']):
 qs=tuple(mp[q] for q in z['qs']);v=bit if z['kind']=='M' else None;op(z['kind'],qs,z['time'],v)
 if v is not None:ds.append({bit});bit+=1
for i,(h,d,l,k) in enumerate(tiles):op('CX',(meters[i],d),18);op('CX',(meters[i],k),19)
b=meas(meters,20,'MX')
for S in GEN:ds.append({b[i] for i in S})
# Outer Z meter is plusL so its logical Z outcome remains random and does not measure the magic state.
for i,q in enumerate(meters):op('RX' if i not in piv else 'R',(q,),21)
for j,layer in enumerate(ENC):
 for a,b in layer:op('CX',(meters[b],meters[a]),22+j)
for i,(h,d,l,k) in enumerate(tiles):op('CX',(h,meters[i]),25);op('CX',(d,meters[i]),26)
b=meas(meters,27,'M')
for S in GEN:ds.append({b[i] for i in S})
for h,d,l,k in tiles:op('CX',(h,d),28);op('T',(d,),29);op('CX',(h,d),30)
def cat(t):
 for i,q in enumerate(meters):op('RX' if i==0 else 'R',(q,),t)
 op('R',(35,),t)
 for j,layer in enumerate([[(0,1)],[(0,2),(1,3)],[(0,4),(1,5),(2,6)]]):
  for a,b in layer:op('CX',(meters[a],meters[b]),t+1+j)
 op('CX',(meters[1],35),t+4);op('CX',(meters[2],35),t+5);b=meas([35],t+6,'M');ds.append({b[0]})
 op('R',(35,),t+7);op('CX',(meters[0],35),t+8);op('CX',(meters[1],35),t+9);b=meas([35],t+10,'M');ds.append({b[0]})
 for i,(h,d,l,k) in enumerate(tiles):op('CX',(meters[i],d),t+11);op('CX',(meters[i],k),t+12)
 b=meas(meters,t+13,'MX');ds.append(set(b))
cat(28);cat(42)
for h,d,l,k in tiles:op('CX',(h,d),55);op('TDG',(d,),56);op('CX',(h,d),57)
for h,d,l,k in tiles:op('CX',(d,k),58);op('CX',(h,l),58);op('CX',(h,d),59)
b=meas([q for h,d,l,k in tiles for q in (k,l)],59,'M')
for z in b:ds.append({z})
ops.sort(key=lambda o:(o.time,o.kind,o.qs));busy=set()
for o in ops:
 for q in o.qs:assert(o.time,q)not in busy,(o.time,q,o.kind);busy.add((o.time,q))
text=emit(ops,ds);stem=H/'flagged_meter';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':out,'abstract':True,'tiles':tiles,'meter':'serial SpiderCSS 0L on shared flag','cat_flags':'two q35 parity checks per round'},indent=2)+'\n')
raw=s.ideal_contract_check(text,out);print('RAW',json.dumps(raw),flush=True)
r={'stem':str(stem),'raw':raw,'cx':sum(o.kind=='CX'for o in ops),'clocks':max(o.time for o in ops)+1,'T':sum(o.kind in ('T','TDG')for o in ops),'detectors':len(ds)}
if raw['ok']:
 s.f.DATA=out;aud=s.record_contract.singles(s.f.make_model(*s.f.parse_current(text)));r['singles']=aud;print('SINGLES',aud['c1'],len(aud['harmful_faults']),flush=True);(H/'flagged_meter.result.json').write_text(json.dumps(r,indent=2)+'\n')
 print('PRICE_START',flush=True);v=s.exact(stem);r['exact']=v;print('RESULT',v['loss'],v['acceptance'],flush=True)
(H/'flagged_meter.result.json').write_text(json.dumps(r,indent=2)+'\n')

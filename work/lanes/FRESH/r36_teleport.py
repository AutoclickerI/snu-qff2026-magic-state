from round35 import *
from r36_static import diagnostic
import stim,itertools
OUT=HERE/'r36';pre=json.loads((OUT/'prefix_release.json').read_text());A=[1,14,8,9,2,16,15];data=pre['meta']['data_qubits'];ROWS=f.SUPPORTS
# Catalog all grid A0 encoders for the fixed logical labeling.
def rowkey(rows):
 rr=list(rows)
 for i in range(3):
  j=min(range(i,3),key=lambda j:(rr[j]&-rr[j]).bit_length());rr[i],rr[j]=rr[j],rr[i];b=rr[i]&-rr[i]
  for j in range(3):
   if j!=i and rr[j]&b:rr[j]^=rr[i]
 return sum(r<<(7*i) for i,r in enumerate(rr))
info=json.loads((ROOT/'work/lanes/BCFB/a30/inputs/library_input.json').read_text());enc=[]
for kind in ('library_encoders','library_depth_encoders'):
 lib=json.loads((ROOT/f'work/lanes/BCFB/a30/inputs/{kind}.json').read_text())
 for emb in info['embeddings']:
  sid,*qs=emb
  if set(qs)!=set(A):continue
  perm=[qs.index(q) for q in A];cid=info['targets'].index(rowkey([sum(1<<perm[i] for i in row) for row in ROWS]));e=lib[sid][cid]
  enc.append(dict(name=f'{kind}_{sid}_{cid}_{qs}',pivots=[qs[i] for i in e['pivots']],ops=[(qs[a],qs[b]) for a,b in e['ops']]))
for e in json.loads((ROOT/'work/lanes/BCFB/a30/inputs/acheck_encoders.json').read_text()):
 enc.append(dict(name='acheck',pivots=list(set(A)-set(e['pivots'])),ops=[(b,a) for layer in e['ops'] for a,b in layer]))
seen=set();valid=[]
for e in enc:
 key=(tuple(sorted(e['pivots'])),tuple(e['ops']))
 if key in seen:continue
 seen.add(key)
 # Fresh resets on every A wire eliminate reused-source residual cones.
 nxt={q:44 for q in A};fresh=[]
 for a,b in reversed(e['ops']):
  t=min(nxt[a],nxt[b])-1;fresh.append(f.Op('CX',(a,b),t));nxt[a]=nxt[b]=t
 for q in A:fresh.append(f.Op('RX' if q in e['pivots'] else 'R',(q,),nxt[q]-1))
 if any(nxt[q]-1<=pre['release'][str(q)] for q in A):continue
 valid.append((e,fresh))
print('CATALOG',len(seen),'FITS',len(valid),flush=True)
out=[]
for k,(e,fresh) in enumerate(valid):
 if k>=8:break
 oo=[f.Op(o['kind'],tuple(o['qs']),o['time'],o['bit'],o['line']) for o in pre['ops']]
 # Remove A terminal decoder/readout. Keep only its seven D->A couplings.
 oo=[o for o in oo if not (o.time>=43 and (o.bit in range(14,21) if o.bit is not None else False)) and not (o.time>=44 and o.kind=='CX' and (set(o.qs)<=set(A) or o.qs==(17,16)))]
 for o in oo:
  if o.kind=='CX' and o.qs in list(zip(data,A)) and o.time>=43:o.time=44
 dd=[set(row) for row in pre['dets'] if not(set(row)&set(range(14,21)))]
 for j,q in enumerate(data):oo.append(f.Op('MX',(q,),46,400+j))
 dd += [{400+j for j in row} for row in ROWS]
 oo+=copy.deepcopy(fresh)
 md=dict(data_qubits=A,R=44)
 stem=emit(f'teleport0_{k}',oo,dd,md,dict(base='MAIN/v35b',encoder=e,prefix_moves=pre['moves'],architecture='encoded identity teleport, output A, logical Z frame from D MX'))
 with stem.with_suffix('.qasm').open('a') as ff:ff.write('// FRAME_Z(0) '+' '.join(f'c[{400+j}]' for j in range(7))+'\n')
 f.FRAME_Z=list(range(400,407));f.FRAME_X=[]
 r=dict(stem=str(stem))
 try:
  r['ideal']=certify(stem);st=diagnostic(stem);r['failed_atoms']=st['failed_atoms'];r['speed']=speed(stem,5000);out.append(str(stem));print('VALID',json.dumps({k:v for k,v in r.items() if k!='ideal'}),flush=True)
 except Exception as ex:print('REJECT',stem.name,repr(ex),flush=True)
 f.FRAME_Z=[]
(OUT/'teleport_stems.json').write_text(json.dumps(out,indent=2))

from round35 import *
from r36_static import diagnostic
from itertools import product
OUT=HERE/'r36';src=ROOT/'work/lanes/MAIN/v35b';ops,dets,md=load(src);A=[1,14,8,9,2,16,15];data=md['data_qubits'];ROWS=f.SUPPORTS
# Preserve all pre-A source measurements; replace only the final |+L> encoder/checks.
init={1:38,14:38,8:36,9:38,2:38,16:41,15:40}
# q9/q15/q16 old known-zero M is a SOURCE flag, so keep it.
old={i for i,o in enumerate(ops) if set(o.qs)<=set(A) and all(o.time>=init[q] for q in o.qs) and o.time<=43}
# D->A outside A are untouched by this selector.
print('oldCX',sum(ops[i].kind=='CX' for i in old),flush=True)
assert sum(ops[i].kind=='CX' for i in old)==11
oldbits={ops[i].bit for i in old if ops[i].bit is not None}
keep=[copy.deepcopy(o) for i,o in enumerate(ops) if i not in old and not(o.kind=='CX' and o.qs==(17,16) and o.time==45)]
release={q:max(o.time for o in keep if q in o.qs and o.time<43) for q in A}
# Restrict releases to source last-use (not old round-readout).
release.update({1:37,14:37,8:35,9:37,2:37,16:40,15:39})
for o in keep:
 if o.bit==55:o.time=37
release[16]=37
knownplus={2,14};zero=set(A)-knownplus

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
# Also dualize previously explored 4-pivot A+ encoders.
for e in json.loads((ROOT/'work/lanes/BCFB/a30/inputs/acheck_encoders.json').read_text()):
 enc.append(dict(name='acheck',pivots=list(set(A)-set(e['pivots'])),ops=[(b,a) for layer in e['ops'] for a,b in layer]))
seen=set();fits=[]
for e in enc:
 key=(tuple(sorted(e['pivots'])),tuple(e['ops']))
 if key in seen:continue
 seen.add(key)
 nxt={q:43 for q in A};fresh=[]
 for a,b in reversed(e['ops']):
  at=min(nxt[a],nxt[b])-1;fresh.append(f.Op('CX',(a,b),at));nxt[a]=nxt[b]=at
 valid=True
 for q in A:
  if (q in e['pivots'])==(q in knownplus):
   if nxt[q]<=release[q]:valid=False;break
  else:
   at=nxt[q]-1
   if at<=release[q]:valid=False;break
   fresh.append(f.Op('RX' if q in e['pivots'] else 'R',(q,),at))
 if not valid:continue
 fits.append((e,fresh))
print('UNIQUE',len(seen),'FITS',len(fits),'release',release,flush=True)
(OUT/'dual_feasibility.json').write_text(json.dumps(dict(unique=len(seen),fits=len(fits),release=release,scope='library encoders, fixed wire order ALAP; no infeasibility claim beyond catalog'),indent=2))
stems=[]
for k,(e,fresh) in enumerate(fits):
 oo=copy.deepcopy(keep);dd=[copy.deepcopy(row) for row in dets if not row&oldbits]
 for row in dd:
  if row&set(range(14,21)):row.discard(24)
 for o in oo:
  if o.kind=='CX' and o.qs in [(q,a) for q,a in zip(data,A)] and o.time>=43:o.qs=o.qs[::-1];o.time=43
  elif o.kind=='CX' and o.time>=44 and set(o.qs)<=set(A):o.qs=o.qs[::-1]
  elif o.kind in ('MX','M') and o.bit in range(14,21):o.kind='M' if o.kind=='MX' else 'MX'
  elif o.kind=='TDG' and o.qs[0] in (10,20) and o.time>=42:o.time=41
 for q in data:oo.extend([f.Op('SDG',(q,),42),f.Op('S',(q,),44)])
 oo+=copy.deepcopy(fresh)
 try:
  stem=emit(f'dualY_{k:03}',oo,dd,md,dict(base=str(src),encoder=e,source_flags_preserved=True,removed_prepcheck_bits=sorted(oldbits),removed_readout_edge=[17,16],Y_check_at=43))
  ideal=certify(stem);st=diagnostic(stem);print(stem.name,'IDEAL',ideal['c1'],'BADATOMS',st['failed_atoms'],flush=True)
  (OUT/(stem.name+'.static.json')).write_text(json.dumps(st,indent=2));stems.append(str(stem))
 except Exception as ex:print('ERROR',k,repr(ex),flush=True)
(OUT/'dual_stems.json').write_text(json.dumps(stems,indent=2))

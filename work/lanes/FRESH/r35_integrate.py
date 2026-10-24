from round35 import *

def reset_pivots():
 ops,dets,md=load(D/'sx_full');stems=[]
 for mask in range(1,8):
  oo=copy.deepcopy(ops);dd=copy.deepcopy(dets);removed=[]
  for j,q in enumerate((26,17,28)):
   if not (mask>>j&1):continue
   xs=[o for o in oo if o.qs==(q,) and o.kind=='MX' and o.time==32];assert len(xs)==1
   op=xs[0];bit=op.bit;op.kind='RX';op.bit=None;removed.append(bit)
   for row in dd:row.discard(bit)
  dd=[row for row in dd if row]
  stems.append(emit(f'sx_reset_{mask}',oo,dd,md,dict(reset_pivots=mask,removed_bits=removed)))
 return stems

def encoders():
 ops,dets,md=load(BASE);A=[1,14,8,9,2,16,15]
 starts={1:(38,'RX'),14:(38,'RX'),8:(36,'RX'),9:(37,'M'),2:(38,'RX'),16:(40,'M'),15:(39,'M')}
 own={i for i,o in enumerate(ops) if set(o.qs)<=set(A) and o.time<43 and all(o.time>=starts[q][0] for q in o.qs)}
 # The two last preparation gates at43 also belong to A prep.
 own|={i for i,o in enumerate(ops) if o.time==43 and o.kind=='CX' and o.qs in ((1,2),(8,14))}
 assert sum(ops[i].kind=='CX' for i in own)==11
 bits={ops[i].bit for i in own if ops[i].bit is not None}
 out=[]
 for name in ('encoders_00000','encoders_00002'):
  payload=json.loads((ROOT/f'work/lanes/BCFB/a34/candidates/{name}.json').read_text());enc=payload['options']['enc'];piv=set(enc['pivots'])
  for checks in ([1,2,9],[],[1,2,9,14]):
   oo=[copy.deepcopy(o) for i,o in enumerate(ops) if i not in own];dd=[copy.deepcopy(row) for row in dets if not row&bits]
   deadlines={q:min(o.time for o in oo if q in o.qs and o.time>=43) for q in A};fresh=[];nxt=dict(deadlines)
   for a,b in reversed(enc['ops']):
    at=min(nxt[a],nxt[b])-1;fresh.append(f.Op('CX',(a,b),at));nxt[a]=nxt[b]=at
   releases={q:max(o.time for o in oo if q in o.qs and o.time<43) for q in A}
   try:
    for q in A:
     at=nxt[q]-1
     if q in checks:
      bit=310+q;fresh.append(f.Op('MX' if q in piv else 'M',(q,),at,bit));dd.append({bit});at-=1
     if q==15:
      # Reuse the known-zero output of the data move. c57 check was in OWN.
      assert q not in piv and nxt[q]>releases[q]
     else:
      assert at>releases[q],(q,at,releases[q])
      if q in (8,9,16) and q not in piv:
       bit=350+q;fresh.append(f.Op('M',(q,),at,bit));dd.append({bit})
      else:fresh.append(f.Op('RX' if q in piv else 'R',(q,),at))
    oo+=fresh
    stem=emit(f'bcfb_{name}_c'+''.join(map(str,checks)),oo,dd,md,dict(external=f'BCFB/a34/candidates/{name}',encoder=enc,checks=checks,reuse_zero15=True,removed_bits=sorted(bits)))
    certify(stem);out.append(stem)
   except Exception as e:print('INFEASIBLE',name,checks,repr(e),flush=True)
 return out

if __name__=='__main__':
 stems=reset_pivots() if sys.argv[1]=='reset' else encoders()
 (D/(sys.argv[1]+'_stems.json')).write_text(json.dumps(list(map(str,stems)),indent=2))
 if sys.argv[1]=='reset':
  for stem in stems:
   try:
    certify(stem);print(stem.name,speed(stem,5000),flush=True)
   except Exception as e:print(stem.name,'ERROR',repr(e),flush=True)

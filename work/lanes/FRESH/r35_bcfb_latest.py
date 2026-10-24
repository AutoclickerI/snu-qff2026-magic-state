from round35 import *

def generate():
 ops,dets,md=load(BASE);A=[1,14,8,9,2,16,15]
 starts={1:(38,'RX'),14:(38,'RX'),8:(36,'RX'),9:(37,'M'),2:(38,'RX'),16:(40,'M'),15:(39,'M')}
 own={i for i,o in enumerate(ops) if set(o.qs)<=set(A) and o.time<43 and all(o.time>=starts[q][0] for q in o.qs)}
 own|={i for i,o in enumerate(ops) if o.time==43 and o.kind=='CX' and o.qs in ((1,2),(8,14))}
 assert sum(ops[i].kind=='CX' for i in own)==11
 oldbits={ops[i].bit for i in own if ops[i].bit is not None};out=[]
 for name in ('encoders_00013','encoders_00014','encoders_00004','encoders_00009'):
  payload=json.loads((ROOT/f'work/lanes/BCFB/a34/candidates/{name}.json').read_text());spec=payload['options'];enc=spec['enc'];piv=set(enc['pivots'])
  for checks in (spec['checks'],[],[1,2]):
   for reuse15 in (False,True):
    oo=[copy.deepcopy(o) for i,o in enumerate(ops) if i not in own];dd=[copy.deepcopy(row) for row in dets if not row&oldbits]
    deadlines={q:min(o.time for o in oo if q in o.qs and o.time>=43) for q in A};fresh=[];nxt=dict(deadlines)
    for a,b in reversed(enc['ops']):
     at=min(nxt[a],nxt[b])-1;fresh.append(f.Op('CX',(a,b),at));nxt[a]=nxt[b]=at
    releases={q:max(o.time for o in oo if q in o.qs and o.time<43) for q in A}
    try:
     for q in A:
      at=nxt[q]-1
      if q in checks:
       bit=310+q;fresh.append(f.Op('MX' if q in piv else 'M',(q,),at,bit));dd.append({bit});at-=1
      if q==14 or (q==15 and reuse15):
       assert (q in piv)==(q==14) and nxt[q]>releases[q]
       if q in checks:assert at+1>releases[q]
      else:
       assert at>releases[q],(q,at,releases[q])
       if q in (8,9,15,16) and q not in piv:
        bit=350+q;fresh.append(f.Op('M',(q,),at,bit));dd.append({bit})
       else:fresh.append(f.Op('RX' if q in piv else 'R',(q,),at))
     stem=emit('bcfb2_'+name+'_c'+''.join(map(str,checks))+f'_r{int(reuse15)}',oo+fresh,dd,md,dict(imported=f'BCFB/a34/candidates/{name}',encoder=enc,checks=checks,reuse14=True,reuse15=reuse15,removed_bits=sorted(oldbits)))
     out.append(stem)
    except Exception as e:print('INFEASIBLE',name,checks,reuse15,repr(e),flush=True)
 (D/'bcfb2_stems.json').write_text(json.dumps(list(map(str,dict.fromkeys(out))),indent=2))
 print('GENERATED',len(out),flush=True)

if __name__=='__main__':generate()

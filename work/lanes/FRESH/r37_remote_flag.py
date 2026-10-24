from r37 import *
# QND X8 measurement via a terminal helper13 and dirty bus14.
# CX13,14 CX14,8 CX13,14 CX14,8 = CX13,8; bus14 restored.
ops,dets,md=load(BASE)
for t in range(18,29):print(t,[(o.kind,o.qs,o.bit) for o in ops if o.time==t],flush=True)
# Remove the conflicting q7 storage guard on helper13; preserve the source read of13.
guardbits={275};removed=[];keep=[]
for o in ops:
 if (o.bit==7 or (o.kind=='RX' and o.qs==(8,) and o.time==22) or
     (o.kind=='R' and o.qs==(13,) and o.time==19) or
     (o.kind=='CX' and o.qs==(7,13) and o.time in (20,23)) or o.bit in guardbits):removed.append(o);continue
 keep.append(copy.deepcopy(o))
assert len(removed)==6,[(o.kind,o.qs,o.time,o.bit) for o in removed]
dd=[row.copy() for row in dets if not row&guardbits]
# One added tick after the copy is complete; reset of13 for B starts later too.
for o in keep:
 if o.time>=23:o.time+=1
keep.extend([f.Op('RX',(13,),18),f.Op('CX',(13,14),19),f.Op('CX',(14,8),21),f.Op('CX',(13,14),22),f.Op('CX',(14,8),23),f.Op('MX',(13,),24,7)])
s=emit37('remote_flag13',keep,dd,dict(md,R=45),dict(remote_copy=[13,14,8],removed_guard=7,purpose='QND X8 flag on terminal13; keep projected q8 without reset'))
r=audit(s);print('AUDIT',json.dumps({k:v for k,v in r.items() if k not in ('ideal','harmful_singles','static','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),r.get('static',{}).get('general_atoms'),flush=True)
if r.get('harmful_singles'):print('HARM',r['harmful_singles'][:5],flush=True)
if r.get('c1',1)<1e-12:print('PRICE',price(s,7),flush=True);print('SPEED',speed(s,10000),flush=True)

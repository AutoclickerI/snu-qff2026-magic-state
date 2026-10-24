from r37 import *
ops,dets,md=load(BASE)
# U V U = CX14->8 CX13->8; accepted X8=+ makes the extra CX14->8 act trivially.
keep=[]
for o in ops:
 if (o.bit in (7,275) or (o.kind=='RX' and o.qs==(8,) and o.time==22) or (o.kind=='R' and o.qs==(13,) and o.time==19) or (o.kind=='CX' and o.qs==(7,13) and o.time in (20,23))):continue
 keep.append(copy.deepcopy(o))
for o in keep:
 if o.time>=23:o.time-=1
keep.extend([f.Op('RX',(13,),18),f.Op('CX',(13,14),19),f.Op('CX',(14,8),21),f.Op('CX',(13,14),22),f.Op('MX',(13,),23,7)])
dd=[row.copy() for row in dets if 275 not in row]
s=emit37('remote3_flag13',keep,dd,dict(md,R=43),dict(remote_copy=[13,14,8],removed_guard=7,postselected_identity='UVU=V CX13->8; V is identity on accepted X8=+ state'))
r=audit(s);print('AUDIT',json.dumps({k:v for k,v in r.items() if k not in ('ideal','static','harmful_singles','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),r.get('static',{}).get('general_atoms'),flush=True)
if r.get('harmful_singles'):print('HARM',r['harmful_singles'][:5],flush=True)
if r.get('c1',1)<1e-12:print('PRICE',price(s,7),flush=True);print('SPEED',speed(s,10000),flush=True)

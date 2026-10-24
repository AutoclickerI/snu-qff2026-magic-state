from r37 import *
src=D/'remote3_flag13';ops,dets,md=load(src)
for o in ops:
 if o.kind=='RX' and o.qs==(13,) and o.time==18:o.time=17
 if o.kind=='CX' and o.qs==(13,14) and o.time==22:o.time=23
 if o.bit==7:o.time=25
ops.extend([f.Op('SDG',(13,),18),f.Op('CX',(7,13),20),f.Op('CX',(7,13),22),f.Op('S',(13,),24)])
s=emit37('remote3_sharedY',ops,dets,md,dict(base=str(src),guard='CY7->13 echoed at20,22; Sdg13@18,S13@24, terminal MX13@25',reason='CY echo commutes with the central bus->flag CX and detects data X faults through an X-read helper'))
r=audit(s);print('AUDIT',json.dumps({k:v for k,v in r.items() if k not in ('ideal','static','harmful_singles','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),r.get('static',{}).get('general_atoms'),flush=True)
if r.get('harmful_singles'):print('HARM',r['harmful_singles'][:5],flush=True)
if r.get('c1',1)<1e-12:print('PRICE',price(s,7),flush=True);print('SPEED',speed(s,10000),flush=True)

from round35 import *
from r35_echo import add
from r36_static import diagnostic
OUT=HERE/'r36';src=ROOT/'work/lanes/SEPBC/v34/checked16_timing_0';ops,dets,md=load(src)
changes=[]
for bit,at in [(45,36),(46,34),(43,30),(3,10),(42,7)]:
 matches=[o for o in ops if o.bit==bit];assert len(matches)==1,(bit,matches);o=matches[0];changes.append(dict(bit=bit,q=o.qs,old=o.time,new=at));o.time=at
for q,old,at in [(13,25,33),(19,13,17)]:
 matches=[o for o in ops if o.kind=='R' and o.qs==(q,) and o.time==old];assert len(matches)==1,(q,old);matches[0].time=at;changes.append(dict(kind='R',q=q,old=old,new=at))
stems=[]
for name,echoes in [('timing',[]),('echo15',[(15,21,'X',19,29)]),('echo20',[(20,26,'Z',18,31)]),('echo_both',[(15,21,'X',19,29),(20,26,'Z',18,31)])]:
 oo,dd=copy.deepcopy(ops),copy.deepcopy(dets)
 try:
  for e in echoes:oo,dd=add(oo,dd,*e)
  s=emit('sepbc_'+name,oo,dd,md,dict(base=str(src),timing=changes,echoes=echoes,provenance='SEPBC12-CX A encoder plus FRESH timing and ST2 echo mechanism'))
  print(s.name,'IDEAL',certify(s)['c1'],flush=True);st=diagnostic(s);print('STATIC',st['failed_atoms'],flush=True);print('PRICE',price(s,7),flush=True);stems.append(str(s))
 except Exception as ex:print('ERROR',name,repr(ex),flush=True)
(OUT/'sepbc_stems.json').write_text(json.dumps(stems,indent=2))

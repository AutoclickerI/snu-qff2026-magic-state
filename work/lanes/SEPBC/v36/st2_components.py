from combine import *
rows=[]
for start in['base','fund_full']:
 c=base()if start=='base'else json.loads((V/(start+'.plan.json')).read_text())
 for kind in['mx1','moveT16','parity13','parity19']:
  d=copy.deepcopy(c);b=bit(d)
  if kind=='mx1':
   o=next(o for o in d['ops']if o['lines']==['reset q[1];','h q[1];']and o['t']==7);o['lines']=['h q[1];',f'measure q[1] -> c[{b}];','h q[1];'];d['tail'].append(f'// DETECTOR c[{b}]')
  elif kind=='moveT16':
   o=next(o for o in d['ops']if o['lines']==['tdg q[16];']);o['lines']=['tdg q[22];'];o['t']=37
  else:
   q=13 if kind=='parity13'else 19;rec=275 if q==13 else 274;o=next(o for o in d['ops']if o['lines']==[f'reset q[{q}];']and 10<o['t']<20);o['t']=19 if q==13 else 17;o['lines']=[f'measure q[{q}] -> c[{b}];'];parity(d,rec,b)
  emit(fix(d),f'{start}_{kind}',dict(family='ST2_new_component',component=kind,base=start),rows)
c=json.loads((V/'delivery_st2.plan.json').read_text());emit(fund(c,'st2'),'delivery_st2_fund_preserve',dict(family='ST2_new_joint',note='Keep c45 because ST2 moved it into the q15 echo readout; it is no longer an initial known-zero check.'),rows)
(V/'st2_component_builds.json').write_text(json.dumps(rows,indent=2))

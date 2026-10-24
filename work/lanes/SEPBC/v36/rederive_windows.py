"""Mechanism ports on actual free windows, including helper-basis restoration."""
from funding import *
rows=[]
for axis in['X','Z']:
 for first,last in[(27,29),(27,28),(28,29)]:
  c=base();o=next(o for o in c['ops']if o['lines']==['reset q[13];']and o['t']>=25);o['t']=last+2
  n=f'window7_{axis}_{first}_{last}';emit(echo(c,7,13,axis,first-1,first,last,last+1),n,dict(family='COMP29_WAITPROT_rederived_window',q=7,h=13,axis=axis,first=first,last=last,restore=last+2),rows)
for q in[10,15]:
 for axis in['X','Z']:
  for first,last in[(25,27),(26,28),(25,28)]:
   c=base();c=remove_check(c,43,'omit');c=echo(c,q,16,axis,first-1,first,last,last+1);c['ops'].append(dict(t=last+2,lines=['reset q[16];'],tag='integration',id=9999));n=f'window{q}_{axis}_{first}_{last}';emit(fix(c),n,dict(family='COMP29_WAITPROT_rederived_window',q=q,h=16,axis=axis,first=first,last=last,restore=last+2,removed_initial_check=43),rows)
(V/'window_builds.json').write_text(json.dumps(rows,indent=2))

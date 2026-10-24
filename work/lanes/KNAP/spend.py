from search import *

def main():
 source=sys.argv[1]if len(sys.argv)>1 else'final_m24_l2';base=loadc(OUT/source);jobs=[]
 for i,u in enumerate(base['u']):
  if u.name not in ('RESET','RX'):continue
  q=u.qs[0];prev=max([j for j in range(i)if q in base['u'][j].qs]+[-1])
  if prev<0:continue
  for axis in('X','Z'):
   for when in set([base['t'][i]-1,base['t'][prev]+1]):
    if when<=base['t'][prev]or when>=base['t'][i]:continue
    c=copy.deepcopy(base);c['u'].insert(i,Unit(([f'h q[{q}];']if axis=='X'else[])+[f'measure q[{q}] -> c[220];']))
    c['t'].insert(i,when);c['tags'].insert(i,c['tags'][i]);c['tail'].append('// DETECTOR c[220]')
    try:jobs.append(write(c,f'watch_{axis}_u{i}_t{when}',dict(kind='watch',source=source,unit=i,q=q,axis=axis,time=when)))
    except Exception as e:print('watch build error',i,axis,when,repr(e),flush=True)
 # Post-reset checks at any idle gap, now including repaired BC resets.
 for i,u in enumerate(base['u']):
  if u.name not in('RESET','RX'):continue
  q=u.qs[0];nxt=next((j for j in range(i+1,len(base['u']))if q in base['u'][j].qs),None)
  if nxt is None:continue
  for when in set([base['t'][i]+1,base['t'][nxt]-1]):
   if when>=base['t'][nxt]or when<=base['t'][i]:continue
   c=copy.deepcopy(base);lines=[f'measure q[{q}] -> c[220];']
   if u.name=='RX':lines=[f'h q[{q}];']+lines+[f'h q[{q}];']
   c['u'].insert(i+1,Unit(lines));c['t'].insert(i+1,when);c['tags'].insert(i+1,c['tags'][i]);c['tail'].append('// DETECTOR c[220]')
   try:jobs.append(write(c,f'post_u{i}_t{when}',dict(kind='postcheck',source=source,unit=i,q=q,axis='X'if u.name=='RX'else'Z',time=when)))
   except Exception as e:print('post build error',i,when,repr(e),flush=True)
 (OUT/'spend_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('spends',len(jobs),flush=True)

if __name__=='__main__':main()

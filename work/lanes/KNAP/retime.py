from search import *

def main():
 source=sys.argv[1]if len(sys.argv)>1 else'final_m2c_l2';base=loadc(OUT/source);jobs=[];per={}
 for i,u in enumerate(base['u']):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for i,u in enumerate(base['u']):
  if u.name not in('CX','T','TDG'):continue
  prev=[per[q][per[q].index(i)-1]for q in u.qs if per[q].index(i)>0];nxt=[per[q][per[q].index(i)+1]for q in u.qs if per[q].index(i)+1<len(per[q])]
  low=max([base['t'][j]+1 for j in prev]+[0]);high=min([base['t'][j]-1 for j in nxt]+[max(base['t'])])
  for t in set([low,high]):
   if t==base['t'][i]or t<low or t>high:continue
   c=copy.deepcopy(base);c['t'][i]=t
   try:jobs.append(write(c,f'gate_u{i}_t{t}',dict(kind='gate_time',source=source,unit=i,old=base['t'][i],time=t,lines=u.lines)))
   except Exception as e:print(i,t,'error',repr(e),flush=True)
 (OUT/'gate_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('gate timings',len(jobs),flush=True)

if __name__=='__main__':main()

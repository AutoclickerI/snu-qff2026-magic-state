from search import *
from build import insert_block
from partial_checks import tile
from blue_reuse import replace_encoder

def timing():
 base=loadc(OUT/'base');jobs=[];per={}
 for i,u in enumerate(base['u']):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for i,u in enumerate(base['u']):
  if u.name not in ('MEASURE','MX','RX','RESET'):continue
  prev=[per[q][per[q].index(i)-1]for q in u.qs if per[q].index(i)>0];nxt=[per[q][per[q].index(i)+1]for q in u.qs if per[q].index(i)+1<len(per[q])]
  low=max([base['t'][j]+1 for j in prev]+[0]);high=min([base['t'][j]-1 for j in nxt]+[max(base['t'])])
  for t in set([low,high]):
   if t==base['t'][i]or t<low or t>high:continue
   c=copy.deepcopy(base);c['t'][i]=t
   try:jobs.append(write(c,f'time_u{i}_t{t}',dict(kind='time',unit=i,old=base['t'][i],time=t)))
   except Exception as e:print('timing error',i,t,str(e),flush=True)
 (OUT/'timing_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('timings',len(jobs),flush=True)

def tiles():
 base=provenance(read(BASE));jobs=[]
 for mask in (1,2,4,3,5,6,7):
  for typ in ('x','xz'):
   for where in (77,129):
    c=insert_block(base,tile(mask,typ),where)
    if where==129 and mask&4:
     inds=[i for i,u in enumerate(c['u'])if u.name in('MX','MEASURE')and u.qs==(10,)and c['tags'][i]!='suffix']
     for i in inds:
      if c['u'][i].name=='MX':c['u'][i]=Unit(c['u'][i].lines[:2])
     add(c,inds[-1]+1,['reset q[10];','h q[10];'])
    c=placement(c,mode='alap')
    for enc in (19,21):
     v=copy.deepcopy(c)
     if enc==21:v=replace_encoder(v,'enc21_joint_d7_rigid')
     # Same reversed Bell convention as v24 on each selected tile.
     for a,b in [(1,2),(13,14),(9,10)]:
      for i,(u,tag)in enumerate(zip(v['u'],v['tags'])):
       if tag!='check_extra':continue
       if u.name=='RX'and u.qs==(a,):v['u'][i]=Unit([f'reset q[{a}];'])
       elif u.name=='RESET'and u.qs==(b,):v['u'][i]=Unit([f'reset q[{b}];',f'h q[{b}];'])
       elif u.lines==[f'cx q[{a}],q[{b}];']:v['u'][i]=Unit([f'cx q[{b}],q[{a}];'])
       elif u.last_is_measure and u.qs in((a,),(b,)):
        line=u.lines[1]if u.name=='MX'else u.lines[0];v['u'][i]=Unit(([f'h q[{b}];']if u.qs==(b,)else[])+[line])
     # These are strong spend candidates; include the virtually lossless budget now.
     v['tail']=[l for l in v['tail']if l.strip()!='// DETECTOR c[3]']
     try:
      v=placement(v,rigid=True);jobs.append(write(v,f'tile_{mask}_{typ}_w{where}_e{enc}',dict(kind='tile',mask=mask,typ=typ,where=where,encoder=enc,drop_c3=True)))
     except Exception as e:print('tile error',mask,typ,where,enc,repr(e),flush=True)
 (OUT/'tile_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('tiles',len(jobs),flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()

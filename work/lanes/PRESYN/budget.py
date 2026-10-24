"""Spend optional suffix preparation checks to make the extra blue XZ viable."""
from core import *
def main():
 jobs=[]
 for src in ['blue_xz_e21_r1_u0','blue_xz_e21_r0_u0','partial_x_enc21_joint_d7_rigid']:
  for reuse in(False,True):
   for budget in('none','c2c9','low_minit','both','low_c2','low_c9'):
    if not reuse and budget=='none':continue
    c=read(OUT/src);c['tags']=c['meta']['component_tags'];drop=set();bits=set()
    if reuse:
     q=2 if '_r1_'in src else 1
     ir=next(i for i,(u,tag)in enumerate(zip(c['u'],c['tags']))if tag=='suffix'and u.name=='RX'and u.qs==(q,))
     im=max(i for i in range(ir)if c['u'][i].name=='MX'and c['u'][i].qs==(q,))
     # Reversed Bell reads q1 in Z, so that recipe cannot supply an X state.
     intervening=[i for i in range(im+1,ir)if q in c['u'][i].qs]
     if intervening:continue
     c['u'][im]=Unit(c['u'][im].lines[:2]+[f'h q[{q}];']);drop.add(ir)
    if budget in('c2c9','both','low_c2','low_c9'):
     checkbits=(54,)if budget=='low_c2'else (53,)if budget=='low_c9'else (53,54)
     for i,(u,tag)in enumerate(zip(c['u'],c['tags'])):
      if tag=='suffix'and u.name=='MX'and any(f'c[{b}]'in' '.join(u.lines)for b in checkbits):
       drop.add(i);bits.update(map(int,re.findall(r'c\[(\d+)\]',' '.join(u.lines))))
    if budget in('low_minit','both','low_c2','low_c9'):
     seen=set()
     for i,u in enumerate(c['u']):
      q=u.qs[0]
      if c['tags'][i]=='suffix'and u.name=='MEASURE'and q not in seen and q not in(27,29):
       bits.update(map(int,re.findall(r'c\[(\d+)\]',u.lines[0])));c['u'][i]=Unit([f'reset q[{q}];'])
      seen.update(u.qs)
    c['tail']=[l for l in c['tail']if not(set(map(int,re.findall(r'c\[(\d+)\]',l)))&bits)]
    for k in('u','t','tags'):c[k]=[v for i,v in enumerate(c[k])if i not in drop]
    name=src+f'_budget_{int(reuse)}_{budget}'
    try:
     c=placement(c,rigid=True);stem=save(c,name,f'{src}; A q1 MX reuse={reuse}; remove optional suffix checks={budget}')
     jobs.append(dict(stem=str(stem),change=c['meta']['change']))
    except Exception as e:print(name,'BUILD ERROR',e,flush=True)
 (OUT/'budget_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')
if __name__=='__main__':main()

"""Co-design the new blue stabilizer check with the injection encoder."""
from core import *
from build import reordered
def replace_encoder(c,enc):
 e=read(OUT/enc);e['tags']=e['meta']['component_tags'];nu=[u for u,tag in zip(e['u'],e['tags'])if tag=='injection']
 rem=[i for i,tag in enumerate(c['tags'])if tag!='injection' and not(c['u'][i].name=='T'and c['u'][i].qs==(7,)and c['t'][i]<10)]
 c=reordered(c,rem);c['u']=nu+c['u'];c['t']=[0]*len(nu)+c['t'];c['tags']=['injection']*len(nu)+c['tags']
 if not enc.startswith('enc21'):
  c['tail']=[x for x in c['tail']if not any(re.fullmatch(r'// DETECTOR c\['+str(b)+r'\]',x.strip())for b in(39,40,41))]
  bs={int(b)for u in nu for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)};c['tail'] += [f'// DETECTOR c[{b}]'for b in bs]
 return c
def main():
 jobs=[]
 for typ in ('x','xz'):
  for enc in ('19','21','24','25'):
   c=read(OUT/f'partial_1_{typ}_129');c['tags']=c['meta']['component_tags']
   if enc!='19':c=replace_encoder(c,{'21':'enc21_joint_d7_rigid','24':'enc24_resource11_rigid','25':'enc25_rigid'}[enc])
   for rev in(False,True):
    v=copy.deepcopy(c)
    if rev:
     for i,(u,tag)in enumerate(zip(v['u'],v['tags'])):
      if tag!='check_extra':continue
      if u.name=='RX'and u.qs==(1,):v['u'][i]=Unit(['reset q[1];'])
      elif u.name=='RESET'and u.qs==(2,):v['u'][i]=Unit(['reset q[2];','h q[2];'])
      elif u.lines==['cx q[1],q[2];']:v['u'][i]=Unit(['cx q[2],q[1];'])
      elif u.last_is_measure and u.qs in((1,),(2,)):
       measure=u.lines[1]if u.name=='MX'else u.lines[0];v['u'][i]=Unit(([f'h q[{u.qs[0]}];']if u.qs==(2,)else[])+[measure])
    for reuse in(False,True):
     w=copy.deepcopy(v);q=2 if rev else 1
     if reuse:
      ir=next(i for i,(u,tag)in enumerate(zip(w['u'],w['tags']))if tag=='check_extra'and u.name=='RX'and u.qs==(q,))
      im=max(i for i in range(ir)if w['u'][i].name=='MX'and w['u'][i].qs==(q,))
      w['u'][im]=Unit(w['u'][im].lines[:2]+[f'h q[{q}];'])
      for k in('u','t','tags'):w[k].pop(ir)
     name=f'blue_{typ}_e{enc}_r{int(rev)}_u{int(reuse)}'
     try:
      w=placement(w,rigid=True);stem=save(w,name,f'blue {typ} check, {enc}-CX encoder, reverse Bell={rev}, reuse verified MX control={reuse}')
      jobs.append(dict(stem=str(stem),change=w['meta']['change']))
     except Exception as e:print(name,'BUILD ERROR',e,flush=True)
 (OUT/'blue_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')
if __name__=='__main__':main()

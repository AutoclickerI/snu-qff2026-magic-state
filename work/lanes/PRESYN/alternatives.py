from core import *
from build import reordered

def main():
 base=provenance(read(BASE));jobs=[]
 def emit(c,name,change,**sched):
  try:
   c=placement(c,**sched);stem=save(c,name,change);jobs.append(dict(stem=str(stem),change=change));print(name,c['meta']['R'],flush=True)
  except Exception as e:jobs.append(dict(name=name,change=change,build_error=str(e)));print('BUILD ERROR',name,e,flush=True)
 remain=[i for i in range(len(base['u']))if base['origin'].get(i,999)>30]
 for file,off in [('work/lanes/TREP/inputs/v17a',0),('work/lanes/TREP2/init_state_d5_s1',-1)]:
  src=read(ROOT/file);nu=[u for u,t in zip(src['u'],src['t'])if t<=10+off or(t==11+off and u.name=='CX')or(t==12+off and u.lines==['cx q[10],q[4];'])]
  tag='enc25'if off==0 else'enc24_resource11'
  for compact in(False,True,'rigid'):
   c=reordered(base,remain);c['u']=nu+c['u'];c['t']=[0]*len(nu)+c['t'];c['tags']=['injection']*len(nu)+c['tags']
   # Original resource uses three noisy first-use measurements at bits 39..41.
   c['tail']=[x for x in c['tail']if not any(re.fullmatch(r'// DETECTOR c\['+str(b)+r'\]',x.strip())for b in(39,40,41))]
   bits={int(b)for u in nu for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)}
   c['tail'] += [f'// DETECTOR c[{b}]'for b in sorted(bits)]
   emit(c,f'{tag}_{compact}',f'replace 19-CX injection with {tag}; schedule={compact}',compact=compact is True,rigid=compact=='rigid')
 for file in ['joint_d7_s0.solver.json','joint_d8_s1.solver.json']:
  w=json.loads((ROOT/'work/lanes/TREP2'/file).read_text());net=w['network'];zs=w['zero'];tq=w['T_site'];cells=sorted({tq,*zs,*[q for L in net for e in L for q in e]})
  nu=[Unit([f'measure q[{q}] -> c[{39+zs.index(q)}];']if q in zs else[f'reset q[{q}];',f'h q[{q}];'])for q in cells]+[Unit([f't q[{tq}];'])]
  nu += [Unit([f'cx q[{x}],q[{y}];'])for L in net for x,y in L]
  for compact in(False,True,'rigid'):
   c=reordered(base,remain);c['u']=nu+c['u'];c['t']=[0]*len(nu)+c['t'];c['tags']=['injection']*len(nu)+c['tags']
   emit(c,f'enc21_{file[:8]}_{compact}',f'TREP2 21-CX synthesized injection {file}; schedule={compact}',compact=compact is True,rigid=compact=='rigid')
 # Every TREP2 protected form is a physically different parity network. Keep
 # its prefix, replace its old suffix by the current v22h suffix. Restore RX10
 # because parity-network prefix measured q10 in Z, unlike base MX reuse.
 suffix=[i for i,tag in enumerate(base['tags'])if tag=='suffix']
 ref=read(OUT/'inputs/encoder19');old_suffix=[u for u,t in zip(ref['u'],ref['t'])if t>29]
 for f in sorted((ROOT/'work/lanes/TREP2').glob('f??_0_parity.qasm')):
  src=read(f.with_suffix(''));avail={}
  for i,u in enumerate(src['u']):avail.setdefault(key(u),[]).append(i)
  drop=set()
  for u in reversed(old_suffix):
   assert key(u) in avail and avail[key(u)],(f.name,u.lines)
   drop.add(avail[key(u)].pop())
  nu=[u for i,u in enumerate(src['u'])if i not in drop];bits={int(b)for u in nu for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)}
  # Give all prefix records fresh IDs, except base q10 readout c8 whose
  # associated suffix corrections are absent (only deterministic checks).
  mp={b:64+j for j,b in enumerate(sorted(bits))}
  nu=[Unit([re.sub(r'c\[(\d+)\]',lambda m:f'c[{mp[int(m[1])]}]',l)for l in u.lines])for u in nu]
  ptail=[re.sub(r'c\[(\d+)\]',lambda m:f'c[{mp[int(m[1])]}]',l)for l in src['tail']if set(map(int,re.findall(r'c\[(\d+)\]',l)))<=bits]
  c=reordered(base,suffix);sbits={int(b)for u in c['u']for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)}
  c['tail']=[l for l in c['tail']if set(map(int,re.findall(r'c\[(\d+)\]',l)))<=sbits]+ptail
  nu += [Unit(['reset q[10];','h q[10];'])]
  c['u']=nu+c['u'];c['t']=[0]*len(nu)+c['t'];c['tags']=['phase_network']*len(nu)+c['tags']
  # Check the zero vacated-cell watch records in the retained suffix through
  # full noiseless verification, rather than assuming parity network frames.
  emit(c,f'form_{f.stem[:5]}','TREP2 protected form '+f.stem+' rebuilt with v22h suffix and all current checks',compact=False)
 (OUT/'alternatives_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')

if __name__=='__main__':main()

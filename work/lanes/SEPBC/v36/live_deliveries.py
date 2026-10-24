from funding import *
sys.path.insert(0,str(H/'v34'));from assemble_layers import fit
rows=[]
src=ROOT/'work/lanes/ST2/pop36b/seed0/winner_Xlong_40_41_42'
if src.with_suffix('.qasm').exists():
 c=read(src);c['meta']['R']=44
 for o in c['ops']:o['tag']='round'if o['t']>=44 else'integration'
 for n,d in [('delivery_st2',c),('delivery_st2_fund',fund(c,'full'))]:emit(d,n,dict(family='live_ST2_v36b_delivery',source=str(src.relative_to(ROOT)),own_change='fund_full'if n.endswith('fund')else'none'),rows)
src=ROOT/'work/lanes/WAITPROT/v35/close_ABCDEF_postT0'
if src.with_suffix('.qasm').exists():
 a=read(V/'inputs/v35a');b=read(src);aa=collections.Counter((o['t'],tuple(o['lines']))for o in a['ops']);bb=collections.Counter((o['t'],tuple(o['lines']))for o in b['ops'])
 def skip(t,ls):return list(ls)==['reset q[1];','h q[1];']and t>=37
 e=dict(remove=[dict(t=t,lines=list(ls))for t,ls in(aa-bb).elements()if not skip(t,ls)],add=[dict(t=t,lines=list(ls))for t,ls in(bb-aa).elements()if not skip(t,ls)],detector_remove=sorted(set(a['tail'])-set(b['tail'])),detector_add=sorted(set(b['tail'])-set(a['tail'])))
 c=patch(base(),e)
 for o in c['ops']:
  if o['t']>=44:o['offset']=o['t']-44
 d,r=fit(c,12,cut=0,phases=True);row=dict(stem='delivery_wait',source=str(src.relative_to(ROOT)),schedule=r,omitted_inapplicable_A_init_shift=True)
 if d:
  try:st,z=write(d,'delivery_wait',row);row['screen']=z
  except Exception as ex:row['error']=repr(ex)
 rows.append(row);print(row,flush=True)
(V/'delivery_builds.json').write_text(json.dumps(rows,indent=2))

"""Port verified non-BC LNS edits onto MAIN's BCSYN2/HOPS/ACHECK merge."""
from compound import *
from moves import init_moves

def variants():
 for family in ['h','w']:
  c=read(OUT/f'inputs/v23{family}_c2c9');source=str(ROOT/f'work/lanes/MAIN/v23{family}_c2c9');orig=read(OUT/'inputs/v22h_c2c9')
  # reset_h's non-BC edits. The new base already has its own six MX pivots.
  c=apply(c,orig,dict(move='swap',units=[97,99]))
  c=apply(c,orig,dict(move='watch_before_reset',unit=34,axis='X'))
  recipe=[]
  for stage in ['fast_compounds_d2fa7dd5be','fast_compound2_774000b526']:
   r=json.loads((OUT/(stage+'.exact.json')).read_text())
   for d in r['desc']['moves']:
    osrc=read(d['source'])
    if d['move']=='reset_to_measure'and osrc['u'][d['unit']].qs==(19,):continue
    c=apply(c,osrc,d);recipe.append(d)
  c['source']=source
  yield c,dict(family='commute',move='BCSYN2_plus_LNS',base=family,recipe=recipe,parent_total=6.92210e-5)
  # Reuse variation priced separately; it has the known sampling-runtime cost.
  for v,d in init_moves(c):
   if d['move']=='reuse_mx'and d.get('q')==8:
    yield v,dict(family='init',move='BCSYN2_plus_LNS_q8reuse',base=family,recipe=recipe,parent_total=6.92210e-5)
    break
if __name__=='__main__':batch(list(variants()),'bc_port',1)

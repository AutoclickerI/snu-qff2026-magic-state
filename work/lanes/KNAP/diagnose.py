from search import *
from combine import apply_recipes
base=loadc(OUT/'base')
sites=[137,142,144,145,146,161]
for mask in [0,1,2,4,8,16,32,3,5,6,9,10,12,17,18,20,24,33,34,36,40,48,7,14,28,49,56,60,63]:
 rs=[dict(kind='bc_reset',unit=i,q=base['u'][i].qs[0],bit=detbits(' '.join(base['u'][i].lines))[0]) for j,i in enumerate(sites) if mask>>j&1]
 name=f'diag_bc_{mask:02x}'
 try: apply_recipes(rs,name)
 except Exception as e: print(name,e)

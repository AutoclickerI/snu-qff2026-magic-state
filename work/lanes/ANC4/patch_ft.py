from pathlib import Path
p=Path(__file__).with_name('synth_grid_ft.py');s=p.read_text();marker=' # Exact B output rows; F can be any independent basis of the four parities.'
insert=''' # Back-propagated X-fault signatures: syndrome(3), parity(1), four flags.
 sig=[[[m.NewBoolVar('') for bit in range(8)] for q in range(11)] for t in range(depth+1)]
 for q in range(11):
  val=(q+1)|8 if q<7 else 1<<(q-3)
  for bit in range(8):m.Add(sig[-1][q][bit]==((val>>bit)&1))
 def safe(bits,condition=None):
  expr=sum(v*(1<<i) for i,v in enumerate(bits));con=m.AddLinearExpressionInDomain(expr,cp_model.Domain.FromIntervals([[0,0],[9,255]]))
  if condition is not None:con.OnlyEnforceIf(condition)
 for t in reversed(range(depth)):
  for q in range(11):
   for bit in range(8):
    inc=[]
    for u,v in ed:
     if u==q:
      z=m.NewBoolVar('');m.AddMultiplicationEquality(z,[s[t][u,v],sig[t+1][v][bit]]);inc.append(z)
    m.AddBoolXOr([sig[t][q][bit],sig[t+1][q][bit],*inc,one])
   safe(sig[t][q])
  for u,v in ed:
   pair=[]
   for bit in range(8):
    z=m.NewBoolVar('');m.AddBoolXOr([z,sig[t+1][u][bit],sig[t+1][v][bit],one]);pair.append(z)
   safe(pair,s[t][u,v])
'''
s=s.replace(marker,insert+marker).replace('max_time_in_seconds=180','max_time_in_seconds=240').replace("f'grid_checker_d{depth}.json'","f'grid_checker_ft{depth}.json'").replace('run(20)','run(24)');p.write_text(s)

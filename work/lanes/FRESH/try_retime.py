import sys,json
sys.path.insert(0,'work/lanes/FRESH');import common
print("loaded",flush=True)
s='work/lanes/FRESH/corr_d11_k57_s35_002_freshbase_w0_fast_zlast';c=common.read(s);print('c loaded',flush=True)
for d in range(-1,-7,-1):
 try:
  x,rec=common.schedule(c,mode='alap',fixed_round=True,delta=d,seconds=20)
  print('delta',d,'x',bool(x),'rec',rec,flush=True)
  if x:
   out=common.save(x,f'early_{45+d}')
   print(d,rec,out)
   try:print(common.score(out))
   except Exception as e:print('scoreerr',e)
 except Exception as e: print(d,'ERR',repr(e))

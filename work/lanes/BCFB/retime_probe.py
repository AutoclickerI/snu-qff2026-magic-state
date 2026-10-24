from evaluate import H,price
import json
D=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text())
for qs in ([6],[13],[6,13]):
 for window in (0,1,2,4):
  opt=dict(mx=D['pivots'],mz=[23,25,27,28,29]+qs,retime_window=window)
  price(D,opt,'retime_m'+'_'.join(map(str,qs))+f'_w{window}','retime_probe')

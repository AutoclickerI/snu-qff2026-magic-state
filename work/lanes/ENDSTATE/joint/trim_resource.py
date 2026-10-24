import argparse,json
from synth_resource import run,H
hint=H/'r89_d10_k45.prep.json'
for cap in (40,36,32,28):
 a=argparse.Namespace(row=89,out=f'r89_d10_k{cap}',depth=10,cap=cap,seed=21,seconds=100,hint=str(hint),eager=True);run(a)
 rec=json.loads((H/(a.out+'.receipt.json')).read_text())
 if rec['status']!='SAT':break
 hint=H/(a.out+'.prep.json')

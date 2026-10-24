import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
from moves import timing_moves,commute_moves
base=read(Path('work/lanes/LNS2/choices_v25k_6dd3b41bd4'))
want=[]
for c,d in timing_moves(base,True):
 if d.get('move')=='single' and d.get('op')==['cx q[10],q[4];'] and d.get('old')==12 and d.get('new')==10: want.append((c,d))
for c,d in commute_moves(base):
 if d.get('ops')==[['cx q[1],q[0];'],['cx q[1],q[7];']]: want.append((c,d))
print('found',len(want))
for k,(c,d) in enumerate(want):
 c=normalize(c); name=f'combo_q8_{"timing10" if k==0 else "commute10"}'
 txt=textof(c); meta=dict(c['meta']); meta['method']=name; meta['source']=str(Path('work/lanes/LNS2/choices_v25k_6dd3b41bd4.qasm')); meta['lns_result']=dict(stem=name,desc=d)
 Path('work/lanes/LNS2',name+'.qasm').write_text(txt);Path('work/lanes/LNS2',name+'.json').write_text(json.dumps(meta,indent=2)+'\n');print(name,d,'depth',meta['native_depth'],'cx',meta['cx'])

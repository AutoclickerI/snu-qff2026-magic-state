from common import *
from guards import echo_options,reuse_echo_options,deferred_readout_options,apply
import itertools
rows=[]
for f in H.glob('a_ports_*.price.json'):
 d=json.loads(f.read_text())
 if d.get('ok'):
  m=json.loads((H/(d['stem']+'.json')).read_text());o=m['A_decoder']
  if o['cx']==2 and set(o['support_labels'])=={0,1,2}:rows.append((d['loss'],d['stem']))
assert rows
out=[]
for _,name in sorted(rows):
 p=load(H/name);end=max(o['t']for o in p['ops']);D=p['meta']['data_qubits'];A=p['meta']['A'];early={o['qs'][0]:o['t']for o in p['ops']if o['region']=='round'and o['name']=='CX'and o['qs'][0]in D and o['qs'][1]in A and o['t']<end-2};cat=echo_options(p)+reuse_echo_options(p)+deferred_readout_options(p);choices=[]
 for q,t in early.items():
  good=[d for d in cat if d['q']==q and d['axis']=='X'and d['first']<=t-1 and d['last']>=end-2];good.sort(key=lambda d:(-(d['last']-d['first']),d['h']));choices.append(good[:3])
 print(name,'early',early,'choices',[len(c)for c in choices],flush=True)
 if any(not c for c in choices):continue
 for i,actions in enumerate(itertools.product(*choices)):
  try:s=save(apply(p,list(actions)),name+f'_cover{i:02d}');out.append(s.name)
  except AssertionError:pass
(H/'decoder_cover_queue.json').write_text(json.dumps(out,indent=2));print('bundles',len(out),flush=True)

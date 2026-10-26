"""Interaction proposals from exact propagated noise signatures, not spatial proximity."""
from pass5 import *

def channels(st):
 fa=E.sw.fa;fa.DATA=json.loads(Path(st).with_suffix('.json').read_text())['data_qubits'];ops,dets=fa.parse_current(Path(st).with_suffix('.qasm').read_text())
 previous=fa.noise_blocks;fa.noise_blocks=lambda text,p,first_order=True:previous(text,p,first_order=False)
 try:m=fa.make_model(ops,dets)
 finally:fa.noise_blocks=previous
 groups=collections.defaultdict(list)
 for f in m.faults:
  ds=tuple(sorted(tuple(sorted(dets[i]))for i in range(len(dets))if f['d']>>i&1))
  groups[f['chan']].append((ds,int(f['s']),int(f['e']),float(f['p'])))
 return collections.Counter(tuple(sorted(v))for v in groups.values())

def diff_features(a,b):
 changed=(a-b)+(b-a);ds=set();ss=ee=0;symbols=set()
 for channel in changed:
  for d,s,e,p in channel:
   ds.update(d);ss|=s;ee|=e;symbols.add((d,s,e))
 return dict(detectors=[list(x)for x in sorted(ds)],rotation=ss,output=ee,symbols=sorted(symbols),changed_channels=sum(changed.values()))

def strength(a,b):
 da=set(map(tuple,a['detectors']));db=set(map(tuple,b['detectors']));det=len(da&db)
 rot=(a['rotation']&b['rotation']).bit_count();out=(a['output']&b['output']).bit_count()
 # Nonzero effects on DIFFERENT output syndrome bits still interact via the shared decoder.
 coupled_output=bool(a['output'] and b['output']);coupled_rotation=bool(a['rotation']and b['rotation'])
 return 8*det+4*rot+2*out+3*coupled_output+coupled_rotation

BASE_CHANNELS=None

def init(st):
 global BASE_CHANNELS
 BASE_CHANNELS=channels(st)

def work(r):
 try:return r['edits'][0],diff_features(BASE_CHANNELS,channels(r['stem']))
 except Exception as ex:return r['edits'][0],dict(error=repr(ex))

def make(st,rows,tag,workers):
 path=R/f'{tag}_signatures.json';out=json.loads(path.read_text())if path.exists()else{}
 todo=[r for r in rows if r['edits'][0]not in out];init(st)
 with get_context('fork').Pool(workers)as pool:
  for k,(i,s)in enumerate(pool.imap_unordered(work,todo),1):
   out[i]=s
   if k%100==0:dump(path,out);print(json.dumps(dict(event='signatures',tag=tag,done=k,total=len(todo))),flush=True)
 dump(path,out);return out

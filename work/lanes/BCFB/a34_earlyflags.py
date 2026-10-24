"""Preserve pre-A readout information before later reset/preparation."""
from a34_search import *
from a34_dedup import physical_key
stems=[];seen=set()
def save(base,changes):
 source=read(D/'candidates'/base);text,md,h,us,ts,tail=source;us=list(us);ts=list(ts);tail=list(tail)
 for q,t,basis,move in changes:
  if move:
   ix=next(i for i,(u,at) in enumerate(zip(us,ts)) if u.qs==(q,) and u.name=='MEASURE' and at>=37 and any('c[358]' in l for l in u.lines));ts[ix]=t
  else:
   bit=380+len(tail)%15
   assert not any(f'c[{bit}]' in l for u in us for l in u.lines)
   ls=([f'h q[{q}];'] if basis=='X' else [])+[f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];'] if basis=='X' else [])
   us.append(U(ls));ts.append(t);tail.append(f'// DETECTOR c[{bit}]')
 h=[re.sub(r'creg c\[\d+\]','creg c[400]',l) for l in h]
 text,meta=emit(h,us,ts,tail,dict(kind='early_readout_flags',source=base,changes=changes),True)
 stem=D/'candidates'/f'earlyflags_{len(stems):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2));key=physical_key(stem)
 if key in seen:stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink();return
 seen.add(key);stems.append(str(stem.relative_to(H)))
for base in ('encoders_00000','encoders_00004'):
 s=read(D/'candidates'/base);first=min(t for u,t in zip(s[3],s[4]) if u.qs==(8,) and t>35)
 for t in range(36,first):save(base,[(8,t,'Z',False)])
for base in ('encoders_00013','checks_00093'):
 s=read(D/'candidates'/base);first=min(t for u,t in zip(s[3],s[4]) if u.qs==(8,) and t>35)
 for t in range(36,first):
  save(base,[(8,t,'Z',True)]);save(base,[(8,t,'Z',False)])
for q,basis,t in [(1,'Z',37),(1,'Z',39),(2,'X',37),(2,'X',38)]:save('encoders_00013',[(q,t,basis,False)])
(D/'earlyflags.json').write_text(json.dumps(dict(stems=stems),indent=2));print('generated',len(stems),flush=True)

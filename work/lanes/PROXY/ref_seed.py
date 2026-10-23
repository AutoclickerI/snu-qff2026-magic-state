from cycles import *
l=json.loads((HERE/'relocations.json').read_text())['layouts'][1]
leaves=[dict(tile=1,data=1,cell=20,parent=14),dict(tile=2,data=5,cell=16,parent=10)]
m=Cycle(l,leaves,(0,1,0))
a=collections.Counter((native(k),qs) for k,qs,b in OPS[NPRE:]);b=collections.Counter((k,qs) for k,qs,bb in m.nodes)
print('source-only',a-b,'model-only',b-a)
print('source',list(zip(range(NPRE,len(OPS)),OPS[NPRE:],[nt[i] for i in range(NPRE,len(OPS))])))
print('model',m.nodes)
print('seed',m.reference_seed())
by=collections.defaultdict(list)
for i,(k,qs,b) in enumerate(OPS[NPRE:],NPRE):by[native(k),qs].append(nt[i])
for v in by.values():v.sort(reverse=True)
ts=[by[k,qs].pop() for k,qs,b in m.nodes]
print('lower failures',[(m.tags[j],m.nodes[j],t,lo) for j,(t,lo) in enumerate(zip(ts,m.lower)) if t<lo])
print('dep failures',[(m.tags[a],m.tags[b],ts[a],ts[b]) for a,b in m.deps if ts[a]>=ts[b]])
sch=[[] for _ in range(7)]
for (tile,d,B),j in m.cp.items():sch[d].append((ts[j],(B,relaxed.W4.index(W4[m.layout['xs' if B=='X' else 'zs'][tile]])),B))
print('relaxed',relaxed.valid(sch))
x,y=m.probes(ts)
print('reference cycle',ep.exact_loss(x,y,details=True),ep.conditional_loss(x,y,details=True))
(HERE/'reference_cycle_proxy.json').write_text(json.dumps(dict(second=ep.exact_loss(x,y),all_orders=ep.conditional_loss(x,y),times=ts),indent=2))

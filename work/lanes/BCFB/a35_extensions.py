from a35_prep import *
ss=[];seen=set();count=collections.Counter();delay_rows=[]
for l in (D/'exenc/pareto_paths.jsonl').open():
 r=json.loads(l);e=r['circuit'];flat=[ab for layer in e['ops'] for ab in layer];nxt={q:43 if q in (9,15) else 44 for q in A};first={q:1000 for q in A}
 for a,b in reversed(flat):
  t=min(nxt[a],nxt[b])-1;nxt[a]=nxt[b]=t;first[a]=first[b]=t
 need=max(0,max(RELEASE[q]+1+int((q in e['pivots'])!=(q in OLDPLUS))-first[q] for q in A))
 delay_rows.append(dict(r,minimal_delay=need))
(D/'pareto_timing.json').write_text(json.dumps(delay_rows,indent=2))
# One witness for each low-blind-count/depth combination at its minimum delay.
chosen={}
for r in delay_rows:
 if r['blind']>3:continue
 k=(r['blind'],r['minimal_delay']);key=(r['detected'],r['cx'],r['depth'])
 if k not in chosen or key<chosen[k][0]:chosen[k]=(key,r)
for k,(_,r) in chosen.items():
 e=dict(r['circuit'],name=f'pareto_blind{k[0]}_delay{k[1]}')
 try:s,m=make(e,[],[2,14],'reset',r['minimal_delay'])
 except (ValueError,AssertionError) as ex:count[str(ex)]+=1;continue
 stem=D/'candidates'/f'frontier_{len(ss):03}';stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));ss.append(str(stem.relative_to(H)))
for t in (37,38,39):
 for mode in ('add','move'):
  uu=list(us);tt=list(ts);tail2=list(tail)
  if mode=='move':i=next(i for i,(u,at) in enumerate(zip(uu,tt)) if u.qs==(16,) and u.name=='MEASURE' and at==40);tt[i]=t
  else:uu.append(U(['measure q[16] -> c[650];']));tt.append(t);tail2.append('// DETECTOR c[650]')
  s,m=finish(uu,tt,tail2,dict(kind='early_q16_flag',time=t,mode=mode));stem=D/'candidates'/f'early16_{mode}_{t}';stem.with_suffix('.qasm').write_text(s);stem.with_suffix('.json').write_text(json.dumps(m,indent=2));ss.append(str(stem.relative_to(H)))
(D/'extensions.json').write_text(json.dumps(ss,indent=2));print('extensions',len(ss),'frontier tuples',sorted(chosen),'errors',dict(count),flush=True)

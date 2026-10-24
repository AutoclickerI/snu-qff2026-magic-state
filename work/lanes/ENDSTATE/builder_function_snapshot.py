def build(x,name):
 pre,tail=prefix(x['args'].get('prefix_variant','base'));R=x['R'];mp={int(k):v for k,v in x['mapping'].items()};ops=[];bit=100
 def add(t,lines,tag,**kw):ops.append(dict(t=t,lines=lines,tag=tag,**kw))
 for i,(u,t)in enumerate(zip(pre,x['prefix_t'])):
  um=dict(zip(u.qs,x['prefix_locs'][i]))if 'prefix_locs'in x else mp
  add(t,rename(u.lines,um),'prefix',prefix_i=i)
 for key,tok in x['tokens'].items():
  k=key[0];i=int(key[1:]);q=tok['pos'][0]
  if k!='d':add(tok['init'],[f'reset q[{q}];']+([f'h q[{q}];']if i in x['encoders'][k][1]else[]),'prep_init')
  for j,z in enumerate(tok['moves']):
   if not z:continue
   u,v=tok['pos'][j:j+2];t=tok['ts'][j];add(t-1,[f'reset q[{v}];']+([f'h q[{v}];']if k=='a'else[]),'move_init')
   aa,bb=(v,u)if k=='a'else(u,v);add(t,[f'cx q[{aa}],q[{bb}];'],'move_cx')
   if k=='d':
    add(t+1,[f'cx q[{v}],q[{u}];'],'data_cx');add(t+2,[f'measure q[{u}] -> c[{bit}];'],'data_watch');tail.append(f'// DETECTOR c[{bit}]');bit+=1
   else:
    add(t+1,([f'h q[{u}];']if k!='a'else[])+[f'measure q[{u}] -> c[{bit}];']+([f'h q[{u}];']if k!='a'else[]),'tele_m',destination=v,axis=0 if k=='a'else 1,bit=bit);bit+=1
 for j in x['jobs']:
  if j['k']=='d':add(j['t'],[f"tdg q[{j['loc'][0]}];"],'data_tdg')
  else:u,v=j['loc'];add(j['t'],[f'cx q[{u}],q[{v}];'],'encoder_'+j['k'])
 read={}
 for i in range(7):
  d,a,b,c=(x['endpoints'][k][i]for k in'dabc');add(R,[f'cx q[{d}],q[{a}];'],'round');add(R,[f'cx q[{b}],q[{c}];'],'round');add(R+1,[f'cx q[{b}],q[{d}];'],'round')
  for k,q,t,basis in[('a',a,R+1,'Z'),('b',b,R+2,'X'),('c',c,R+1,'Z')]:
   add(t,([f'h q[{q}];']if basis=='X'else[])+[f'measure q[{q}] -> c[{bit}];'],'read',bit=bit);read[k,i]=bit;bit+=1
 ops.sort(key=lambda o:(o['t'],o['tag']!='tele_m'));frames={q:[set(),set()]for q in range(36)};corr={}
 for o in ops:
  u=unit(o);qs=list(map(int,S.QRE.findall(o['lines'][0])))
  if u.name in('RESET','RX'):frames[qs[0]]=[set(),set()]
  elif u.name=='CX':a,b=qs;frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
  elif o['tag']=='tele_m':
   q=qs[0];axis=o['axis'];frames[o['destination']][axis]^=frames[q][axis]^{o['bit']};frames[q]=[set(),set()]
  elif o['tag']=='read':corr[o['bit']]=frames[qs[0]][1 if u.name=='MX'else 0].copy()
  elif u.name=='H':frames[qs[0]].reverse()
  elif u.name in('T','TDG'):assert not any(frames[qs[0]]),('output frame on T',o,frames[qs[0]])
 assert all(not any(frames[q])for q in x['endpoints']['d'])
 for k in'abc':
  for g in ROWS+([list(range(7))]if k=='c'else[]):
   bs={read[k,i]for i in g}
   for i in g:bs^=corr[read[k,i]]
   tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
 for i,o in enumerate(ops):o['id']=i
 compact={t:i for i,t in enumerate(sorted({o['t']for o in ops}))}
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];'],ops=ops,tail=tail,meta=dict(data_qubits=x['endpoints']['d'],R=compact[R],R_model=R,source='complete prefix-round redesign',free_prefix=x['args'].get('free_prefix',False),embedding=x['embedding_description'],encoder=x['args']['encoder'],catalog=x['args']['catalog'],block_teleports=sum(sum(v['moves'])for k,v in x['tokens'].items()if k[0]!='d'),data_hops=sum(sum(v['moves'])for k,v in x['tokens'].items()if k[0]=='d')))
 return save(c,name)

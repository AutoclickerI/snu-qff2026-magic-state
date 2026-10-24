from a35_prep import *
ss=[]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]];BITS=dict(zip(A,range(14,21)))
def zf(v,ops):
 for a,b in ops:
  if v>>A.index(b)&1:v^=1<<A.index(a)
 return v
for base in ['inputs/v35b','candidates/enc_00060','candidates/f0_guard_gain_fund10','candidates/f0_headroom_fund8']:
 src=D/base;s=read(src);depth=max(s[4])+1;delta=depth-47
 uu=[];tt=[]
 for u,t in zip(s[3],s[4]):
  if u.name=='CX' and t==45+delta and u.lines[0]=='cx q[8],q[9];':u=cx(9,8)
  if u.qs==(8,) and u.name=='MX' and t==46+delta:u=U(['measure q[8] -> c[16];'])
  if u.qs==(9,) and u.name=='MEASURE' and t==46+delta:u=U(['h q[9];','measure q[9] -> c[17];','h q[9];'])
  uu.append(u);tt.append(t)
 ta=[l for l in s[5] if not set(map(int,re.findall(r'c\[(\d+)\]',l)))&set(range(14,21))]
 ops=[(9,15),(14,15),(9,8)]
 for row in ROWS:
  z=zf(sum(1<<i for i in row),ops);assert not z>>A.index(9)&1;bs=[BITS[A[i]] for i in range(7) if z>>i&1]
  if z>>A.index(16)&1:bs.append(24)
  ta.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bs))
 ta.append('// DETECTOR c[17]')
 body,md=finish(uu,tt,ta,dict(kind='A_flag_root9',source=base,delay=delta,flag_physical_support=[8,9,15],root=9));stem=D/'candidates'/('root9_'+src.name);stem.with_suffix('.qasm').write_text(body);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));ss.append(str(stem.relative_to(H)))
(D/'flagroots.json').write_text(json.dumps(ss,indent=2));print('flag root variants',len(ss),flush=True)

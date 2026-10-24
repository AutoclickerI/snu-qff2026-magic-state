from pathlib import Path
p=Path(__file__).with_name('flags_multi.py');s=p.read_text();a=s.index("for b,f in [(13,12)");b=s.index("  groups={t:s.copy()",a)
s=s[:a]+'''b,f=13,12
opts=[t for t in range(20,40) if b not in busy[t] and columns[t].get(b)]
windows=[]
for num in [2,3]:
 for times in itertools.combinations(opts,num):
  v=columns[45][b]
  for t in times:v^=columns[t][b]
  if v==0:windows.append(times)
windows.sort(key=lambda t:(len(t),45-t[0],t))
seen=set()
for times in windows:
  # Evaluate one latest tuple per sequence of symbolic B values.
  key=tuple(columns[t][b] for t in times)
  if key in seen:continue
  seen.add(key);start=times[0];end=45
'''+s[b:]
s=s.replace("outdir=HERE/'flags'","outdir=HERE/'flags_multi'")
s=s.replace("groups[start].append(f'cx q[{b}],q[{f}];');", "\n  for t in times:groups[t].append(f'cx q[{b}],q[{f}];')\n  ")
s=s.replace("name=f'f{f}_b{b}_t{start}'", "name='f12_t'+'_'.join(map(str,times))")
s=s.replace("flag=[b,f,start,45],cx=j['cx']+2", "flag=[b,f,*times,45],cx=j['cx']+len(times)+1")
s=s.replace("'flags_singles.json'", "'flags_multi_singles.json'")
p.write_text(s)

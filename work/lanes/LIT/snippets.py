import sys,re
from pathlib import Path
id,pattern=sys.argv[1:3]
for n,p in enumerate(Path(f'work/lanes/LIT/papers/{id}.txt').read_text(errors='replace').split('\f'),1):
 p=re.sub(r'<latexit[^>]*>.*?</latexit>', '',p,flags=re.S)
 lines=[' '.join(l.split()) for l in p.splitlines()]
 matches=[i for i,l in enumerate(lines) if re.search(pattern,l,re.I)]
 if matches:
  print(f'== {id} PDF p{n} ==')
  seen=set()
  for i in matches[:8]:
   for j in range(max(0,i-2),min(len(lines),i+4)):
    if j not in seen: print(lines[j]);seen.add(j)

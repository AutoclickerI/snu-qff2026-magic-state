from pathlib import Path
import re,sys
f=sys.argv[1]; pages=Path(f'work/lanes/LIT/papers/{f}.txt').read_text(errors='replace').split('\f')
for spec in sys.argv[2:]:
 lo,hi=map(int,spec.split('-')) if '-' in spec else (int(spec),int(spec))
 for n in range(lo,hi+1):
  s=re.sub(r'<latexit[^>]*>.*?</latexit>', '',pages[n-1],flags=re.S)
  s='\n'.join(re.sub(' {3,}','  ',l).rstrip() for l in s.splitlines())
  print(f'=== {f} PDF page {n} ===\n{s}')

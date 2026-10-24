import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'MAIN' / 'sparse'))
from frontend import parse_current
stem = Path(sys.argv[1]); lo=int(sys.argv[2]); hi=int(sys.argv[3])
ops, dets = parse_current(stem.with_suffix('.qasm').read_text())
for t in range(lo, hi+1):
    s=[]
    for o in ops:
        if o.time==t:
            s.append(o.kind+':'+'>'.join(map(str,o.qs))+(f'[c{o.bit}]' if o.bit is not None else ''))
    print(t, ' '.join(s))

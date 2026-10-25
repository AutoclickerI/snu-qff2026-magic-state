"""Remove every pre-round detector: upper acceptance for fixed square checks."""
import sys,json,re
from build_rounds import H
sys.path.insert(0,str(H/'sparse'))
from frontend import parse_current
name=sys.argv[1];stem=H/'builds'/name
m=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text()
ops,_=parse_current(text);finalbits={o.bit for o in ops if o.time==m['round_start']+2 and o.bit is not None}
lines=[];dropped=[]
for line in text.splitlines():
    if line.startswith('// DETECTOR') and not set(map(int,re.findall(r'c\[(\d+)\]',line)))<=finalbits:dropped.append(line)
    else:lines.append(line)
n=name+'_accept_ceiling';p=H/'builds'/n
p.with_suffix('.qasm').write_text('\n'.join(lines)+'\n')
p.with_suffix('.json').write_text(json.dumps(dict(m,change='diagnostic: all pre-round checks removed; fixed-round-check acceptance ceiling',
    dropped_detectors=dropped),indent=2)+'\n');print(n)

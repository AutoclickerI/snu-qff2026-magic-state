"""Cut a circuit at a tick boundary for M08's incoming-state table.

Keeps every operation in ticks <= LAST except listed couplings, prunes operations outside the backward light
cone of (data at the cut, kept detectors), keeps detectors whose records all fall in ticks <= LAST.
Usage: truncate.py <stem> <last_tick> <out_stem> [drop 'q0,q1' ...]
"""
import re, sys, json
from pathlib import Path
stem=Path(sys.argv[1]); last=int(sys.argv[2]); out=Path(sys.argv[3])
drop={tuple(map(int,s.split(','))) for s in sys.argv[4:]}
data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
lines=stem.with_suffix('.qasm').read_text().splitlines()
header=[l for l in lines[:4]]
t=0; body=[]   # (tick, line)
for l in lines[4:]:
    if l.startswith('// DETECTOR'): continue
    if l.startswith('barrier'):
        t+=1
        if t>last: break
        body.append((t,l)); continue
    if t>last: break
    qs=tuple(map(int,re.findall(r'q\[(\d+)\]',l)))
    if l.startswith('cx') and qs in drop and t==last: continue
    body.append((t,l))
mtick={}
for tk,l in body:
    b=re.findall(r'c\[(\d+)\]',l)
    if b: mtick[int(b[0])]=tk
dets=[l for l in lines if l.startswith('// DETECTOR')]
keep=[d for d in dets if all(int(b) in mtick for b in re.findall(r'c\[(\d+)\]',d))]
kbits={int(b) for d in keep for b in re.findall(r'c\[(\d+)\]',d)}
live=set(data); kept=[]
for tk,l in reversed(body):
    if l.startswith('barrier'): kept.append(l); continue
    qs=list(map(int,re.findall(r'q\[(\d+)\]',l)))
    op=l.split()[0]
    if op=='measure':
        b=int(re.findall(r'c\[(\d+)\]',l)[0])
        if b in kbits or qs[0] in live:
            live.add(qs[0]); kept.append(l)
        continue
    if op=='reset':
        if qs[0] in live: kept.append(l); live.discard(qs[0])
        continue
    if op=='cx':
        if live & set(qs): live.update(qs); kept.append(l)
        continue
    if qs[0] in live: kept.append(l)
kept.reverse()
# 'h' left dangling right after a dropped reset would be wrong; check every kept qubit starts sanely
out.with_suffix('.qasm').write_text('\n'.join(header+kept+keep)+'\n')
meta=dict(data_qubits=data,source=str(stem),cut_after_tick=last,dropped=sorted(drop),detectors_kept=len(keep),detectors_total=len(dets))
out.with_suffix('.json').write_text(json.dumps(meta,indent=1)+'\n')
print(json.dumps(meta))

"""Print the native schedule of a qasm by barrier tick, with role labels (v36c roles)."""
import re, sys, json
from pathlib import Path
stem = Path(sys.argv[1])
first = int(sys.argv[2]) if len(sys.argv) > 2 else 0
D=[0,20,7,10,3,22,21]; A=[1,14,8,9,2,16,15]; B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
def role(q):
    for n,L in (('D',D),('A',A),('B',B),('C',C)):
        if q in L: return f'{n}{q}'
    return f'h{q}'
t=0; rows={}
lines=stem.with_suffix('.qasm').read_text().splitlines()
i=0
while i < len(lines):
    l=lines[i]
    if l.startswith('barrier'): t+=1; i+=1; continue
    if l.startswith(('OPENQASM','include','qreg','creg','//')) or not l.strip(): i+=1; continue
    qs=list(map(int,re.findall(r'q\[(\d+)\]',l))); bits=re.findall(r'c\[(\d+)\]',l)
    op=l.split()[0]
    # fold h;measure;h and reset;h
    if op=='h' and i+1<len(lines) and lines[i+1].startswith('measure') and re.findall(r'q\[(\d+)\]',lines[i+1])==[str(qs[0])]:
        b=re.findall(r'c\[(\d+)\]',lines[i+1])[0]
        rows.setdefault(t,[]).append(f'MX {role(qs[0])}->c{b}')
        i+=3 if i+2<len(lines) and lines[i+2].strip()==f'h q[{qs[0]}];' else 2
        continue
    if op=='reset' and i+1<len(lines) and lines[i+1].startswith('h') and re.findall(r'q\[(\d+)\]',lines[i+1])==[str(qs[0])]:
        rows.setdefault(t,[]).append(f'RX {role(qs[0])}'); i+=2; continue
    s={'measure':'M','reset':'R','cx':'CX'}.get(op,op.upper())
    rows.setdefault(t,[]).append(s+' '+'->'.join(role(q) for q in qs)+(f'->c{bits[0]}' if bits else ''))
    i+=1
for k in sorted(rows):
    if k>=first: print(k, '; '.join(rows[k]))

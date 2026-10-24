"""v36c + D21 reversed: B27->D21 at 44, D21->A15 and B27->C28 at 45 (C checks B27 after its data coupling),
A15 keeps the flag's pre-44 coverage; drops the 14->15 readout edge and the C28->h34 copy that collide."""
import re, json
src=open('../MAIN/v36c.qasm').read().splitlines()
out=[]; t=0
for l in src:
    if l.startswith('barrier'): t+=1; out.append(l); continue
    if t==43 and l=='cx q[21],q[15];': continue
    if t==44 and l=='cx q[27],q[28];': out.append('cx q[27],q[21];'); continue
    if t==44 and l=='reset q[34];': continue
    if t==45 and l=='cx q[27],q[21];': out.append('cx q[27],q[28];'); out.append('cx q[21],q[15];'); continue
    if t==45 and l in ('cx q[14],q[15];','cx q[28],q[34];'): continue
    if t==46 and l=='measure q[34] -> c[268];': continue
    if l=='// DETECTOR c[27] c[268]': continue
    if l.startswith('// DETECTOR') and 'c[20]' in l:
        bits=set(re.findall(r'c\[(\d+)\]',l)); bits^={'15'}
        l='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bits,key=int))
    out.append(l)
open('v36c_d21r.qasm','w').write('\n'.join(out)+'\n')
meta=json.load(open('v36c.json')); meta['cx']=sum(1 for l in out if l.startswith('cx')); meta['source']='TERM v36c + D21 reversed order'
json.dump(meta,open('v36c_d21r.json','w'),indent=2)
print(meta['cx'])

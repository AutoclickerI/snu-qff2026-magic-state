"""v36c without the A partial decoder: D10->A9, D21->A15 at tick 44 (not 43), no CX9->15 / CX8->9, A8 read in Z."""
import json, sys
src = open('../MAIN/v36c.qasm').read().split('\n')
out = []
for i, l in enumerate(src, 1):
    if i in (421, 422, 459):
        continue
    if i == 440:
        out += ['cx q[10],q[9];', 'cx q[21],q[15];']
        continue
    if i in (461, 463):
        assert l == 'h q[8];', l
        continue
    if l == '// DETECTOR c[14] c[15] c[17] c[18] c[20]':
        out.append('// DETECTOR c[14] c[15] c[16] c[18] c[20]'); continue
    if l == '// DETECTOR c[17] c[19] c[20] c[24]':
        out.append('// DETECTOR c[16] c[19] c[20] c[24]'); continue
    if l == '// DETECTOR c[15] c[18] c[19] c[20] c[24]':
        out.append('// DETECTOR c[15] c[17] c[18] c[19] c[20] c[24]'); continue
    if l == '// DETECTOR c[16]':
        continue
    out.append(l)
name = sys.argv[1] if len(sys.argv) > 1 else 'v36c_nodec'
open(name + '.qasm', 'w').write('\n'.join(out))
j = json.load(open('../MAIN/v36c.json')); j['cx'] -= 2; j['source'] = 'IDEAS: v36c minus A partial decoder'
json.dump(j, open(name + '.json', 'w'), indent=2)

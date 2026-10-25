"""v36h + identity pair CX10->16 at 42 and 44 around D10->A9 (43), D22->A16 moved 44 -> 43, q10's T_DAG 42 -> 41.
Both pair CX have q10 as control (commutes with D10->A9) and q16 as target (commutes with D22->A16), so the ideal
circuit and every detector are unchanged; the pair protects q10's flag gap at 44, q22 gains a gap at 44."""
import sys, json
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/R43')
from qedit import load

c = load('v36h')
def find1(t, line):
    hits = [j for j, g in enumerate(c.segs[t]) if g == [line]]
    assert len(hits) == 1, (t, line, c.segs[t])
    return hits[0]
c.move(42, find1(42, 'tdg q[10];'), 41)
c.move(44, find1(44, 'cx q[22],q[16];'), 43)
c.segs[42].append(['cx q[10],q[16];'])
c.segs[44].append(['cx q[10],q[16];'])
open('v36h_e16.qasm', 'w').write(c.text())
j = json.load(open('v36h.json'))
for k in ('additions', 'allorders_ev2', 'allorders_acceptance_ev2', 'incumbent_v36g', 'fast_check_1e6_seed0', 'speed'):
    j.pop(k, None)
j.update(source='FLAG: v36h + echo pair CX10->16 @42/@44, D22->A16 @43, tdg q10 @41', base='MAIN/v36h', cx=j['cx'] + 2)
json.dump(j, open('v36h_e16.json', 'w'), indent=1)

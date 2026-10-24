import sys, json
sys.path.insert(0, '.')
from qcirc import parse
from decompose import split, is_round
units, dets = parse(open('../MAIN/v36c.qasm').read())
life_of, find, entry, comp = split(units)
pre = []
for root, idx in comp.items():
    ts = [units[i]['t'] for i in idx]
    qs = {q for i in idx for q in units[i]['q']}
    if root in entry or max(ts) <= 31 or (qs == {22} and max(ts) == 34):
        pre += idx
pre = sorted(i for i in pre if not is_round(units[i]))
json.dump(dict(name='v36c prefix+data wait noiseless', units=[[units[i]['t'], list(units[i]['q'])] for i in pre]), open('spec_prefix.json', 'w'))
json.dump(sorted(pre), open('v36c_prefix_idx.json', 'w'))
print(len(pre), sum(units[i]['k']=='CX' for i in pre))

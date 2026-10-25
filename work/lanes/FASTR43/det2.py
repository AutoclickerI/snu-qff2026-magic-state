import sys,collections,json
from fr import *
import general_atoms as g
stem=C/sys.argv[1]
text,_,_=g.noisy_text(str(stem))
sig=xtim._xtim.deferred_signature(text);parts=[p for p in sig.split(';')[1:] if p and not p.startswith('reads=')]
r=json.loads(Path(str(stem)+'.atoms.json').read_text())
bad=collections.Counter(a['first_bad_gate'] for a in r['atoms'])
print(bad)
for j in bad:
    print(j, parts[max(0,j-12):j+3])
# which noise instruction indices, and their wires
ni=collections.Counter(a['noise_index'] for a in r['atoms'])
print(sorted(ni)[:10], sorted(ni)[-10:])
# wire-8 gate history in signature
hist=[(i,p) for i,p in enumerate(parts) if p.startswith('0:') and '8' in p.split(':')[1].split(',')[1:]]
print(hist)

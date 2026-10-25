import sys
from lib import *
c = read(sys.argv[1])
by = collections.defaultdict(list)
for o in c['ops']:
    by[o['t']].append(' '.join(l for l in o['lines']))
for t in sorted(by):
    print(t, ' | '.join(by[t]))

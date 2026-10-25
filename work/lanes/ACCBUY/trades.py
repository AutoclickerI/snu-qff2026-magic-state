"""Apply a list of INTEG2-style trades (bit:mode) to a base. usage: trades.py <base stem> <out> bit:mode ..."""
import sys
from elements import *
c = read(sys.argv[1])
done = []
for s in sys.argv[3:]:
    b, mode = s.split(':')
    try:
        c = remove_check(c, int(b), mode)
        done.append(s)
    except Exception as e:
        print('skip', s, repr(e)[:80])
print(save(c, sys.argv[2], desc=dict(trades=done)), len(done))

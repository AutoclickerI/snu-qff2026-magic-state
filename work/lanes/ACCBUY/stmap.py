import sys
from gadgets import *
c = read(sys.argv[1])
st = status(c)
T = depth(c)
print('     ' + ''.join(str(t % 10) for t in range(T)))
for q in range(36):
    print(f'q{q:2d}  ' + ''.join({'busy': '#', 'live': '.', 'dead': ' ', 'pre': '-', 'prem': 'm'}[x] for x in st[q]))

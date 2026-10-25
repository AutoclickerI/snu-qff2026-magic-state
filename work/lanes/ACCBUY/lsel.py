import sys
from elements import *
c = read(sys.argv[1])
for e in elements(c) + q6_elements(c):
    print(e['name'], e['kind'], e['edits'][:6])

import sys,collections
from fr import *
r=atoms(C/sys.argv[1],True)
print(r['prediction'],r['general_atoms'])
# group failing atoms by noise instruction wire and first bad gate
cnt=collections.Counter((a['noise_instruction'],a['axis'],a['gate_instruction']) for a in r.get('atoms',[]))
for k,v in cnt.most_common(60):print(v,k)

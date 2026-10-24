import json,re,sys
from pathlib import Path
src,out,mask=sys.argv[1],sys.argv[2],int(sys.argv[3],0); L=Path(src+'.qasm').read_text().splitlines();qs=[14,2,9,20,16,28,29,23,27,25,21,22];chosen={q for i,q in enumerate(qs) if mask>>i&1};qmap={}
for i,l in enumerate(L):
 m=re.match(r'measure q\[(\d+)\] -> c\[(\d+)\];',l)
 if m and int(m.group(1)) in qs:qmap.setdefault(int(m.group(1)),(i,int(m.group(2))))
N=[]
for i,l in enumerate(L):
 m=re.match(r'measure q\[(\d+)\] -> c\[(\d+)\];',l)
 if m and int(m.group(1)) in chosen and qmap[int(m.group(1))][0]==i:N.append(f'reset q[{int(m.group(1))}];')
 elif l.startswith('// DETECTOR'):
  bits=[int(x) for x in re.findall(r'c\[(\d+)\]',l)];bits=[b for b in bits if not any(b==qmap[q][1] for q in chosen)]
  if bits:N.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bits))
 else:N.append(l)
Path(out+'.qasm').write_text('\n'.join(N)+'\n');d=json.loads(Path(src+'.json').read_text());d['source']=f'{src} with init reset mask {mask:#x}';d['init_reset']=sorted(chosen);json.dump(d,open(out+'.json','w'))

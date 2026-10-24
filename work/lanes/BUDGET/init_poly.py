#!/usr/bin/env python3
import json,re,sys,itertools,random, pathlib
src=pathlib.Path('work/lanes/MAIN/spec/v17a.qasm')
out=pathlib.Path('work/lanes/BUDGET/init_scan')
text=src.read_text().splitlines()
# q -> (measure line index, classical bit)
qs=[14,2,9,20,16,28,29,23,27,25,21,22]
qmap={}
for i,l in enumerate(text):
 m=re.match(r'measure q\[(\d+)\] -> c\[(\d+)\];',l)
 if m and int(m.group(1)) in qs:
  qmap.setdefault(int(m.group(1)),(i,int(m.group(2))))
assert len(qmap)==12

def emit(mask,tag):
 chosen={q for j,q in enumerate(qs) if mask>>j&1}
 lines=[]
 for li,l in enumerate(text):
  m=re.match(r'measure q\[(\d+)\] -> c\[(\d+)\];',l)
  if m and int(m.group(1)) in chosen and qmap[int(m.group(1))][0] == li:
   q=int(m.group(1)); lines.append(f'reset q[{q}];')
  elif l.startswith('// DETECTOR'):
   bits=[int(x) for x in re.findall(r'c\[(\d+)\]',l)]
   # selected initial records are standalone in v17a; drop selected bits robustly
   bits=[b for b in bits if not any(b==qmap[q][1] for q in chosen)]
   if not bits: continue
   lines.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bits))
  else: lines.append(l)
 # keep creg width, records unused are okay
 p=out/f'v17a_i{mask:03x}.qasm'; j=p.with_suffix('.json')
 p.write_text('\n'.join(lines)+'\n')
 j.write_text(json.dumps({'data_qubits':[0,20,7,10,3,22,21],'source':f'v17a init reset subset {sorted(chosen)}','init_reset':sorted(chosen)}))

# all variants (mask bits 1 = reset, 0 = original measure-init)
for mask in range(1<<len(qs)): emit(mask, f'{mask:03x}')
# deterministic design: empty + all singles/pairs/triples; heldout random 64 from weight 4..12
# write manifest with feature vector and role
rng=random.Random(20261024)
design=[]
for k in range(4):
 for comb in itertools.combinations(range(12),k): design.append(sum(1<<i for i in comb))
held=set()
while len(held)<64:
 m=rng.randrange(1<<12)
 if m not in design: held.add(m)
allm=set(range(1<<12)); train=set(design); hold=held
json.dump({'qs':qs,'train':sorted(train),'heldout':sorted(hold),'all':sorted(allm)},open(out/'manifest.json','w'),indent=2)
print(len(train),len(hold),len(allm))

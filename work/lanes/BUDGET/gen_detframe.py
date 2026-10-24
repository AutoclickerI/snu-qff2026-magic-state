import json,re,itertools
from pathlib import Path
base=Path('work/lanes/MAIN/spec/v17a.qasm');lines=base.read_text().splitlines();out=Path('work/lanes/BUDGET/det_scan');out.mkdir(exist_ok=True)
det_idx=[i for i,l in enumerate(lines) if l.startswith('// DETECTOR')]
# record standalone fresh init detectors and all detector indices
records=[35,36,37,38,39,40,41,42,43,44,45,46]
# detector line associated with each record
rec_to_i={r:next(i for i in det_idx if re.findall(r'c\[(\d+)\]',lines[i])==[str(r)]) for r in records}
meta={'data_qubits':[0,20,7,10,3,22,21]}
def emit(name,drop=(),frames=()):
 L=[]
 drop=set(drop)
 for i,l in enumerate(lines):
  if i in drop: continue
  L.append(l)
 if frames:
  by=dict(frames)
  for P in ('X','Z'):
   if P in by: L.append(f'// FRAME_{P}(0) c[{by[P]}]')
   else: L.append(f'// FRAME_{P}(0) c[0]')
 p=out/(name+'.qasm');p.write_text('\n'.join(L)+'\n');d=dict(meta);d.update({'drop_detectors':[next((r for r,ii in rec_to_i.items() if ii==i), f'det_index_{det_idx.index(i)}') for i in drop],'frames':frames});json.dump(d,open(out/(name+'.json'),'w'))
# baseline and singles, init-detector pairs, and detector drops paired with frame X/Z/Y
emit('base')
for j,i in enumerate(det_idx): emit(f'drop_d{j:02d}',[i])
for a,b in itertools.combinations(range(len(records)),2):
 emit(f'drop_init_{records[a]}_{records[b]}',[rec_to_i[records[a]],rec_to_i[records[b]]])
for r in records:
 i=rec_to_i[r]
 for tag,fr in [('x',[('X',r)]),('z',[('Z',r)]),('y',[('X',r),('Z',r)])]: emit(f'drop_init_{r}_frame{tag}',[i],fr)
json.dump({'detector_records':records,'all_detector_indices':det_idx,'record_to_line':rec_to_i},open(out/'manifest.json','w'),indent=2)
print('variants',len(list(out.glob('*.qasm'))))

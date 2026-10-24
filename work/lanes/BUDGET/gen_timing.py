import json,re
from pathlib import Path
base=Path('work/lanes/MAIN/spec/v17a.qasm'); txt=base.read_text().splitlines(); out=Path('work/lanes/BUDGET/timing');out.mkdir(exist_ok=True)
meta={'data_qubits':[0,20,7,10,3,22,21],'source':'v17a timing variant'}
# identify barriers by line context: barrier immediately before q17 final measure; and before q1 final Z block
ib17=next(i for i,l in enumerate(txt) if l.startswith('measure q[17]'))
b17=max(i for i in range(ib17) if txt[i].startswith('barrier'))
ib1=next(i for i,l in enumerate(txt) if l.startswith('measure q[1] -> c[14]'))
b1=max(i for i in range(ib1) if txt[i].startswith('barrier'))

def emit(name,lines):
 p=out/(name+'.qasm');p.write_text('\n'.join(lines)+'\n');d=dict(meta);d['name']=name;json.dump(d,open(out/(name+'.json'),'w'))

def drop(name,which):
 L=list(txt)
 for i in sorted(which,reverse=True): L.pop(i)
 emit(name,L)
emit('base',txt)
drop('drop_final_barrier',[b17]);drop('drop_zblock_barrier',[b1]);drop('drop_both',[b17,b1])
# Add candidate dummy CXs immediately after final barrier, before final q17 Z readout block.
for name,ops in {
 'dummy_q19_q20':['cx q[19],q[20];'],
 'dummy_q16_q10':['cx q[16],q[10];'],
 'dummy_q16_q22':['cx q[16],q[22];'],
 'dummy_q16_two':['cx q[16],q[10];','cx q[16],q[22];'],
 'dummy_three':['cx q[19],q[20];','cx q[16],q[10];','cx q[16],q[22];'],
}.items():
 L=list(txt); L[b17+1:b17+1]=ops;emit(name,L)

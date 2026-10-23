"""Executable audit probes; outputs are copied into REPORT.md."""
import sys
from pathlib import Path
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
import tprep
from tprep.qasm import to_stim
from tprep.check import _sample, final_round
import xtim

ROOT=Path('/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
DATA=[0,6,13,2,7,8,1]
base=(ROOT/'examples/injection.qasm').read_text()

print('noise_insertion')
print('\n'.join(tprep.apply_noise('H 0\nCX 0 1\nM 2\nR 2\nMX 0\nRX 1',1e-3).splitlines()))
native='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncreg c[1];\nreset q[0];\nh q[0];\nh q[1];\nmeasure q[1] -> c[0];\n'
print('native_x', to_stim(native)[0])
for name in ('DEPOLARIZE1(0.001) 0', 'swap q[0],q[1];', 'ch q[0],q[1];'):
    text='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\n'+name+'\n'
    print('reject',name,to_stim(text)[1])
print('barrier_standard',tprep.apply_noise('H 0\nCX 0 1\nCX 1 2\n',1e-3).splitlines())
print('barrier_idle',tprep.apply_noise('H 0\nCX 0 1\nCX 1 2\n',1e-3,tprep.IDLE).splitlines())
qhead='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\n'
for b in ('', 'barrier q[1],q[2];\n'):
    qtext=qhead+'h q[0];\ncx q[0],q[1];\n'+b+'reset q[2];\ncx q[1],q[2];\n'
    stim,err=to_stim(qtext)
    print('qasm_barrier',b.strip(),err,tprep.apply_noise(stim,1e-3).splitlines())

stim=to_stim(base)[0]
tail=final_round(DATA)+''.join(f'\nPAULI_EXPECTATION({k}) '+'*'.join(f'{P}{q}' for q in DATA) for k,P in enumerate('XY'))
for err in (f'X_ERROR(1) {DATA[3]}', f'X_ERROR(1) {DATA[3]} {DATA[4]}', f'Z_ERROR(1) {DATA[3]} {DATA[4]}'):
    print('final_correction',err,_sample(xtim.Circuit(stim+'\n'+err+'\n'+tail),256,0)['score'])

meas='h q[0];\ntdg q[0];\nh q[1];\ncx q[1],q[0];\nh q[1];\nmeasure q[1] -> m[0];\nreset q[1];\nt q[0];\n'
for tail2 in ('// FRAME_X(0)\n// FRAME_Z(0) m[0]\n','// POSTSELECT(0) m[0]\n', '// POSTSELECT(1) m[0]\n// FRAME_X(0)\n// FRAME_Z(1)\n'):
    text=base.replace('qreg q[36];','qreg q[36];\ncreg m[1];').replace('h q[0];\nt q[0];\n',meas,1)+tail2
    r=tprep.check(text,DATA,p=1e-3,shots=200000,seed=0)
    print('postselect',tail2.replace('\n','|'),r.acceptance,r.score,r.passed)

c=Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_0.qasm').read_text()
d=eval(Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_0.meta').read_text())
for sh in (200000,1000000):
    r=tprep.check(c,d,p=1e-3,shots=sh,seed=0)
    print('best_construction',sh,r.acceptance,r.score,r.passed,r.n_2q)
c2=Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_0_reset_h.qasm').read_text()
for sh in (200000,1000000):
    r=tprep.check(c2,d,p=1e-3,shots=sh,seed=0)
    print('best_reset_h',sh,r.acceptance,r.score,r.passed,r.n_2q)

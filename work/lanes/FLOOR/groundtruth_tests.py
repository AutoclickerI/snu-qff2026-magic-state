"""Ground-truth scheduler/raw correctness probes; no reviewer dependencies."""
import dataclasses, json, os
from pathlib import Path
import tprep, xtim
from tprep.qasm import to_stim
from tprep.noise import schedule, apply_noise
from tprep.exact import verify
from tprep.parse import declarations

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
xtim.cache_dir=str(OUT/'cache/xtim')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(OUT/'cache/twirl')
DATA=[0,6,13,2,7,8,1]
BASE=(ROOT/'upstream/snu-qff2026-problem/examples/injection.qasm').read_text().replace('qreg q[36];','qreg q[36];\ncreg c[8];')
HEADER='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[8];\n'

def write_case(name,text):
    (OUT/'experiments'/f'{name}.qasm').write_text(text)
    (OUT/'experiments'/f'{name}.json').write_text(json.dumps({'data_qubits':DATA})+'\n')

def main():
    rows={}
    probes={
      'ordinary_gates':'\n'.join(f'{g} q[{k}];' for k,g in enumerate(['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg'])),
      'terminal_idle':'h q[0];\ncx q[0],q[1];\nmeasure q[1] -> c[0];',
      'first_use_and_reset_gap':'h q[0];\nid q[0];\nbarrier q[0],q[2];\nreset q[2];\ncx q[1],q[2];',
      'final_measure_no_idle':'measure q[1] -> c[0];\nh q[0];\nid q[0];\nid q[0];',
      'reused_measure_idle':'measure q[1] -> c[0];\nh q[0];\nid q[0];\nbarrier q[0],q[1];\nid q[1];',
      'native_x':'reset q[0];\nh q[0];\ncx q[0],q[1];\nh q[0];\nmeasure q[0] -> c[0];\nh q[0];\nid q[0];',
      'native_across_barrier':'reset q[0];\nbarrier q[0],q[1];\nh q[0];\ncx q[0],q[1];\nh q[0];\nbarrier q[0],q[1];\nmeasure q[0] -> c[0];',
      'trailing_barrier':'h q[0];\ncx q[0],q[1];\nbarrier q;',
      'record_overwrite':'measure q[0] -> c[0];\nmeasure q[1] -> c[0];\n// DETECTOR c[0]\n// FRAME_X(0) c[0]\n// FRAME_Z(0)',
      'forbidden_feedforward':'measure q[0] -> c[0];\nif(c==1) x q[1];',
    }
    for name,tail in probes.items():
        text=HEADER+tail+'\n'; write_case(name,text)
        st,errs=to_stim(text)
        row=dict(errors=errs,stim=st)
        if not errs:
            prog,steps,gaps=schedule(st)
            row.update(steps=steps,gaps=gaps,noisy=apply_noise(st,.001))
        rows[name]=row
    for name,tail in {
      'base':'', 'output_M':'measure q[0] -> c[0];',
      'output_MX':'h q[0];\nmeasure q[0] -> c[0];\nh q[0];',
      'output_R':'reset q[0];', 'output_RX':'reset q[0];\nh q[0];',
      'output_M_postselect':'measure q[0] -> c[0];\n// POSTSELECT(0) c[0]',
      'wrong_physical_frame':'x q[0];\n// FRAME_X(0)\n// FRAME_Z(0)',
      'logical_X_frame':'\n'.join(f'x q[{q}];' for q in DATA)+'\n// FRAME_X(1)\n// FRAME_Z(0)',
      'late_helper_M':'barrier q;\nmeasure q[35] -> c[0];',
      'unused_output':'',
    }.items():
        text=BASE+tail+'\n'; write_case(name,text)
        st,errs=to_stim(text)
        data=DATA if name!='unused_output' else [35]+DATA[1:]
        frame,post=declarations(st)
        raw=verify(st,data,frame=frame,postselect=post)
        # The actual public entry point additionally checks xtim class and raw/xtim agreement.
        r=tprep.check(text,data,p=0,shots=64)
        rows[name]=dict(raw=raw,judge=str(r),passed=r.passed)
        print(name,rows[name],flush=True)
    (OUT/'experiments/groundtruth.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('COMPLETE',flush=True)

if __name__=='__main__':main()

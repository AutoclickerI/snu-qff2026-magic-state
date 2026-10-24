#!/usr/bin/env python3
"""Static exact-engine speed screen for grid T-preparation circuits.

  .venv/bin/python work/lanes/FRESH/general_atoms.py <stem> [--details]

Uses the installed judge's STANDARD noise and tail, and xtim's own normalized /
deferred signature. Counts noise X/Z basis atoms that leave the fast diagonal
representation. A zero-shot installed-engine compile distinguishes a legal PPR
retry from a class rejection. Does not sample shots or modify xtim / the judge.

FAST predicts the diagonal replay path, not a universal runtime guarantee;
SLOW predicts the circuit-wide general path on every shot with a fired event.
The 20 s/1e6 timing gate must still be measured for finalists.
"""
from __future__ import annotations
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,fcntl,hashlib,importlib,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'))
import xtim
from tprep.qasm import to_stim
from tprep.noise import STANDARD,apply_noise
checkmod=importlib.import_module('tprep.check')
BUILD=HERE/'.general_atoms'

def executable():
 source=HERE/'general_atoms.cpp';digest=hashlib.sha256(source.read_bytes()).hexdigest()[:16]
 BUILD.mkdir(exist_ok=True);binary=BUILD/('atoms_'+digest)
 with (BUILD/'build.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  if not binary.exists():
   target=binary.with_name(binary.name+f'.{os.getpid()}.tmp')
   env=dict(os.environ,TMPDIR=str(BUILD))
   subprocess.run(['g++','-std=c++17','-O3',str(source),'-o',str(target)],check=True,capture_output=True,env=env)
   target.replace(binary)
 return binary

def noisy_text(stem):
 stem=Path(stem)
 if stem.suffix=='.qasm':stem=stem.with_suffix('')
 qasm=stem.with_suffix('.qasm').read_text();native,errors=to_stim(qasm)
 if errors:raise ValueError('; '.join(errors))
 data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
 noisy=apply_noise(native,.001,STANDARD)
 npre=xtim.Circuit(noisy).num_measurements
 # Pauli frames affect record signs, not the gate/noise propagation table.
 plan=checkmod.Plan(data,{'X':(0,[]),'Z':(0,[])},(),npre)
 return noisy+'\n'+plan.tail,stem,hashlib.sha256(qasm.encode()).hexdigest()

def analyze_text(text,details=False):
 signature=xtim._xtim.deferred_signature(text);parts=signature.split(';')
 n=int(parts[0][2:]);instructions=[]
 for row in parts[1:]:
  if row.startswith('reads='):break
  if not row:continue
  kind,body=row.split(':');xs=body.split(',')
  targets=[int(x) for x in xs[1:] if x.lstrip('-').isdigit()]
  instructions.append((int(kind),int(xs[0]) if xs[0].isdigit() else -1,targets,row))
 payload=f'{n} {len(instructions)}\n'+'\n'.join(f'{k} {g} {len(q)} '+' '.join(map(str,q)) for k,g,q,_ in instructions)
 result=subprocess.run([str(executable())],input=payload,text=True,capture_output=True,check=True)
 raw=json.loads(result.stdout)
 program=xtim._xtim.CompiledProgram(text,'')
 if not program.ok:raise ValueError(program.errors)
 verdict=program.sample(0,0,False,False,False,False)
 rejected=bool(verdict['rejected'])
 out=dict(prediction='REJECTED' if rejected else ('SLOW' if raw['failed_atoms'] else 'FAST'),
          general_atoms=None if rejected else raw['failed_atoms'],standard_failures=raw['failed_atoms'],
          total_atoms=raw['total_atoms'],class_rejected=rejected,
          reject_gate_index=verdict['reject_gate_index'],deferred_wires=n,
          normalized_instructions=len(instructions),offending_gates=[dict(index=j,qubit=q,atoms=c,instruction=instructions[j][3]) for j,q,c in raw['bad_gates']],
          scope='Exact-engine dispatch screen; validated on current T-prep family. FAST is not a universal <=20s runtime certificate.')
 if details:
  out['atoms']=[dict(noise_index=i,noise_instruction=instructions[i][3],qubit=q,axis='XZ'[axis],first_bad_gate=j,gate_instruction=instructions[j][3]) for i,q,axis,j,gq in raw['failures']]
 return out

def analyze(stem,details=False):
 start=time.perf_counter();text,path,sha=noisy_text(stem);out=analyze_text(text,details)
 out.update(stem=str(path),qasm_sha256=sha,seconds=time.perf_counter()-start)
 return out

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stem');parser.add_argument('--details',action='store_true');a=parser.parse_args()
 try:print(json.dumps(analyze(a.stem,a.details),sort_keys=True))
 except Exception as ex:
  print(json.dumps(dict(prediction='ERROR',error=repr(ex))),flush=True);raise SystemExit(2)

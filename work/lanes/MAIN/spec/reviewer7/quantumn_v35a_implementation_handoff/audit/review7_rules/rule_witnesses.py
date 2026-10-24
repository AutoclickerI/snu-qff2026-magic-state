"""Small legal witnesses for rule freedoms, not optimization candidates.

Uses the unchanged official judge from its pinned review6 installation.
Full-target witnesses use the organizer's injection example; simple native
probes establish parser/scheduler/class semantics only.
"""
from pathlib import Path
import dataclasses, hashlib, json, math, re, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'audit/review6_validation/official'))
import tprep, xtim
from tprep.qasm import to_stim
from tprep.noise import schedule, noise_blocks, apply_noise

HEADER = 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[2];\n'
DATA = [0,6,13,2,7,8,1]

def native_case(name, body):
    text = HEADER + body
    native, errors = to_stim(text)
    out = dict(name=name, scope='native conversion/schedule/class only; not a target-state circuit',
               format_errors=errors)
    if native:
        prog, steps, gaps = schedule(native)
        out.update(native=native, schedule=[dict(instruction=i.text, ticks=[t for _,t in ss])
                   for i,ss in zip(prog,steps)], idle_gaps=gaps,
                   noise_blocks=noise_blocks(native,.001)[1])
        try:
            diagnosis = xtim.diagnose(xtim.Circuit(apply_noise(native,0)))
            out['class_passed'] = True
        except Exception as exc:
            out.update(class_passed=False,class_error=f'{type(exc).__name__}: {exc}')
    return out

def full_case(name,text):
    path=HERE/(name+'.qasm');path.write_text(text)
    start=time.perf_counter()
    report=tprep.check(text,DATA,shots=10000,seed=0)
    out=dict(name=name,scope='full target, official four-gate check at 10000 shots; no optimization claim',
             qasm_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
             seconds=time.perf_counter()-start,
             gates={k:getattr(report,k) for k in ['format_ok','class_ok','correct_ok','acceptance_ok','passed']},
             report=dataclasses.asdict(report))
    (HERE/(name+'.json')).write_text(json.dumps(out,indent=2,default=str)+'\n')
    return out

def main():
    native=[
      native_case('native_RX','reset q[0];\nh q[0];\n'),
      native_case('native_MX_reuse','h q[0];\nmeasure q[0] -> c[0];\nh q[0];\ncx q[0],q[1];\n'),
      native_case('native_SX','sx q[0];\nsxdg q[0];\n'),
      native_case('partial_barrier','h q[0];\nt q[0];\ntdg q[0];\nbarrier q[0];\nreset q[1];\nh q[1];\ncx q[1],q[2];\n'),
      native_case('global_barrier','h q[0];\nt q[0];\ntdg q[0];\nbarrier q[0],q[1],q[2];\nreset q[1];\nh q[1];\ncx q[1],q[2];\n'),
      native_case('commuting_temporally_separated_T','h q[0];\nh q[1];\nt q[0];\ncx q[0],q[1];\nt q[1];\ncx q[0],q[1];\n'),
      native_case('noncommuting_T_rejected','h q[0];\nt q[0];\nh q[0];\nt q[0];\nh q[0];\n'),
      native_case('legacy_CZ_rejected','cz q[0],q[1];\n'),
      native_case('initial_and_terminal_lifetimes','h q[0];\nt q[0];\ntdg q[0];\nmeasure q[0] -> c[0];\nh q[1];\nbarrier q[0],q[1];\nreset q[1];\n'),
    ]
    problem=(HERE/'official/problem.md').read_text()
    examples=re.findall(r'```qasm\n(.*?)\n```',problem,re.S)
    embedded=next(t for t in examples if 'qreg q[36]'in t)+'\n'
    # problem.md's inline copy is stale; use the actual linked example file.
    _,embedded_errors=to_stim(embedded)
    injection=(HERE/'official/examples/injection.qasm').read_text()
    assert 'q[35]'not in injection
    base=injection.replace('qreg q[36];','qreg q[36];\ncreg c[2];')
    coin=base.replace('creg c[2];','creg c[2];\nh q[35];\nt q[35];\nh q[35];\nmeasure q[35] -> c[0];')
    full=[
      full_case('organizer_injection_control',base),
      full_case('biased_noiseless_postselection',coin+'// POSTSELECT(0) c[0]\n// FRAME_X(0)\n// FRAME_Z(0)\n'),
      full_case('conditional_detector',coin+'// POSTSELECT(0) c[0]\n// DETECTOR c[0]\n// FRAME_X(0)\n// FRAME_Z(0)\n'),
      full_case('constant_logical_X_frame',base+''.join(f'x q[{q}];\n'for q in DATA)+'// FRAME_X(1)\n// FRAME_Z(0)\n'),
    ]
    result=dict(official_commit='76fe47c0324f1c1f8b72a7d55af200e88043b522',
       description=__doc__,data_qubits=DATA,native_witnesses=native,full_target_witnesses=full,
       biased_selector_exact_ideal_acceptance=math.cos(math.pi/8)**2,
       stale_inline_problem_example_format_errors=embedded_errors,
       precision_note='Official exact means deterministic algebra up to floating-point roundoff, not interval arithmetic.')
    assert all(r['gates']['passed'] for r in full)
    assert abs(full[1]['report']['ideal_acceptance']-math.cos(math.pi/8)**2)<1e-12
    (HERE/'rule_witnesses.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    print(json.dumps(dict(native=[{k:r[k]for k in ['name','format_errors','class_passed']if k in r}for r in native],
       full=[dict(name=r['name'],gates=r['gates'],ideal_acceptance=r['report']['ideal_acceptance'],
                  noisy_acceptance=r['report']['acceptance'])for r in full]),indent=2))

if __name__=='__main__':main()

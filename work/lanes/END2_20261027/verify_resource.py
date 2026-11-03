"""Independent official-simulator check of all14 resource stabilizers."""
import json,sys
from pathlib import Path
from joint import f,emit,HERE
from tprep.exact import run

def verify(path):
    path=Path(path);sol=json.loads(path.read_text());m=sol['module'];B=m['B'];C=m['C']
    ops=[f.Op(i['kind'],(i['q'],),i['time'],i['bit']) for i in m['initializations']]
    ops += [f.Op('CX',tuple(edge),t) for t,layer in enumerate(m['layers']) for edge in layer]
    ops.sort(key=lambda o:o.time)
    state,inv,records,_,wires=run(f.native_text(ops)[0],36)
    bits={o.bit:records[i] for i,o in enumerate(o for o in ops if o.bit is not None)}
    def expectation(qs,P,refs=()):
        p=state.stim.PauliString(state.n)
        for q in qs:p[wires[q]]=P
        for bit in refs:p[bits[bit]]='Z'
        return state.expectation(p,inv)
    values=[]
    for check in m['B_X_checks']:
        values.append({'name':'B_X_'+str(check['B_indices']),'expectation':expectation([B[i] for i in check['B_indices']],'X',check['initial_record_xor'])})
    for row in f.SUPPORTS:
        values.append({'name':'B_Z_'+str(sorted(row)),'expectation':expectation([B[i] for i in row],'Z')})
    values.append({'name':'B_Z_logical','expectation':expectation(B,'Z')})
    cz=m['C_Z_checks'] if isinstance(m['C_Z_checks'],list) else [{'C_indices':[i]} for i in range(7)]
    for check in cz:values.append({'name':'C_Z_'+str(check['C_indices']),'expectation':expectation([C[i] for i in check['C_indices']],'Z')})
    for check in m.get('C_X_generators',[]):
        values.append({'name':'C_X_'+str(check['C_indices']),'expectation':expectation([C[i] for i in check['C_indices']],'X',check['initial_record_xor'])})
    init_values=[]
    for row in m['initial_zero_detectors']:
        p=state.stim.PauliString(state.n)
        for bit in row:p[bits[bit]]='Z'
        init_values.append(state.expectation(p,inv))
    out={'solution':str(path),'generators':values,'zero_initialization_expectations':init_values,
         'ok':all(abs(v['expectation']-1)<1e-10 for v in values) and all(abs(v-1)<1e-10 for v in init_values)}
    sol['resource_raw']=out;path.write_text(json.dumps(sol,indent=2)+'\n')
    path.with_suffix('.resource.qasm').write_text(emit(ops,[set(r) for r in m['initial_zero_detectors']]))
    print(json.dumps(out,indent=2));return out

if __name__=='__main__':verify(sys.argv[1])

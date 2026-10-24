#!/home/jihoon/competitions/quantumn/.venv/bin/python
import json,sys
sys.path.insert(0,'/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
import tprep
q,d=sys.argv[1],json.load(open(sys.argv[2]));r=tprep.check(open(q).read(),d['data_qubits'],shots=10**6,seed=0)
o={'passed':r.passed,'format':r.format_ok,'class':r.class_ok,'correctness':r.correct_ok,'acceptance_ok':r.acceptance_ok,'acceptance':r.acceptance,'score':r.score,'n_2q':r.n_2q,'sem':r.sem,'format_errors':r.format_errors,'correctness_errors':r.correctness_errors}
print(json.dumps(o),flush=True);sys.exit(0 if r.passed else 1)

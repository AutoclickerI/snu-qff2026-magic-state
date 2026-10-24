"""Reproduce reviewer's isolated-storage a^3 coefficient, not the full noisy circuit."""
import itertools,json
from pathlib import Path
LINES=[{0,1,2},{0,3,4},{1,3,5},{2,4,5},{2,3,6},{1,4,6},{0,5,6}]
def coeff(protected):
 # Accepted triples on a Fano line: XXX costs 1/2, ZZZ costs1, YYY costs1/2.
 # Z protection deletes Z/Y there and doubles X exposure (data + helper).
 return sum(.5*2**len(line&protected)+(1.5 if not line&protected else 0.) for line in LINES)
rows={}
for n in range(8):
 vals=[dict(positions=list(s),coefficient=coeff(set(s)),fano=set(s) in LINES) for s in itertools.combinations(range(7),n)]
 rows[str(n)]=vals
summary={'none':coeff(set()),'one':coeff({0}),'two':coeff({0,1}),'fano_three':coeff({0,1,2}),'all_seven':coeff(set(range(7)))}
assert summary==dict(none=14.,one=11.,two=10.,fano_three=10.,all_seven=28.)
def dual_coeff(protected):
 return sum(2**len(line&protected)+(1. if not line&protected else 0.) for line in LINES)
dual={k:dual_coeff(v) for k,v in dict(none=set(),one={0},two={0,1},fano_three={0,1,2},all_seven=set(range(7))).items()}
assert dual==dict(none=14.,one=14.,two=16.,fano_three=20.,all_seven=56.)
Path(__file__).with_suffix('.json').write_text(json.dumps(dict(summary=summary,x_dual=dual,rows=rows),indent=2))
print(json.dumps(summary))
print(json.dumps(dual))

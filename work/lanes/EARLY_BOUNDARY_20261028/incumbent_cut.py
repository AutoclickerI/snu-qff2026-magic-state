import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'work/lanes/NATIVE2_20261027'))
from incumbent_a_sx import f,emit,to_stim,run
P=next((R/'work/lanes/SOTA_20261028/native_best').glob('*.qasm'));ops,dets=f.parse_current(P.read_text());prefix=[o for o in ops if o.time<39];bits={o.bit for o in prefix if o.bit is not None};native,err=to_stim(emit(prefix,[r for r in dets if r<=bits]));assert not err
s,inv,records,_,w=run(native,36)
def E(terms):
 p=s.stim.PauliString(s.n)
 for q,a in terms:p[w[q]]=a
 return s.expectation(p,inv)
rows={
 'Z15Z16':[(15,'Z'),(16,'Z')],
 'X15X16X19X20X22':[(q,'X') for q in [15,16,19,20,22]],
 'X15X16X19X20Y22':[(q,'X') for q in [15,16,19,20]]+[(22,'Y')],
 'X15':[(15,'X')],'Y15':[(15,'Y')],'Z15':[(15,'Z')],
 'Z21':[(21,'Z')],
}
out={k:E(v) for k,v in rows.items()};print(json.dumps(out));(H/'incumbent_cut.json').write_text(json.dumps(out,indent=2)+'\n')

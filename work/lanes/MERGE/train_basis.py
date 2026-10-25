import os,sys,json,time,contextlib,io
from pathlib import Path
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H));import ev37 as E
if __name__=='__main__':
 stem=Path(sys.argv[1]);target=Path(sys.argv[2]);sw=E.sw
 with contextlib.redirect_stdout(io.StringIO()):m,eng,groups,nd,ks,*_=sw.prepare(stem,True)
 bases=json.loads(sw.WARM.read_text());choices=[]
 for name,warm in bases['bases'].items():
  ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=0);choices.append((cost,name,warm,ops))
 cost,name,warm,ops=min(choices)
 print('best replay',name,cost,flush=True)
 ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=int(sys.argv[3]) if len(sys.argv)>3 else 1000)
 keys=[','.join(map(str,sorted(d))) for d in m.dets]
 bases['bases']['MERGE_current']=[[keys[t],keys[s]] for t,s in ops]
 target.write_text(json.dumps(bases,indent=2)+'\n')
 print('trained',cost,target,flush=True)

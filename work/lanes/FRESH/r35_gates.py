from round35 import *
import re,subprocess

def gate(stem,procs,preonly=False):
 stem=Path(stem).resolve();a=json.loads(Path(str(stem)+'.allorders.json').read_text());assert a['loss']<BASE_LOSS and a['acceptance']>=.5005
 cert=certify(stem);sp=speed(stem);print('SPEED',sp,flush=True)
 assert sp['classification']=='FAST'
 import fast_check
 start=time.monotonic();rep=fast_check.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=1)
 j=dict(passed=rep.passed,acceptance=rep.acceptance,score=rep.score,sem=rep.sem,n_2q=rep.n_2q,seconds=time.monotonic()-start,report=repr(rep))
 Path(str(stem)+'.judge.json').write_text(json.dumps(j,indent=2));print('JUDGE',j,flush=True);assert j['passed'] and j['acceptance']>=.5 and j['seconds']<=20
 if preonly:return
 argv=[str(ROOT/'work/lanes/MAIN/spec/mc3.py'),str(stem),'--procs',str(procs)]
 code="import os,sys,runpy,xtim;xtim.cache_dir=os.environ['XTIM_TWIRL_CACHE_DIR'];sys.argv="+repr(argv)+";runpy.run_path(sys.argv[0],run_name='__main__')"
 with Path(str(stem)+'.mc3.log').open('w') as log:
  p=subprocess.run([sys.executable,'-B','-c',code],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
 assert p.returncode==0
 txt=Path(str(stem)+'.mc3.log').read_text();seeds=[float(v) for v in re.findall(r' (?:0|1000|2000) ([\deE+.-]+) ±',txt)];assert len(seeds)==3,txt
 out=dict(ideal=cert,allorders={k:a[k] for k in ('loss','acceptance')},speed=sp,judge=j,seeds=seeds,mean=sum(seeds)/3)
 Path(str(stem)+'.verified.json').write_text(json.dumps(out,indent=2));print('VERIFIED',json.dumps(out),flush=True)
 import runpy
 runpy.run_path(str(HERE/'r35_report.py'),run_name='__main__')

if __name__=='__main__':gate(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 7,'--pre' in sys.argv)

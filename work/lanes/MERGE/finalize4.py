from pass4 import *
import importlib.util,statistics,socket,runpy

def original_replay(st):
 src=H/'archive/sparse_walsh_before_best_warm.py';spec=importlib.util.spec_from_file_location('original_sparse_pass4',src);sw=importlib.util.module_from_spec(spec);spec.loader.exec_module(sw)
 sw.WARM=E.sw.WARM;sw.SEARCH_WIDTH=12;contract=sw.contract_quotient
 def empty(compiled,states,emask,order):
  if len(states)==0:return sw.np.empty(0,dtype=float),0
  return contract(compiled,states,emask,order)
 sw.contract_quotient=empty;t=time.monotonic()
 with contextlib.redirect_stdout(io.StringIO()):
  m,eng,groups,nd,ks,psi,where,de=sw.prepare(st,True);compiled,elim=sw.compile_best(m,eng,groups,nd,ks);sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim);rows=[sw._row(k)for k in [None]+eng.keys[:72]]
 A=rows[0]['value'];obs=sum(w*b*r['value']for w,b,r in zip(eng.W,eng.beta,rows[1:]));return dict(sha256=sha(st),loss=(A-obs)/(2*A),acceptance=A,seconds=time.monotonic()-t,width=elim['width'],core_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),basis_sha256=hashlib.sha256(sw.WARM.read_bytes()).hexdigest())

def cli(st):
 sys.path.insert(0,str(ROOT/'work'));import xtim
 xtim.cache_dir=str(H/'.xtim_cache');sys.argv=[str(ROOT/'work/fast_check.py'),str(st.with_suffix('.qasm')),str(st.with_suffix('.json')),'1000000','1'];out=io.StringIO()
 with contextlib.redirect_stdout(out):state=runpy.run_path(str(ROOT/'work/fast_check.py'),run_name='__main__')
 r=dict(sha256=sha(st),seconds=time.time()-state['t'],gates_ok=bool(state['rep'].correct_ok),shots=10**6,procs=1,host=socket.gethostname(),stdout=out.getvalue());print(json.dumps(dict(event='final_cli',**r)),flush=True);return r

def main():
 outcome=json.loads((R/'wide_outcome.json').read_text());assert outcome['complete']and outcome['last_gain']<1e-9
 best=outcome['price'];assert feasible(best);st=Path(best['stem']);E.configure(Path(best['evaluator_basis']),12);replay=original_replay(st);dump(R/'final_replay.json',replay)
 assert abs(replay['loss']-best['loss'])<1e-13 and abs(replay['acceptance']-best['acceptance'])<1e-13
 controls=[];runs=[]
 for i in range(3):
  for name,path in ([('base',C/'base'),('candidate',st)]if i%2==0 else [('candidate',st),('base',C/'base')]):
   r=cli(path);(controls if name=='base'else runs).append(r)
 b=statistics.median(r['seconds']for r in controls);c=statistics.median(r['seconds']for r in runs)
 judge=dict(sha256=sha(st),host=socket.gethostname(),gates_ok=all(r['gates_ok']for r in runs),speed_ok=c<=1.5*b,median_seconds=c,baseline_median_seconds=b,ratio=c/b,judge_runs=runs,baseline_runs=controls)
 dump(R/'final_cli.json',judge);assert judge['gates_ok']and judge['speed_ok'],judge
 best=dict(best,judge_1e6=judge,independent_replay=replay,tau=TAU,J_tau=best['acceptance']*(best['loss']-TAU));name='merge4_final'if best['loss']<TAU-3e-8 else 'merge4_best_below_target';dest=H/'cand'/name
 plan=M.read(st);best.update(cx=sum(M.unit(o).name=='CX'for o in plan['ops']),native_depth=M.depth(plan),source=dict(base='v37f',transport='all four PREPFREE/POLISH modules',rounds=outcome['rounds'],history='res37f/wide_history.json'))
 assert name=='merge4_final','Best does not qualify; retain only in builds with its report'
 shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),best);dump(R/'final_artifact.json',dict(name=name,sha256=sha(st),loss=best['loss'],acceptance=best['acceptance'],J_tau=best['J_tau'],cx=best['cx'],native_depth=best['native_depth'],judge=judge))
 print(json.dumps(dict(event='finalized',name=name,loss=best['loss'],acceptance=best['acceptance'],ratio=judge['ratio'])),flush=True)
if __name__=='__main__':main()

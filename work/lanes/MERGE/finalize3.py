from pass3 import *
import runpy,importlib.util,socket,re
def replay(st,basis):
 # Independently replay the archived pre-optimization evaluator implementation.
 sys.path.insert(0,str(H/'sparse_v37'))
 oldfile=H/'archive/sparse_walsh_before_best_warm.py'
 spec=importlib.util.spec_from_file_location('original_merge_evaluator',oldfile);sw=importlib.util.module_from_spec(spec);spec.loader.exec_module(sw)
 sw.WARM=Path(basis);sw.SEARCH_WIDTH=12
 original=sw.contract_quotient
 def empty(compiled,states,emask,order):
  return (sw.np.empty(0,dtype=float),0)if len(states)==0 else original(compiled,states,emask,order)
 sw.contract_quotient=empty;t=time.monotonic()
 with contextlib.redirect_stdout(io.StringIO()):
  m,eng,groups,nd,ks,psi,where,de=sw.prepare(st,True);compiled,elim=sw.compile_best(m,eng,groups,nd,ks)
  sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim);rows=[sw._row(k)for k in [None]+eng.keys[:72]]
 A=rows[0]['value'];obs=sum(w*b*r['value']for w,b,r in zip(eng.W,eng.beta,rows[1:]))
 return dict(sha256=sha(st),loss=(A-obs)/(2*A),acceptance=A,width=elim['width'],seconds=time.monotonic()-t,core_sha256=hashlib.sha256(oldfile.read_bytes()).hexdigest(),basis_sha256=hashlib.sha256(sw.WARM.read_bytes()).hexdigest())
def main():
 outcome=json.loads((R/'bc3polish_outcome.json').read_text());h=outcome['history'];best=outcome['price'];assert h[-1]['stop']
 st=Path(best['stem']);v=json.loads((R/f"judge_{best['sha256']}.json").read_text());assert v['gates_ok']and v['speed_ok']
 dest=H/'cand/merge3_final';shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'));c=M.read(st)
 meta=dict(best,source=dict(base='MAIN/v37d',base_sha256=sha(C/'base'),BC3_core='v37d/bc3_7',BC3_core_sha256=sha(C/'bc3_7'),greedy_edits=h[-1]['selected']),judge_1e6=v,
           cx=sum(M.unit(o).name=='CX'for o in c['ops']),native_depth=M.depth(c),gain=TAU-best['loss'],tau=TAU)
 dump(dest.with_suffix('.json'),meta)
 import xtim
 xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
 sys.path.insert(0,str(ROOT/'work'));sys.argv=[str(ROOT/'work/fast_check.py'),str(dest.with_suffix('.qasm')),str(dest.with_suffix('.json')),'1000000','1']
 with (H/'logs37d/final_fast_check.txt').open('w')as f,contextlib.redirect_stdout(f):state=runpy.run_path(str(ROOT/'work/fast_check.py'),run_name='__main__')
 seconds=state['time'].time()-state['t'];gates_ok=bool(state['rep'].correct_ok)
 log=(H/'logs37d/final_fast_check.txt').read_text();print(log,flush=True)
 assert gates_ok and seconds<=4.8,(gates_ok,seconds,log)
 meta['final_cli_check']=dict(host=socket.gethostname(),shots=1000000,procs=1,gates_ok=True,seconds=seconds,log='logs37d/final_fast_check.txt')
 r=replay(st,best.get('evaluator_basis',R/'basis_fused.json'));assert abs(r['loss']-best['loss'])<1e-13 and abs(r['acceptance']-best['acceptance'])<1e-13
 dump(R/'final_replay.json',r);meta['independent_replay']=r;dump(dest.with_suffix('.json'),meta)
 print(json.dumps(dict(event='FINAL',path=str(dest),**meta)),flush=True)
if __name__=='__main__':main()

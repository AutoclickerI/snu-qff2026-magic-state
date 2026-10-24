"""Native prefix metadata, pre-only/no-pre ablation, and separate 9-CX grid-free R33."""
import os,sys,json,re,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT/'inputs'),str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work/lanes/MAIN'),str(ROOT/'work/lanes/MAIN/gf'),str(ROOT/'work/lanes/EARLY'),str(ROOT/'work/lanes/DR')]
import schedule as S
from util import native_times
import exact2,ablate,model

def score(text,data,procs):
    ev=exact2.Eval(text,data);r=exact2.run(ev,procs,third=True,keep_thr=1)
    out={k:float(r[k])for k in ['loss1','loss2','A1']};out['exp_minus_A1']=float(exact2.np.exp(-r['A1']))
    if abs(r['loss1'])<1e-12:out['loss3']=exact2.third_order(ev,procs)[0]+r['t3bc'];out['total']=r['loss']+out['loss3']
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--procs',type=int,default=8);ap.add_argument('--full',action='store_true');ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    stem=OUT/a.stem;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());data=meta['data_qubits'];end=meta['pre_end'];R=meta['R']
    head,raw,tail=S.qasm_ops(text);units=S.fold_units(raw);times=native_times(text,units)
    preids=set(meta.get('prefix_unit_indices',[i for i,t in enumerate(times)if t<=end]));prefix=[(u,t)for i,(u,t)in enumerate(zip(units,times))if i in preids]
    info=dict(pre_cx=sum(u.name=='CX'for u,t in prefix),pre_depth=max(t for u,t in prefix)+1,full_cx=sum(u.name=='CX'for u in units),depth=max(times)+1,
              release={q:max(t for u,t in prefix if q in u.qs)+1 for q in [1,6,13,2,9,14]})
    labels=ablate.labeller(set(data),set([1,14,8,9,2,16,15]),end,R)
    def provenance_patch(keep):
        converted,clabels,errs=model.convert(text,36,model.STANDARD);assert not errs
        qmap=S.native_qasm_index(text);raw_to_unit={j:i for i,u in enumerate(units)for j in u.raw_indices}
        def nb(stim,p,noise,first_order=False):
            prog,blocks=ablate._orig(stim,p,noise,first_order);_,steps,gaps=model.schedule(stim)
            ownership={}
            for i,ins in enumerate(prog):
                lab=clabels[ins.line_no-1];mt=re.match(r'instruction (\d+)',lab)
                ownership[i]=bool(mt and int(mt.group(1))in qmap and raw_to_unit[qmap[int(mt.group(1))]]in preids)
                if not keep('pre'if ownership[i]else'post'):
                    block=blocks[i];k=block.index(ins.text);nidle=sum(g[0]==i for g in gaps)
                    for j in range(len(block)-nidle):
                        if j!=k:block[j]=re.sub(r'\(([^)]*)\)','(0)',block[j],count=1)
            for i,q,first,n in gaps:
                if not keep('pre'if ownership[i]else'post'):
                    for j in range(len(blocks[i])-1,-1,-1):
                        line=blocks[i][j]
                        if line.startswith('DEPOLARIZE1(')and line.split()[-1]==str(q)and '(0)'not in line:
                            blocks[i][j]=re.sub(r'\(([^)]*)\)','(0)',line,count=1);break
            return prog,blocks
        return nb
    if a.resume and (OUT/(a.stem+'.price.json')).exists():info.update(json.loads((OUT/(a.stem+'.price.json')).read_text()))
    for name,keep in [('only_pre',lambda r:r=='pre'),('no_pre',lambda r:r!='pre')]:
        if a.resume and name in info:continue
        model.noise_blocks=provenance_patch(keep) if 'prefix_unit_indices'in meta else ablate.patched(keep,*labels)
        try:info[name]=score(text,data,a.procs)
        finally:model.noise_blocks=ablate._orig
        print(name,info[name],flush=True);(OUT/(a.stem+'.price.json')).write_text(json.dumps(info,indent=2)+'\n')
    if a.full:info['full']=score(text,data,a.procs);print('full',info['full'],flush=True)
    # Load just the dependency-free encoder and constants from the copied gf33
    # source. Remote mirrors need not contain the unused early_merge builder.
    import ast,types
    tree=ast.parse((OUT/'inputs/gf33.py').read_text());wanted={'PRE_DATA','FREE','PIV','LAYERS0'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='enc' or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in wanted for t in n.targets)]
    namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'gf33.enc','exec'),namespace)
    gf33=types.SimpleNamespace(**namespace,GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]])
    predata=gf33.PRE_DATA;A,B,C=gf33.FREE[:7],gf33.FREE[7:14],gf33.FREE[14:21];newu=[u for u,t in prefix];newt=[t for u,t in prefix]
    if max(newt)>32:
        from ortools.sat.python import cp_model
        sm=cp_model.CpModel();tv=[sm.new_int_var(0,32,f'p{i}')for i in range(len(newu))];last={}
        for i,u in enumerate(newu):
            for q in u.qs:
                if q in last:sm.add(tv[i]>tv[last[q]])
                last[q]=i
        sm.maximize(sum(tv));ss=cp_model.CpSolver();ss.parameters.num_search_workers=a.procs;status=ss.solve(sm);assert status in(cp_model.OPTIMAL,cp_model.FEASIBLE)
        newt=[ss.value(t)for t in tv];info['gf33_rescheduled_prefix']='ALAP under native step 32 deadline; same parity network'
    for cells,plus in [(A,True),(B,False),(C,False)]:
        by={}
        for t,l in gf33.enc(cells,plus,30):by.setdefault(t,[]).append(l)
        for t,ls in by.items():
            us=S.fold_units(ls);newu.extend(us);newt.extend([t]*len(us))
    bits={};n=14
    for i in range(7):
        newu.append(S.Unit([f'cx q[{predata[i]}],q[{A[i]}];'],[]));newt.append(33)
        newu.append(S.Unit([f'cx q[{B[i]}],q[{C[i]}];'],[]));newt.append(33)
    for k,cells in [('a',A),('c',C),('b',B)]:
        for i,q in enumerate(cells):
            bits[k,i]=n;ls=([f'h q[{q}];']if k=='b'else[])+[f'measure q[{q}] -> c[{n}];'];n+=1
            newu.append(S.Unit(ls,[]));newt.append(35 if k=='b' else 34)
    for i in range(7):newu.append(S.Unit([f'cx q[{B[i]}],q[{predata[i]}];'],[]));newt.append(34)
    det=[l for l in tail if l.startswith('// DETECTOR')and all(int(x)<14 or int(x)in(39,40,41,42)for x in re.findall(r'c\[(\d+)\]',l))]
    for k in ['a','b','c']:
        for g in gf33.GENS:det.append('// DETECTOR '+' '.join(f'c[{bits[k,i]}]'for i in g))
    det.append('// DETECTOR '+' '.join(f'c[{bits["c",i]}]'for i in range(7)))
    # Empty initial steps have no physical effect. Explicit idles on a C cell
    # that is subsequently reset preserve the requested absolute R=33 label.
    for t in range(29):
        if t not in newt:newu.append(S.Unit(['id q[35];'],[]));newt.append(t)
    gf=S.emit(head,newu,newt,det);gstem=OUT/(a.stem+'_gf33');gstem.with_suffix('.qasm').write_text(gf);gstem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=predata,R=33,grid_free=True))+'\n')
    import tprep.qasm
    tprep.qasm.adjacent=lambda a,b:True
    info['gf33']=score(gf,predata,a.procs);print('gf33',info['gf33'],flush=True)
    (OUT/(a.stem+'.price.json')).write_text(json.dumps(info,indent=2)+'\n')

if __name__=='__main__':main()

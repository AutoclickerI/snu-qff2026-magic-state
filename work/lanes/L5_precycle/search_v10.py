"""L5 continuation: fixed-v10 cycle, movable pre-cycle gates, official MC objective."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import sys
sys.dont_write_bytecode = True
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.chdir(HERE)
sys.path[:0] = [str(HERE), str(ROOT/'lanes/me_layout'), str(ROOT)]
import json, random, hashlib, time, copy, argparse, statistics
import tprep
import fast_check
import run_moves as R
from verify import load_assign
from schedules import greedy, dag, commute
from experiment import emit, from_times

SEEDS = (0,1000,2000)

def base():
    spec = ROOT/'lanes/me_layout/res_A1_9b_1792752451.json'
    cost,a,o,_,name = json.loads(spec.read_text())[0]
    raw,data = R.variant(name).full_circuit(load_assign(a),o,lazy=False)
    split = next(i for i,op in enumerate(raw.sops) if op[0]=='barrier')
    pre = raw.sops[:split]
    pt = greedy(pre,4,True,True)
    cycle = emit(raw.sops[split:],raw)
    c_ops,c_times=[],[]
    for t,layer in enumerate(cycle.layers(True)):
        for op in layer:c_ops.append(op);c_times.append(t)
    offset=max(pt)+1
    ops=pre+c_ops
    times=pt+[t+offset for t in c_times]
    return raw,data,ops,times,len(pre)

def text_for(raw,ops,times):
    shift=min(times)
    native=[('MX' if k=='MX_KEEP' else k,qs,b) for k,qs,b in ops]
    text=from_times(native,[t-shift for t in times],raw).rescheduled(lazy_init=True).text()
    for k,qs,b in ops:
        if k=='MX_KEEP':
            old=f'measure q[{qs[0]}] -> c[{b}];'
            text=text.replace(old,old+f'\nh q[{qs[0]}];')
    return text

def save(label,raw,data,ops,times,npre,source):
    text=text_for(raw,ops,times)
    meta={'data_qubits':data,'source':source,'n_2q':sum(k=='cx' for k,qs,b in ops),
          'schedule':{'ops':ops,'times':times,'npre':npre},'sha256':hashlib.sha256(text.encode()).hexdigest()}
    (HERE/f'{label}.qasm').write_text(text)
    (HERE/f'{label}.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta

def pack_pre(ops,times,npre,seed=0,boundary_commute=False,end_cap=0,jitter=3):
    """Reverse list schedule pre-gates around fixed cycle deadlines/resources."""
    pre=ops[:npre]; cyc=ops[npre:]; ct=times[npre:]
    cpred,csucc=dag(pre,True)
    start=min(ct)
    limits=[]
    for op in pre:
        bounds=[t-1 for cop,t in zip(cyc,ct) if set(op[1])&set(cop[1]) and not(boundary_commute and commute(op,cop))]
        limits.append(min(bounds,default=start+end_cap))
    occupied={(q,t) for op,t in zip(cyc,ct) for q in op[1]}
    distance=[0]*npre
    for i in range(npre): distance[i]=1+max((distance[j] for j in cpred[i]),default=0)
    rng=random.Random(seed)
    priorities=[distance[i]+rng.random()*jitter for i in range(npre)]
    out=[None]*npre;remaining=set(range(npre));done=set()
    t=max(limits)
    while remaining:
        ready=sorted((i for i in remaining if csucc[i]<=done and t<=limits[i]),key=lambda i:(-priorities[i],i))
        selected=[]
        for i in ready:
            if any((q,t) in occupied for q in pre[i][1]):continue
            if any(out[j]<=t for j in csucc[i]):continue
            selected.append(i)
            occupied.update((q,t) for q in pre[i][1])
            out[i]=t
        remaining.difference_update(selected);done.update(selected);t-=1
        if t < -1000:raise RuntimeError('schedule did not terminate')
    return out+ct

def check_one(label,procs=16,seeds=SEEDS,shots=10**8,tag='official'):
    path=HERE/f'{label}.json'; meta=json.loads(path.read_text());text=(HERE/f'{label}.qasm').read_text()
    rows=[]
    for seed in seeds:
        start=time.monotonic()
        rep=fast_check.check(text,meta['data_qubits'],shots=shots,seed=seed,procs=procs)
        row={'seed':seed,'score':rep.score,'sem':rep.sem,'acceptance':rep.acceptance,'passed':rep.passed,
             'gates':{'format':rep.format_ok,'class':rep.class_ok,'correctness':rep.correct_ok,'acceptance':rep.acceptance_ok},
             'seconds':time.monotonic()-start,'report':str(rep)}
        rows.append(row)
        print(json.dumps({'label':label,'tag':tag,**{k:v for k,v in row.items() if k!='report'}}),flush=True)
        if not rep.passed:break
    result={'shots':shots,'seeds':rows,'mean':statistics.mean(r['score'] for r in rows) if all(r['score'] is not None for r in rows) else None,
            'passed':all(r['passed'] for r in rows)}
    meta=json.loads(path.read_text())
    meta[tag]=result
    if shots==10**8 and tuple(seeds)==SEEDS:
        meta.update(score=rows[0]['score'],seeds={str(r['seed']):r['score'] for r in rows},mean=result['mean'],passed=result['passed'])
    path.write_text(json.dumps(meta,indent=2)+'\n')
    with (HERE/f'{tag}_results.jsonl').open('a') as f:f.write(json.dumps({'label':label,**result})+'\n')
    return result

def generate():
    raw,data,ops,times,npre=base()
    text=text_for(raw,ops,times)
    expected=(ROOT/'submissions/v10_A1i_alap.qasm').read_text()
    assert text==expected, 'baseline reconstruction differs'
    save('v10_reference',raw,data,ops,times,npre,'Exact reconstruction of submitted v10, ALAP priority seed 4')
    labels=['v10_reference']; seen={hashlib.sha256(text.encode()).hexdigest()}
    for cm in (False,True):
        for seed in range(8):
            ts=pack_pre(ops,times,npre,seed,cm)
            qasm=text_for(raw,ops,ts); h=hashlib.sha256(qasm.encode()).hexdigest()
            if h in seen:continue
            seen.add(h)
            label=f'boundary_cm{int(cm)}_s{seed}'
            save(label,raw,data,ops,ts,npre,f'Pre-cycle reverse schedule with per-qubit deadlines; boundary commute={cm}, priority seed={seed}; v10 final-cycle times fixed')
            labels.append(label)
    (HERE/'boundary_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
    print(json.dumps({'labels':labels,'npre':npre,'predepth':max(times[:npre])+1,'cycledepth':max(times[npre:])-min(times[npre:])+1}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['generate','check']);p.add_argument('labels',nargs='*');p.add_argument('--procs',type=int,default=16);p.add_argument('--shots',type=int,default=10**8);p.add_argument('--seeds',default='0,1000,2000');p.add_argument('--tag',default='official')
    args=p.parse_args()
    if args.mode=='generate':generate()
    else:
        labels=args.labels
        if len(labels)==1 and labels[0].endswith('.json'):labels=json.loads((HERE/labels[0]).read_text())
        for label in labels:check_one(label,args.procs,tuple(map(int,args.seeds.split(','))),args.shots,args.tag)

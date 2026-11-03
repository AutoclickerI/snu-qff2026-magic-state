"""Finite partition/order screen at fixed complete noisy circuit/ending."""
import argparse,concurrent.futures,contextlib,io,itertools,json,time
import smallcat as s

def run(job):
    number,args=job
    stem,out=s.build(**args)
    assert out['raw']['ok'],(stem,out['raw'])
    s.f.DATA=out['data_qubits'];ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
    out['singles']=s.record_contract.singles(s.f.make_model(ops,dets))
    if out['singles']['c1']<1e-10:
        with contextlib.redirect_stdout(io.StringIO()):p=s.pairs.audit(stem)
        out['c2']=p['c2']
    out['completed']=True
    stem.with_suffix('.result.json').write_text(json.dumps(out,indent=2)+'\n')
    return dict(number=number,name=stem.name,groups=out['cat_groups'],c1=out['singles']['c1'],c2=out.get('c2'),cx=out['cx'],ticks=out['ticks'])

def partitions():
    for triple in itertools.combinations(range(7),3):
        if (triple[0]+1)^(triple[1]+1)^(triple[2]+1)==0:continue
        rest=sorted(set(range(7))-set(triple));a=rest[0]
        for b in rest[1:]:
            yield [list(triple),[a,b],sorted(set(rest)-{a,b})]

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['partitions','orders','two'],default='partitions')
    ap.add_argument('--groups');ap.add_argument('--herald',action='store_true');args=ap.parse_args()
    rows=[]
    if args.mode=='partitions':groups=list(partitions())
    elif args.mode=='two':
        groups=[]
        for triple in itertools.combinations(range(7),3):
            if (triple[0]+1)^(triple[1]+1)^(triple[2]+1)==0:continue
            groups.append([list(triple),sorted(set(range(7))-set(triple))])
    else:
        base=json.loads(args.groups);groups=[]
        for order in itertools.permutations(range(len(base))):
            for g in itertools.product(*(list(itertools.permutations(base[i])) for i in order)):
                groups.append(list(map(list,g)))
    ncat=len(groups[0]);tag=f'{args.mode}_h{int(args.herald)}'
    jobs=[(i,dict(ncat=ncat,groups=g,interleaved=True,herald=args.herald,staggered=args.herald,
                 name=f'{tag}_{i:04d}'))for i,g in enumerate(groups)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
        for row in ex.map(run,jobs):
            rows.append(row)
            if len(rows)%10==0:print(json.dumps(dict(done=len(rows),total=len(jobs),best=min((r for r in rows if r['c2'] is not None),key=lambda r:r['c2']))),flush=True)
    rows.sort(key=lambda r:r['c2']if r['c2'] is not None else float('inf'))
    for row in rows[:5]:
        out=s.exact(s.HERE/'cand'/row['name']);row.update(loss=out['loss'],acceptance=out['acceptance'])
    (s.HERE/f'{tag}.json').write_text(json.dumps(dict(completed=True,jobs=len(jobs),rows=rows),indent=2)+'\n')
    print(json.dumps(dict(completed=True,jobs=len(jobs),top=rows[:8])),flush=True)

"""Complete noisy source with the original A preparation/herald instrument.

The old A encoder and every herald gate/read are retained. B is prepared by a
real encoder and checked against a real C encoder. Abstract layout only.
"""
import contextlib,hashlib,io,json
import smallcat as s
from multicat import color

def build(reps=2,kind='same',seed=0,late_source=False,no_prechecks=False,precheck_mode=None):
    triples=[[0,1,3],[0,2,4],[0,3,6],[1,2,3]]
    rounds=[s.GROUPS[2]if kind=='same'else [triples[r],sorted(set(range(7))-set(triples[r]))]for r in range(reps)]
    name=f'oldA_bell{reps}_{kind}_s{seed:03d}'+('_late'if late_source else'')+('_nopre'if no_prechecks else'')
    mode=precheck_mode if precheck_mode is not None else not no_prechecks
    if precheck_mode is not None:name+='_pre'+precheck_mode
    first=(8 if mode is False or mode=='B' else 11)+int(late_source)
    stem,meta=s.build(ncat=2,interleaved=True,round_groups=rounds,coupling_layers=color(rounds,seed),tail_delay=int(not late_source),first_coupling=first,prechecks=mode,name=name)
    ops,_=s.f.parse_current(stem.with_suffix('.qasm').read_text())
    floor=-1 if mode is False or mode=='B' else 8
    ops=[o for o in ops if not(set(o.qs)&set(s.A) and o.time>floor)]
    if late_source:
        # Physical TDG commutes through its data-control A tap. The old A
        # instrument taps data3/6 one clock before the other five coordinates.
        for o in ops:
            if o.kind=='TDG'and o.qs[0]in (s.D[3],s.D[6]):o.time+=1
    source=s.ROOT/'work/lanes/PREFIX20261027/cand/final_phase_random_1.qasm'
    old,_=s.f.parse_current(source.read_text())
    oa=[1,14,8,9,2,16,15];od=[0,20,7,10,3,22,21]
    mapping=dict(zip(oa+od,s.A+s.D));offset=meta['tail_start']-28
    bits={14+i:107+i for i in range(7)};bits[278]=121
    for o in old:
        if o.time<20 or not(set(o.qs)&set(oa))or not set(o.qs)<=set(oa+od):continue
        if o.time==20 and o.kind=='M'and o.bit>=500:continue
        ops.append(s.f.Op(o.kind,tuple(mapping[q]for q in o.qs),o.time+offset,bits[o.bit]if o.bit is not None else None))
    # Original transfer leaves these inputs in zero; now explicitly reset them.
    for i in (0,6):
        first=min(o.time for o in ops if s.A[i]in o.qs and o.time>floor)
        ops.append(s.f.Op('R',(s.A[i],),first-1))
    ops.sort(key=lambda o:o.time);used=set()
    for o in ops:
        keys={(o.time,q)for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
    s.f.DATA=s.D;m=s.f.make_model(ops,[]);contract=s.record_contract.complete(m,[])
    assert all(not row['reference']for row in contract['missing'])
    text=s.emit(ops,[set(row['bits'])for row in contract['missing']])
    stem.with_suffix('.qasm').write_text(text)
    meta.update(raw=s.ideal_contract_check(text,s.D),A_instrument='Original A preparation and logical-X herald remapped abstractly; carry-zero inputs are explicit noisy resets.',
                A_logical_X_herald=True,record_contract=contract,cx=sum(o.kind=='CX'for o in ops),ticks=max(o.time for o in ops)+1,
                qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),old_A_source=str(source))
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return stem,meta

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--late-source',action='store_true');args=ap.parse_args()
    results=[]
    for reps,kind,seed in [(2,'same',0),(3,'same',2),(4,'mixed',3)]:
        stem,out=build(reps,kind,seed,args.late_source)
        print(json.dumps(dict(name=stem.name,raw=out['raw'],cx=out['cx'],ticks=out['ticks'])),flush=True)
        if out['raw']['ok']:
            s.f.DATA=s.D;ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
            out['singles']=s.record_contract.singles(s.f.make_model(ops,dets))
            with contextlib.redirect_stdout(io.StringIO()):p=s.pairs.audit(stem)
            out['c2']=p['c2'];out['exact']=s.exact(stem)
        out['completed']=True
        stem.with_suffix('.result.json').write_text(json.dumps(out,indent=2)+'\n')
        row=dict(name=stem.name,cx=out['cx'],ticks=out['ticks'],raw=out['raw']['ok'],c1=out.get('singles',{}).get('c1'),c2=out.get('c2'),loss=out.get('exact',{}).get('loss'),acceptance=out.get('exact',{}).get('acceptance'))
        results.append(row);print(json.dumps(row),flush=True)
    (s.HERE/('old_a_late.json'if args.late_source else'old_a.json')).write_text(json.dumps(dict(completed=True,rows=results),indent=2)+'\n')

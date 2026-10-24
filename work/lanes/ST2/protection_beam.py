"""Enumerate released-helper subwindows, composing complete echo gadgets."""
import sys,json,random,lzma
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import directed as d
from concurrent.futures import ProcessPoolExecutor,as_completed

def neighbors(c,dynamic=False):
    us,ts,R=c['u'],c['t'],c['meta']['R']
    for q in (d.C.D+[4,15,16] if dynamic else d.C.D):
        seq=[i for i,u in enumerate(us) if q in u.qs]
        for ia,ib in zip(seq,seq[1:]):
            a,b=ts[ia]+1,min(ts[ib]-1,R-1)
            if b-a<3 or b<18:continue
            for h in range(36):
                if (h in d.C.D and not dynamic) or abs(q//6-h//6)+abs(q%6-h%6)!=1:continue
                hs=[i for i,u in enumerate(us) if h in u.qs]
                free=[];start=None
                busy={ts[i] for i in hs}
                for t in range(a,b+2):
                    if t<=b and t not in busy:
                        if start is None:start=t
                    elif start is not None:
                        if t-start>=4:free.append((start,t-1))
                        start=None
                for aa,bb in free:
                    prev=[i for i in hs if ts[i]<aa];nxt=[i for i in hs if ts[i]>bb]
                    if prev and us[prev[-1]].name not in ('MX','MEASURE'):continue
                    if nxt and us[nxt[0]].name not in ('RX','RESET','MX','MEASURE'):continue
                    # Entire maximal intersection and two halves when useful.
                    windows={(aa,bb)}
                    if bb-aa>=7:windows|={(aa,aa+3),(bb-3,bb)}
                    for a0,b0 in sorted(windows):
                        for axis in ['X','Z']:
                            x=d.C.clone(c);bit=d.C.bit(x)
                            init=[f'reset q[{h}];']+([f'h q[{h}];'] if axis=='Z' else [])
                            edge=f'cx q[{q}],q[{h}];' if axis=='X' else f'cx q[{h}],q[{q}];'
                            meas=[f'measure q[{h}] -> c[{bit}];']
                            if axis=='Z':meas=[f'h q[{h}];']+meas+[f'h q[{h}];']
                            for lines,t in [(init,a0),([edge],a0+1),([edge],b0-1),(meas,b0)]:x['u'].append(d.C.Unit(lines));x['t'].append(t)
                            x['tail'].append(f'// DETECTOR c[{bit}]')
                            try:x=d.normalize(x)
                            except Exception:continue
                            yield x,dict(family='released_helper_subwindow',qubit=q,helper=h,axis=axis,window=[a0,b0])

def main():
    dynamic=len(sys.argv)>1 and sys.argv[1]=='dynamic'
    h=d.H;out=h/('dynamic_run' if dynamic else 'protection_run');out.mkdir(exist_ok=True);rng=random.Random(112);cache={};circuits={};prov={};seen=set();trace=[]
    if dynamic:
        base=json.loads((h/'protection_run/results.json').read_text())[0];p=h/'protection_run'/base['stem']
    else:
        base=json.loads((h/'directed_run/summary.json').read_text())['ranked'][0];p=h/'directed_run'/base['stem']
    c=d.normalize(d.C.read(p));name='seed_'+d.digest(c);d.save(c,out/name);circuits[name]=c;prov[name]=base['moves'];cache[name]=dict(base,stem=name);seen.add(d.digest(c));beam=[name]
    for gen in range(3 if dynamic else 4):
        jobs=[]
        for parent in beam:
            for x,desc in neighbors(circuits[parent],dynamic):
                fp=d.digest(x)
                if fp in seen:continue
                seen.add(fp);n=f'p{gen}_{fp}';circuits[n]=d.save(x,out/n);prov[n]=prov[parent]+[desc];jobs.append(n)
        print('generation',gen,'new',len(jobs),flush=True)
        with ProcessPoolExecutor(10) as pool:
            fs={pool.submit(d.score_job,(str(out/n),base['source'],prov[n])):n for n in jobs}
            for f in as_completed(fs):
                n=fs[f];r=f.result();cache[n]=r;trace.append(r);(out/(n+'.score.json')).write_text(json.dumps(r,indent=2))
                print(n,r.get('allorders'),r.get('acceptance'),r.get('error',''),flush=True)
        good=sorted([r for r in cache.values() if r.get('ok') and r.get('acceptance',0)>=.5],key=lambda r:(round(r['allorders'],13),len(r['moves'])))
        selected=good[:3];rest=[r for r in good[3:] if r['stem'] in jobs]
        if rest:selected += [rng.choice(rest)]
        beam=[r['stem'] for r in selected]
        (out/f'generation_{gen}.json').write_text(json.dumps(dict(evaluations=len(trace),best=good[0],selected=selected),indent=2))
        with lzma.open(out/'trace.jsonl.xz','wt') as f:
            for r in trace:f.write(json.dumps(r)+'\n')
        print('BEST',gen,good[0]['stem'],good[0]['allorders'],flush=True)
        if not jobs:break
    (out/'results.json').write_text(json.dumps(good,indent=2))
    keep={r['stem'] for r in good[:10]}
    for n in circuits:
        if n not in keep:
            for ext in ['.qasm','.json','.score.json']:(out/(n+ext)).unlink(missing_ok=True)
    print('DONE',len(trace),'best',good[0]['stem'],good[0]['allorders'],flush=True)
if __name__=='__main__':main()

from pass4 import *
import random
CTX=None

def work(seed):
 m,eng,groups,nd,ks,best,free,keys=CTX;rng=random.Random(seed);warm=list(best)
 for _ in range({19231:0,39709:4,59611:8}[seed]):
  i,j=rng.sample(free,2);warm.append([keys[i],keys[j]])
 t=time.monotonic();ops,cost=E.sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=5000,seed=seed)
 return dict(seed=seed,ops=ops,cost=cost,seconds=time.monotonic()-t)

if __name__=='__main__':
 st=Path(sys.argv[1]);s=sha(st);source=R/f'basis_{s}.json';E.configure(source,12);sw=E.sw
 with contextlib.redirect_stdout(io.StringIO()):m,eng,groups,nd,ks,*_=sw.prepare(st,True)
 bases=json.loads(source.read_text());before=(None,(10**12,100));warm=None
 for v in bases['bases'].values():
  answer=sw.search_basis(m,eng,groups,nd,set(ks),v,trials=0)
  if answer[1]<before[1]:before=answer;warm=v
 keys=[','.join(map(str,sorted(d)))for d in m.dets];free=[i for i in range(nd)if i not in ks and tuple(eng.projs[i])==(0,0,1)and int(eng.v[i])==0];CTX=(m,eng,groups,nd,ks,warm,free,keys)
 with get_context('fork').Pool(3)as pool:rs=list(pool.imap_unordered(work,[19231,39709,59611]))
 best=min(rs+[dict(ops=before[0],cost=before[1],seed=None)],key=lambda x:x['cost']);bases['bases']['PERTURB4_'+s[:12]]=[[keys[t],keys[j]]for t,j in best['ops']];target=R/f'basis2_{s}.json';dump(target,bases);dump(R/f'basis_refinement_{s}.json',dict(before=before[1],after=best['cost'],trials=rs));E.configure(target,12);expected=json.loads(st.with_suffix('.json').read_text());r=record(st,'perturbed exact basis replay',expected['loss']);assert abs(r['loss']-expected['loss'])<1e-13 and abs(r['acceptance']-expected['acceptance'])<1e-13
 with(R/'basis_controls.jsonl').open('a')as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(dict(event='refined',before=before[1],after=best['cost'],seconds=r['seconds'],loss=r['loss'])),flush=True)

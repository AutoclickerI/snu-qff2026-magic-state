"""Freeze and verify an exact detector basis for each changed incumbent."""
from pass5 import *
CTX=None

def train(seed):
 m,eng,groups,nd,ks,warm=CTX;t=time.monotonic();ops,cost=E.sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=5000,seed=seed)
 return dict(seed=seed,ops=ops,cost=cost,seconds=time.monotonic()-t)

def specialize(st,expected):
 global CTX
 st=Path(st);target=R/f'basis_{sha(st)}.json';sw=E.sw
 if (R/f'basis2_{sha(st)}.json').exists():target=R/f'basis2_{sha(st)}.json'
 if not target.exists():
  with contextlib.redirect_stdout(io.StringIO()):m,eng,groups,nd,ks,*_=sw.prepare(st,True)
  bases=json.loads(sw.WARM.read_text());choices=[]
  for name,warm in bases['bases'].items():
   ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=0);choices.append((cost,name,warm))
  cost,name,warm=min(choices)
  if cost[1]<=10:
   print(json.dumps(dict(event='basis_replay_sufficient',sha256=sha(st),cost=cost)),flush=True);return
  CTX=(m,eng,groups,nd,ks,warm)
  with get_context('fork').Pool(3)as pool:results=list(pool.imap_unordered(train,[9911,17027,41283]))
  best=min(results,key=lambda x:x['cost']);keys=[','.join(map(str,sorted(d)))for d in m.dets]
  bases['bases']['MERGE4_'+sha(st)[:12]]=[[keys[t],keys[s]]for t,s in best['ops']];dump(target,bases);dump(R/f'basis_training_{sha(st)}.json',dict(before=cost,after=best['cost'],trials=results))
 E.configure(target,12);r=record(st,dict(kind='incumbent exact basis control',basis=str(target)),expected['loss'])
 assert abs(r['loss']-expected['loss'])<1e-13 and abs(r['acceptance']-expected['acceptance'])<1e-13
 with (R/'basis_controls.jsonl').open('a')as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(dict(event='basis_specialized',sha256=sha(st),width=r['width'],seconds=r['seconds'],loss=r['loss'],acceptance=r['acceptance'])),flush=True)
if __name__=='__main__':
 st=Path(sys.argv[1]);specialize(st,json.loads(st.with_suffix('.json').read_text()))

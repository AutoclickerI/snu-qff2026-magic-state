from pass3 import *
import search3
def specialize(stem,expected):
 sw=E.sw;stem=Path(stem);target=R/f"basis_active_{sha(stem)}.json"
 if not target.exists():
  with contextlib.redirect_stdout(io.StringIO()):m,eng,groups,nd,ks,*_=sw.prepare(stem,True)
  bases=json.loads(sw.WARM.read_text())
  for name,path in [('BC3',R/'basis_bc3.json'),('FUSED11',R/'basis_fused.json')]:
   if path.exists():bases['bases'][name]=json.loads(path.read_text())['bases']['MERGE_current']
  choices=[(sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=0),warm)for warm in bases['bases'].values()]
  (ops,cost),warm=min(choices,key=lambda v:v[0][1])
  if cost[1]>10:ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=1000)
  keys=[','.join(map(str,sorted(d)))for d in m.dets]
  bases['bases']['MERGE_'+sha(stem)[:12]]=[[keys[t],keys[s]]for t,s in ops];bases['training_cost']=cost
  dump(target,bases)
 E.configure(target,12);r=price(stem,dict(kind='round basis control',basis=str(target)))
 assert abs(r['loss']-expected['loss'])<1e-13 and abs(r['acceptance']-expected['acceptance'])<1e-13,(r,expected)
 print(json.dumps(dict(event='round_basis',width=r['width'],seconds=r['seconds'],basis=str(target))),flush=True)
def run(stem,tag,workers):
 stem=Path(stem);hf=R/f'{tag}_history.json';history=json.loads(hf.read_text())if hf.exists()else[]
 if '--resume'not in sys.argv:
  prep(stem,tag)
  batch(stem,R/f'{tag}_menu.json',R/f'{tag}_tasks.json',tag+'_s1',workers)
  search3.connected(tag,stem);search3.contexts(tag,stem,workers)
  batch(stem,R/f'{tag}_menu.json',R/f'{tag}_b2_tasks.json',tag+'_b2',workers)
 if history and history[-1]['stop']:return history[-1]['price']
 for rnd in itertools.count(len(history)+1):
  history=json.loads(hf.read_text())if hf.exists()else[]
  if history:specialize(history[-1]['price']['stem'],history[-1]['price'])
  search3.greedy_prepare(tag,stem,rnd)
  batch(stem,R/f'{tag}_menu.json',R/f'{tag}_g{rnd}_tasks.json',f'{tag}_g{rnd}',workers)
  search3.fund_prepare(tag,rnd)
  batch(stem,R/f'{tag}_menu.json',R/f'{tag}_g{rnd}_fund_tasks.json',f'{tag}_g{rnd}_fund',workers)
  event=search3.select(tag,rnd)
  if event['stop']:
   dump(R/f'{tag}_outcome.json',dict(base=str(stem),price=event['price'],history=json.loads((R/f'{tag}_history.json').read_text()),complete=True));return event['price']
if __name__=='__main__':print(json.dumps(run(Path(sys.argv[1]),sys.argv[2],int(sys.argv[3]))),flush=True)

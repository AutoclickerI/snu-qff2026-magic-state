"""Run the unmodified exact2 CLI; collect additional provenance and triple diagnostics.
The sole physical override is qasm.adjacent, as in MAIN/gf/exact_gf.py.
"""
import os,sys,json,math,collections,time,traceback
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(HERE/'.xtim_cache')
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import exact2,tprep.qasm
from engine import Engine
if __name__=='__main__' and not getattr(Engine,'ladder_pruned',False) and os.environ.get('LADDER_PRUNE','1')=='1':
 import runpy
 runpy.run_path(str(HERE/'filtered_price.py'),run_name='__main__')
 sys.exit(0)
original_adjacent=tprep.qasm.adjacent
tprep.qasm.adjacent=lambda a,b:True
oldrun=exact2.run;oldthird=exact2.third_order
STATE={}
def run(ev,*args,**kwargs):
 kwargs['keep_thr']=0.0
 r=oldrun(ev,*args,**kwargs);STATE.update(ev=ev,r=r);return r
def third(ev,*args,**kwargs):
 r=oldthird(ev,*args,**kwargs);STATE.update(triple=r);return r
exact2.run=run;exact2.third_order=third
if __name__=='__main__':
 stem=Path(sys.argv[1]).with_suffix('');meta=json.loads(stem.with_suffix('.json').read_text())
 out=stem.with_suffix('.price.json');begin=time.monotonic()
 try:
  exact2.main()
  ev,r=STATE['ev'],STATE['r'];tt,big3=STATE.get('triple',(float('nan'),[]))
  # Physical data-token locations during the suffix. Prefix cells are labelled literally,
  # including long data-cell idle runs that begin before step32.
  ops=meta['units'];prefix=[x for x in ops if x['tag']=='prefix']
  data=set([0,20,7,4,3,15,8]);seen=collections.Counter();trans=[]
  for x in sorted(ops,key=lambda x:x['t']):
   if x['tag']=='hop' and x['lines'][0].startswith('cx '):
    qs=list(map(int,exact2.re.findall(r'q\[(\d+)\]',x['lines'][0])));pair=frozenset(qs);seen[pair]+=1
    if seen[pair]==2:
     if len(data&pair)==1:data.symmetric_difference_update(pair)
     trans.append((x['t'],set(data)))
  def reg(c):
   lab=ev.chan_label(c);tag=meta['line_tags'].get(str(lab['line']),'unknown')
   if lab['kind']=='idle':
    first=int(lab['steps'].split('..')[0]);last=int(lab['steps'].split('..')[-1]);q=lab['qubits'][0]
    ds=set([0,20,7,4,3,15,8])
    for t,d in trans:
     if t<first:ds=d
    if q in ds and first<meta['R']:return 'data_cell_idle'
    if first>=meta['R']:return 'round'
   return tag
  regs=[reg(c) for c in range(len(ev.m.chans))]
  pairs=collections.Counter();ptop={}
  for v,i,j,n,a in r['big']:
   k=' x '.join(sorted([regs[ev.fch[i]],regs[ev.fch[j]]]));pairs[k]+=v
   if v>ptop.get(k,[0])[0]:ptop[k]=[v,ev.fault_label(i),ev.fault_label(j)]
  triples=collections.Counter()
  for v,*ijk in big3:triples[' x '.join(sorted(regs[ev.fch[i]] for i in ijk))]+=v
  top3=[[v,*[ev.fault_label(i) for i in ijk]] for v,*ijk in sorted(big3,reverse=True)[:50]]
  row=dict(evaluator='exact2 with algebraic zero-class pruning' if getattr(Engine,'ladder_pruned',False) else 'unmodified exact2',status='PASS' if abs(r['loss1'])<1e-12 else 'NONZERO_C1',second=r['loss2'],third=tt+r['t3bc'],total=r['loss']+tt+r['t3bc'],weight3=tt,pair_times_others=r['t3bc'],c1=r['loss1'],A0=ev.e.A0,exp_minus_A1=math.exp(-r['A1']),A1=r['A1'],CX=meta['CX'],R=meta['R'],pair_classes=dict(pairs.most_common()),pair_class_examples=ptop,triple_classes_kept=dict(triples.most_common()),triple_kept=sum(triples.values()),top_triples=top3,seconds=time.monotonic()-begin)
  print('\nPROVENANCE PAIRS',json.dumps(row['pair_classes']),flush=True)
  print('TRIPLES retained',row['triple_kept'],'of full weight3',tt,flush=True)
  for x in top3[:15]:print('TRIPLE',*x,flush=True)
  out.write_text(json.dumps(row,indent=2)+'\n')
 except Exception as e:
  out.write_text(json.dumps(dict(status='ERROR',error=str(e),traceback=traceback.format_exc()),indent=2));raise

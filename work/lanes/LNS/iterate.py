from moves import *
import hops
from round_lns import proposals

def beststem():
 vals=[]
 for f in OUT.glob('*.exact.json'):
  r=json.loads(f.read_text())
  if r.get('exp_minus_A1',0)>=.505:vals.append((r['total'],str(f).replace('.exact.json','')))
 return min(vals)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=8);ap.add_argument('--start',type=int,default=1);a=ap.parse_args();stage=a.start
 while True:
  val,stem=beststem();base=read(stem);print('START',stage,stem,val,flush=True);candidates=[];coverage={}
  families=[('timing',lambda b:timing_moves(b,True)),('commute',commute_moves),('init',init_moves),('phase',phase_moves),('readout',readout_moves),('detector',detector_moves),('hop',hops.moves),('round',proposals)]
  for family,gen in families:
   cc=list(gen(base));coverage[family]=len(cc)
   for c,d in cc:d['parent_total']=val;d['iteration']=stage
   candidates+=cc
  batch(candidates,f'iter{stage}',a.workers)
  new,newstem=beststem();receipt=dict(iteration=stage,base=stem,base_total=val,best=newstem,best_total=new,coverage=coverage,improved=new<val-1e-12)
  (OUT/f'iter{stage}.coverage.json').write_text(json.dumps(receipt,indent=2));print('ROUND',receipt,flush=True)
  if new>=val-1e-12:break
  stage+=1

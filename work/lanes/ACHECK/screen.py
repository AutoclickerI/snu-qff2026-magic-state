from common import *
import fast_exact
import exact2,multiprocessing as mp,time,math
def run(name):
 t=time.monotonic();p=HERE/name;md=json.loads(p.with_suffix('.json').read_text())
 if p.with_suffix('.screen.json').exists():return json.loads(p.with_suffix('.screen.json').read_text())
 try:
  ev=exact2.Eval(p.with_suffix('.qasm').read_text(),D);r=exact2.run(ev,1,keep_thr=1)
  out=dict(name=name,c1=r['loss1'],second=r['loss'],exp_A1=math.exp(-r['A1']),R=md.get('R'),cx=md['cx'],seconds=time.monotonic()-t)
 except Exception as e:out=dict(name=name,error=str(e))
 p.with_suffix('.screen.json').write_text(json.dumps(out));return out
if __name__=='__main__':
 n=int(sys.argv[1]);names=[p.stem for p in sorted(HERE.glob('enc_[0-9][0-9][0-9].qasm'))];rows=[]
 with mp.get_context('fork').Pool(n) as pool:
  for row in pool.imap_unordered(run,names):
   rows.append(row);(HERE/'encoder_screen.json').write_text(json.dumps(sorted(rows,key=lambda x:x.get('second',1)),indent=1));print(row,flush=True)

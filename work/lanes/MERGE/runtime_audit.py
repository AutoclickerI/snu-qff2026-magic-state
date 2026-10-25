from campaign import *
from speed_predict import predict
def probe(stem):
 s=sha(stem);r=dict(predict(str(stem),shots=2000,repeats=1),sha256=s)
 with (H/'res/runtime_probes.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(r),flush=True);return r
def main():
 out=json.loads((H/'res/final_repair_outcome.json').read_text());seq=[out['start']]+[r['price'] for r in out['history'] if r.get('accepted')]
 lo=-1;hi=len(seq)-1
 first=probe(seq[0]['stem']);last=probe(seq[-1]['stem'])
 if first['classification']=='FAST':lo=0
 while hi-lo>1:
  k=(lo+hi)//2;r=probe(seq[k]['stem'])
  if r['classification']=='FAST':lo=k
  else:hi=k
 write(H/'res/runtime_bisect.json',dict(last_fast=seq[lo] if lo>=0 else None,first_slow=seq[hi],first_slow_index=hi,sequence=seq))
 print(json.dumps(dict(event='runtime_bisect',last_fast=seq[lo]['stem'] if lo>=0 else None,first_slow=seq[hi]['stem'],change=seq[hi].get('what_moved'))),flush=True)
if __name__=='__main__':main()

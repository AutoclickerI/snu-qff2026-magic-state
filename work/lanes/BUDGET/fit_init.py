import json,math
from pathlib import Path
import numpy as np
ROOT=Path('work/lanes/BUDGET/init_scan');m=json.loads((ROOT/'manifest.json').read_text()); q=m['qs']; evdir=ROOT/'eval'
def load(ms,key):
 X=[];y=[];rows=[]
 for mask in ms:
  z=json.loads((evdir/f'{mask:03x}.json').read_text())
  if key not in z or z[key] is None: continue
  feat=[1.0]+[float((mask>>i)&1) for i in range(12)]
  feat += [float(((mask>>i)&1)*((mask>>j)&1)) for i in range(12) for j in range(i+1,12)]
  feat += [float(((mask>>i)&1)*((mask>>j)&1)*((mask>>k)&1)) for i in range(12) for j in range(i+1,12) for k in range(j+1,12)]
  X.append(feat);y.append(float(z[key]));rows.append((mask,z))
 return np.array(X),np.array(y),rows
out={}
for key in ('second','A1','exp_minus_A1'):
 X,y,rows=load(m['train'],key)
 beta,res,rank,s=np.linalg.lstsq(X,y,rcond=None)
 pred=[]
 for mask in m['heldout']:
  z=json.loads((evdir/f'{mask:03x}.json').read_text());
  feat=[1.0]+[float((mask>>i)&1) for i in range(12)]
  feat += [float(((mask>>i)&1)*((mask>>j)&1)) for i in range(12) for j in range(i+1,12)]
  feat += [float(((mask>>i)&1)*((mask>>j)&1)*((mask>>k)&1)) for i in range(12) for j in range(i+1,12) for k in range(j+1,12)]
  if key in z and z[key] is not None: pred.append((mask,float(np.dot(feat,beta)),float(z[key])))
 err=np.array([a-b for _,a,b in pred]) if pred else np.array([])
 out[key]={'n_train':len(y),'rank':int(rank),'n_terms':X.shape[1],'fit_residual_max':float(np.max(np.abs(X@beta-y))) if len(y) else None,'heldout_n':len(pred),'heldout_mae':float(np.mean(np.abs(err))) if len(err) else None,'heldout_rmse':float(np.sqrt(np.mean(err*err))) if len(err) else None,'heldout_max':float(np.max(np.abs(err))) if len(err) else None,'beta':beta.tolist(),'heldout':pred}
 # write predictions all combos for this key
 allpred=[]
 for mask in m['all']:
  feat=[1.0]+[float((mask>>i)&1) for i in range(12)]
  feat += [float(((mask>>i)&1)*((mask>>j)&1)) for i in range(12) for j in range(i+1,12)]
  feat += [float(((mask>>i)&1)*((mask>>j)&1)*((mask>>k)&1)) for i in range(12) for j in range(i+1,12) for k in range(j+1,12)]
  allpred.append(float(np.dot(feat,beta)))
 out[key]['all_predictions']=allpred
json.dump(out,open('work/lanes/BUDGET/init_polynomial.json','w'),indent=2)
# rank using predicted total and acceptance predicted; emit top 20 and exact rows
if 'second' in out:
 ranked=[]
 for mask,v in enumerate(out['second']['all_predictions']):
  a=out['exp_minus_A1']['all_predictions'][mask] if 'exp_minus_A1' in out else 0
  ranked.append((v,mask,a))
 json.dump([{'mask':mask,'pred_second':v,'pred_exp_minus_A1':a,'reset_qubits':[q[i] for i in range(12) if mask>>i&1]} for v,mask,a in sorted(ranked)[:100]],open('work/lanes/BUDGET/init_pred_top100.json','w'),indent=2)
print(json.dumps({k:{x:v[x] for x in ('n_train','heldout_n','heldout_mae','heldout_rmse','heldout_max','fit_residual_max')} for k,v in out.items()},indent=2))

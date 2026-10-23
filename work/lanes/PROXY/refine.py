"""Independent anneal chains seeded by the exact submitted v12 cycle and its best continuation."""
from cycles import *
import multiprocessing as mp,argparse

def refine_one(args):
 seed,steps,startrow=args
 m=Cycle(startrow['layout'],startrow['leaves'],startrow['orient'])
 ts=startrow['times'] if seed%2 else m.reference_seed()
 assert ts is not None
 score,ts=m.anneal(ts,seed,steps);text=m.text(ts);name=f'refine_{seed}'
 r=dict(source='v12 exact fixed prefix / cycle_0058',seed=seed,layout=m.layout,leaves=m.leaves,orient=m.orient,times=ts,nodes=m.nodes,detectors=m.detectors,data_qubits=m.pos,nbits=m.nbits,depth=max(ts)+1,proxy=score,proxy_second=ep.exact_loss(*m.probes(ts)),prefix_audit=audit(text))
 rep=tprep.check(text,m.pos,shots=10**6,seed=0);assert rep.passed,str(rep)
 r['check']=dict(passed=rep.passed,shots=10**6,score=rep.score,acceptance=rep.acceptance,report=str(rep))
 (HERE/f'{name}.qasm').write_text(text);(HERE/f'{name}.json').write_text(json.dumps(r,indent=2))
 out=dict(name=name,seed=seed,proxy=score,proxy_second=r['proxy_second'],depth=r['depth'],check_score=rep.score);print(json.dumps(out),flush=True);return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=11);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=2);p.add_argument('--steps',type=int,default=12000);p.add_argument('--chains',type=int,default=48);a=p.parse_args()
 row=json.loads((HERE/'cycle_0058.json').read_text());tasks=[(5000+i,a.steps,row) for i in range(a.chains) if i%a.shards==a.shard]
 with mp.get_context('fork').Pool(a.workers) as pool:r=list(pool.imap_unordered(refine_one,tasks))
 (HERE/f'refine_results_{a.shard}.json').write_text(json.dumps(r,indent=2))

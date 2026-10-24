"""Trust-region CP-SAT timing descent using the full exact second+cubic derivative.
Zero-probability channels price newly opened waits; every proposal uses the unchanged scorer.
"""
from common import *
import moments_gradient as mg,numpy as np,argparse,gzip
import zero_idle,detector_order
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--iterations',type=int,default=8);p.add_argument('--radius',type=int,default=2);a=p.parse_args();stem=Path(a.stem);c=json.loads(stem.with_suffix('.plan.json').read_text());rows=[];best=None
for it in range(a.iterations):
 c,txt=normalized(c);ev,proof=detector_order.evaluate(txt,c['meta']['data_qubits'],zero_idle.evaluate);base,grad=mg.evaluate(ev);best=base
 per={}
 for i,o in enumerate(c['ops']):
  for q in unit(o).qs:per.setdefault(q,[]).append(i)
 old=[o['t']for o in c['ops']];R=c['meta']['R'];mx=max(old);m=cp_model.CpModel();ts=[m.NewIntVar(max(0,t-a.radius),min(mx,t+a.radius),f't{i}')for i,t in enumerate(old)]
 c4='C4'in c['meta'].get('source','');acontacts=[];bcouples=[]
 if not c4:
  for i,t in enumerate(old):
   if t>=R:m.Add(ts[i]==t)
 else:
  first_read_bit=100+c['meta']['data_hops']+c['meta']['block_teleports'];reads={o['bit']:i for i,o in enumerate(c['ops'])if o.get('tag')=='read'}
  for j in range(7):
   ai=reads[first_read_bit+2*j];bi=reads[first_read_bit+2*j+1];aq=unit(c['ops'][ai]).qs[0];bq=unit(c['ops'][bi]).qs[0];aseq=per[aq];bseq=per[bq];ao=aseq[aseq.index(ai)-1];bo=bseq[bseq.index(bi)-1];vo=bseq[bseq.index(bo)-1]
   assert c['ops'][ao]['tag']=='round'and c['ops'][bo]['tag']=='round'and c['ops'][vo]['tag']=='verify'
   m.Add(ts[ai]==ts[ao]+1);m.Add(ts[bi]==ts[bo]+1);m.Add(ts[bo]==ts[vo]+1);acontacts.append(ao);bcouples.append(bo)
  last=max((reads[first_read_bit+2*j+1]for j in range(7)),key=lambda i:old[i]);m.Add(ts[last]==mx)
  for j in range(4):
   ci=reads[first_read_bit+14+j];q=unit(c['ops'][ci]).qs[0];seq=per[q];vo=seq[seq.index(ci)-1];assert c['ops'][vo]['tag']=='verify';m.Add(ts[ci]==ts[vo]+1)
 ends={}
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):
   m.Add(ts[j]>ts[i]);ends[q,old[i]+1]=(i,j)
  ends[q,old[seq[-1]]+1]=(seq[-1],None)
 loss=[];acc=[];by=np.bincount(ev.fch,weights=ev.fp*grad,minlength=len(ev.m.chans));byA=np.bincount(ev.fch,weights=ev.fp*(1-ev.a_single),minlength=len(ev.m.chans))
 for ci,ch in enumerate(ev.m.chans):
  if ch['gap']is None:continue
  q,start,n=ch['gap'];i,j=ends[q,start];end=mx+1 if j is None else ts[j];delta=end-ts[i]-1-n;assert(mx+1 if j is None else old[j])-old[i]-1==n,(q,start,n,i,j)
  dp=-.75*math.log1p(-4e-3/3)*(1-4e-3/3)**n;ix=np.flatnonzero(ev.fch==ci);gl=by[ci]/ch['prob']if ch['prob']else float(np.mean(grad[ix]));ga=byA[ci]/ch['prob']if ch['prob']else float(np.mean(1-ev.a_single[ix]));loss.append(round(gl*dp*1e13)*delta);acc.append(round(ga*dp*1e10)*delta)
 m.Add(sum(acc)<=max(0,round((-math.log(.5002)+math.log(base['exp_minus_A1']))*1e10)));m.Minimize(sum(loss));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=10;s.parameters.cp_model_presolve=False
 st=s.Solve(m)
 if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):break
 if s.ObjectiveValue()>=-1:break
 d=copy.deepcopy(c)
 for i,o in enumerate(d['ops']):o['t']=s.Value(ts[i])
 comp={t:i for i,t in enumerate(sorted({o['t']for o in d['ops']}))};d,dtxt=normalized(d)
 if c4:
  nreads={o['bit']:o['t']for o in d['ops']if o.get('tag')=='read'};d['meta']['R']=min(nreads[first_read_bit+2*j]-1 for j in range(7));d['meta']['R_last']=max(nreads[first_read_bit+2*j+1]-2 for j in range(7))
 else:d['meta']['R']=comp[R]
 ee,proof=detector_order.evaluate(dtxt,d['meta']['data_qubits'],exact2.Eval);r=mom.evaluate(ee);row=dict(iteration=it,predicted=base['total']+s.ObjectiveValue()/1e13,base=base,result=r,plan=d,detector_order_proof=proof);rows.append(row)
 with gzip.open(H/(stem.name+'.full_gradient_witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(row)+'\n')
 append_result(stem.name+':gradient'+str(it),dict(predicted=row['predicted'],**r),'Exact pair/triple channel sensitivity converted to CP-SAT idle-interval weights; full circuit repriced. New zero-width waits priced with zero-probability channels; per-wire order preserved, C4 last-verifier/data-coupling adjacency preserved; complete end time fixed.');print(json.dumps({k:v for k,v in row.items()if k!='plan'}),flush=True)
 if r['total']>=base['total']-1e-12 or r['exp_minus_A1']<min(.5002,base['exp_minus_A1'])-1e-8:break
 c=d;best=r;out=save(c,stem.name+'_full_gradient_best');out.with_suffix('.screen.json').write_text(json.dumps(r,indent=2))
print('DONE',json.dumps(best),flush=True)

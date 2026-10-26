from pass4 import *
CTX=None

def train(seed):
 sw=E.sw;m,eng,groups,nd,ks,warm=CTX;t=time.monotonic();ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=5000,seed=seed)
 return dict(seed=seed,ops=ops,cost=cost,seconds=time.monotonic()-t)

def main():
 global CTX
 b=M.read(C/'base');es=json.loads((R/'ports_menu.json').read_text());c,txt=apply(b,list(es.values()));st=E.write_stem(txt,c['meta']['data_qubits']);sw=E.sw
 with contextlib.redirect_stdout(io.StringIO()):m,eng,groups,nd,ks,*_=sw.prepare(st,True)
 bases=json.loads(sw.WARM.read_text());choices=[]
 for name,warm in bases['bases'].items():
  ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=0);choices.append((cost,name,warm))
 cost,name,warm=min(choices);print(json.dumps(dict(event='basis_before',cost=cost,name=name)),flush=True);CTX=(m,eng,groups,nd,ks,warm)
 with get_context('fork').Pool(3)as pool:results=list(pool.imap_unordered(train,[9911,17027,41283]))
 best=min(results,key=lambda x:x['cost']);keys=[','.join(map(str,sorted(d)))for d in m.dets];bases['bases']['MERGE4_ports']=[[keys[t],keys[s]]for t,s in best['ops']];target=R/'basis4_trained.json';dump(target,bases);dump(R/'basis4_training.json',dict(before=cost,after=best['cost'],trials=results))
 expected=json.loads((R/'ports_outcome.json').read_text())['best'];E.configure(target,12);r=record(st,'new exact basis control');assert abs(r['loss']-expected['loss'])<1e-13 and abs(r['acceptance']-expected['acceptance'])<1e-13
 with (R/'local_controls.jsonl').open('a')as f:f.write(json.dumps(r)+'\n')
 dump(R/'basis4_control.json',r);print(json.dumps(dict(event='basis_after',cost=best['cost'],seconds=r['seconds'],loss=r['loss'],acceptance=r['acceptance'])),flush=True)
if __name__=='__main__':main()

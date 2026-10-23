from search import *
from accelerate import prepare

CASES={
    'v12': [[256],[2048],[256,2048],[4],[8],[8,256,2048],[4,256,2048],[4,8,256,2048]],
    'cand2': [[64],[1024],[64,1024],[2],[2048],[512],[8192],[2,64,1024],[64,1024,258,514]],
}

def main():
    for name in sys.argv[1:] or CASES:
        stem=TARGETS[name];text=stem.with_suffix('.qasm').read_text()
        data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
        space=json.loads((HERE/f'{name}_space.json').read_text())
        ev=Eval(text,data)
        output=HERE/f'{name}_third.jsonl'
        done=[]
        if output.exists():
            done=[json.loads(s)['kernel'] for s in output.read_text().splitlines()]
        for kernel in CASES[name]:
            if kernel in done:
                continue
            t=time.time()
            procs=min(4,max(1,int(46-os.getloadavg()[0])))
            records=records_for(kernel,space['full_records'])
            sub=rebind(ev,records)
            prepare(sub)
            r=run(sub,procs=procs,third=True)
            assert abs(r['loss1'])<1e-14
            r['T3a'],_=third_order(sub,procs)
            r['loss3']=r['T3a']+r['t3bc']
            r['total3']=r['loss']+r['loss3']
            r['exp_acc']=math.exp(-r['A1'])
            out=scalar(r);out.update(kernel=kernel,rank=len(records),seconds=time.time()-t,procs=procs,
                                    exact_zero_spectrum_filter=True)
            with output.open('a') as f:
                f.write(json.dumps(out)+'\n')
            print(name,json.dumps(out),flush=True)

if __name__=='__main__':
    main()

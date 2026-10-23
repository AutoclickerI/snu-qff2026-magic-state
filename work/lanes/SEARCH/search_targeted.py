import json,subprocess,time,os
from pathlib import Path
R=Path(__file__).resolve().parent
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
qs=['"snu-qff2026"','"tprep" "data_qubits"','"2607.22498"','"Chamberland" "Noh" language:Python','"Reed_Muller" "Steane" language:Python','"flag" "magic" language:Python','"magic" language:OpenQASM extension:qasm','"Steane" "preparation" language:Python']
prev=0
for i,q in enumerate(qs):
    time.sleep(max(0,prev+7-time.monotonic()));prev=time.monotonic()
    p=subprocess.run(['gh','api','-X','GET','search/code','-f','q='+q,'-f','per_page=100'],capture_output=True,text=True)
    raw=json.loads(p.stdout) if p.returncode==0 else {}
    data={'query':q,'total_count':raw.get('total_count'),'error':p.stderr if p.returncode else None,'items':[{'url':x['html_url'],'path':x['path'],'sha':x['sha'],'repo':x['repository']['full_name'],'description':x['repository'].get('description')} for x in raw.get('items',[])]}
    (R/'searches'/f'github-target-{i:02}.json').write_text(json.dumps(data,indent=2))
    print(q,data['total_count'],data['error'],flush=True)
    if i<2:
        with (R/'searches'/'excluded.jsonl').open('a') as f:
            for name in sorted(set(x['repo'] for x in data['items'])):
                if name not in ['snu-qff2026/snu-qff2026-problem']:f.write(json.dumps({'url':'https://github.com/'+name})+'\n')

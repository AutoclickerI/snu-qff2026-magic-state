import concurrent.futures as cf
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'public-research-artifact-survey/1.0'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()

def papers():
    ids = ['2609.12698','2601.13313','2607.22498','2610.09749','2511.13700','2512.23799','2506.14169','2403.03991','2409.17595']
    def one(a):
        d=ROOT/'found'/('arxiv-'+a);d.mkdir(exist_ok=True)
        for kind,url in [('abstract.html',f'https://arxiv.org/abs/{a}'),('paper.pdf',f'https://arxiv.org/pdf/{a}'),('paper.html',f'https://arxiv.org/html/{a}')]:
            try:
                b=get(url);(d/kind).write_bytes(b)
                print(json.dumps({'url':url,'bytes':len(b)}),flush=True)
            except Exception as e:
                print(json.dumps({'url':url,'error':str(e)}),flush=True)
        (d/'provenance.json').write_text(json.dumps({'url':f'https://arxiv.org/abs/{a}','commit':None,'licence':'See abstract.html arXiv licence link; paper and code licences must be distinguished.','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir() if p.is_file()}},indent=2))
    with cf.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(one,ids))

def github():
    queries=[
        'language:OpenQASM Steane', 'language:OpenQASM "magic"',
        'language:OpenQASM "reed"', 'language:OpenQASM "flag"',
        '"Steane" "magic"', '"Steane" "injection"',
        '"transversal" "T" "Reed"', '"gauge" "fixing" "Steane"',
        '"magic state cultivation"', '"fault-tolerant" "state" "preparation"',
        '"flag" "Steane"', '"DETECTOR" "S_DAG" "OBSERVABLE_INCLUDE" extension:stim',
        '"DETECTOR" "T" "OBSERVABLE_INCLUDE" extension:stim',
        '"2609.12698"', '"2607.22498"', '"2601.13313"',
        '"Chamberland" "Cross" "magic"', '"Noh" "flag"',
        '"H_state" "Steane"', '"15" "7" "code switching"',
    ]
    prev=0
    summary=[]
    for i,q in enumerate(queries):
        # This wait is required by the user-specified network quota.
        delay=max(0,prev+7-time.monotonic())
        if delay:time.sleep(delay)
        prev=time.monotonic()
        p=subprocess.run(['gh','api','-X','GET','search/code','-f','q='+q,'-f','per_page=100'],capture_output=True,text=True)
        path=ROOT/'searches'/f'github-code-{i:02}.json'
        if p.returncode:
            data={'query':q,'error':p.stderr,'returncode':p.returncode}
        else:
            raw=json.loads(p.stdout)
            # No text-match preview is requested. Save only repository/path metadata.
            data={'query':q,'total_count':raw['total_count'],'incomplete_results':raw.get('incomplete_results'),'items':[{'url':x['html_url'],'path':x['path'],'sha':x['sha'],'repo':x['repository']['full_name'],'description':x['repository'].get('description')} for x in raw['items']]}
        path.write_text(json.dumps(data,indent=2))
        summary.append({'query':q,'total_count':data.get('total_count'),'returned':len(data.get('items',[])),'error':data.get('error')})
        (ROOT/'searches/github-summary.json').write_text(json.dumps(summary,indent=2))
        print(json.dumps(summary[-1]),flush=True)
        with (ROOT/'REPORT.md').open('a') as f:f.write(f"\nGitHub code query `{q}`: total={data.get('total_count','ERROR')}, saved metadata={len(data.get('items',[]))}.\n")

if __name__=='__main__':
    import sys
    {'papers':papers,'github':github}[sys.argv[1]]()

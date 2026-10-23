import hashlib,json,os,re,subprocess,urllib.request,urllib.parse,zipfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(ROOT/'tmp'))
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'public-research-survey'}),timeout=90) as r:return r.read()
def api(endpoint):
    p=subprocess.run(['gh','api',endpoint],capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr)
    return json.loads(p.stdout)
def repo(name):
    name,sep,ref=name.partition('@')
    slug=name.replace('/','--')+('--'+ref if sep else '');d=ROOT/'found'/slug;d.mkdir(exist_ok=True)
    meta=api('repos/'+name)
    if re.search(r'snu.?qff.?2026|tprep|6.?[x×].?6.*(?:grid|Steane)',json.dumps({k:meta.get(k) for k in ['full_name','description','topics']}),re.I):
        (ROOT/'searches'/'excluded.jsonl').open('a').write(json.dumps({'url':meta['html_url']})+'\n');return
    sha=api('repos/'+name+'/commits/'+(ref or meta['default_branch']))['sha']
    tree=api('repos/'+name+'/git/trees/'+sha+'?recursive=1')
    if any(re.search(r'snu.?qff.?2026|(?:^|/)tprep(?:/|\.)|submit_credentials',x['path'],re.I) for x in tree.get('tree',[])):
        (ROOT/'searches'/'excluded.jsonl').open('a').write(json.dumps({'url':meta['html_url']})+'\n');return
    (d/'metadata.json').write_text(json.dumps(meta,indent=2));(d/'tree.json').write_text(json.dumps(tree,indent=2))
    licence=(meta.get('license') or {}).get('spdx_id','not specified')
    paths=[x for x in tree.get('tree',[]) if x['type']=='blob' and x.get('size',0)<4_000_000 and (re.search(r'\.(py|stim|qasm|ipynb|json|md|txt|csv|toml|jl)$',x['path'],re.I) or re.search(r'licen[cs]e|copying',x['path'],re.I))]
    # Avoid bulk unrelated examples in large SDKs; preserve the relevant preparation subsystem.
    if 'qecc' in name.lower():paths=[x for x in paths if re.search(r'state_prep|state-prep|steane|licen[cs]e|readme|pyproject|permutation|circuit_mod|synthesis|/faults.py|/simulation.py|/noise.py',x['path'],re.I)]
    if 'FTEC_flag' in name:paths=[x for x in paths if re.search(r'protocols/|licen[cs]e|readme',x['path'],re.I)]
    if name=='PECOS-packages/PECOS':paths=[x for x in paths if re.search(r'qeclib/steane/preps/|^LICENSE|^README',x['path'],re.I)]
    if name=='IBM/gauging_clifford_measurement':paths=[x for x in paths if re.search(r'd3|README|LICENSE|\.py$',x['path'],re.I)]
    files={}
    for x in paths:
        url='https://raw.githubusercontent.com/'+name+'/'+sha+'/'+urllib.parse.quote(x['path'])
        try:
            b=get(url);p=d/'source'/x['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);files[x['path']]={'url':url,'sha256':hashlib.sha256(b).hexdigest()}
        except Exception as e:files[x['path']]={'url':url,'error':str(e)}
    (d/'provenance.json').write_text(json.dumps({'url':meta['html_url'],'licence':licence,'commit':sha,'files':files},indent=2))
    print(json.dumps({'repo':name,'commit':sha,'licence':licence,'files':len(files)}),flush=True)
if __name__=='__main__':
    import sys
    for name in sys.argv[1:]:
        try:repo(name)
        except Exception as e:print(json.dumps({'repo':name,'error':str(e)}),flush=True)

import hashlib,json,re,urllib.request,urllib.parse,urllib.error,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'public-research-survey'}),timeout=60) as r:return r.read()
for i,q in enumerate(['Steane','"magic state"','Postler','Heussen']):
    url='https://zenodo.org/api/records?'+urllib.parse.urlencode({'q':q,'size':25})
    try:
        d=json.loads(get(url));(ROOT/'searches'/f'zenodo-fixed-{i}.json').write_text(json.dumps({'query':q,'raw':d},indent=2))
        print(q,d.get('hits',{}).get('total'),[(x['id'],x['metadata']['title']) for x in d.get('hits',{}).get('hits',[])],flush=True)
    except Exception as e:print(q,str(e),flush=True)

for p in sorted((ROOT/'found').glob('zenodo-*/metadata.json')):
    d=p.parent;meta=json.loads(p.read_text());files={}
    for f in meta.get('files',[]):
        target=d/f['key']
        if not target.exists() and d.name=='zenodo-6244536' and f['key'] in ['fig4b_circuit.pdf','fig4b_data.csv','fig4_circuit_ft.pdf','fig4_circuit_nft.pdf','fig4c_data.csv','fig4_circuit_nft+mh.pdf']:
            try:target.write_bytes(get(f['links']['self']))
            except Exception as e:print(f['key'],str(e),flush=True)
        if target.exists():
            b=target.read_bytes();actual='md5:'+hashlib.md5(b).hexdigest()
            files[f['key']]={'url':f['links']['self'],'sha256':hashlib.sha256(b).hexdigest(),'catalog_checksum':f.get('checksum'),'checksum_matches':actual==f.get('checksum')}
    (d/'provenance.json').write_text(json.dumps({'url':f'https://zenodo.org/records/{meta["id"]}','licence':meta['metadata'].get('license'),'commit':None,'commit_note':'Versioned Zenodo deposit; no git hash supplied. Files pinned by checksum.','doi':meta.get('doi'),'files':files},indent=2))

for rid in [23535237,27550992]:
    d=ROOT/'found'/f'figshare-{rid}';d.mkdir(exist_ok=True)
    try:
        meta=json.loads(get(f'https://api.figshare.com/v2/articles/{rid}'));(d/'metadata.json').write_text(json.dumps(meta,indent=2));files={}
        for f in meta['files']:
            if f['size']>20_000_000:continue
            b=get(f['download_url']);(d/f['name']).write_bytes(b);files[f['name']]={'url':f['download_url'],'sha256':hashlib.sha256(b).hexdigest()}
        (d/'provenance.json').write_text(json.dumps({'url':meta.get('url_public_html'),'licence':meta.get('license'),'commit':None,'version':meta.get('version'),'doi':meta.get('doi'),'files':files},indent=2))
        print('Figshare',rid,meta['title'],[(f['name'],f['size']) for f in meta['files']],flush=True)
    except Exception as e:print('Figshare',rid,str(e),flush=True)

for p in (ROOT/'found').glob('arxiv-*/provenance.json'):
    d=json.loads(p.read_text());s=(p.parent/'abstract.html').read_text()
    candidates=re.findall(r'href="([^"]*(?:licenses/|creativecommons.org/licenses)[^"]*)"',s)
    d['licence']=list(dict.fromkeys(candidates)) or 'not found in downloaded abstract'
    d['commit_note']='arXiv version, not git; see submission history in abstract.html'
    p.write_text(json.dumps(d,indent=2))

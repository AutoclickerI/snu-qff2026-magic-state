import hashlib,json,os,subprocess,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def get(url,data=None):
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'public-research-survey','Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read()
def catalogs():
    for host in ['zenodo','figshare']:
        for q in ['"Steane"','"magic state"','"fault-tolerant" "Postler"','"Heussen"']:
            name=host+'-'+str(['"Steane"','"magic state"','"fault-tolerant" "Postler"','"Heussen"'].index(q))
            try:
                if host=='zenodo':
                    url='https://zenodo.org/api/records?'+urllib.parse.urlencode({'q':q,'size':100})
                    d=json.loads(get(url)); count=d.get('hits',{}).get('total'); items=d.get('hits',{}).get('hits',[])
                    summary=[{'id':x['id'],'title':x['metadata']['title'],'url':x['links']['html']} for x in items]
                else:
                    url='https://api.figshare.com/v2/articles/search'
                    d=json.loads(get(url,json.dumps({'search_for':q,'page_size':100}).encode()));count=len(d)
                    summary=[{'id':x['id'],'title':x['title'],'url':x.get('url_public_html')} for x in d]
                (ROOT/'searches'/f'{name}.json').write_text(json.dumps({'query':q,'count':count,'results':summary,'raw':d},indent=2))
                print(json.dumps({'catalog':host,'q':q,'count':count,'results':summary}),flush=True)
            except Exception as e:
                (ROOT/'searches'/f'{name}.json').write_text(json.dumps({'query':q,'error':str(e)}));print(host,q,str(e),flush=True)
    for rid in ['6244536','10390470','15747203','15674835','13777072']:
        d=ROOT/'found'/('zenodo-'+rid);d.mkdir(exist_ok=True)
        try:
            meta=json.loads(get('https://zenodo.org/api/records/'+rid));(d/'metadata.json').write_text(json.dumps(meta,indent=2))
            files={}
            for f in meta.get('files',[]):
                if f.get('size',0)>60_000_000:files[f['key']]={'url':f['links']['self'],'size':f['size'],'not_downloaded':'large data; inspect metadata first'};continue
                b=get(f['links']['self']);path=d/f['key'];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
                files[f['key']]={'url':f['links']['self'],'sha256':hashlib.sha256(b).hexdigest()}
            (d/'provenance.json').write_text(json.dumps({'url':meta['links']['html'],'licence':meta['metadata'].get('license'),'commit':None,'version':meta['metadata'].get('version'),'doi':meta.get('doi'),'files':files},indent=2))
            print(json.dumps({'record':rid,'title':meta['metadata']['title'],'files':files}),flush=True)
        except Exception as e:print(json.dumps({'record':rid,'error':str(e)}),flush=True)
def papers():
    for a in ['2111.12654','2301.10017','2312.09745','1811.00566','2003.03049']:
        d=ROOT/'found'/('arxiv-'+a);d.mkdir(exist_ok=True)
        for kind,url in [('abstract.html',f'https://arxiv.org/abs/{a}'),('paper.pdf',f'https://arxiv.org/pdf/{a}')]:
            try:(d/kind).write_bytes(get(url))
            except Exception as e:print(url,str(e),flush=True)
        if (d/'paper.pdf').exists():subprocess.run(['pdftotext','-layout',str(d/'paper.pdf'),str(d/'paper.txt')])
        (d/'provenance.json').write_text(json.dumps({'url':f'https://arxiv.org/abs/{a}','commit':None,'licence':'See abstract.html license link','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir() if p.is_file()}},indent=2))
if __name__=='__main__':
    import sys
    {'catalogs':catalogs,'papers':papers}[sys.argv[1]]()

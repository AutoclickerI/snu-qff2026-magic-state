from common import *
import concurrent.futures,traceback

def one(name):
 try:r=score(H/name,1);r['ok']=True
 except Exception as e:r=dict(stem=name,ok=False,error=repr(e),traceback=traceback.format_exc())
 (H/(name+'.price.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True);return r
if __name__=='__main__':
 names=json.loads(Path(sys.argv[1]).read_text());workers=int(sys.argv[2])
 with concurrent.futures.ProcessPoolExecutor(workers)as pool:out=list(pool.map(one,names))
 (H/(Path(sys.argv[1]).stem+'.receipts.json')).write_text(json.dumps(out,indent=2))

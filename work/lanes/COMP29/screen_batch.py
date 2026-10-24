from common import *
import concurrent.futures,traceback
def one(row):
    try:return dict(row,**screen(row['stem']))
    except Exception as e:return dict(row,error=repr(e),traceback=traceback.format_exc())
if __name__=='__main__':
    label=sys.argv[2] if len(sys.argv)>2 else 'manifest'
    rows=json.loads((H/(label+'.json')).read_text())
    with concurrent.futures.ProcessPoolExecutor(int(sys.argv[1]) if len(sys.argv)>1 else 8) as pool:
        with (H/('screens.jsonl' if label=='manifest' else label+'.screens.jsonl')).open('w') as f:
            for r in pool.map(one,rows):
                f.write(json.dumps(r)+'\n');f.flush()
                print(r['stem'],r.get('total',r.get('error')),r.get('exp_minus_A1'),flush=True)

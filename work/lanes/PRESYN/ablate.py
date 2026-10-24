from core import *
import concurrent.futures
from decompose import label_channels,LABELS
import moments
def run(job):
 kind,name=job;c=read(OUT/'base');c['tags']=c['meta']['component_tags'];ev=exact2.Eval(textof(c),D);ids,detail=label_channels(ev,c)
 selected=np.array([LABELS[k]==name if name!='pre'else LABELS[k]in LABELS[:6]for k in ids])
 keep=~selected if kind=='no'else selected
 ev.fp=ev.fp*keep[ev.fch];r=moments.evaluate(ev);r.update(mode=kind,region=name)
 return r
if __name__=='__main__':
 jobs=[('no',r)for r in ['pre',*LABELS]]+[('only',r)for r in ['pre','internal_idle','round']]
 with concurrent.futures.ProcessPoolExecutor(int(sys.argv[1]))as p:
  rows=[]
  for r in p.map(run,jobs):rows.append(r);print(json.dumps(r),flush=True);(OUT/'ablation.json').write_text(json.dumps(rows,indent=2)+'\n')

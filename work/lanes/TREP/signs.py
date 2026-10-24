"""Evaluate all exact signed representations on a physically resynthesized support."""
import os,sys,json,re,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import exact2

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--procs',type=int,default=8);a=ap.parse_args()
    base=OUT/a.stem;src=base.with_suffix('.qasm').read_text();meta=json.loads(base.with_suffix('.json').read_text());data=meta['data_qubits']
    en=json.loads((OUT/'enumeration.json').read_text());form=next(f for f in en['forms']if f['id']=='f00_0')
    original_sites=[7,0,7,8,20,3,4,15,8,15,4,3,20,7,0]
    by_site={}
    for q,x in zip(original_sites,en['axes']):by_site.setdefault(q,[]).append(x['coordinate'])
    out=[]
    for sg in form['signed_representations']:
        coeff=dict(zip(form['support'],sg['coefficients']));lines=src.splitlines();j=0;seen={}
        for i,l in enumerate(lines):
            if re.match(r'^(t|tdg) ',l):
                q=int(re.search(r'q\[(\d+)\]',l).group(1));k=seen.get(q,0);seen[q]=k+1
                lines[i]=re.sub(r'^\w+',('t' if coeff[by_site[q][k]]==1 else 'tdg'),l);j+=1
        assert j==15
        text='\n'.join(lines)+'\n';tag=f'{a.stem}_sign{sg["sign_character"]:02d}';row={'name':tag,'sign':sg['sign_character']}
        (OUT/(tag+'.qasm')).write_text(text);(OUT/(tag+'.json')).write_text(json.dumps(dict(meta,sign_character=sg['sign_character']))+'\n')
        try:
            ev=exact2.Eval(text,data);r=exact2.run(ev,a.procs,third=True,keep_thr=1)
            row.update(c1=r['loss1'],second=r['loss2'],A1=r['A1'],t3bc=r['t3bc'],correct=True)
        except Exception as ex:row.update(correct=False,error=str(ex))
        out.append(row);print(json.dumps(row),flush=True)
        (OUT/(a.stem+'.signs.json')).write_text(json.dumps(out,indent=2)+'\n')

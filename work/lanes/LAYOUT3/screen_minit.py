import os,sys,json,glob,re
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path.insert(0,'work/lanes/EVAL');import exact2
out={}
for f in sorted(glob.glob('work/lanes/LAYOUT3/l3_base_m*.qasm')):
 stem=f[:-5];data=json.load(open(stem+'.json'))['data_qubits'];ev=exact2.Eval(open(f).read(),data);x=exact2.run(ev,4,third=False);out[stem]=dict(c1=x['loss1'],second=x['loss2'],exp=__import__('math').exp(-x['A1'])) ;print(stem,out[stem],flush=True)
json.dump(out,open('work/lanes/LAYOUT3/minit_screen.json','w'),indent=2)

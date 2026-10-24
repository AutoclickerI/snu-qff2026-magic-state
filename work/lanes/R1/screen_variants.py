import sys, json, re, subprocess, os
from pathlib import Path
HERE=Path(__file__).parent; src=Path('/home/jihoon/competitions/quantumn/work/candidates/v16_bc2m.qasm').read_text().splitlines()
def make(name,drop=(),release=True):
 groups=[];cur=[];bars=[];t=0
 for l in src:
  if l.startswith('barrier'):
   groups.append(cur);cur=[];bars.append(l);t+=1
   if t==33:break
  else:cur.append(l)
 out=[]
 for i,(g,b) in enumerate(zip(groups,bars)):
  out+=g
  if i not in drop:
   if release:
    qs=[int(q) for q in re.findall(r'q\[(\d+)\]',b)]
    if i>=15 and 19 in qs:qs.remove(19)
    if i>=19 and 13 in qs:qs.remove(13)
    b='barrier '+','.join(f'q[{q}]' for q in qs)+';'
   out.append(b)
 idx=next(j+1 for j,l in enumerate(src) if l.startswith('barrier') and sum(x.startswith('barrier') for x in src[:j+1])==33)
 out+=src[idx:]; p=HERE/(name+'.qasm');p.write_text('\n'.join(out)+'\n');d=json.loads(Path('/home/jihoon/competitions/quantumn/work/candidates/v16_bc2m.json').read_text());d['source']='R1 release/drop screen';(HERE/(name+'.json')).write_text(json.dumps(d));return p
if __name__=='__main__':
 out=[]
 for i in range(33):
  n=f'vs_drop{i:02d}';p=make(n,(i,));
  cmd=['/home/jihoon/competitions/quantumn/.venv/bin/python',str(HERE.parent/'EVAL/exact2.py'),str(p),'--procs','4','--top','0'];r=subprocess.run(cmd,cwd=HERE,capture_output=True,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'});m=re.search(r'1-F \(2nd order\) = ([\deE+.-]+)',r.stdout);c=re.search(r'c1 p = ([\deE+.-]+)',r.stdout);print(n,m.group(1) if m else 'ERR',c.group(1) if c else '',flush=True)

from core import *
import argparse,subprocess
p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=6);p.add_argument('--manifest');p.add_argument('names',nargs='*');a=p.parse_args()
names=a.names
if a.manifest:
 data=json.loads((V/a.manifest).read_text());names=[r['stem']for r in data if'screen'in r and not r.get('byte_identical_to')]
for name in names:
 st=V/name
 if st.with_suffix('.allorders.json').exists():continue
 with st.with_suffix('.allorders.log').open('w')as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),str(V/'sparse/sparse_walsh.py'),str(st),'72','canonical',str(a.procs)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,env=os.environ)
 if r.returncode:
  print(name,'all-orders failed',r.returncode,flush=True);continue
 row=json.loads((V/'sparse'/(st.name+'_canonical_sparse_result.json')).read_text());row['qasm_sha256']=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest();st.with_suffix('.allorders.json').write_text(json.dumps(row,indent=2));print(name,row['loss'],row['acceptance'],flush=True)
 with(H/'REPORT.md').open('a')as f:f.write(f'\nPrice `{name}`: all-orders{row["loss"]:.12e}, acceptance{row["acceptance"]:.9f}. Gates/MC are separate.\n')

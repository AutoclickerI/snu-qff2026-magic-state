import sys,json,re
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ['grid_flag','grid_flag_re','grid_ft24','grid_ft24_re']:
 p=HERE/(name+'.qasm');j=json.loads(p.with_suffix('.json').read_text());ls=p.read_text().splitlines();qs=set(j['layout']['b']+j['layout']['f']);n=int(re.search(r'creg c\[(\d+)\]',p.read_text())[1]);extra=[];changed=[]
 for i,s in enumerate(ls):
  m=re.match(r'reset q\[(\d+)\];',s)
  if not m:continue
  q=int(m[1])
  if q not in qs or (i+1<len(ls) and ls[i+1]==f'h q[{q}];'):continue
  ls[i]=f'measure q[{q}] -> c[{n}];';extra.append(f'// DETECTOR c[{n}]');changed.append(dict(line=i+1,qubit=q,bit=n));n+=1
 ls=[f'creg c[{n}];' if s.startswith('creg') else s for s in ls]+extra
 out=HERE/(name+'_m');out.with_suffix('.qasm').write_text('\n'.join(ls)+'\n');j['measure_init']=changed;out.with_suffix('.json').write_text(json.dumps(j,indent=2)+'\n');print(out.name,len(changed))

exec(open('work/lanes/SOTA_RESOURCE_20261028/screen.py').read().split('rows=[]')[0])
sys.path.insert(0,str(R/"work/lanes/REBUILD20261027"))
import record_contract
f.DATA=data;record_contract.fa=f
out=[]
for path in sorted(here.glob('delete_*.qasm')):
 try:
  s=record_contract.singles(f.make_model(*f.parse_current(path.read_text())))
  row={'stem':str(path.with_suffix('')),'c1':s['c1'],'harmful':len(s['harmful_faults'])}
 except Exception as e: row={'stem':str(path.with_suffix('')),'error':str(e)}
 out.append(row);print(json.dumps(row),flush=True)
(here/'singles.json').write_text(json.dumps(out,indent=2)+'\n')

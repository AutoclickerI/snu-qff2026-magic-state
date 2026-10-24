from round35 import *
import re,runpy
stem=Path(sys.argv[1]).resolve()
a=json.loads(Path(str(stem)+'.allorders.json').read_text());sp=json.loads(Path(str(stem)+'.speed.json').read_text());j=json.loads(Path(str(stem)+'.judge.json').read_text());cert=json.loads(Path(str(stem)+'.ideal.json').read_text())
s=[float(x) for x in re.findall(r' (?:0|1000|2000) ([\deE+.-]+) ±',Path(str(stem)+'.mc3.log').read_text())];assert len(s)==3 and j['passed'] and sp['classification']=='FAST'
r=dict(ideal=cert,allorders={k:a[k] for k in ('loss','acceptance')},speed=sp,judge=j,seeds=s,mean=sum(s)/3)
Path(str(stem)+'.verified.json').write_text(json.dumps(r,indent=2));runpy.run_path(str(HERE/'r35_report.py'),run_name='__main__');print(json.dumps(r))

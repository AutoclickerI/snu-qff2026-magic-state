from common import *
import subprocess,concurrent.futures
names=sys.argv[1:]
def run(name):
 p=subprocess.run([sys.executable,str(HERE/'evaluate.py'),name,'4'],cwd=HERE,capture_output=True,text=True)
 (HERE/(name+'.eval.log')).write_text(p.stdout+p.stderr)
 return name,p.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for name,code in pool.map(run,names):print(name,code,flush=True)

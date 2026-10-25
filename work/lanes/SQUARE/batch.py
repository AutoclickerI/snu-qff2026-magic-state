import sys,json,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
H=Path(__file__).resolve().parent
def run(n):
    p=subprocess.run([sys.executable,str(H/'price.py'),n,'1'],text=True,capture_output=True)
    print(p.stdout or p.stderr,flush=True)
    if p.returncode:raise RuntimeError(n+': '+p.stderr)
if __name__=='__main__':
    names=sys.argv[1:]
    with ThreadPoolExecutor(3) as pool:list(pool.map(run,names))

"""Stop this lane's remaining central-reset variants after the reference finishes."""
from search_v10 import *
import signal
r=json.loads((HERE/'nreset_s4_b0.json').read_text())
assert len(r['seeds'])==3 and r['passed']
pid=int(sys.argv[1]);cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'lanes/L5_precycle/search_v10.py check nreset_manifest.json --procs 6' in cmd,cmd
os.kill(pid,signal.SIGSTOP)
children=[];pending=[pid]
while pending:
    parent=pending.pop()
    try:found=list(map(int,Path(f'/proc/{parent}/task/{parent}/children').read_text().split()))
    except FileNotFoundError:found=[]
    children.extend(found);pending.extend(found)
for child in reversed(children):
    try:os.kill(child,signal.SIGTERM)
    except ProcessLookupError:pass
os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT)
row={'stopped_pid':pid,'children':children,'completed_candidate':'nreset_s4_b0','mean':r['mean'],
     'reason':'Central retained-readout variant saves one layer but yields only a small three-seed difference and takes about 500 seconds per seed at six workers; prioritize measured 5-6 percent boundary/retention gains. Remaining 15 priority variants remain screen-only.'}
(HERE/'nreset_stop.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)

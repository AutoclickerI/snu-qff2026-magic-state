"""Receive actual completion events, preserving remote full result receipts."""
import sys,json,os
from pathlib import Path
H=Path(__file__).resolve().parent
for line in sys.stdin:
    event=json.loads(line);n=event['stem'];r=event['result']
    target=H/(n+'.allorders.json');tmp=target.with_name(target.name+f'.tmp.{os.getpid()}');tmp.write_text(json.dumps(r,indent=2)+'\n');os.replace(tmp,target)
    from report34 import refresh
    refresh()
    print(json.dumps(dict(stem=n,loss=r.get('loss'),acceptance=r.get('acceptance'),error=r.get('error'),exit_code=event['exit_code'])),flush=True)

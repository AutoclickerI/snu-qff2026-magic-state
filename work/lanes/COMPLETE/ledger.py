import json,fcntl
from pathlib import Path
H=Path(__file__).resolve().parent
def merge(sha,row):
    with (H/'.results.lock').open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        all=json.loads((H/'results.json').read_text());old=all.get(sha,{})
        di={**old.get('diagnostics',{}),**row.get('diagnostics',{})}
        aliases=sorted(set(old.get('aliases',[])+row.get('aliases',[])))
        all[sha]={**old,**row}
        if di:all[sha]['diagnostics']=di
        if aliases:all[sha]['aliases']=aliases
        (H/'results.json').write_text(json.dumps(all,indent=2)+'\n')

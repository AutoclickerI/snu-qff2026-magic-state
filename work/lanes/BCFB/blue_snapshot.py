import os,sys
sys.dont_write_bytecode=True
from pathlib import Path
import sqlite3,json,time
D=Path(__file__).resolve().parent/'blue'
with sqlite3.connect(D/'search.sqlite',timeout=120) as src,sqlite3.connect(D/'snapshot.sqlite') as dst:src.backup(dst)
with sqlite3.connect(D/'snapshot.sqlite') as db:
 print(json.dumps(dict(time=time.time(),rows=db.execute('select count(*) from prices').fetchone()[0],kinds=db.execute('select kind,count(*),min(value) from prices group by kind').fetchall())),flush=True)

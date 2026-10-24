import sqlite3,json,zlib
from pathlib import Path
H=Path(__file__).resolve().parent
with sqlite3.connect(H/'search.sqlite',timeout=120) as src,sqlite3.connect(H/'search_snapshot.sqlite') as dst:src.backup(dst)
with sqlite3.connect(H/'search_snapshot.sqlite') as db:
 print(json.dumps(list(db.execute('select kind,count(*),min(value) from prices group by kind'))))
 for tag,value,row in db.execute('select tag,value,row from prices where value is not null order by value limit 5'):print(tag,value,json.loads(row).get('exp_minus_A1'))

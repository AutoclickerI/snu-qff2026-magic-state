"""Event-driven shared queue for bounded physical CPU slots on owl."""
from a35_queue import *
import sqlite3,multiprocessing
DB=D/'runs/price_queue.sqlite'
def worker(_):
 db=sqlite3.connect(DB,timeout=120)
 while True:
  db.execute('begin immediate');row=db.execute("select id,stem from tasks where status='pending' order by id limit 1").fetchone()
  if row is None:db.commit();break
  i,s=row;db.execute("update tasks set status='running',pid=? where id=?",(os.getpid(),i));db.commit()
  r=work(s);db.execute("update tasks set status='done',result=? where id=?",(json.dumps(r),i));db.commit();print('RESULT',json.dumps(r),flush=True)
 db.close();return os.getpid()
if __name__=='__main__':
 if sys.argv[1]=='init':
  ss=json.loads(Path(sys.argv[2]).read_text());db=sqlite3.connect(DB);db.execute('create table tasks(id integer primary key,stem text unique,status text,pid integer,result text)');db.executemany('insert into tasks(id,stem,status) values(?,?,?)',[(i,s,'pending') for i,s in enumerate(ss)]);db.commit();print('queued',len(ss),flush=True)
 else:
  n=int(sys.argv[1])
  with multiprocessing.get_context('fork').Pool(n) as p:p.map(worker,range(n))
  print('WORKERS_EXITED',n,flush=True)

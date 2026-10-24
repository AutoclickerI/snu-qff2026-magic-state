"""Use a newly available reference slot for a finite finalist job, then resume it.

No child process is created. The all-orders physics functions are unchanged.
"""
import os,sys,json,fcntl,time,hashlib,traceback,runpy
from pathlib import Path
H=Path(__file__).resolve().parent

def run_one(resume):
    todo=H/'priority30.json'
    if not todo.exists():return
    for task in json.loads(todo.read_text()):
        receipt=H/(task['id']+'.priority.json')
        if receipt.exists():continue
        lock=(H/(task['id']+'.priority.lock')).open('a+')
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:lock.close();continue
        if receipt.exists():lock.close();continue
        start=time.monotonic();stem=H/task['stem']
        result=dict(task=task,source_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest())
        with (H/(task['id']+'.priority.log')).open('w') as log:
            import contextlib
            with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
                try:
                    if task['kind']=='unfold_family':
                        from unfold_family30 import run
                        result.update(run(),passed=True)
                    elif task['kind']=='unfold_extensions':
                        from unfold_family30 import extensions
                        result.update(extensions(),passed=True)
                    elif task['kind']=='gate':
                        sys.argv=[str(H/'gate.py'),*task.get('stems',[task['stem']])]
                        runpy.run_path(str(H/'gate.py'),run_name='__main__')
                        result['passed']=True
                    elif task['kind']=='allorders':
                        import allorders_general as a
                        a.G=a.prepare(stem)
                        validation=a.validate(stem,a.G)
                        keys=[None]+a.G[1].keys
                        rows=[]
                        for index in range(task['part'],len(keys),task['parts']):
                            row=a.one(keys[index]);row['index']=index;rows.append(row);print(json.dumps(row),flush=True)
                        result.update(validation=validation,rows=rows,keys=len(keys),passed=True)
                    elif task['kind']=='exact':
                        os.environ['COMP29_PRIORITY_INNER']='1'
                        sys.argv=[str(H/'exact_job.py'),task['stem'],'1']
                        runpy.run_path(str(H/'exact_job.py'),run_name='__main__')
                        result['passed']=True
                    else:raise ValueError(task)
                except BaseException as e:
                    result.update(passed=False,error=repr(e));traceback.print_exc()
        result['seconds']=time.monotonic()-start
        receipt.write_text(json.dumps(result,indent=2)+'\n')
        print('Priority job finished',task['id'],result['passed'],flush=True)
        os.environ['COMP29_PRIORITY_RESUME']='1'
        os.execv(sys.executable,[sys.executable,str(H/'exact_job.py'),*resume])


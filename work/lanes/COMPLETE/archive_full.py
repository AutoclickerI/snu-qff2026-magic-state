"""Archive actual native source-cell releases, not just last completion gates."""
import os,sys,json,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from build import H,generate,lib
BITS={64,67,54,55,56,57,8,12,274,45}
def prof(st):
    c=lib.read(st);events=[]
    for o in c['ops']:
        if set(lib.bits_of(o))&BITS:
            events.append(dict(cell=lib.unit(o).qs[0],release=o['t']+1,record=lib.bits_of(o)[0]))
    return sorted(events,key=lambda x:(x['cell'],x['record']))
def run():
    comps=json.loads((H/'completions.json').read_text())['completions'];rows=[];seen=set()
    chosen=['swap8_2_rebind','swap8_14_rebind','swap8_9_rebind']
    for name in chosen:
        st=H/'builds'/name;md=json.loads(st.with_suffix('.json').read_text());p=prof(st)
        key=tuple((x['cell'],x['release'],x['record']) for x in p);seen.add(key)
        rows.append(dict(id=f'f{len(rows):02}',stem=name,completion=md['completion'],release_profile=p,
                         sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()))
    failures=[]
    for i,comp in enumerate(comps):
        if len(rows)>=30:break
        try:st=generate(comp,f'archive_{i:03}',seconds=2)
        except Exception as e:failures.append(dict(index=i,error=str(e)[:200]));continue
        p=prof(st);key=tuple((x['cell'],x['release'],x['record']) for x in p)
        if key in seen:continue
        seen.add(key);rows.append(dict(id=f'f{len(rows):02}',stem=st.name,completion=comp,release_profile=p,
                         sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()))
        print('archive',len(rows),st.name,flush=True)
    assert len(rows)>=20,len(rows)
    old=H/'archive.json';old.rename(H/'completion_end_archive.json')
    old.write_text(json.dumps(dict(profiles=rows,failures=failures,
       meaning='Actual native source-record cell release times in complete routed schedules. Output placement and occupancy are in each saved plan; release does not imply that a later role leaves the cell idle.',
       selection='Preserve 30 distinct release vectors before scoring; first three are the selected downstream families.'),indent=2)+'\n')
if __name__=='__main__':run()

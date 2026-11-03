"""Add deterministic mid-factory zero reads to catch existing propagation hooks."""
import argparse,copy,json,sys
from pathlib import Path
from b_resource import contract
from resource_pauli_audit import audit


def choices(module,pc,allow_delay=False):
    ops=module['operations'];rows={int(q):v for q,v in module['initial_rows'].items()}
    helpers=set(rows)-set(pc.B)
    used={q for o in ops for q in o['qs']};helpers &= used
    grouped={}
    for o in ops:grouped.setdefault(o['time'],[]).append(o)
    times={q:sorted(o['time'] for o in ops if q in o['qs']) for q in used}
    out=[]
    for t,batch in sorted(grouped.items()):
        for o in batch:
            if o['kind']=='CX':a,b=o['qs'];rows[b]^=rows[a]
            elif o['kind']=='R':rows[o['qs'][0]]=0
            elif o['kind']=='RX':rows[o['qs'][0]]=int(module['initial_rows'].get(str(o['qs'][0]),module['initial_rows'].get(o['qs'][0],0)))
        for o in batch:
            if o['kind'] not in ('CX','R','RX'):continue
            for q in set(o['qs'])&helpers:
                if rows[q]:continue
                future=[z for z in times[q] if z>t]
                if not future:continue
                nxt=min(future)
                for nt in range(t+1,nxt):out.append((q,nt,False))
                if allow_delay and nxt==t+1:out.append((q,t+1,True))
    return sorted(set(out))


def add(module,choice,pc):
    q,t,delay=choice;row=copy.deepcopy(module)
    if delay:
        for o in row['operations']:
            if o['time']>=t:o['time']+=1
    row['operations'].append(dict(time=t,kind='M',qs=[q],zero_flag=True,mid_factory_herald=True))
    row['operations'].sort(key=lambda o:(o['time'],o['kind'],o['qs']))
    row['module_end']=max(o['time'] for o in row['operations'])+1
    row['resource_ready']=max(o['time']+1 for o in row['operations'] if set(o['qs'])&set(pc.B))
    row['resource_c1']=audit(pc,row)['resource_c1']
    row.setdefault('added_heralds',[]).append(dict(q=q,time=t,global_delay=delay))
    return row


def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--limit',type=int,default=8);ap.add_argument('--delay',action='store_true');ap.add_argument('--output')
    a=ap.parse_args();doc=json.loads(Path(a.input).read_text());pc=contract(doc.get('swapped',False));results=[]
    for index,old in enumerate(doc['candidates'][:a.limit]):
        row=copy.deepcopy(old);steps=0
        for step in range(20):
            if row['resource_c1']<1e-12:break
            best=row
            for c in choices(row,pc,a.delay):
                trial=add(row,c,pc)
                if (trial['resource_c1'],trial['resource_ready'])<(best['resource_c1']-1e-12,best['resource_ready']):best=trial
            if best is row:break
            row=best;steps+=1
        row['input_index']=index;results.append(row)
        print(json.dumps(dict(index=index,steps=steps,c1=row['resource_c1'],ready=row['resource_ready'],cx=row['cx'],heralds=row.get('added_heralds',[]))),flush=True)
    doc['candidates']=sorted(results,key=lambda r:(r['resource_c1'],r['resource_ready'],r['cx']))
    doc['herald_source']=a.input
    out=Path(a.output or Path(a.input).with_suffix('.heralded.json'));out.write_text(json.dumps(doc,indent=2)+'\n')


if __name__=='__main__':main()

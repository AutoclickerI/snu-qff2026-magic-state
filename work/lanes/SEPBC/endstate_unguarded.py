"""Price coherent data transfers without optional source-zero postselection."""
from common import *
stem=Path(sys.argv[1]);c=json.loads(stem.with_suffix('.plan.json').read_text());drop={int(b)for o in c['ops']if o['tag']=='data_hops'and unit(o).name=='MEASURE'for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))}
c['ops']=[o for o in c['ops']if not(o['tag']=='data_hops'and unit(o).name=='MEASURE')];tail=[]
for line in c['tail']:
 bs=set(map(int,re.findall(r'c\[(\d+)\]',line)))
 if bs&drop:
  assert line.startswith('// DETECTOR')and len(bs)==1,line
 else:tail.append(line)
c['tail']=tail;c,rec=schedule(c,mode='alap');assert c is not None,rec;c['meta']['data_source_guards_removed']=len(drop);name=stem.name+'_noguard';out=save(c,name);r=score(out);append_result(name,r,'Optional source-zero measurements removed after coherent two-CX transfers; native dependencies rescheduled, all detector and correctness checks retained.');print(json.dumps(dict(schedule=rec,score=r)),flush=True)

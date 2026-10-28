import os,sys,json,copy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/CONTINUE_20261028'),str(R/'work/lanes/END2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from qtools import write_stem,price
from joint import emit
import record_contract,instrument_probe
D=[6,20,19,10,2,22,16];f.DATA=D
names=['cat7_bdelay16_','cat7_bdelay17_','cat7_bdelay18_','cat7_opt_t11_m0_d21_','cat7_one_r1_n3_d20_','cat7_flag_bdelay23_'];jobs=[(n,False) for n in names]+[('cat7_opt_t11_m0_d21_',True),('cat7_bdelay17_',True)]
rows=[]
for name,rx in jobs:
 P=next((R/'work/lanes/NATIVE_CAT7_20261028/boundary').glob(name+'*.qasm'));meta=json.load(open(P.with_suffix('.integration.json')));base,d=f.parse_current(P.read_text());ops=copy.deepcopy(base)
 ad=json.load(open(meta['a_module']));aops=ad['candidates'][0]['operations'];at=min(x['time'] for x in aops if 15 in x['qs']);qt=at-1
 assert not any(o.time==qt and 15 in o.qs for o in ops),(name,qt);ops.append(f.Op('R',(15,),qt))
 if rx:
  mx=next(o for o in ops if o.kind=='MX' and o.qs==(26,));bt=mx.time-1;assert not any(o.time==bt and 26 in o.qs for o in ops),(name,bt);ops.append(f.Op('RX',(26,),bt))
 ops.sort(key=lambda x:(x.time,x.kind,x.qs));c=record_contract.complete(f.make_model(ops,[]),[]);ds=[set(x['bits']) for x in c['missing'] if not x['reference']];text=emit(ops,ds);raw=raw_check(text,D)
 row={'parent':str(P),'R15_time':qt,'RX26':rx,'raw':raw,'detectors':len(ds)}
 print('RAW',name,rx,json.dumps(raw),flush=True)
 if raw['ok']:
  stem=write_stem(text,D,H,'repair_'+name.strip('_')+('_rx26' if rx else ''),source=row);m=f.make_model(*f.parse_current(text));ss=record_contract.singles(m);row.update(stem=str(stem),c1=ss['c1'],harmful=len(ss['harmful_faults']));cut=max(o.time for o in ops if o.kind=='TDG')+1;probe=instrument_probe.probe(stem,cut);row['instrument']=probe['summary'];p=price(stem,1);row['exact']=p;print('RESULT',name,'rx26',rx,'L',p['loss'],'A',p['acceptance'],'c1',ss['c1'],'probe',json.dumps(row['instrument']),flush=True)
 rows.append(row);(H/'rerank.json').write_text(json.dumps(rows,indent=2)+'\n')

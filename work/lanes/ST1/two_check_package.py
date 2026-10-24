from common import *
import itertools,collections
sys.path.insert(0,str(ROOT/'work/lanes/ENDSTATE'))
from library import rowkey
L=json.loads((ROOT/'work/lanes/ENDSTATE/library_input.json').read_text());ENC=json.loads((ROOT/'work/lanes/ENDSTATE/library_encoders.json').read_text())
initial=[7,8,9,14,15,20,21];final={q:({8:2,15:16}.get(q,q))for q in initial};h0={7,8,9,14};h1={9,14,15,21};pair=[(7,8),(15,21),(9,14)];native=next(r for r in L['embeddings']if set(r[1:])==set(initial));sid=native[0];native=native[1:];rows=[];seen=set()
for choice in itertools.product([0,1],repeat=3):
 h2={20}|{pair[i][j]for i,j in enumerate(choice)};Hrows=[h0,h1,h2];target=rowkey([sum(1<<native.index(q)for q in h)for h in Hrows])
 if target in seen:continue
 seen.add(target);cid=L['targets'].index(target);b=ENC[sid][cid];ops=[[native[u],native[v]]for u,v in b['ops']];piv=[native[i]for i in b['pivots']];labels={q:sum((q in h)<<i for i,h in enumerate(Hrows))-1 for q in initial};assert sorted(labels.values())==list(range(7));ib=[None]*7;fb=[None]*7
 for q,i in labels.items():ib[i]=q;fb[i]=final[q]
 logical_ops=[[labels[u],labels[v]]for u,v in ops];logical_piv=[labels[q]for q in piv];faults=[]
 for loc in range(-1,len(logical_ops)):
  es=[1<<i for i in range(7)if i not in logical_piv]if loc<0 else[1<<logical_ops[loc][0],1<<logical_ops[loc][1],sum(1<<i for i in logical_ops[loc])]
  for e in es:
   for u,v in logical_ops[loc+1:]:
    if e>>u&1:e^=1<<v
   sy=0
   for i in range(7):
    if e>>i&1:sy^=i+1
   bad=(e.bit_count()%2)^int(sy!=0)
   if bad:faults.append(dict(location=loc,pattern=e,syndrome=sy,detected=bool(sy&3)))
 out=dict(initial_b=ib,final_b=fb,checker_cells=[8,15],check_rows=[[0,2,4,6],[1,2,5,6]],encoder_b=dict(ops=logical_ops,pivots=logical_piv),encoder_cx=b['cx'],shape=sid,code_class=cid,first_order_B_pass=all(f['detected']for f in faults),harmful_faults=faults)
 rows.append(out);print(json.dumps(out),flush=True)
(H/'two_check_packages.json').write_text(json.dumps(rows,indent=2));valid=[r for r in rows if r['first_order_B_pass']];assert valid,'No safe package';best=min(valid,key=lambda r:r['encoder_cx']);(H/'two_check_package.json').write_text(json.dumps(best,indent=2));append_result('two_check_package',dict(encoder_cx=best['encoder_cx'],shape=best['shape'],code_class=best['code_class'],initial_b=best['initial_b'],final_b=best['final_b'],checker_cells=best['checker_cells'],B_single_fault_pass=True),'Native B prep, two one-CX transfers, and two static four-body Z checks. Every harmful encoder X-component single is detected by the two checks. Full-circuit c1 and higher orders remain to be verified.')

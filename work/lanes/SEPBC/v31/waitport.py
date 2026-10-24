"""Port WAITPROT's six verified mechanisms into actual R44 idle intervals."""
from build import *
recipes=[(0,6,'Z',39,43),(20,19,'X',18,35),(7,13,'X',20,23),(10,11,'X',19,26),(10,4,'Z',35,38),(4,5,'X',18,30)]
base=json.loads((V/'A44_feedback_0.plan.json').read_text());br=json.loads((V/'A44_feedback_0.screen.json').read_text());busy={q:{o['t']for o in base['ops']if q in unit(o).qs}for q in range(36)}
def add(c,rec):
 q,h,axis,start,end=rec;c=copy.deepcopy(c);b=bit(c);edge=(h,q)if axis=='Z'else(q,h)
 for lines,t in [([f'reset q[{h}];']+([f'h q[{h}];']if axis=='Z'else[]),start-1),([f'cx q[{edge[0]}],q[{edge[1]}];'],start),([f'cx q[{edge[0]}],q[{edge[1]}];'],end),(([f'h q[{h}];']if axis=='Z'else[])+[f'measure q[{h}] -> c[{b}];']+([f'h q[{h}];']if axis=='Z'else[]),end+1)]:c['ops'].append(dict(lines=lines,t=t,id=10000+len(c['ops']),tag='wait_guard'))
 c['tail'].append(f'// DETECTOR c[{b}]');return fix(c)
rows=[]
for j,(q,h,axis,a,b)in enumerate(recipes):
 feasible=[]
 for start in range(max(1,a-6),a+2):
  for end in range(max(start+2,b-6),min(b+1,base['meta']['R']-2)+1):
   if not any(t in busy[q]for t in range(start,end+1))and not any(t in busy[h]for t in range(start-1,end+2)):
    feasible.append((-(end-start),abs(start-a)+abs(end-b),start,end))
 if not feasible:print('no native slot',j,recipes[j],flush=True);continue
 _,_,start,end=min(feasible);rec=(q,h,axis,start,end);name=f'guard_{j}'
 try:
  st=save(add(base,rec),'v31/'+name);r=score(st);row=dict(stem=name,recipe=rec,screen=r,gain=br['total']-r.get('total',1),cost_A1=math.log(br['exp_minus_A1']/r['exp_minus_A1']));rows.append(row);print(name,json.dumps(row),flush=True);append_result(name,row,'WAITPROT identity port in a verified idle slot of the R44 circuit; no old gate/tick moved. Full fault model repriced.')
 except Exception as e:print(name,repr(e),flush=True)
(V/'waitport_singles.json').write_text(json.dumps(rows,indent=2));current=base;cr=br;chosen=[];joint=[]
for k in range(6):
 trials=[]
 for row in rows:
  if row['stem']in chosen:continue
  d=add(current,row['recipe'])
  try:
   d,txt=normalized(d);s=mom.evaluate(exact2.Eval(txt,d['meta']['data_qubits']))
   if s['exp_minus_A1']>=.5002 and s['total']<cr['total']-1e-12:trials.append((s['total'],row,d,s))
  except Exception:continue
 if not trials:break
 _,row,current,cr=min(trials,key=lambda x:x[0]);chosen.append(row['stem']);name=f'guard_joint_{k}';st=save(current,'v31/'+name);cr=score(st);r=dict(stem=name,chosen=chosen[:],screen=cr);joint.append(r);append_result(name,r,'Full joint heralding price, not a sum of single-guard gains; acceptance constrained.');print(name,json.dumps(r),flush=True)
(V/'waitport_joint.json').write_text(json.dumps(joint,indent=2))

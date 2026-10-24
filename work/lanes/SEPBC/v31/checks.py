from build import *
import collections

def add(c,ch):
 if ch['kind']=='mz':return edit(c,'mz'+str(ch['q']))
 c=copy.deepcopy(c);q=ch['q'];b=bit(c);lines=([f'h q[{q}];']if ch['axis']=='X'else[])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];']if ch['axis']=='X'else[])
 c['ops'].append(dict(lines=lines,t=ch['t'],id=10000+b,tag='known_state_check'));c['tail'].append(f'// DETECTOR c[{ch["source"]}] c[{b}]');return fix(c)
base=json.loads((V/'full_port.plan.json').read_text());br=json.loads((V/'full_port.screen.json').read_text());ops=base['ops'];R=base['meta']['R'];checks=[]
for i,o in enumerate(ops):
 u=unit(o)
 if u.name not in('MX','MEASURE')or o['t']>=R:continue
 q=u.qs[0];nxt=next((v for v in ops[i+1:]if q in unit(v).qs),None)
 if nxt is None or nxt['t']-o['t']<2 or nxt['t']>=R:continue
 rec=int(re.search(r'c\[(\d+)\]',' '.join(o['lines']))[1]);checks.append(dict(kind='repeat',q=q,t=nxt['t']-1,axis='X'if u.name=='MX'else'Z',source=rec))
checks.append(dict(kind='mz',q=19));rows=[]
for j,ch in enumerate(checks):
 name=f'check_{j:02d}_q{ch["q"]}'
 try:
  st=save(add(base,ch),'v31/'+name);r=score(st);cost=math.log(br['exp_minus_A1']/r['exp_minus_A1']);gain=br['total']-r.get('total',1);row=dict(stem=name,check=ch,screen=r,gain=gain,acceptance_cost_A1=cost,efficiency=gain/cost if cost>0 else None);rows.append(row);append_result(name,row,'Repeat a measured known state in an existing idle slot, or measured known-zero initialization; full-circuit detector/noise price.');print(name,gain,r['exp_minus_A1'],ch,flush=True)
 except Exception as e:rows.append(dict(stem=name,check=ch,error=repr(e)));print(name,repr(e),flush=True)
(V/'check_scan.json').write_text(json.dumps(rows,indent=2));pool=[r for r in rows if r.get('gain',0)>0 and r['screen']['exp_minus_A1']>=.5002];pool.sort(key=lambda r:-(r['efficiency']or 0));current=base;cr=br;chosen=[];greedy=[]
for k in range(8):
 trials=[]
 for r in pool:
  if r['stem']in chosen:continue
  d=add(current,r['check']);d,txt=normalized(d);ev=exact2.Eval(txt,d['meta']['data_qubits']);s=mom.evaluate(ev)
  if s['exp_minus_A1']>=.5002 and s['total']<cr['total']-1e-12:trials.append((s['total'],r,d,s))
 if not trials:break
 _,r,current,cr=min(trials,key=lambda x:x[0]);chosen.append(r['stem']);name=f'checks_joint_{k}';st=save(current,'v31/'+name);cr=score(st);row=dict(stem=name,checks=chosen[:],screen=cr);greedy.append(row);append_result(name,row,'Jointly repriced detector selection under acceptance floor; non-additive fault interactions retained.');print('JOINT',json.dumps(row),flush=True)
(V/'check_selection.json').write_text(json.dumps(greedy,indent=2))

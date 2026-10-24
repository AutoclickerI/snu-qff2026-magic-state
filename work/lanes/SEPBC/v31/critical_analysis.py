"""Current native-wire certificates and conditional R43 scheduling test."""
from build import *
sys.path.insert(0,str(H/'v30'));from critical import analyze
from retime import solve
import collections
rows=[];lines=['# v31s and R44 critical paths','','Native steps are zero based. ES/LS use the emitted per-wire operation order. Component ready slack is R minus earliest completion, not a freely movable interval. CP feasibility additionally permits the specified commuting CX/phase exchanges; it is conditional on the physical operations and measurements.','']
for name,path in [('v31s',H/'v30/sensitivity_tail.plan.json'),('full_timing_0',V/'full_timing_0.plan.json'),('A44_feedback_0',V/'A44_feedback_0.plan.json'),('guard_joint_2',V/'guard_joint_2.plan.json')]:
 c=json.loads(path.read_text());d=analyze(c);(V/(name+'.critical.json')).write_text(json.dumps(d,indent=2));R=c['meta']['R'];regions=collections.defaultdict(list)
 for o,z in zip(c['ops'],d['operations']):
  if o['t']<R:regions[o.get('tag','untagged')].append(z)
 component={k:dict(actual_ready=max(z['t']for z in zs)+1,earliest_ready=max(z['es']for z in zs)+1,ready_slack=R-max(z['es']for z in zs)-1)for k,zs in regions.items()}
 tg=[z for z in d['operations']if any(l.startswith(('t ','tdg '))for l in z['lines'])]
 component['terminal_Tdag']=dict(actual_ready=max(z['t']for z in tg)+1,earliest_ready=max(z['es']for z in tg)+1,ready_slack=R-max(z['es']for z in tg)-1)
 row=dict(stem=name,R=R,fixed_order_minimum=d['minimum_R'],components=component);rows.append(row)
 lines +=[f'## {name}: R{R}; fixed-order minimum R{d["minimum_R"]}','','| Component | Actual ready | Earliest ready | Ready slack |','|---|---:|---:|---:|']
 for k,z in component.items():lines.append(f'| {k} | {z["actual_ready"]} | {z["earliest_ready"]} | {z["ready_slack"]} |')
 lines+=['','One binding suffix (the JSON includes all nodes and representative longest paths):','']
 for i in d['longest_paths'][0]:
  z=d['operations'][i]
  if z['es']>=27:lines.append(f'- step {z["es"]}, actual {z["t"]}, slack {z["slack"]}: '+ ' / '.join(z['lines']))
 lines+=['']
c=json.loads((V/'A44_feedback_0.plan.json').read_text())
for phases in [False,True]:
 _,r=solve(c,27,15,1,fixR=43,phases=phases);rows.append(dict(stem='A44_feedback_0',fixed_R43=r));lines.append(f'R43 feasibility on A44_feedback_0, commuting control phases={phases}: `{json.dumps(r)}`.');print(r,flush=True)
(V/'critical_summary.json').write_text(json.dumps(rows,indent=2));(V/'CRITICAL_PATH.md').write_text('\n'.join(lines)+'\n');print(json.dumps(rows),flush=True)

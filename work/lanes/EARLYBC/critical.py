from core import *
us,_=parse_source();pre=[u for u in us if u['region']=='pre'];prep=[u for u in us if u['region']=='prep'];end={};last={};trace=[]
for u in pre:
 for q in u['qs']:end[q]=max(end.get(q,0),u['t']+1);last[q]=None
for i,u in enumerate(prep):
 q=max(u['qs'],key=lambda q:end.get(q,0));t=end.get(q,0);trace.append(dict(t=t,stmts=u['stmts'],parent=last.get(q),through=q))
 for q in u['qs']:end[q]=t+1;last[q]=i
q=max(end,key=end.get);j=last[q];chain=[]
while j is not None:chain.append(trace[j]);j=trace[j]['parent']
chain.reverse();(HERE/'fixed_critical_path.json').write_text(json.dumps(chain,indent=2));print('R',end[q]);print('\n'.join(f"{x['t']}: {' '.join(x['stmts'])}" for x in chain))

"""Attempt every remaining blocked prep with the same small move budget over the full tick window."""
from pass5 import *
cur=json.loads((R/'wide_history.json').read_text())[-1]['price'];st=Path(cur['stem']);c=M.read(st);gap=json.loads((R/'wide_r6_herald_coverage.json').read_text());es={};audit=[]
for row in gap:
 if row['available']:continue
 idx=next(i for i,o in enumerate(c['ops'])if o['t']==row['t']and M.unit(o).name==row['name']and M.unit(o).qs==(row['q'],));q=row['q'];old=M.ADJ[q];M.ADJ[q]=list(range(36))
 try:movesets=H5.joint_cpsat(c,idx,4)
 finally:M.ADJ[q]=old
 for moves in movesets:
  digest=hashlib.sha256(json.dumps(moves,sort_keys=True).encode()).hexdigest()[:12];i=f'herald:{row["name"]}{q}@{row["t"]}:wide{digest}'
  e=dict(id=i,fam='herald',q=q,t=row['t'],name=row['name'],moves=moves,solver='CP-SAT full tick window, <=8 moved CX/M, +/-2ticks');es[i]=e
 audit.append(dict(q=q,t=row['t'],name=row['name'],solutions=len(movesets)))
p=R/'wide_prep_menu.json';dump(p,es);dump(R/'wide_prep_coverage.json',audit);print(json.dumps(dict(event='wide_prep_solved',coverage=audit,proposals=len(es))),flush=True)
E.configure(R/('basis_'+cur['sha256']+'.json'),12);rs=batch(st,p,[[i]for i in es],'wide_prep',1,cur['loss']);dump(R/'wide_prep_outcome.json',dict(base=cur,audit=audit,rows=rs,best=choose(rs,cur)))

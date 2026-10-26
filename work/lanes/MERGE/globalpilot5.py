from pass5 import *
hist=json.loads((R/'wide_history.json').read_text());cur=hist[-1]['price'];E.configure(R/('basis_'+sha(cur['stem'])+'.json'),12)
rows=[]
for name,st in [('current',Path(cur['stem'])),('fast',H/'cand/merge5_live_8f4b236e8e56')]:
 c=M.read(st);m=M.op_of_bit(c,365);o=[o for o in M.ops_on(c,25)if o['t']<m['t']][-1];assert tuple(M.cx_qs(o))==(25,24)
 e=M.mk(fam='rev',a=25,b=24,t=o['t']);d,txt=apply(c,[e]);out=E.write_stem(txt,d['meta']['data_qubits']);r=price(out,dict(kind='GLOBAL residual reversal pilot',base=str(st),edit=e),cur['loss']);r.update(pilot=name,edits=[e['id']]);rows.append(r)
dump(R/'global_pilot_outcome.json',rows)
print(json.dumps(dict(event='global_pilot_complete',prices=[dict(name=r['pilot'],loss=r.get('loss'),acceptance=r.get('acceptance'),sha256=r['sha256'])for r in rows])),flush=True)

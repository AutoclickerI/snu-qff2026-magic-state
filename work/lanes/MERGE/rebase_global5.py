from wide5 import *
from judge5 import verify
hf=R/'wide_history.json';hist=json.loads(hf.read_text());assert len(hist)==3
cur=hist[-1]['price'];ancestor=hist[1];rows=[json.loads(l)for l in (R/'global_knapsack.jsonl').read_text().splitlines()]
best=cur
for r in sorted([r for r in rows if feasible(r)and r['loss']<cur['loss']],key=lambda r:r['loss']):
 j=verify(r['stem'])
 if j.get('gates_ok')and j['speed_ok']:best=dict(r,judge_1e6=j);break
assert cur['loss']-best['loss']>=1e-9
# Reconstruct primitive inverses on the exact ancestor used by this solver screen.
es=json.loads((R/'global_knapsack_menu.json').read_text());remaining=copy.deepcopy(ancestor['atoms']);c=M.read(ancestor['price']['stem']);selected=best['edits']
patches=[i for i in selected if es[i]['fam']=='patch']
if patches:
 c,_=apply(c,[es[i]for i in patches])
 for i in patches:remaining.pop(i)
for e in M.canon([es[i]for i in selected if es[i]['fam']!='patch']):
 before=copy.deepcopy(c);c=M.apply_edit(c,e);name='ejectglobal:'+e['id'];remaining[name]=patch_edit(name,c,before)
c,txt=M.normalized(M.fix(c));assert hashlib.sha256(txt.encode()).hexdigest()==best['sha256']
# A reviewable, exact transport delta binds the branch switch to the latest selected parent.
name='import5:funded_GLOBAL';old=M.read(cur['stem']);transport=patch_edit(name,old,c)
# Preserve operation order as part of the saved QASM identity, including simultaneous gates.
transport['delta'].update(remove=copy.deepcopy(old['ops']),add=copy.deepcopy(c['ops']),tail_remove=list(old['tail']),tail_add=list(c['tail']))
dump(R/'wide_r4_menu.json',{name:transport});dump(R/'wide_r4_all_atoms.json',hist[-1]['atoms'])
check,txt=apply(M.read(cur['stem']),[transport]);assert hashlib.sha256(txt.encode()).hexdigest()==best['sha256']
event=dict(round=4,before=cur,price=best,selected=[name],gain=cur['loss']-best['loss'],stop=False,atoms=remaining,rejected=[],phase='funded GLOBAL reversal branch selected after exact 34-proposal screen',original_recipe=selected,original_base=ancestor['price']['stem'])
dump(R/'wide_r4_outcome.json',event);hist.append(event);dump(hf,hist)
dest=H/'cand'/f'merge5_r4_{best["sha256"][:12]}';shutil.copyfile(Path(best['stem']).with_suffix('.qasm'),dest.with_suffix('.qasm'));dump(dest.with_suffix('.json'),dict(best,source=event['phase']))
update_status('running',best,hist,phase=event['phase']);print(json.dumps(dict(event='round_selected',round=4,loss=best['loss'],acceptance=best['acceptance'],gain=event['gain'],selected=selected)),flush=True)
print(json.dumps(dict(event='main_started',pid=os.getpid(),workers=20)),flush=True)
run(20)

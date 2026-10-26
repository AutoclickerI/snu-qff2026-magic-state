from pass4 import *
def promote(r,name):
 j=json.loads((R/f"judge_{r['sha256']}.json").read_text());assert feasible(r)and r['loss']<TAU-3e-8 and j['gates_ok']and j['speed_ok']
 st=Path(r['stem']);c=M.read(st);dest=H/'cand'/name;shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'))
 out=dict(r,tau=TAU,J_tau=r['acceptance']*(r['loss']-TAU),judge_1e6=j,cx=sum(M.unit(o).name=='CX'for o in c['ops']),native_depth=M.depth(c),source=dict(base='v37f',transport='PREPFREE M12/M25 and final POLISH',edits=r.get('edits',[])))
 dump(dest.with_suffix('.json'),out);return out
if __name__=='__main__':
 rows=[json.loads(x)for x in (R/'wide_r1_singles.jsonl').read_text().splitlines()];r=next(r for r in rows if r['edits']==['cx:11_17@32']);promote(r,'merge4_early')

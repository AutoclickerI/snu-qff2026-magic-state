"""Compose useful menu guards on the ST2 timing seed plus certified free timing."""
from ports35 import *
if __name__=='__main__':
    menu=json.loads((H/'v35_menu_snapshot.json').read_text());source=C.read(H/'h_v35a');base=C.read(H/'h_ST2_feedback_prep');rows=[];errors=[]
    indices=[84,69,70,85,122,120,121,103,88,73,13,14,15,16,117,118,133,135,136,137,138,141,142]
    for i in indices:
        if i>=len(menu['entries']):continue
        e=menu['entries'][i]
        if not e.get('ok') or 'lines' not in e:continue
        n=f'h_seed_guard_{i:03d}'
        try:
            c,proof=apply_menu(base,e,source);r=save(c,n,['h_ST2_feedback_prep',e['gadget'],proof]);r.update(family='seed_guard',menu_indices=[i],gadget=e['gadget']);rows.append(r)
        except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    # Pair combinations preserve both existing guards and are repriced whole.
    for indices in [[84,122],[69,122],[70,122],[84,103],[69,103],[122,103],[84,122,103],[69,122,103]]:
        n='h_seed_joint_'+'_'.join(map(str,indices));c=C.clone(base)
        try:
            proofs=[]
            for i in indices:c,p=apply_menu(c,menu['entries'][i],source);proofs.append(p)
            r=save(c,n,['h_ST2_feedback_prep','native menu combination',indices,proofs]);r.update(family='seed_guard_combination',menu_indices=indices);rows.append(r)
        except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    (H/'v35_combinations.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v35_combination_errors.json').write_text(json.dumps(errors,indent=2)+'\n');print(dict(built=len(rows),errors=errors))

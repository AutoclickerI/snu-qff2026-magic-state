from build30 import *
if __name__=='__main__':
    catalog=json.loads((H/'v30_edit_catalog.json').read_text());kinds=catalog['kinds'];base=C.read(H/'f_base');rows=[];errors=[]
    for n in range(len(kinds)+1):
        for ks in itertools.combinations(kinds,n):
            try:
                c=C.clone(base)
                for k in ks:c=edit30(c,k)
                if not ks:name='f_base'
                elif len(ks)==1:name='f_'+ks[0]
                else:name='f_c'+format(sum(1<<kinds.index(k) for k in ks),'03x')
                rows.append(save(c,name,list(ks)))
            except Exception as e:errors.append(dict(edits=ks,error=repr(e)))
    (H/'v30_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    (H/'v30_combination_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(dict(candidates=len(rows),errors=len(errors),examples=errors[:10]),flush=True)

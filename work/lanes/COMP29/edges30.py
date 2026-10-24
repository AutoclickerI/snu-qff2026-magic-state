from build30 import *
if __name__=='__main__':
    base=C.read(H/'f_timing_mz_5_12');rows=[]
    for c,d in M.readout_moves(base):
        if d.get('move')!='add_edge':continue
        name='f_edge_'+'_'.join(map(str,d['edge']))
        try:
            r=save(finish(c),name,['f_timing_mz_5_12',d]);r.update(screen(name));rows.append(r);print(name,r['total'],r['exp_minus_A1'],flush=True)
        except Exception as e:rows.append(dict(stem=name,error=repr(e)));print(name,repr(e),flush=True)
    (H/'v30_extra_edges.json').write_text(json.dumps(rows,indent=2)+'\n')

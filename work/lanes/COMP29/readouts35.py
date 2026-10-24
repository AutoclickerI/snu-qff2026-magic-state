"""Native v35b terminal readout and second-A-flag ports."""
from core35 import *
def remove_copy(base,q,helper):
    c=cancel_added(build(base,[(q,helper)]));assert c['meta']['terminal_cancellations']
    tr=terminal(c);b=tr[helper]['bit'];c=remove_check(c,b,'omit')
    ids=[i for i,u in enumerate(c['u']) if helper in u.qs]
    assert all(c['u'][i].qs==(helper,) and c['u'][i].name in ('RESET','RX') for i in ids)
    for i in reversed(ids):del c['u'][i];del c['t'][i]
    return c
def fit(base):
    targets={i:t for i,t in enumerate(base['t']) if t<=35}
    c=C.retime(C.clone(base),targets=targets,horizon=46)
    if c is None:return None
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order];return c
if __name__=='__main__':
    base=C.read(H/'h_prep_07');rows=[];errors=[]
    def emit(c,name,edits):
        r=save(c,name,edits);r['family']='readout';rows.append(r)
        if r['native_depth']>47:
            fitted=fit(c)
            if fitted is not None:
                rr=save(fitted,name+'_fit',edits+['retimed inside 47 layers']);rr['family']='readout';rows.append(rr)
            else:errors.append(dict(stem=name+'_fit',error='no 47-layer schedule with prefix through t35 fixed'))
    for edge in [(28,29),(29,28)]:emit(build(base,[edge]),f'h_Cadd_{edge[0]}_{edge[1]}',['h_prep_07','terminal C edge',edge])
    uncopy=remove_copy(remove_copy(base,28,34),29,35)
    emit(uncopy,'h_C_uncopy',['h_prep_07','remove two terminal C readout copies with detector repair'])
    for edge in [(28,29),(29,28)]:emit(build(uncopy,[edge]),f'h_Cuncopy_{edge[0]}_{edge[1]}',['h_C_uncopy','terminal C edge',edge])
    new=json.loads((H/'v35_decoder_enumeration.json').read_text())['networks']
    for i,r in enumerate(new):emit(build(base,r['network'],axes={q:'X' for q in r['free']},flags=r['free']),f'h_Anew_{i:02d}',['h_prep_07','second independent A flag',r])
    old=json.loads((H/'v34_decoder_enumeration.json').read_text())['networks']
    parent=cancel_added(build(base,[(14,15)]));assert parent['meta']['terminal_cancellations']
    for i,r in enumerate(old):
        try:emit(build(parent,r['network'],axes={q:'X' for q in r['free']},flags=r['free']),f'h_Aold_{i:02d}',['h_prep_07','undo terminal edge14->15; port prior second A flag',r])
        except Exception as e:errors.append(dict(stem=f'h_Aold_{i:02d}',error=repr(e)))
    (H/'v35_readouts.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v35_readout_errors.json').write_text(json.dumps(errors,indent=2)+'\n');print(dict(built=len(rows),errors=errors))

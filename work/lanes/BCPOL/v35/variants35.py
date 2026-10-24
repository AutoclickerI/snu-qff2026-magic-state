"""Known-zero instruments, state-equivalent encoder deletions, and flag carriers."""
from core35 import *

def valid_css(c):
    init=init_indices(c);rows={q:None for q in BC};piv=[q for q,i in init.items() if c['us'][i].name in ('MX','RX')]
    for i in sorted(range(len(c['us'])),key=lambda i:(c['ts'][i],i)):
        u=c['us'][i]
        if c['ts'][i]>44:break
        if i in init.values():
            q=u.qs[0];rows[q]=1<<piv.index(q) if q in piv else 0
        elif u.name=='CX' and set(u.qs)<=BC and all(rows[q] is not None for q in u.qs):
            a,b=edge(u);rows[b]^=rows[a]
        elif u.name=='MEASURE' and u.qs[0] in BC and rows[u.qs[0]] is not None:
            if rows[u.qs[0]]!=0:return None
    return rows

def generate():
    base=load();target=valid_css(base);rows=[];errors=[];ix=prep_indices(base)
    for i in ix:
        c=copy.deepcopy(base);del c['us'][i];del c['ts'][i]
        if valid_css(c)!=target:continue
        tag=f'delete_cx_{i}';emit(c,V/'finalists'/tag,dict(delete_encoder_index=i,deleted=base['us'][i].lines));rows.append(tag)
    # Move the existing deterministic q13 flag across control-CX operations,
    # a change absent from fixed per-wire timing-coordinate scans.
    fi=next(i for i,u in enumerate(base['us']) if u.name=='MEASURE' and bit(u)==263)
    for t in range(26,37):
        if t==base['ts'][fi] or any(13 in u.qs and base['ts'][i]==t for i,u in enumerate(base['us'])):continue
        c=copy.deepcopy(base);c['ts'][fi]=t
        if valid_css(c)!=target:continue
        tag=f'flag13_t{t}';emit(c,V/'finalists'/tag,dict(flag13_time=t));rows.append(tag)
    # q18 is adjacent to both C12 and C19. Preserve the helper record and
    # conjugate the comparison to whichever C output is copied.
    for early in (False,True):
        c=copy.deepcopy(base)
        for i,u in enumerate(c['us']):
            if u.name=='CX' and edge(u)==(19,18) and c['ts'][i]==45:c['us'][i]=S.Unit(['cx q[12],q[18];'],[])
            if u.name=='MEASURE' and bit(u)==21:c['ts'][i]=46
            if early and u.name=='MEASURE' and bit(u)==23:c['ts'][i]=45
        c['tail']=[l.replace('c[23] c[265]','c[21] c[265]') for l in c['tail']]
        tag='copy12_'+str(int(early));emit(c,V/'finalists'/tag,dict(flag_carrier=[12,18],C19_early=early));rows.append(tag)
    # Move a flag helper to the unused left neighbor; all native times retained.
    c=copy.deepcopy(base)
    for i,u in enumerate(c['us']):
        if c['ts'][i]>=44 and 31 in u.qs:c['us'][i]=S.Unit([s.replace('q[31]','q[24]') for s in u.lines],[])
    tag='copy25_to24';emit(c,V/'finalists'/tag,dict(flag_carrier=[25,24]));rows.append(tag)
    (V/'variants.selected.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))

if __name__=='__main__':generate()

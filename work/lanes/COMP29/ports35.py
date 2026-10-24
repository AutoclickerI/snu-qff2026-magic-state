"""Strict native replay of WAITPROT/ST2 menu edits, with record reallocation."""
from core35 import *

def bits(line):return set(map(int,re.findall(r'c\[(\d+)\]',line)))
def apply_menu(base,entry,source):
    c=C.clone(base);patch=entry['lines'];source_records={}
    for u,t in zip(source['u'],source['t']):
        if u.name in ('MX','MEASURE'):
            b=next(iter(bits(' '.join(u.lines))));source_records[b]=(u,t)
    oldbits=set(source_records);present={b for u in c['u'] for b in bits(' '.join(u.lines))};restored=[];changed=[]
    dependencies=set()
    for line in patch.get('detector_remove',[]):dependencies|=bits(line)&oldbits
    own_added_bits={b for item in patch.get('add',[]) for b in bits(' '.join(item['lines']))}
    for line in patch.get('detector_add',[]):dependencies|=(bits(line)&oldbits)-own_added_bits
    rb=entry.get('description',{}).get('readbit')
    if rb is not None:dependencies.add(rb)
    initial_missing=oldbits-present
    # A v35b-funded initialization may have replaced/omitted the old readout
    # that a menu gadget explicitly uses. Restore that dependency, then price it.
    for b in sorted(dependencies-present):
        u,t=source_records[b];assert known_zero(source,b)
        conflicts=[i for i,(v,tt) in enumerate(zip(c['u'],c['t'])) if tt==t and set(v.qs)&set(u.qs)]
        for i in reversed(conflicts):
            assert c['u'][i].qs==u.qs and c['u'][i].name in ('RESET','RX'),('dependency collision',b,t,c['u'][i].lines)
            del c['u'][i];del c['t'][i]
        c['u'].append(C.Unit(u.lines.copy()));c['t'].append(t);c['tail'].append(f'// DETECTOR c[{b}]');restored.append(b)
    newbits=sorted({b for item in patch.get('add',[]) for b in bits(' '.join(item['lines']))}-oldbits)
    remap={};fresh=C.bit(c)
    for b in newbits:
        item=next(item for item in patch['add'] if b in bits(' '.join(item['lines'])));u=C.Unit(item['lines']);t=item['t']
        matches=[v for v,tt in zip(c['u'],c['t']) if tt==t and v.qs==u.qs and v.name==u.name and v.name in ('MX','MEASURE')]
        if matches:remap[b]=next(iter(bits(' '.join(matches[0].lines))))
        else:remap[b]=fresh;fresh+=1
    rename=lambda s:re.sub(r'c\[(\d+)\]',lambda m:f'c[{remap.get(int(m[1]),int(m[1]))}]',s)
    added=[dict(t=x['t'],lines=[rename(s) for s in x['lines']]) for x in patch.get('add',[])]
    for item in patch.get('remove',[]):
        key=(item['t'],item['lines']);ids=[i for i,(u,t) in enumerate(zip(c['u'],c['t'])) if (t,u.lines)==key]
        if ids:
            assert len(ids)==1;i=ids[0];del c['u'][i];del c['t'][i];changed.append(['remove',item])
        else:
            u=C.Unit(item['lines']);fulfilled=any(C.Unit(x['lines']).qs==u.qs and any(tt==x['t'] and v.lines==x['lines'] for v,tt in zip(c['u'],c['t'])) for x in added)
            if u.name in ('MX','MEASURE') and bits(' '.join(u.lines))<=initial_missing:fulfilled=True
            assert fulfilled,('missing source unit',item)
    for item in added:
        if any(tt==item['t'] and u.lines==item['lines'] for u,tt in zip(c['u'],c['t'])):continue
        u=C.Unit(item['lines']);collisions=[i for i,(v,tt) in enumerate(zip(c['u'],c['t'])) if tt==item['t'] and set(v.qs)&set(u.qs)]
        for i in reversed(collisions):
            v=c['u'][i]
            assert u.qs==v.qs and ((u.name=='MEASURE' and v.name=='RESET') or (u.name=='MX' and v.name=='RX')),('added unit collision',item)
            changed.append(['replace initialization by checked readout',dict(t=c['t'][i],lines=v.lines)])
            del c['u'][i];del c['t'][i]
        c['u'].append(u);c['t'].append(item['t']);changed.append(['add',item])
    for line in patch.get('detector_remove',[]):
        bs=bits(rename(line));ids=[i for i,l in enumerate(c['tail']) if bits(l)==bs]
        if not ids and bits(line)<=initial_missing:continue
        assert ids,('missing source detector',line)
        del c['tail'][ids[0]];changed.append(['detector_remove',line])
    for line in patch.get('detector_add',[]):
        line=rename(line)
        if any(bits(line)==bits(old) for old in c['tail']):continue
        c['tail'].append(line);changed.append(['detector_add',line])
    order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i] for i in order];c['t']=[c['t'][i] for i in order]
    return c,dict(changes=changed,restored_check_dependencies=restored,record_map=remap)

if __name__=='__main__':
    menu=json.loads((ROOT/'work/lanes/WAITPROT/menu_v35a.json').read_text());source=C.read(H/'h_v35a');base=C.read(H/'h_prep_07');rows=[];errors=[]
    for i,entry in enumerate(menu['entries']):
        if not entry.get('ok') or 'lines' not in entry:continue
        name=f'h_port_{i:03d}'
        try:
            c,proof=apply_menu(base,entry,source)
            if not proof['changes'] and not proof['restored_check_dependencies']:
                errors.append(dict(stem=name,gadget=entry['gadget'],status='already present'));continue
            r=save(c,name,['h_prep_07',entry['gadget'],proof]);r.update(family='guard_port',menu_index=i,gadget=entry['gadget'],port=proof);rows.append(r)
        except Exception as e:errors.append(dict(stem=name,gadget=entry['gadget'],error=repr(e)))
    (H/'v35_menu_snapshot.json').write_text(json.dumps(menu,indent=2)+'\n');(H/'v35_ports.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v35_port_errors.json').write_text(json.dumps(errors,indent=2)+'\n');print(dict(built=len(rows),rejected=len(errors)));print(errors)

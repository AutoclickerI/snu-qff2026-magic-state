"""PRESYN's blue X/XZ stabilizer check (partial_checks.py + blue_reuse.py) rebuilt on v23h_c2c9."""
from core import *
from build import insert_block
from partial_checks import tile
from blue_reuse import replace_encoder


def main():
    base = provenance(read(BASE))
    out = []
    for typ in ('x', 'xz'):
        c = insert_block(base, tile(1, typ), 129)
        c = placement(c, mode='alap')
        save(c, f'partial_1_{typ}_129', f'extra tile mask 1, {typ} stabilizers at boundary 129 (v23h_c2c9 base)')
        for enc in ('19', '21'):
            c = read(OUT / f'partial_1_{typ}_129')
            c['tags'] = c['meta']['component_tags']
            if enc != '19':
                c = replace_encoder(c, 'enc21_joint_d7_rigid')
            for rev in (False, True):
                v = copy.deepcopy(c)
                if rev:
                    for i, (u, tag) in enumerate(zip(v['u'], v['tags'])):
                        if tag != 'check_extra':
                            continue
                        if u.name == 'RX' and u.qs == (1,):
                            v['u'][i] = Unit(['reset q[1];'])
                        elif u.name == 'RESET' and u.qs == (2,):
                            v['u'][i] = Unit(['reset q[2];', 'h q[2];'])
                        elif u.lines == ['cx q[1],q[2];']:
                            v['u'][i] = Unit(['cx q[2],q[1];'])
                        elif u.last_is_measure and u.qs in ((1,), (2,)):
                            m = u.lines[1] if u.name == 'MX' else u.lines[0]
                            v['u'][i] = Unit(([f'h q[{u.qs[0]}];'] if u.qs == (2,) else []) + [m])
                name = f'blue_{typ}_e{enc}_r{int(rev)}'
                try:
                    v = placement(v, rigid=True)
                    save(v, name, f'blue {typ} check, {enc}-CX encoder, reverse Bell={rev} (v23h_c2c9 base)')
                    out.append(name)
                    print('built', name, v['meta']['R'], v['meta']['cx'], flush=True)
                except Exception as e:
                    print(name, 'BUILD ERROR', e, flush=True)
    (OUT / 'port23_manifest.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()

"""Acceptance-only funding on a plan: prep delays, measure-init removals, unchecked preps."""
from lib import *


def uncheck(c, b):
    """Prep RX/RESET followed by its MX/MEASURE check `b`: drop the check, prepare at the check's tick."""
    c = copy.deepcopy(c)
    o = op_of_bit(c, b)
    u = unit(o)
    q = u.qs[0]
    s = seq(c, q)
    i = s.index(o)
    p = s[i - 1]
    assert unit(p).name in ('RX', 'RESET'), (b, p)
    c['ops'].remove(p)
    o['lines'] = [f'reset q[{q}];'] + ([f'h q[{q}];'] if u.name == 'MX' else [])
    drop_bit_from_tail(c, b)
    return fix(c)


def fund(c, omit=(), reset=(), unchecked=(), delay=True):
    for b in unchecked:
        c = uncheck(c, b)
    for b in omit:
        c = remove_check(c, b, 'omit')
    for b in reset:
        c = remove_check(c, b, 'reset')
    if delay:
        c = delay_preps(c, prep_options(c))
    return c


MI = (39, 40, 42, 46, 271)
UN = (181, 182, 184, 187, 188)

if __name__ == '__main__':
    c = read(C / 'v36c')
    V = {
        'F0': dict(),
        'F1': dict(omit=MI, reset=(43,)),
        'F2': dict(omit=MI, reset=(43,), unchecked=UN),
        'F3': dict(omit=MI + (257,), reset=(43,), unchecked=UN),
        'F4': dict(omit=MI, reset=(43,), unchecked=UN + (183, 186)),
        'F5': dict(omit=MI + (257,), reset=(43,), unchecked=UN + (183, 186)),
        'F6': dict(omit=MI + (257,), reset=(43,), unchecked=UN + (183, 186, 185)),
    }
    for k, v in V.items():
        save(fund(c, **v), k, dict(kind='fund', **{a: list(b) for a, b in v.items()}))
        print(k, 'ok')

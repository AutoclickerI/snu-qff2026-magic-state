"""Optimistic bound for guarding resource idles: all-orders with idle noise removed on B/C cells (ticks lo..hi),
and on single (q, t) slots.  usage: idlebound.py <stem> <lo> <hi> [q:t ...]"""
import sys, json, time
import abl
BC = set(abl.chan.ROLES['B'] + abl.chan.ROLES['C'])

def idle_on(qset, lo, hi):
    def pred(md):
        return md['kind'] == 'idle' and set(md['qs']) <= qset and md['t0'] + md['n'] - 1 >= lo and md['t0'] <= hi
    return pred

if __name__ == '__main__':
    stem, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    t = time.time()
    ctx = abl.Ctx(stem)
    idl = [md for md in ctx.meta if md['kind'] == 'idle' and set(md['qs']) <= BC and md['t0'] + md['n'] - 1 >= lo and md['t0'] <= hi]
    print(json.dumps(sorted({(md['qs'][0], md['t0'], md['n']) for md in idl})), flush=True)
    specs = {'base': abl.ALL, 'bc_idle_%d_%d' % (lo, hi): abl.drop(idle_on(BC, lo, hi))}
    for a in sys.argv[4:]:
        q, tt = map(int, a.split(':'))
        specs['slot_%d_%d' % (q, tt)] = abl.drop(idle_on({q}, tt, tt))
    print(json.dumps(ctx.many(specs)), round(time.time() - t, 1))

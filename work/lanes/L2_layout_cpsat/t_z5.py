import sys, collections
sys.path.insert(0, '.')
import l2model as L
m = L.variant('v6+z42')
errs = collections.Counter(); nok = 0; tot = 0
for i in range(30):
    g = L.Gen(m, 9, parity=(i % 2 == 0))
    for a, o in g.solutions(20, 5, i, rand_obj=5):
        tot += 1
        try:
            m.proxy(a, o); nok += 1
        except Exception as e:
            s = str(e)
            errs['det' if 'detectors' in s else 'obs' if 'observ' in s else s[:60]] += 1
print('tot', tot, 'valid', nok, errs)

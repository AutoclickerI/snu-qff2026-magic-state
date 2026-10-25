import importlib.util
import json
import math
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('threshold', LANE/'patched/work/race_threshold.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def main():
    boundaries = probes = 0
    for exponent in range(-7, 1):
        for mantissa in range(100, 1000):
            key = float(f'{mantissa / 100:.2f}e{exponent}')
            for cx in (326, 327, 328):
                for earlier in (False, True):
                    cut = m.first_losing(key, 327, cx, earlier=earlier)
                    boundaries += 1
                    xs = [cut]
                    lo = hi = cut
                    for _ in range(7):
                        lo = math.nextafter(lo, 0.)
                        hi = math.nextafter(hi, math.inf)
                        xs += [lo, hi]
                    for x in xs:
                        # Independent tuple expression, including official numeric formatter.
                        oracle = (float(f'{x:.3g}'), cx, 0 if earlier else 2) < (key, 327, 1)
                        assert (x < cut) == oracle, (key, cx, earlier, x.hex(), cut.hex())
                        probes += 1
                    assert float(f'{math.nextafter(cut, 0):.3g}') <= key
    a = m.first_losing(3.53e-5, 327, 326)
    b = m.first_losing(1e-5, 327, 327)
    assert 3.534e-5 < a
    assert 9.99e-6 < b
    # Subnormal/near-overflow search, where decimal arithmetic is especially unsafe.
    for key in (float.fromhex('0x0.0000000000001p-1022'), 1e-300, 1e300, 1.79e308):
        for cx in (326, 327, 328):
            cut = m.first_losing(key, 327, cx)
            assert m.wins(math.nextafter(cut, 0), cx, key, 327)
            assert not m.wins(cut, cx, key, 327)
    receipt = dict(status='PASS', keys=7200, boundaries=boundaries, neighboring_doubles=probes,
                   counterexample_A=dict(cut=a, hex=a.hex()),
                   counterexample_B=dict(cut=b, hex=b.hex()),
                   incumbent_cuts={str(cx): m.first_losing(3.53e-5,327,cx) for cx in (326,327,328)},
                   formatter='float(format(score, ".3g")); tprep/check.py:82')
    (LANE/'receipts/01_threshold.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()

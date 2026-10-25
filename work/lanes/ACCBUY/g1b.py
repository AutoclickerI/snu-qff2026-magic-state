import sys, itertools
sys.argv = sys.argv[:1]
exec(open('g1.py').read().split("variant('g4_3_37_39'")[0])
for pat in itertools.product((3, 10), repeat=3):
    seq = list(zip((37, 38, 39), pat))
    if pat in ((3, 3, 3), (3, 10, 3)):
        continue
    try:
        variant('g4p_' + '_'.join(map(str, pat)), seq)
    except ValueError as e:
        print('skip', pat)
variant('g4p_rm_only', [], rt=37)

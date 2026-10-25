import sys, itertools
sys.argv = sys.argv[:1]
exec(open('g1.py').read().split("variant('g4_3_37_39'")[0])
for pat in itertools.product((3, 10, 5), (3, 10, 5), (3, 5)):
    seq = list(zip((37, 38, 39), pat))
    try:
        variant('g4q_' + '_'.join(map(str, pat)), seq)
    except ValueError as e:
        print('skip', pat)

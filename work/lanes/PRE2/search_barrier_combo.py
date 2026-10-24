import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_candidates as bc
from search_barriers import pattern_prefix

HERE = Path(__file__).resolve().parent
_, n = pattern_prefix(set())
for i in range(n - 2):
    name = f'compact_dropcombo_{i:02d}_31_32'
    p = bc.write_prefix(name, pattern_prefix({i, n - 2, n - 1})[0])
    bc.merge(name, p, compact=True)
    bc.measure_init(name)
print('generated', n - 2)

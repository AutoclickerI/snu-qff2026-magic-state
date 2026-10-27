"""All-orders comparison of four distinct placements tied at pair order."""
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
from axis_echo import exact

HERE=Path(__file__).resolve().parent
NAMES=[
    'spacetime_c1_t38q12_t39q5_r1',
    'spacetime_c1_t39q5_t41q18_r0',
    'spacetime_c1_t39q5_t45q12_r0',
    'spacetime_c1_t39q5_t45q12_r1',
]


def score(row):
    result=exact(row['stem'])
    Path(row['stem']).with_suffix('.exact.json').write_text(json.dumps(result,indent=2)+'\n')
    return dict(**row,exact=result)


def main():
    original=json.loads((HERE/'spacetime_phase/results.json').read_text())['results']
    jobs=[next(r for r in original if r['name']==name) for name in NAMES]
    assert all(r['raw']['ok'] and r['c1']<1e-10 for r in jobs)
    rows=[]
    with ProcessPoolExecutor(max_workers=2) as pool:
        for row in pool.map(score,jobs):
            rows.append(row)
            (HERE/'spacetime_phase/exact_results.json').write_text(json.dumps(dict(
                reason='Resolve all-orders effects of different phase times and signs with identical c2.',
                results=rows),indent=2)+'\n')
            print(json.dumps(dict(name=row['name'],c2=row['c2'],loss=row['exact']['loss'],
                                 acceptance=row['exact']['acceptance'])),flush=True)


if __name__=='__main__':main()

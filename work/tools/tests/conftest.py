import os
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parents[1]
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
# pytest scratch files must stay within the authorized subtree.
(HERE / 'cache' / 'tmp').mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(HERE / 'cache' / 'tmp')


def pytest_configure(config):
    if config.option.basetemp is None:
        config.option.basetemp = str(HERE / 'cache' / 'pytest-tmp')

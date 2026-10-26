"""Shared Steane preparation tools. Heavy numerical imports happen only on cache misses."""
import os
import sys

for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'
sys.dont_write_bytecode = True

from .stems import identity, write_stem
from .version import EVALUATOR_VERSION
from .pricing import InvalidCircuit, price
from .validity import raw_check, judge_check, validate
from .policy import expected_key_delta, is_finalist

__all__ = ['identity', 'write_stem', 'EVALUATOR_VERSION', 'price', 'InvalidCircuit',
           'raw_check', 'judge_check', 'validate', 'expected_key_delta', 'is_finalist']

import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v
names={'meas_42_omit','meas_39_omit','meas_40_omit','meas_41_omit','meas_43_reset','meas_45_reset','meas_46_reset','meas_185_reset','meas_186_reset','meas_187_reset','meas_188_reset','meas_182_reset','meas_181_reset','meas_183_reset','meas_184_reset'}
v.a.batch((x for x in v.physical()if x[0]in names or x[0].startswith('guard_')),'fasttrack',5)

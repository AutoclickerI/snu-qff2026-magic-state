"""On q6c_g1 (q6 Z-guard + q14 echo extension): q21's 2-CX Z-echo on q20 (33, 34; M 36) re-timed or turned into a
Z-guard now that q20 idles at 35; leave-one-out of INTEG's pairR_14_20_40 in the new context."""
import sys
sys.path.insert(0, '.')
from redit import *
from build_q6c import base_g, q14ext, BASE


def best():
    return q14ext(base_g())


V = {}
c = best(); rm(c, 34, 'cx q[20],q[21]'); add(c, 35, ['cx q[20],q[21];']); V['z_a'] = c
c = best(); rm(c, 33, 'cx q[20],q[21]'); rm(c, 34, 'cx q[20],q[21]')
for t in (33, 34, 35):
    add(c, t, ['cx q[21],q[20];'])
V['z_b'] = c
c = best(); rm(c, 40, 'cx q[20],q[14]'); rm(c, 41, 'cx q[20],q[14]'); V['z_e'] = c
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_z ' + k))
print(list(V))

# leave-one-out around z_a (q6 Z-guard + q1-q0 pair + q14 echo extension + q21 echo end 34->35)
from build_q6c import S
from build_q6 import strip_q6, zguard


def shift21(c):
    rm(c, 34, 'cx q[20],q[21]'); add(c, 35, ['cx q[20],q[21];'])
    return c


L = {}
L['loo_noq6'] = shift21(q14ext(load(BASE)))                      # v36d + q14ext + q21 shift
c = strip_q6(); rm(c, 41, 'reset q[6]')
for t in (35, 36):
    rm(c, t, 'cx q[1],q[7]')
L['loo_nopair'] = shift21(q14ext(zguard(c, 6, S('32=7,33=0,34=7,35=7,36=7,37=7,38=7,39=7,40=7'), 31, 41)))
c = strip_q6(); rm(c, 41, 'reset q[6]')
L['loo_pair17'] = shift21(q14ext(zguard(c, 6, S('32=7,33=0,34=7,35=0,36=0,37=7,38=7,39=7,40=7'), 31, 41)))
for k, c in L.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_z ' + k))
print(list(L))

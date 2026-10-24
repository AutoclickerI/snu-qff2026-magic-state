"""On nom_7 (z_a with q6's guard unread, guarding q7 through 41): B cells guarding their data up to the B role
without a readout (their guard X faults enter B and are caught by the B/C detectors).
n1: q11 (B from 34) adds CX 11->10 at 32 to its 30-31 CX pair (a |0> control = guard) and drops its M at 33 (c269).
n2: q13 (B from 34): its Z-echo on q7 (CX 7->13 at 27/31, M 32, R 33) and q12's X-echo on q13 (CX 12->13 at 28/30)
    become a Z-guard CX 13->7 at 27, 28, 31 with no readout."""
import sys
sys.path.insert(0, '.')
from redit import *
from build_q6c import BASE


def n1(c):
    add(c, 32, ['cx q[11],q[10];'])
    rm(c, 33, 'measure q[11] -> c[269]'); rmdet(c, 269)
    return c


def n2(c):
    rm(c, 27, 'cx q[7],q[13]'); rm(c, 31, 'cx q[7],q[13]')
    rm(c, 28, 'cx q[12],q[13]'); rm(c, 30, 'cx q[12],q[13]')
    rm(c, 32, 'measure q[13] -> c[280]'); rmdet(c, 280); rm(c, 33, 'reset q[13]')
    for t in (27, 28, 31):
        add(c, t, ['cx q[13],q[7];'])
    return c


V = {'n1': n1(load('c/nom_7')), 'n2': n2(load('c/nom_7')), 'n12': n2(n1(load('c/nom_7')))}
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_n ' + k))
print(list(V))

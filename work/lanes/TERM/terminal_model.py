"""Exact second-order data-side terminal cost from per-qubit undetected Pauli rates.

Each data qubit i carries independent undetected single-qubit Pauli rates r_i = (X, Y, Z) in units of p/15.
At second order the judge's loss is sum_{i<j} r_i^T L r_j p^2 / 225, with L(P,Q) the logical loss of P_i Q_j
after ideal decoding (X/Y-type flip 1/2, Z-type flip 1; X_i Z_j is corrected). Same-qubit pairs are corrected.
Validated against ARCH's exact2 decomposition (Steane round 28.84 p^2) and TERM's exact2 run of the B-first
template (round-only 2.5573e-5).
"""
import itertools, json
L = {('X','X'):.5,('X','Y'):.5,('X','Z'):0,('Y','X'):.5,('Y','Y'):.5,('Y','Z'):1,('Z','X'):0,('Z','Y'):1,('Z','Z'):1}
def cost(rs):
    tot=0
    for i,j in itertools.combinations(range(len(rs)),2):
        for a,P in enumerate('XYZ'):
            for b,Q in enumerate('XYZ'):
                tot+=rs[i][a]*rs[j][b]*L[P,Q]
    return tot/225   # in units of p^2
def v(x=0,y=0,z=0): return (x,y,z)
def add(*vs): return tuple(sum(c) for c in zip(*vs))
IDLE=v(5,5,5)          # final idle D1(p): p/3 each
LAST=v(2,2,2)          # last data CX, partner measured at T: (I|M) x (X,Y,Z) = 2/15 each
rows=[]
def row(name,rs,mech): rows.append(dict(template=name,second_order_p2=round(cost(rs),4),mechanism=mech)); 
U=lambda r:[r]*7
row('final idle only (proved-floor tail)',U(IDLE),'last tick D1(p) on 7 outputs')
row('class floor: CX at T-1 with measured partner + final idle',U(add(IDLE,LAST)),'(I|M)xP survivors of the last CX are invisible to the partner')
row('+ T-2 CX leak 1/15 X (T-2 partner fully checked afterwards)',U(add(IDLE,LAST,v(1))),'(I_P,X_D) of the T-2 CX survives a Z-check at T-1')
row('+ T-1 partner prep leak 1/15 X (two-check class floor)',U(add(IDLE,LAST,v(2))),'(X_B,I_Q) of B\'s last pre-use CX propagates through B->D')
row('Steane round, full A X-parity coverage after D->A',U(add(IDLE,LAST,v(1),v(2))),'D->A leak 1/15, literal-zero C leaves B leak 2/15')
row('Steane round (ARCH grid-free)',U(add(IDLE,LAST,v(2),v(2))),'D->A leak 2/15 X (A read in Z, Z_A invisible), B->C leak 2/15 X')
row('B-first template, A perfect (brief template)',U(add(IDLE,LAST,v(z=1))),'B fully checked after B->D: only (I_B,Z_D) leaks; A Z errors excluded')
# v36c terminal: data order [0,20,7,10,3,22,21]; flag X8X9X15 covers D7,D10,D21 D->A leaks; D10,D21 idle at 44 (X-only p/3)
v36=[add(IDLE,LAST,v(2),v(2)), add(IDLE,LAST,v(2),v(2)), add(IDLE,LAST,v(1),v(2)), add(IDLE,LAST,v(1),v(2),v(5)),
     add(IDLE,LAST,v(2),v(2)), add(IDLE,LAST,v(2),v(2)), add(IDLE,LAST,v(1),v(2),v(5))]
row('v36c terminal (flag on D7,D10,D21; D10,D21 idle at 44)',v36,'model of the actual schedule')
nogap=[add(IDLE,LAST,v(2),v(2))]*7
row('v36c without flag, no gap (all D->A at 44)',nogap,'reference for the flag/gap trade')
for r in rows: print(json.dumps(r))
json.dump(rows,open('terminal_model.json','w'),indent=1)

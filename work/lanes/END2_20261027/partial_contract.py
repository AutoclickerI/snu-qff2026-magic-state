"""Exact joint CSS resource for the incumbent six-square/one-tree ending."""
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
D = [6, 20, 19, 10, 2, 22, 16]
A = [7, 21, 18, 4, 8, 23, 17]
B = [12, 26, 25, 11, 3, 28, 15]
C = [13, 27, 24, 5, 9, 29, 14]
CELLS = A + B + C
HELPERS = sorted(set(range(36)) - set(D + CELLS))
STEANE_X = [85, 102, 120]
A_X = STEANE_X + [7]
C_X = [7, 25, 42, 64]
ROWS = [set(A[i] for i in range(7) if mask >> i & 1) for mask in A_X]
ROWS += [set(q for i in range(7) if mask >> i & 1 for q in (B[i], C[i])) for mask in STEANE_X]
ROWS += [set(C[i] for i in range(7) if mask >> i & 1) for mask in C_X]
COLS = {q: sum(1 << j for j, row in enumerate(ROWS) if q in row) for q in range(36) if q not in D}


def terminal(roles=None, square_mask=63):
    """(kind, qubits, relative tick, record index or None)."""
    dd,aa,bb,cc=(D,A,B,C) if roles is None else (roles[k] for k in ('D','A','B','C'))
    ops = [('CX', (d,a), 0, None) for d,a in zip(dd,aa)]
    ops += [('CX', (b,c), 0, None) for b,c in zip(bb,cc)]
    ops += [('CX', (b,d), 1, None) for b,d in zip(bb,dd)]
    ops += [('CX', (cc[i],aa[i]), 1, None) for i in range(7) if square_mask>>i&1]
    for offset, block, kind in [(0,aa,'M'),(7,bb,'MX'),(14,cc,'MX')]:
        ops += [(kind, (q,), 2, offset+i) for i,q in enumerate(block)]
    return ops


DETECTORS = [[1,2,3,4],[0,2,3,5],[0,1,3,6],
             [8,9,10,11],[7,9,10,12],[7,8,10,13],
             [14,15,16],[14,17,18],[15,17,19],[20]]


def fault_signature(q, pauli, helpers=(), roles=None, square_mask=63, detectors=None):
    """CSS output class (syndrome3, parity1) and terminal check flips.

    Helper cells finish at zero and may be measured in Z at the first terminal
    tick. Their literal checks augment X-fault detection only.
    """
    x = 1 << q if pauli == 'X' else 0
    z = 1 << q if pauli == 'Z' else 0
    flips = 0
    dd=D if roles is None else roles['D']
    for kind, qs, _, bit in terminal(roles,square_mask):
        if kind == 'CX':
            a,b = qs
            if x >> a & 1:
                x ^= 1 << b
            if z >> b & 1:
                z ^= 1 << a
        elif (kind == 'M' and x >> qs[0] & 1) or (kind == 'MX' and z >> qs[0] & 1):
            flips ^= 1 << bit
    err = x if pauli == 'X' else z
    pattern = sum((err >> d & 1) << i for i,d in enumerate(dd))
    out = sum(((pattern & row).bit_count() & 1) << j for j,row in enumerate(STEANE_X))
    out |= (pattern.bit_count() & 1) << 3
    dets=DETECTORS if detectors is None else detectors
    rows = dets[:3] if pauli == 'X' else dets[3:]
    out |= sum((sum(flips >> b & 1 for b in row) & 1) << (4+j) for j,row in enumerate(rows))
    if pauli == 'X' and q in helpers:
        out |= 1 << (7 + list(helpers).index(q))
    return out


def make_contract(mask=0, late_c14=False):
    """Pure namespace factory for the 64 orientations of the same six tiles.

    Each low bit swaps A_i/B_i on square i. The seventh tree stays fixed.
    With late_c14, ROWS/COLS describe rank-ten preparation ending with q14
    zero; a final RX14 restores the independent plus factor. Its pre-reset
    endpoint fault signatures are zero because that reset erases old faults.
    """
    if not 0<=mask<64:
        raise ValueError(mask)
    aa,bb=list(A),list(B)
    for i in range(6):
        if mask>>i&1:aa[i],bb[i]=bb[i],aa[i]
    roles=dict(D=list(D),A=aa,B=bb,C=list(C))
    full_rows=[{aa[i] for i in range(7) if g>>i&1} for g in A_X]
    full_rows += [{q for i in range(7) if g>>i&1 for q in (bb[i],C[i])} for g in STEANE_X]
    full_rows += [{C[i] for i in range(7) if g>>i&1} for g in C_X]
    rows=[r-{14} for r in full_rows[:-1]] if late_c14 else full_rows
    cols={q:sum(1<<j for j,row in enumerate(rows) if q in row) for q in range(36) if q not in D}
    full_cols={q:sum(1<<j for j,row in enumerate(full_rows) if q in row) for q in cols}
    def signature(q,pauli,helpers=()):
        return 0 if late_c14 and q==14 else fault_signature(q,pauli,helpers,roles)
    return SimpleNamespace(D=list(D),A=aa,B=bb,C=list(C),CELLS=aa+bb+list(C),HELPERS=list(HELPERS),
        COLS=cols,ROWS=rows,FULL_COLS=full_cols,FULL_ROWS=full_rows,DETECTORS=DETECTORS,
        orientation=mask,rank=len(rows),late_c14=late_c14,late_plus=[14] if late_c14 else [],roles=roles,
        kind='six_square',square_mask=63,post_h=[],dual_a=False,
        terminal=lambda:terminal(roles),fault_signature=signature)


def make_partial_contract(roles,square_mask,late_free=True,dual_a=False):
    """Compensate any missing C→A coordinates using ker(H diag(E)) on C."""
    dd,aa,bb,cc=[list(roles[k]) for k in ('D','A','B','C')]
    roles=dict(D=dd,A=aa,B=bb,C=cc)
    piv={};short=[]
    for v in range(1,128):
        if v&~square_mask or any((v&g).bit_count()%2 for g in STEANE_X):continue
        w=v
        while w:
            k=w.bit_length()-1
            if k not in piv:piv[k]=w;short.append(v);break
            w^=piv[k]
    free=[i for i in range(7) if not(square_mask>>i&1)]
    crows=short+[1<<i for i in free]
    arows=STEANE_X if dual_a else A_X
    full_rows=[{aa[i] for i in range(7) if g>>i&1} for g in arows]
    full_rows += [{q for i in range(7) if g>>i&1 for q in (bb[i],cc[i])} for g in STEANE_X]
    full_rows += [{cc[i] for i in range(7) if g>>i&1} for g in crows]
    late=[cc[i] for i in free] if late_free else []
    rows=[r-set(late) for r in full_rows[:len(arows)+3+len(short)]] if late_free else full_rows
    cells=aa+bb+cc;helpers=sorted(set(range(36))-set(dd+cells))
    cols={q:sum(1<<j for j,row in enumerate(rows) if q in row) for q in range(36) if q not in dd}
    full_cols={q:sum(1<<j for j,row in enumerate(full_rows) if q in row) for q in cols}
    dets=[[i for i in range(7) if g>>i&1] for g in STEANE_X]
    dets += [[7+i for i in range(7) if g>>i&1] for g in STEANE_X]
    dets += [[14+i for i in range(7) if g>>i&1] for g in crows]
    def signature(q,pauli,flags=()):
        if dual_a:raise ValueError('Dual A with cross-block bridges requires full Pauli signatures; use state synthesis and exact full-fault audit.')
        return 0 if q in late else fault_signature(q,pauli,flags,roles,square_mask,dets)
    return SimpleNamespace(D=dd,A=aa,B=bb,C=cc,CELLS=cells,HELPERS=helpers,ROWS=rows,COLS=cols,
        FULL_ROWS=full_rows,FULL_COLS=full_cols,DETECTORS=dets,orientation=None,rank=len(rows),
        late_c14=False,late_plus=late,roles=roles,kind='partial_square',square_mask=square_mask,
        C_rows=crows,C_short_rows=short,dual_a=dual_a,post_h=aa if dual_a else [],
        terminal=lambda:terminal(roles,square_mask),fault_signature=signature)


def make_four_square_contract(late_free=True,dual_a=False):
    pc=make_partial_contract(dict(D=D,A=[7,14,18,4,8,21,15],B=[12,26,25,11,3,28,17],
                                  C=[13,27,24,5,9,29,23]),29,late_free,dual_a)
    pc.kind='four_square'
    return pc


def save():
    out = dict(D=D, A=A, B=B, C=C, helpers=HELPERS,
        rank=len(ROWS), rows=[sorted(row) for row in ROWS],
        physical_row_masks=[sum(1 << q for q in row) for row in ROWS],
        columns=COLS, detectors=DETECTORS,
        state='Equal positive superposition over span(rows), all helper cells zero.',
        logical_contract='A plusL; B zeroL; C span(012,034,135,6); conjugate B/C by transversal B->C.',
        terminal=terminal())
    (HERE/'partial_resource_contract.json').write_text(json.dumps(out,indent=2)+'\n')
    return out


if __name__ == '__main__':
    print(json.dumps(save(),indent=2))

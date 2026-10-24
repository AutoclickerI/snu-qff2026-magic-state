"""Layout bound for every translation class of v36c's kept prefix (6 translations cover all 48 embeddings)."""
import sys, json
sys.path.insert(0, '.')
import layout as L
S0, R0, REL0 = dict(L.START), dict(L.READY), dict(L.REL)
pref_cells = [c for c, v in REL0.items() if v > 0]
for dr in range(3):
    for dc in range(2):
        mv = lambda c: c + 6 * dr + dc
        if any((c % 6) + dc > 5 or (c // 6) + dr > 5 for c in pref_cells):
            print(dr, dc, 'does not fit'); continue
        L.START.clear(); L.START.update({i: mv(c) for i, c in S0.items()})
        L.READY.clear(); L.READY.update(R0)
        L.REL.clear(); L.REL.update({q: 0 for q in range(36)})
        for c in pref_cells:
            L.REL[mv(c)] = REL0[c]
        for A_LEN in (5, 4):
            o = L.solve(A_LEN=A_LEN, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3)
            print(dr, dc, A_LEN, o.get('status'), o.get('R'), o.get('hops'), o.get('D'), flush=True)

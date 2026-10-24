import json
from build import BASE, DATA, build
from tprep.exact import verify
from tprep.grid import SUPPORTS
from tprep.parse import declarations

# The same three-block verified Steane round used by the RM_PROTO lane, with
# the DK output block as data.  The previously measured RM15 wires are reset
# and reused; 35 of the 36 chip wires are active at peak.
ENC = [[(0, 2), (1, 5), (3, 6)],
       [(0, 4), (1, 6), (3, 5)],
       [(0, 6), (1, 2), (3, 4)]]


def append_round(c, reverse=False):
    c.stage('verified_steane_round')
    A = list(range(1, 8))
    B = list(range(8, 15))
    C = [15, 16, 17, 18, 19, 27, 28]
    for block, dual in [(A, True), (B, False), (C, False)]:
        for i, q in enumerate(block):
            c.reset(q, 'X' if (i not in [0, 1, 3]) == dual else 'Z')
        for layer in ENC:
            for p, q in layer:
                c.gate('cx', *((block[q], block[p]) if dual else (block[p], block[q])))

    c.barrier(A + B + C + list(range(20, 27)))
    # Verify B's X faults in C immediately before B touches data.  Then A's
    # Z check and B's X check are the two final data couplings.
    for b, cc in zip(B, C):
        c.gate('cx', b, cc)
    data_paper_order = [x + 1 for x in DATA]  # physical labels [24,22,23,20,25,21,26]
    if reverse:
        for b, d in zip(B, data_paper_order):
            c.gate('cx', b, d)
        rb = [c.meas(b, 'X') for b in B]
        for d, a in zip(data_paper_order, A):
            c.gate('cx', d, a)
        ra = [c.meas(a) for a in A]
    else:
        for d, a in zip(data_paper_order, A):
            c.gate('cx', d, a)
        ra = [c.meas(a) for a in A]
        for b, d in zip(B, data_paper_order):
            c.gate('cx', b, d)
        rb = [c.meas(b, 'X') for b in B]
    rc = [c.meas(cc) for cc in C]
    for rec in [ra, rb, rc]:
        for g in SUPPORTS:
            c.dets.append([rec[i] for i in sorted(g)])
    c.dets.append(rc)


def main():
    c = build(barriers=True)
    append_round(c)
    _, stim, info = c.write(
        'dk_steane',
        dict(protocol='Daguerre-Kim two-block switch plus verified Steane output round',
             source='arXiv:2410.07327v3 Figs. 3-7; RM_PROTO verified three-block round',
             status='grid-free adjacency bypass only'))
    frame, post = declarations(stim)
    ex = verify(stim, DATA, frame=frame, postselect=post, n_qubits=36)
    info.update(noiseless=ex,
                status='verified grid-free' if not ex['errors'] else 'INVALID')
    (BASE / 'dk_steane.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(info, indent=2), flush=True)


if __name__ == '__main__':
    main()

Main session: you stopped correctly on tom's load (other users). Continue on owl instead: owl <= 24 processes in total,
only inside docker (docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1
-e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w <dir> --cpus=N fnc-build:22.04
/home/jihoon/competitions/quantumn/.venv/bin/python ...; stop a container with docker kill <id>, PID 1 ignores SIGTERM).
owl has its own disk: rsync -a --exclude .submit_credentials this lane dir (and any input it reads) to owl first and
results back. Do not use tom again; zebra <= 4 for light work.

Priority is the decisive test of the path ending on the grid, not more repairs of the 1.05e-3 builds. Your phantom
result (real E prep, synchronized D->A, final gap layer retired: 3.4542e-5 at A 0.4893 vs v37c 3.6904e-5) says the
prize is about -2.2e-6 after an acceptance buy; the obstacle is room for E next to all seven A cells. Lanes SQUARE and
SQPROJ just closed the square on the grid for the same reason (every built way to prepare interleaved blocks costs
>= 1e-4; docs/FINDINGS.md "Square final round"), so a layout witness is what decides this. Run the joint A/B/C/E
placement + in-place preparation CP-SAT model to a witness or an infeasibility certificate at R45-R47 with more
time and workers (portfolio of seeds/objectives across the 24 owl processes); relax what the square lanes showed is
not needed (a block may be prepared in other free cells and moved by measured one-CX moves, docs/reference/judge.md
"Spec freedoms"), and allow E to replace A's partial decoder and the flag-gap helpers so their cells become E's.
With a witness, build, price exactly, repair (your copied INTEG/ACCBUY tools or work/lanes/MERGE's menu) and buy
acceptance back. Incumbent is now v37d (3.676346632406467e-5, A 0.5023547642585299, work/lanes/MAIN/v37d), a finalist
needs L < L(v37d) - 1e-7 at exact A >= 0.5002, judge gates_ok at 1e6, judge speed within 1.5x of v37d's 3.2 s per
1e6. Stop with a finalist that no longer improves, or with the measured cost or certificate that closes the path
ending on this grid. Same rules as before: write only under this lane, no submission/commit/push, never read
.submit_credentials, no spawn_agent, wait on PIDs and kill by PID. Update REPORT.md (<= 100 lines, < 2,000 chars each).

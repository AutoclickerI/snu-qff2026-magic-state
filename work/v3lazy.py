import cultiv_port as cp
c = cp.build(("inject", "check", "cycle"), "Tswap", z_first=True, lockstep=True).rescheduled(lazy_init=True)
DATA = cp.DATA

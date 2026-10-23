import stav
for gap in [0,2,6]:
    for pin in [0,2e-2]:
        r=stav.score("s7307","std",pin,gap); print(gap,pin,r,flush=True)

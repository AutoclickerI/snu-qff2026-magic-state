import stav
for pin in [0,0.1]:
    for sd in [None,"std"]:
        print(pin, sd, stav.score("std", sd, pin)[:2], flush=True)

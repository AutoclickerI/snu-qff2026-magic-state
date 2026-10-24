from pathlib import Path
from evaluate import score
from allsite_screen import make
HERE=Path(__file__).resolve().parent
for seed in (3,5,6,4):
    name=f'clean_d14_late3_k82_s{seed}'
    score(HERE/name,20,True)
    score(make(name),20,True)

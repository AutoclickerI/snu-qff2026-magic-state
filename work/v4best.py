import json, glob, os
import batch_score
res = json.load(open("batch_1792737466.json"))
best = [r for r in res if r["passed"]][0]
c, DATA = batch_score.make(best["spec"])
LABEL = best["label"]

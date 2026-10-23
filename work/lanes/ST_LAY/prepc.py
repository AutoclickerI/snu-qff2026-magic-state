import sys, json
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/ST_LAY")
from prep import best
l = json.load(open(sys.argv[1])); k = sys.argv[2]
cells = l["stage"][k]; avail = cells + l["helpers"][k]
r = best(cells, avail, k == "a", float(sys.argv[3]), 8, (0,1,2,3), 5, 9)
print(k, r and (r["layers"], r["cx"], r["danger"]))
json.dump(r, open(sys.argv[4], "w"))

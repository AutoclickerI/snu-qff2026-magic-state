import glob,json,math
from pathlib import Path
fs=glob.glob('work/lanes/BUDGET/init_scan/eval/*.json');xs=[]
for f in fs:
 z=json.load(open(f));
 if 'second' in z:xs.append(z)
# order by second then acceptance headroom (higher exp accepted) as screening proxy
xs.sort(key=lambda z:(z['second'],-math.exp(-z['A1'])))
print('n',len(xs));
for z in xs[:50]: print(f"{z['mask']:03x} {z['second']:.12e} {math.exp(-z['A1']):.8f}")
json.dump(xs[:100],open('work/lanes/BUDGET/init_second_top100.json','w'),indent=2)

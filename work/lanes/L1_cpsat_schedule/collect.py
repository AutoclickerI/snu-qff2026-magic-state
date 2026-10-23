"""Collect distinct schedules, optionally check all readout orientations, and snapshot."""
import argparse
import itertools
from common import *
from cpsat import compact

def main():
    ap=argparse.ArgumentParser();ap.add_argument('files',nargs='+');ap.add_argument('--tag',default='candidates');ap.add_argument('--orientations',action='store_true');ap.add_argument('--count',type=int,default=50)
    args=ap.parse_args();m=g2.Model(EXTRAS);seen=set();out=[];tried=invalid=0
    for fname in args.files:
        rows=json.load(open(fname))
        for idx,row in enumerate(rows):
            if row[0] is None:continue
            a,o=decode(row);a=compact(a)
            for oo in itertools.product(range(2),repeat=3) if args.orientations else [o]:
                key=(tuple(a[k] for k in m.keys),tuple(oo))
                if key in seen:continue
                seen.add(key);tried+=1;p=m.cost(a,oo)
                if p is None:invalid+=1;continue
                out.append(encode(p,a,oo,f'{Path(fname).name}:{idx}'))
    out.sort(key=lambda row:row[0]);save(args.tag+'.json',out[:args.count]);save(args.tag+'_collection.json',dict(tried=tried,invalid=invalid,valid=len(out),saved=min(len(out),args.count),sources=args.files))
    print(dict(tried=tried,invalid=invalid,valid=len(out),best_proxy=out[0][0] if out else None),flush=True)

if __name__=='__main__':main()

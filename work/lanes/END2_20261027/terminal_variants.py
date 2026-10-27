"""Native terminal simplifications, evaluated with explicitly ideal resources.

The free C factors at nonsquare positions never carry useful information.
Their B->C gates act identically on |+>, and the independent factors can be
removed altogether. These diagnostics retain the actual noisy source; they
are not complete submission circuits until a native factory is integrated.
"""
import argparse,json
from pathlib import Path
from types import SimpleNamespace
from partial_contract import make_partial_contract, make_four_square_contract, STEANE_X
from contract_counterfactual import build,evaluate,HERE


def make_variant(square_mask=29,swap_mask=0,drop_free=True,dual_a=False,omit_free_cx=True,base_roles=None):
    base=make_four_square_contract()
    roles={k:list(v) for k,v in (base_roles or base.roles).items()}
    for i in range(7):
        if swap_mask>>i&1:roles['A'][i],roles['B'][i]=roles['B'][i],roles['A'][i]
    pc=make_partial_contract(roles,square_mask,True,dual_a)
    free=[i for i in range(7) if not(square_mask>>i&1)]
    freeq={roles['C'][i] for i in free}
    old_terminal=list(pc.terminal())
    terminal=[o for o in old_terminal if not(omit_free_cx and o[0]=='CX' and o[2]==0 and o[1][1] in freeq)]
    if drop_free:
        terminal=[o for o in terminal if not(set(o[1])&freeq)]
        pc.CELLS=[q for q in pc.CELLS if q not in freeq]
        pc.HELPERS=sorted(set(range(36))-set(pc.D+pc.CELLS))
        pc.ROWS=[r-freeq for r in pc.ROWS if r-freeq]
        pc.FULL_ROWS=[r-freeq for r in pc.FULL_ROWS if r-freeq]
        pc.COLS={q:sum(1<<j for j,r in enumerate(pc.ROWS) if q in r) for q in range(36) if q not in pc.D}
        pc.FULL_COLS={q:sum(1<<j for j,r in enumerate(pc.FULL_ROWS) if q in r) for q in pc.COLS}
        pc.DETECTORS=pc.DETECTORS[:6]+[row for row in pc.DETECTORS[6:] if not any(b-14 in free for b in row)]
        pc.late_plus=[]
    pc.terminal=lambda:list(terminal)
    pc.rank=len(pc.ROWS)
    pc.orientation=swap_mask
    pc.kind=f'variant_s{swap_mask:02x}_{"drop" if drop_free else "keep"}_{"omit" if omit_free_cx else "all"}'
    def signature(q,axis,helpers=()):
        if dual_a:raise ValueError('Need full Pauli propagation through post-H for dual A.')
        x=1<<q if axis=='X' else 0;z=1<<q if axis=='Z' else 0;flips=0
        for kind,qs,_,bit in terminal:
            if kind=='CX':
                a,b=qs
                if x>>a&1:x^=1<<b
                if z>>b&1:z^=1<<a
            elif (kind=='M' and x>>qs[0]&1) or (kind=='MX' and z>>qs[0]&1):flips^=1<<bit
        err=x if axis=='X' else z
        pattern=sum((err>>d&1)<<i for i,d in enumerate(pc.D))
        out=sum(((pattern&row).bit_count()&1)<<j for j,row in enumerate(STEANE_X))
        out|=(pattern.bit_count()&1)<<3
        ds=pc.DETECTORS[:3] if axis=='X' else pc.DETECTORS[3:]
        out|=sum((sum(flips>>b&1 for b in row)&1)<<(4+j) for j,row in enumerate(ds))
        if axis=='X' and q in helpers:out|=1<<(7+list(helpers).index(q))
        return out
    pc.fault_signature=signature
    for kind,qs,_,_ in terminal:
        if kind=='CX':assert abs(qs[0]//6-qs[1]//6)+abs(qs[0]%6-qs[1]%6)==1,(kind,qs)
    return pc


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--masks',default='29,25');ap.add_argument('--swaps',default='0')
    ap.add_argument('--delay',type=int,default=0);ap.add_argument('--tail',action='store_true');ap.add_argument('--keep-free',action='store_true')
    args=ap.parse_args();results=[]
    for mask in map(lambda x:int(x,0),args.masks.split(',')):
        for swap in map(lambda x:int(x,0),args.swaps.split(',')):
            pc=make_variant(mask,swap,not args.keep_free)
            stem=build(pc,not args.tail,args.delay)
            out=evaluate(stem)
            out.update(square_mask=mask,swap_mask=swap,drop_free=not args.keep_free,
                       roles=pc.roles,rank=pc.rank,terminal_cx=sum(o[0]=='CX' for o in pc.terminal()))
            results.append(out)
            (HERE/f'terminal_variants_{"tail" if args.tail else "source"}_{"keep" if args.keep_free else "drop"}_delay{args.delay}.json').write_text(json.dumps(results,indent=2)+'\n')
    return results

if __name__=='__main__':main()

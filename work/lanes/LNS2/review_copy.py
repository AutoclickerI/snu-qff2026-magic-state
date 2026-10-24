import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def copy4(src,out,startbit=230,full_barrier=False):
    L=Path(src).with_suffix('.qasm').read_text().splitlines()
    hits=[i for i,l in enumerate(L) if l.strip()=='cx q[19],q[25];']
    if not hits: raise ValueError('no CX 19->25')
    old=hits[-1]
    b=next(j for j in range(old+1,len(L)) if L[j].startswith('barrier'))
    prev=max(j for j in range(old) if L[j].startswith('barrier'))
    helpers=(18,31,35,34)
    reset_lines=[f'reset q[{q}];' for q in helpers]
    if full_barrier:
        barrier='barrier q['+'],q['.join(map(str,range(36)))+'];'
        L[prev:prev+1]=reset_lines+[barrier]
    else:
        L[prev:prev+1]=reset_lines+[L[prev]]
    old+=len(reset_lines); b+=len(reset_lines)
    L[old]=None
    copies=[f'cx q[19],q[18];',f'cx q[25],q[31];',f'cx q[29],q[35];',f'cx q[28],q[34];']
    L[b:b]=copies; b+=len(copies)
    L=[x for x in L if x is not None]
    # preserve terminal MX native frame: insert closing H after final X-basis readings
    for q in (6,26,13,11,4,23,27):
        i=0
        while i<len(L):
            if L[i]==f'h q[{q}];' and i+1<len(L) and L[i+1].startswith(f'measure q[{q}]'):
                if i+2>=len(L) or L[i+2]!=f'h q[{q}];': L.insert(i+2,f'h q[{q}];')
                break
            i+=1
    mi=next(i+1 for i,l in enumerate(L) if l.startswith('measure q[25] -> c[22]'))
    L[mi:mi]=[f'measure q[{q}] -> c[{startbit+k}];' for k,q in enumerate(helpers)]
    for i,l in enumerate(L):
        if l=='// DETECTOR c[22] c[26] c[27]': L[i]='// DETECTOR c[22] c[23] c[26] c[27]'
        elif l=='// DETECTOR c[21] c[22] c[24] c[25] c[26] c[27]': L[i]='// DETECTOR c[21] c[22] c[23] c[24] c[25] c[26] c[27]'
    # The v25k barriers omit fresh helper cells; include them at every barrier so
    # xtim does not model them as full-circuit idles.
    hs=set(helpers)
    for j,line in enumerate(L):
        if line.startswith('barrier q['):
            qs=list(map(int,re.findall(r'q\[(\d+)\]',line)))
            qs=sorted(set(qs)|hs)
            L[j]='barrier q['+'],q['.join(map(str,qs))+'];'
    L += [f'// DETECTOR c[23] c[{startbit}]',f'// DETECTOR c[22] c[{startbit+1}]',f'// DETECTOR c[26] c[{startbit+2}]',f'// DETECTOR c[27] c[{startbit+3}]']
    Path(out).with_suffix('.qasm').write_text('\n'.join(L)+'\n')
    meta=json.loads(Path(src).with_suffix('.json').read_text());meta.update(source=str(src),method='reviewer3 item 1 readout copy4',cx=int(meta.get('cx',0))+3,reviewer_copy_bits=list(range(startbit,startbit+4)))
    Path(out).with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')

if __name__=='__main__':
    copy4(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 230, bool(int(sys.argv[4])) if len(sys.argv)>4 else False)

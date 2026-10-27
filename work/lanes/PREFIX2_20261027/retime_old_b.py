"""Targeted source contractions and one-tick earlier verified B factory.

The source edits cancel four explicit CX pairs and move commuting operations.
The B factory retains all measurements and their original record identities;
only two initial identity parking CXs are removed. Its remaining operations
keep their order on every physical wire. Full circuit pricing is required.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,copy,contextlib,io,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from measured_assemble import assemble


def source():
    boundary=json.loads((ROOT/'work/lanes/NATIVE2_20261027/prefix_release.json').read_text())
    text=Path(boundary['stem']).with_suffix('.qasm').read_text();ops,dets=f.parse_current(text)
    ops=copy.deepcopy(ops);changes=[]
    def find(kind,qs,t):
        match=[o for o in ops if o.kind==kind and o.qs==tuple(qs) and o.time==t]
        assert len(match)==1,(kind,qs,t,len(match));return match[0]
    def drop(kind,qs,t):
        o=find(kind,qs,t);ops.remove(o);changes.append(dict(action='remove',kind=kind,qs=qs,time=t))
    def move(kind,qs,t,nt):
        o=find(kind,qs,t);o.time=nt;changes.append(dict(action='move',kind=kind,qs=qs,time=t,new_time=nt))
    for t in (26,27):drop('CX',[16,17],t)
    move('CX',[17,11],28,26);move('MX',[17],29,27)
    for t in (31,32):drop('CX',[11,10],t)
    move('CX',[11,10],33,31);move('M',[11],34,32)
    for t in (29,30):drop('CX',[19,25],t)
    for t in (29,31):drop('CX',[12,13],t)
    move('MX',[12],32,29);move('M',[24],32,29)
    move('M',[5],35,34)
    move('CX',[4,10],34,33);move('MX',[4],35,34)
    occupied=set()
    for o in ops:
        for q in o.qs:
            key=o.time,q;assert key not in occupied,('Source collision',key)
            occupied.add(key)
    ops.sort(key=lambda o:o.time);data=[6,20,19,10,2,22,16]
    text=emit(ops,dets);raw=raw_check(text,data);assert raw['ok'],raw
    stem=write_stem(text,data,HERE/'retimed','source_aligned',source=dict(parent=boundary['stem'],edits=changes,raw=raw))
    release={q:max((o.time+1 for o in ops if q in o.qs),default=0) for q in range(36) if q not in data}
    receipt=dict(stem=str(stem),release=release,source_edits=changes,raw=raw,cx=sum(o.kind=='CX' for o in ops))
    (HERE/'retimed/source_release.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def b_module(src,park_cut=2,jit=True):
    doc=json.loads((ROOT/'work/lanes/NATIVE2_20261027/old_b_module.json').read_text())
    assert doc.get('allow_record_faults') and not doc.get('ignore_original_records'), 'Use current physical mode-completion policy'
    ops=[];deleted=[]
    for old in doc['candidates'][0]['operations']:
        if old['kind']=='CX' and old['qs']==[32,26] and 16<=old['time']<16+park_cut:
            deleted.append(old);continue
        o=copy.deepcopy(old);o['original_time']=o['time'];ops.append(o)
    busy={int(q):t for q,t in src['release'].items()}
    for o in ops:
        o['time']=max(busy[q] for q in o['qs'])
        for q in o['qs']:busy[q]=o['time']+1
    if jit:
        # Each reset is single-wire. Moving it towards its next operation
        # preserves every wire order and cannot cross another physical use.
        for i,o in enumerate(ops):
            if o['kind'] not in ('R','RX'):continue
            q=o['qs'][0];future=[p['time'] for p in ops[i+1:] if q in p['qs']]
            if future:o['time']=min(future)-1
    B=doc['roles']['B'];ready=max(o['time']+1 for o in ops if set(o['qs'])&set(B))
    out=copy.deepcopy(doc);out['prefix_stem']=src['stem']
    out['terminal_operations']=[('CX',[b,d],0,None) for b,d in zip(B,doc['roles']['D'])]
    out['terminal_operations'] += [('MX',[q],1,7+i) for i,q in enumerate(B)]
    out['candidates']=[dict(operations=ops,cx=sum(o['kind']=='CX' for o in ops),resource_ready=ready,
                            module_end=max(o['time'] for o in ops)+1,preserved_wire_order=True,
                            parking_removed=deleted,jit_resets=jit)]
    path=HERE/f'retimed/old_b_cut{park_cut}_{"jit" if jit else "asap"}.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    return path,out


def a_module(src):
    doc=json.loads((ROOT/'work/lanes/NATIVE2_20261027/compact_a_logical_read_a_module.json').read_text())
    doc['prefix_stem']=src['stem'];ops=doc['candidates'][0]['operations']
    # The ten-CX encoder finishes q7/q8 at43 and all A cells by44.
    # Advance only the subsequent instrument, preserving its operation order.
    for o in ops:
        if o['time']>=45:o['time']-=1
    path=HERE/'retimed/compact_a_48tick.json';path.write_text(json.dumps(doc,indent=2)+'\n');return path


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--park-cut',type=int,default=2);ap.add_argument('--no-jit',action='store_true')
    ap.add_argument('--assemble',action='store_true');ap.add_argument('--price',action='store_true');ap.add_argument('--singles',action='store_true');a=ap.parse_args()
    src=source();bp,bd=b_module(src,a.park_cut,not a.no_jit);apath=a_module(src)
    out=dict(source=src,b_module=str(bp),a_module=str(apath),b_ready=bd['candidates'][0]['resource_ready'])
    if a.assemble:
        with contextlib.redirect_stdout(io.StringIO()):
            result=assemble(apath,bp,0,0,f'aligned48_cut{a.park_cut}_{"asap" if a.no_jit else "jit"}',
                            do_price=a.price,do_singles=a.singles)
        out['full']=result
    path=HERE/f'retimed/result_cut{a.park_cut}_{"asap" if a.no_jit else "jit"}.json';path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(receipt=str(path),source_stem=src['stem'],source_cx=src['cx'],b_ready=out['b_ready'],
        **({k:out['full'][k] for k in ('stem','raw','cx','ticks','singles','exact') if k in out['full']} if 'full' in out else {})),indent=2),flush=True)


if __name__=='__main__':main()

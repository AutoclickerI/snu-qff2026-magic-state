#!/usr/bin/env python3
"""Make v30f/COMP29 records consumable by the lane-local native parser.

The judge circuits use a classical register larger than the parser's fixed
256-bit working register.  Bits are only labels in measurements, detectors,
and frames, so unused low labels are a semantics-preserving replacement.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def remap(src, dst):
    src = Path(src); dst = Path(dst)
    text = src.with_suffix('.qasm').read_text()
    bits = sorted({int(x) for x in re.findall(r'c\[(\d+)\]', text)})
    high = [b for b in bits if b >= 256]
    used = {b for b in bits if b < 256}
    free = [b for b in range(256) if b not in used]
    if len(free) < len(high):
        raise ValueError((src, bits, free, high))
    mapping = dict(zip(high, free[:len(high)]))
    for a, b in sorted(mapping.items(), reverse=True):
        text = text.replace(f'c[{a}]', f'c[{b}]')
    text = re.sub(r'creg c\[\d+\];', 'creg c[256];', text, count=1)
    dst.with_suffix('.qasm').write_text(text)
    md = json.loads(src.with_suffix('.json').read_text())
    md.update({'source_st2': str(src), 'bit_remap': mapping, 'data_qubits': md.get('data_qubits', [0,20,7,10,3,22,21])})
    dst.with_suffix('.json').write_text(json.dumps(md, indent=2) + '\n')
    return mapping

def main():
    stems = [ROOT/'work/lanes/MAIN/v30f']
    manifest = ROOT/'work/lanes/COMP29/v30_manifest.json'
    if manifest.exists():
        rows = json.loads(manifest.read_text())
        # The complete product is large; retain the best screen-ranked ports
        # plus each singleton and the clean base as population seeds.
        scores = {}
        for p in (ROOT/'work/lanes/COMP29').glob('*.screen.json'):
            try: scores[p.stem[:-7]] = json.loads(p.read_text()).get('total', 1e9)
            except Exception: pass
        rows = sorted(rows, key=lambda r: scores.get(r['stem'], 1e9))
        keep = []
        for r in rows:
            s = r['stem']
            if s in {'f_base','f_prefix_feedback','f_copy4','f_instrument15','f_timing10','f_commute1','f_q19check','f_q11measure','f_edge14to15','f_zero_13_39'} or len(keep) < 24:
                keep.append(s)
        stems += [ROOT/'work/lanes/COMP29'/s for s in keep]
    seen = set(); outrows=[]
    for src in stems:
        try:
            raw = src.with_suffix('.qasm').read_bytes()
            key = __import__('hashlib').sha256(raw).hexdigest()
            if key in seen: continue
            seen.add(key)
            dst = OUT / ('v30_base' if src.name == 'v30f' else 'comp29_' + src.name)
            mapping = remap(src, dst)
            outrows.append({'name': dst.name, 'source': str(src), 'bit_remap': mapping})
        except Exception as e:
            print('skip', src, repr(e), file=sys.stderr)
    (OUT/'v30_seed_manifest.json').write_text(json.dumps(outrows, indent=2) + '\n')
    print(json.dumps({'seeds': len(outrows), 'names': [x['name'] for x in outrows]}))

if __name__ == '__main__': main()

"""Partition the incumbent into source, B factory, and native A instrument.

The A instrument includes its interleaved data taps and final measurements.
The source phase gates are already retimed by prefix_boundary and must not
be restored a second time. A single cross-edge,13->12 at41, is retained as
part of the instrument; its source-side control is initially zero.
"""
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
from qtools.evaluator import frontend as f
from qtools import write_stem
from old_b_new_a import old_b, D, A, B, C
from measured_assemble import assemble
import prefix_boundary as pb
from joint import emit


def extract():
    pre, dets, boundary = pb.extract(False)
    prefix_stem = write_stem(emit(pre, dets), D, HERE / 'boundary', 'source_prefix_unretimed', source=boundary)
    boundary['stem'] = str(prefix_stem)
    old, old_dets = f.parse_current((ROOT / 'work/lanes/MAIN/v37j.qasm').read_text())
    bdoc = json.loads(old_b().read_text())
    bdoc['prefix_stem'] = str(prefix_stem)
    bops = bdoc['candidates'][0]['operations']
    keys = {(o.time, o.kind, o.qs, o.bit) for o in pre}
    keys |= {(r['time'], r['kind'], tuple(r['qs']), r.get('original_bit')) for r in bops}
    terminal = [o for o in old if (o.kind == 'CX' and o.time == 47 and o.qs[0] in B and o.qs[1] in D)
                or (o.kind == 'MX' and o.time == 48 and o.qs[0] in B)]
    terminal_keys = {(o.time, o.kind, o.qs, o.bit) for o in terminal}
    inst = [o for o in old if o.kind not in ('T', 'TDG')
            and (o.time, o.kind, o.qs, o.bit) not in keys | terminal_keys
            and not (o.qs == (1,) and o.time == 29 and o.bit == 366)]
    rows = [dict(time=o.time, kind=o.kind, qs=list(o.qs), original_bit=o.bit) for o in inst]
    doc = dict(prefix_stem=boundary['stem'], A=A,
               candidates=[dict(A=A, operations=rows, cx=sum(o.kind == 'CX' for o in inst))],
               scope='Incumbent native A measurement instrument, including its actual interleaved data taps.',
               original_detector_rows=[sorted(r) for r in old_dets],
               phase_exclusion='Original T/TDG gates are excluded because this prefix already contains them at their original clock slots.',
               source_phase_note='The retimed source cannot be overlaid unchanged: TDG20 at37 would collide with an original data-to-A tap. This descriptor uses the unretimed source.')
    apath = HERE / 'old_a_instrument.json'
    apath.write_text(json.dumps(doc, indent=2) + '\n')
    bdoc['terminal_operations'] = [(o.kind, list(o.qs), o.time - 47, o.bit) for o in terminal]
    bpath = HERE / 'old_b_instrument_module.json'
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    print(json.dumps(dict(a_module=str(apath), b_module=str(bpath),
                         a_cx=sum(o.kind == 'CX' for o in inst),
                         b_cx=bdoc['candidates'][0]['cx'], source_cx=boundary['cx'],
                         a_operations=len(inst), b_operations=len(bops)), indent=2), flush=True)
    return apath, bpath


if __name__ == '__main__':
    a, b = extract()
    assemble(a, b, 0, 0, 'restored_a_instrument', terminal_start=47, do_singles=True)

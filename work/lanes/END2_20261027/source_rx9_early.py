"""Real noisy RX9 at38 replaces H9@38/MX9@39 on the cut3 source.

This intentionally removes the c321 source herald. It is a different physical
acceptance contract, whose complete noisy circuit must be audited and priced.
"""
import json
from pathlib import Path
from source_product_boundaries import HERE, f, save


def main():
    boundary=HERE.parent/'NATIVE2_20261027/q15_early39_cut3_release.json'
    parent=Path(json.loads(boundary.read_text())['stem'])
    ops,dets=f.parse_current(parent.with_suffix('.qasm').read_text())
    h9=next(op for op in ops if (op.kind,op.qs,op.time)==('H',(9,),38))
    m9=next(op for op in ops if (op.kind,op.qs,op.time)==('MX',(9,),39))
    assert m9.bit==321
    h9.kind='RX'
    ops.remove(m9)
    removed=[sorted(row) for row in dets if m9.bit in row]
    dets=[row-{m9.bit} for row in dets if row-{m9.bit}]
    changes=[dict(action='replace',old_kind='H',new_kind='RX',qs=[9],time=38,
                  note='Actual noisy reset-plus preparation; no ideal initialization is assumed.'),
             dict(action='remove',kind='MX',qs=[9],time=39,bit=m9.bit,
                  removed_record_from_checks=removed)]
    result=save('cut3_rx9_early',ops,dets,parent,changes)
    assert result['release'][9]==39


if __name__=='__main__':main()

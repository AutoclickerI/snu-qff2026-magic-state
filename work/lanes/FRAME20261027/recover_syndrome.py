"""Try affine frame recovery of one-dimensional old-data syndrome sectors."""
from frame_tools import *
import traceback
def make(v,correction,base=OUT/'btele_fresh'):
    ops,dets,md=load(base)
    rows=[{400+j for j in row} for row in f.SUPPORTS]
    assert all(row in dets for row in rows)
    pivot=(v&-v).bit_length()-1
    remain=[i for i in range(3) if i!=pivot]
    dd=[row for row in dets if row not in rows]
    dd += [rows[i]^rows[pivot] if v>>i&1 else rows[i] for i in remain]
    frame=parse_frames(base.with_suffix('.qasm').read_text())
    for P,on in [('X',correction&1),('Z',correction&2)]:
        if on:frame[P]=(frame[P][0],frame[P][1]^rows[pivot])
    return emit(f'recover_d{v}_p{correction}',ops,dd,md['data_qubits'],frame,
                {'accepted_extra_syndrome':v,'logical_frame_correction':correction})
if __name__=='__main__':
    summaries=[];valid=[]
    for v in range(1,8):
        for correction in range(4):
            s=make(v,correction)
            try:
                raw=raw_check(s.with_suffix('.qasm').read_text(),json.loads(s.with_suffix('.json').read_text())['data_qubits'])
                single=singles(s)
                summary={'v':v,'correction':correction,'raw':raw,'c1_contribution':single['first_order_loss'],'harmful_count':single['harmful_count']}
                print(json.dumps(summary),flush=True);summaries.append(summary)
                if raw['ok'] and single['first_order_loss']<1e-12:valid.append(s)
            except Exception:traceback.print_exc()
    (HERE/'recovery_single_summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    for s in valid:
        try:print('PRICE',json.dumps(price(s)),flush=True)
        except Exception:traceback.print_exc()


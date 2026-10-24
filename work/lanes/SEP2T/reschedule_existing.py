from reschedule import *
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=8);a=p.parse_args();src=HERE/a.stem;meta=json.loads(src.with_suffix('.json').read_text());ops=json.loads(src.with_suffix('.units.json').read_text());head,raw,dets=S.qasm_ops(src.with_suffix('.qasm').read_text());schedule_build(ops,dets,meta['data_qubits'],HERE/a.out,a.workers,dict(data_hops=meta['data_hops'],block_moves=meta['block_moves'],source=a.stem))

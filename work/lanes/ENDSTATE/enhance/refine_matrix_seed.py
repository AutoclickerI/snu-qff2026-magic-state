from common import *
from neighbors import run
p=load(H/'matrix_R38_pack03');p['meta'].update(search_base='matrix_R38',seed_price_source='matrix_R38_pack03');save(p,'matrix_refine_seed');run('matrix_refine_seed','refine2')
names=json.loads((H/'refine2.queue.json').read_text());mid=(len(names)+1)//2;(H/'refine2a.queue.json').write_text(json.dumps(names[:mid]));(H/'refine2b.queue.json').write_text(json.dumps(names[mid:]));print('partitions',mid,len(names)-mid,flush=True)

from common import *
from guards import apply
from neighbors import run
old=json.loads((H/'refine0_072.json').read_text())['protection_actions'];acts=json.loads((H/'matrix_R38.actions.json').read_text())
def key(a):return json.dumps({k:v for k,v in a.items()if k!='id'},sort_keys=True)
bykey={key(a):a for a in acts};chosen=[bykey[key(a)]for a in old];p=apply(load(H/'matrix_R38'),chosen);p['meta']['search_base']='matrix_R38';save(p,'matrix_seed');run('matrix_seed','refine1')

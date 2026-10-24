from round35 import *
from r36_static import diagnostic
OUT=HERE/'r36';pre=json.loads((OUT/'prefix_release.json').read_text());src=ROOT/'work/lanes/MAIN/v35b';orig,dets,md=load(src);A={1,14,8,9,2,16,15};init={1:38,14:38,8:36,9:38,2:38,16:41,15:40}
owned=[o for o in orig if set(o.qs)<=A and all(o.time>=init[q] for q in o.qs) and o.time<=43]
new=[f.Op(o['kind'],tuple(o['qs']),o['time'],o['bit'],o['line']) for o in pre['ops']]+copy.deepcopy(owned)
s=emit('prefix_release_base',new,dets,md,dict(base=str(src),moves=pre['moves'],purpose='commuting prefix retiming, original A+ and decoder retained'))
print('IDEAL',certify(s),flush=True);st=diagnostic(s);print('STATIC',st['failed_atoms'],flush=True);print('PRICE',price(s,7),flush=True);print('SPEED',speed(s,10000),flush=True)

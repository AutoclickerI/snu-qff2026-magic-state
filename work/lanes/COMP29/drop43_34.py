"""Remove an independent intermediate check between two retained Z projections."""
from decoder34 import *
def drop43(base):
    c=C.clone(base);seq=[]
    for i,(u,t) in enumerate(zip(c['u'],c['t'])):
        if 16 in u.qs and 27<=t<=30:seq.append((i,u,t))
    assert [(t,u.name) for i,u,t in seq]==[(27,'MEASURE'),(28,'MEASURE'),(30,'MEASURE')]
    assert [int(re.search(r'c\[(\d+)\]',u.lines[0])[1]) for i,u,t in seq]==[270,43,266]
    assert '// DETECTOR c[270]' in c['tail'] and '// DETECTOR c[43]' in c['tail']
    relevant=[set(map(int,re.findall(r'c\[(\d+)\]',line))) for line in c['tail'] if 43 in set(map(int,re.findall(r'c\[(\d+)\]',line)))]
    assert len(relevant)==2 and {43} in relevant and {43,266} in relevant
    i=seq[1][0];del c['u'][i];del c['t'][i]
    tail=[]
    for line in c['tail']:
        bits=[int(b) for b in re.findall(r'c\[(\d+)\]',line) if int(b)!=43]
        if bits:tail.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bits))
    c['tail']=tail
    c['meta']['removed_independent_check']=dict(record=43,qubit=16,first_checked_record=270,last_checked_record=266)
    return c

if __name__=='__main__':
    p=.001;q=2*p/3
    old=(1+(1-2*q)*(1-2*p))/2*(1+(1-2*q)**2*(1-2*p))/2
    new=(1+(1-2*q)**3*(1-2*p))/2
    cert=dict(acceptance_multiplier=new/old,conditional_loss_identical=True,proof='Both circuits first require the q16 Z measurement at t27 to be zero. Its rank-one projection leaves q16 in |0>, followed by independent depolarization, factorized from the data. The only operations on q16 before the retained checked Z measurement at t30 are one optional checked Z measurement at t28 and idle noise. Both versions end in the identical post-measurement-depolarized |0> state. All intervening q16 noise contributes a scalar to accepted A and N, so conditional N/A is unchanged. Record c43 occurs only in its zero detector and c266 XOR c43, which becomes the retained c266 zero detector.',A_old_segment=old,A_new_segment=new,noise=dict(p=p,bit_flip_from_depolarization=q))
    (H/'v34_drop43_certificate.json').write_text(json.dumps(cert,indent=2)+'\n')
    rows=[]
    names=['g_base','g_ro_00010','g_ro_00011','g_ro_00001']
    for source in names:
        c=drop43(C.read(H/source));n='g_drop43_'+source.removeprefix('g_');rows.append(save(c,n,[source,'remove scalar-only intermediate q16 check c43']))
    (H/'v34_drop43.json').write_text(json.dumps(rows,indent=2)+'\n');print(cert['acceptance_multiplier'])

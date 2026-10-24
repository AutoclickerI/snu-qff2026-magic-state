import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v
c=v.C.read(v.V/'refined/echo10_27_omit_16_21_22')
i=next(i for i,u in enumerate(c['u'])if 186 in v.a.bits(' '.join(u.lines)));q=c['u'][i].qs[0];assert c['u'][i].name=='MX'
c['u'][i]=v.C.Unit([f'reset q[{q}];',f'h q[{q}];']);v.a.strip_bits(c,[186])
v.a.batch([('long_echo_funded',c,dict(family='exact_acceptance_repair',parent='refined/echo10_27_omit_16_21_22',funding='meas_186_reset',budget_screen=True))],'repaired',1)

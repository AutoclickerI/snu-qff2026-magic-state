from pass3 import *
if __name__=='__main__':
 st=Path(sys.argv[1]).resolve();basis=Path(sys.argv[2]).resolve();old=record(st,'basis control before')
 E.configure(basis,12);new=price(st,dict(kind='trained basis control',basis=str(basis)))
 assert abs(old['loss']-new['loss'])<1e-13 and abs(old['acceptance']-new['acceptance'])<1e-13,(old,new)
 dump(R/'basis_control_latest.json',dict(before=old,after=new,basis=str(basis)))

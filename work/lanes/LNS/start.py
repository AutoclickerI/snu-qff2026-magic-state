from core import *
if __name__=='__main__':
 cs=[]
 for family in ['h','w']:
  c=read(ROOT/f'work/lanes/MAIN/v22{family}_c2c9');cs.append((c,dict(family='control',base=family)))
 batch(cs,'control',2)

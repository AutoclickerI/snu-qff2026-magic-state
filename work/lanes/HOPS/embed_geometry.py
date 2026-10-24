from build import *
src=(OUT/'geometry.py').read_text().replace('m.add(DH<=5);m.minimize(3*DH+BH)','m.add(DH<=6);m.minimize(2*DH+BH)')
src=src.replace("(OUT/('geom_auto.json'if permute else'geom_fixed.json'))", "(OUT/(TAG+'.geometry.json'))")
ns={'__file__':str(OUT/'embed_geometry.py'),'__name__':'hops_embedded_geometry'};exec(compile(src,str(OUT/'embed_geometry.py'),'exec'),ns)
for row in range(3):
 for col in range(2):
  ns['D0']=[q+6*row+col for q in [0,20,7,4,3,15,8]];ns['TAG']=f'embed_r{row}c{col}'
  ns['solve'](True)

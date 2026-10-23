from evaluate import *
if __name__=='__main__':
 names=json.loads((HERE/'refine_shortlist.json').read_text())
 with mp.get_context('fork').Pool(3) as p:rows=list(p.imap_unordered(screen_one,names))
 (HERE/'refine_screen_results.json').write_text(json.dumps(rows,indent=2))

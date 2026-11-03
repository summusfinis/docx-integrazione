import re,io,sys,json,os
sys.path.insert(0,'/home/user/work/bin')
from xmltext import PARA,nodes,apply_edits,repl_span
DOC=sys.argv[1]; MAP='/home/user/work/pagine.json'
if not os.path.exists(MAP): print('numeri di pagina: mappa assente, saltato'); sys.exit()
pg=json.load(io.open(MAP,encoding='utf-8'))
d=io.open(DOC,encoding='utf-8').read()
body=None; edits=[]; n=0; miss=0
P=[(m.start(),m.end(),m.group(0)) for m in PARA.finditer(d)]
for s,e,pm in P:
    if 'Titolo2' in pm or 'Titolo1' in pm: body=True; continue
    if 'w:anchor' not in pm and 'Titolo' not in pm: continue
for s,e,pm in P:
    t,pos=nodes(d,s,e)
    ts=t.strip()
    k=None
    mm=re.match(r'(Scheda \d+|Titolo [IVX]+) – ',ts)
    if mm and 'Titolo2' not in pm and 'Titolo1' not in pm: k=mm.group(1)
    if not k or k not in pg: 
        if k: miss+=1
        continue
    mnum=re.search(r'(\d+)\s*$',t)
    if not mnum: miss+=1; continue
    edits+=repl_span(pos,mnum.start(1),mnum.end(1),str(pg[k])); n+=1
d=apply_edits(d,edits)
io.open(DOC,'w',encoding='utf-8').write(d)
print('numeri di pagina aggiornati:',n,'| non trovati:',miss)

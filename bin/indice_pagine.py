import os as _os
_BIN = _os.path.dirname(_os.path.abspath(__file__))
_WORK = _os.environ.get('DOCX_WORK') or _os.path.join(_os.getcwd(), 'lavoro')
import re,io,sys,json,os
sys.path.insert(0,_BIN)
from xmltext import PARA,nodes,apply_edits,repl_span
DOC=sys.argv[1]; MAP=_os.path.join(_WORK,'pagine.json')
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
    mm=re.match(r'(Scheda \d+|Titolo [IVX]+) – ',ts)
    if not mm or 'Titolo2' in pm or 'Titolo1' in pm: continue
    k=mm.group(1)
    if k not in pg: miss+=1; continue
    last=list(re.finditer(r'<w:t(?:\s[^>]*)?>(\d+)</w:t>',pm))
    if not last: miss+=1; continue
    g=last[-1]
    edits.append((s+g.start(1),len(g.group(1)),str(pg[k]))); n+=1
d=apply_edits(d,edits)
io.open(DOC,'w',encoding='utf-8').write(d)
print('numeri di pagina aggiornati:',n,'| non trovati:',miss)

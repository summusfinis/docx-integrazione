import re,sys,io,json,glob
sys.path.insert(0,'/home/user/work/bin')
from xmltext import PARA, nodes, apply_edits, repl_span
from mk import runs as mkruns

DOC=sys.argv[1]; APPLY='--apply' in sys.argv
# proposte accettate: (file, indice nella lista, numero nuovo, numero della scheda che la segue)
ACC=[('p1.json',0,179,180),('p4.json',1,184,185),('p6.json',0,191,192),
     ('p6.json',1,193,194),('p8.json',0,204,205),('p4.json',0,206,207)]
# proposte da NON creare: il contenuto confluisce in una scheda esistente (gestito da integra.py)
d=io.open(DOC,encoding='utf-8').read()

# ---- 1) rinumerazione: old -> new
MAP={}
for n in range(179,235):
    k=n
    for old in (178,182,188,189,199,200):
        if n>old: k+=1
    MAP[n]=k
edits=[]; cnt=0
for m in PARA.finditer(d):
    t,pos=nodes(d,m.start(),m.end())
    mm=re.search(r'Scheda (\d+)',t)
    if not mm: continue
    n=int(mm.group(1))
    if n in MAP and MAP[n]!=n:
        edits+=repl_span(pos,mm.start(1),mm.end(1),str(MAP[n])); cnt+=1
d=apply_edits(d,edits)
print('voci rinumerate:',cnt)

# ---- 2) inserimento delle nuove schede
def paras(): return [(m.start(),m.end(),m.group(0),nodes(d,m.start(),m.end())[0].strip()) for m in PARA.finditer(d)]
def first_rpr(pm):
    r=re.search(r'<w:r(?:\s[^>]*)?>(?:(?!</w:r>).)*?(<w:rPr>.*?</w:rPr>)',pm,re.S)
    return r.group(1) if r else ''
def ppr(pm):
    r=re.search(r'<w:pPr>.*?</w:pPr>',pm,re.S); return r.group(0) if r else ''

PROP={}
for f in glob.glob('/home/user/work/delta/*.json'):
    PROP[f.split('/')[-1]]=json.load(io.open(f,encoding='utf-8')).get('_nuove_schede') or []

rep=[]
for fname,idx,num,after in sorted(ACC,key=lambda x:-x[2]):
    pr=PROP[fname][idx]
    P=paras()
    body=[i for i,(s,e,pm,t) in enumerate(P) if t.startswith(f'Scheda {after} ') and 'Titolo2' in pm]
    ix  =[i for i,(s,e,pm,t) in enumerate(P) if t.startswith(f'Scheda {after} ') and 'Titolo2' not in pm and 'w:anchor' in pm]
    if len(body)!=1 or len(ix)!=1:
        rep.append(f'Scheda {num}: ANCORA {len(body)} corpo / {len(ix)} indice'); continue
    bi=body[0]; xi=ix[0]
    h2=P[bi]
    som=next((p for p in P[bi+1:bi+4] if p[3].startswith('Sommario')),None)
    h3=next((p for p in P[bi+1:bi+40] if 'Titolo3' in p[2]),None)
    bodyp=next((p for p in P[bi+1:bi+60] if 'Titolo' not in p[2] and len(p[3])>150),None)
    if not (som and h3 and bodyp):
        rep.append(f'Scheda {num}: MODELLI MANCANTI'); continue
    secs=pr['sections']
    titles=[s['title'] for s in secs]
    xml=f'<w:p>{ppr(h2[2])}'+mkruns(f"Scheda {num} – {pr['title']}",first_rpr(h2[2]))+'</w:p>'
    lab=re.search(r'<w:r(?:\s[^>]*)?>.*?</w:r>',som[2],re.S).group(0)
    lab=re.sub(r'(<w:t[^>]*>)[^<]*(</w:t>)',r'\1Sommario: \2',lab,count=1)
    rest=' – '.join(f'{i+1}. {t}' for i,t in enumerate(titles))
    allr=list(re.finditer(r'<w:r(?:\s[^>]*)?>.*?</w:r>',som[2],re.S))
    rp=re.search(r'<w:rPr>.*?</w:rPr>',allr[-1].group(0),re.S)
    xml+=f'<w:p>{ppr(som[2])}{lab}'+mkruns(rest,rp.group(0) if rp else '')+'</w:p>'
    for i,s in enumerate(secs,1):
        xml+=f'<w:p>{ppr(h3[2])}'+mkruns(f"{i}. {s['title']}",first_rpr(h3[2]))+'</w:p>'
        for par in s['paras']:
            xml+=f'<w:p>{ppr(bodyp[2])}'+mkruns(par,first_rpr(bodyp[2]))+'</w:p>'
    # voce di indice
    ixp=P[xi]
    rpi=first_rpr(ixp[2])
    last=list(re.finditer(r'<w:r(?:\s[^>]*)?>.*?</w:r>',ixp[2],re.S))[-1].group(0)
    pagerun=re.sub(r'(<w:t[^>]*>)[^<]*(</w:t>)',r'\g<1>0\2',last,count=1)
    ixml=f'<w:p>{ppr(ixp[2])}'+mkruns(f"Scheda {num} – {pr['title']}",rpi)+pagerun+'</w:p>'
    if APPLY:
        d=d[:h2[0]]+xml+d[h2[0]:]
        d=d[:ixp[0]]+ixml+d[ixp[0]:]
    rep.append(f'Scheda {num}: {len(secs)} sez, {sum(len(s["paras"]) for s in secs)} capoversi, prima di {after}')
print('\n'.join(rep))
if APPLY:
    io.open(DOC,'w',encoding='utf-8').write(d)
    print('APPLICATO; doc',len(d),'byte')

import re, sys, io
sys.path.insert(0,'/home/user/work/bin')
from xmltext import PARA
from runs import chars

DOC=sys.argv[1]; APPLY='--apply' in sys.argv
BL="""Mappa concettuale|a prima richiesta|senza eccezioni|a monte|di riflesso|non producono altri effetti|
perdita subita|mancato guadagno|dolosa preordinazione|a seconda dei casi|effetto sorpresa|in fatto|fuori mercato|
salvo che la legge disponga diversamente|immobile da costruire|ad ogni effetto|sulla carta|ti pagherò se vorrò|
se vorrò|persona sensata|diritto al diritto|se…allora|più probabile che non|alla francese|tutto compreso|
rapporto giuridico|a valle|possesso vale titolo|no prohibitio domini|deliberate no law|contextual no law|My Way|
For You|Code Napoléon|malgrado la buona fede|Digital Service Act|Engel criteria|interna corporis|
best interest of child|e null’altro|e null'altro"""
BLACK={x.strip() for x in re.split(r'[|\n]',BL) if x.strip()}
WHITE=set("""ratio facere res solvens accipiens titulus dominus traditio usucapio privacy online software deepfake
lockdown telemarketing trustee settlor revirement astreinte astreintes disgorgement accountability influencer
denuntiatio quomodo compensatio omnibus trust hardship octies septies sexies quinquies quater undecies""".split())
voc=[]
for line in io.open('/home/user/work/vocab.txt',encoding='utf-8'):
    n,t=line.rstrip('\n').split(' | ',1); n=int(n)
    if t in BLACK: continue
    if ' ' in t:
        if n>=2: voc.append(t)
    elif t in WHITE and n>=3: voc.append(t)
voc=sorted(set(voc),key=len,reverse=True)
RX=re.compile(r'(?<![\w’])('+'|'.join(re.escape(v) for v in voc)+r')(?![\w’])')
SUF=re.compile(r'(?<=\d)-(bis|ter|quater|quinquies|sexies|septies|octies|novies|decies|undecies|duodecies)(?![\w])')

RUNRX=re.compile(r'<w:r(?:\s[^>]*)?>.*?</w:r>',re.S)
TNRX=re.compile(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>')
RPRRX=re.compile(r'<w:rPr>(.*?)</w:rPr>',re.S)
ORDER=['rStyle','rFonts','b','bCs','i','iCs','caps','smallCaps','strike','dstrike','outline','shadow','emboss',
'imprint','noProof','snapToGrid','vanish','webHidden','color','spacing','w','kern','position','sz','szCs',
'highlight','u','effect','bdr','shd','fitText','vertAlign','rtl','cs','em','lang','eastAsianLayout','specVanish','oMath']
def add_i(pr):
    m=RPRRX.search(pr); inner=m.group(1) if m else ''
    if '<w:i/>' in inner: return pr
    toks=re.findall(r'<w:[a-zA-Z]+[^>]*/>|<w:([a-zA-Z]+)[^>]*>.*?</w:\1>',inner,re.S)
    toks=[t if isinstance(t,str) else t for t in re.findall(r'<w:[a-zA-Z]+[^>]*/>|<w:[a-zA-Z]+[^>]*>(?:(?!</?w:[a-zA-Z]).)*</w:[a-zA-Z]+>',inner,re.S)]
    toks.append('<w:i/>')
    toks.sort(key=lambda t:(ORDER.index(re.match(r'<w:([a-zA-Z]+)',t).group(1)) if re.match(r'<w:([a-zA-Z]+)',t).group(1) in ORDER else len(ORDER)))
    return '<w:rPr>'+''.join(toks)+'</w:rPr>'

d=io.open(DOC,encoding='utf-8').read()
want={}   # run_start -> (run_end, run_xml, set(indici char da mettere in corsivo))
nspan=0; skipped=0
for pm in PARA.finditer(d):
    P=pm.group(0)
    cs=chars(P)
    if not cs: continue
    txt=''.join(c[0] for c in cs)
    spans=[(m.start(1),m.end(1)) for m in RX.finditer(txt)]+[(m.start(1),m.end(1)) for m in SUF.finditer(txt)]
    if not spans: continue
    runs=[(pm.start()+m.start(),pm.start()+m.end(),m.group(0)) for m in RUNRX.finditer(P)]
    for a,b in spans:
        if all(cs[k][2] for k in range(a,b)): continue
        nspan+=1
        for k in range(a,b):
            if cs[k][2]: continue
            pos=cs[k][3]+pm.start()
            r=next(((s,e,x) for s,e,x in runs if s<=pos<e),None)
            if r is None: continue
            s,e,x=r
            if len(TNRX.findall(x))!=1 or x.count('<w:t')!=1:
                skipped+=1; continue
            tm=TNRX.search(x); base=s+tm.start(1)
            want.setdefault(s,(e,x,base,set()))[3].add(pos-base)
print('dizionario:',len(voc),'| espressioni da correggere:',nspan,'| run coinvolti:',len(want),'| saltati:',skipped)
if APPLY:
    def R(pr,t): return '' if t=='' else '<w:r>'+pr+'<w:t xml:space="preserve">'+t+'</w:t></w:r>'
    out=[]
    for s,(e,x,base,idx) in want.items():
        pr=RPRRX.search(x); pr=pr.group(0) if pr else ''
        pri=add_i(pr); full=TNRX.search(x).group(1)
        new=''; i=0
        while i<len(full):
            j=i
            if i in idx:
                while j<len(full) and j in idx: j+=1
                new+=R(pri,full[i:j])
            else:
                while j<len(full) and j not in idx: j+=1
                new+=R(pr,full[i:j])
            i=j
        out.append((s,e-s,new))
    for p,L,s in sorted(out,key=lambda z:-z[0]): d=d[:p]+s+d[p+L:]
    io.open(DOC,'w',encoding='utf-8').write(d)
    print('APPLICATO',len(out),'run riscritti; doc',len(d),'byte')

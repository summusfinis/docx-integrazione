import os as _os
_BIN = _os.path.dirname(_os.path.abspath(__file__))
_WORK = _os.environ.get('DOCX_WORK') or _os.path.join(_os.getcwd(), 'lavoro')
import re,sys,io
sys.path.insert(0,_BIN)
from xmltext import PARA,nodes,apply_edits,repl_span
from mk import runs as mkruns
DOC=sys.argv[1]; APPLY='--apply' in sys.argv
d=io.open(DOC,encoding='utf-8').read()
def scan():
    return [(m.start(),m.end(),m.group(0),nodes(d,m.start(),m.end())[0].strip()) for m in PARA.finditer(d)]
P=scan()
BODY=next(k for k,p in enumerate(P) if 'w:val="Titolo1"' in p[2] and p[3].startswith('Titolo'))

# ---- 0) spazi persi fra run adiacenti ("ladatio in solutum")
ed=[]
for m in PARA.finditer(d):
    t,pos=nodes(d,m.start(),m.end())
    for mm in re.finditer(r'(?<=[a-zàèéìòù])datio (in solutum|rei)',t):
        ed.append((pos[mm.start()],0,' '))
d=apply_edits(d,ed)
print('spazi ripristinati:',len(ed))
P=scan()
BODY=next(k for k,p in enumerate(P) if 'w:val="Titolo1"' in p[2] and p[3].startswith('Titolo'))

# ---- A) sezioni non consecutive: rinumera e rifa' il Sommario
blocks=[]; cur=None
for k in range(BODY,len(P)):
    pm,t=P[k][2],P[k][3]
    if 'Titolo2' in pm and t.startswith('Scheda '):
        if cur: blocks.append(cur)
        cur={'n':t.split('–')[0].strip(),'start':k,'h3':[],'som':None}
    elif cur is not None:
        if 'Titolo3' in pm:
            m=re.match(r'(\d+)\.\s*(.*)',t)
            if m: cur['h3'].append((k,int(m.group(1)),m.group(2)))
        elif t.startswith('Sommario') and cur['som'] is None: cur['som']=k
if cur: blocks.append(cur)
def nz(x): return re.sub(r'\s+',' ',x).strip().replace('\u2019',"'")
edits=[]; fixed=[]
for b in blocks:
    nums=[x[1] for x in b['h3']]
    if not nums: continue
    att=nz(' – '.join(f'{i}. {t}' for i,(_,_,t) in enumerate(b['h3'],1)))
    som=nz(P[b['som']][3].split('Sommario:',1)[-1]) if b['som'] is not None else None
    if nums==list(range(1,len(nums)+1)) and som==att: continue
    fixed.append((b['n'],nums))
    for i,(k,old,title) in enumerate(b['h3'],1):
        if old==i: continue
        t,pos=nodes(d,P[k][0],P[k][1])
        m=re.match(r'(\d+)',t.lstrip())
        off=len(t)-len(t.lstrip())
        edits+=repl_span(pos,off,off+len(m.group(1)),str(i))
    if b['som'] is not None:
        k=b['som']; pm=P[k][2]
        ppr=re.search(r'<w:pPr>.*?</w:pPr>',pm,re.S)
        ppr=ppr.group(0) if ppr else ''
        runs=list(re.finditer(r'<w:r(?:\s[^>]*)?>.*?</w:r>',pm,re.S))
        lab=re.sub(r'(<w:t[^>]*>)[^<]*(</w:t>)',r'\1Sommario: \2',runs[0].group(0),count=1)
        rp=re.search(r'<w:rPr>.*?</w:rPr>',runs[-1].group(0),re.S)
        body=' – '.join(f'{i}. {t}' for i,(_,_,t) in enumerate(b['h3'],1))
        new=f'<w:p>{ppr}{lab}'+mkruns(body,rp.group(0) if rp else '')+'</w:p>'
        edits.append((P[k][0],P[k][1]-P[k][0],new))
d=apply_edits(d,edits)
print('schede rinumerate:',len(fixed),[f for f,_ in fixed])

# ---- B) corpo delle schede a 10,5 (sz 21)
P=scan()
tbl=[(m.start(),d.find('</w:tbl>',m.start())) for m in re.finditer(r'<w:tbl>',d)]
def intab(x):
    for a,b in tbl:
        if a<=x<b: return True
    return False
edits=[]; nrun=0; npar=0
for s,e,pm,t in P:
    if s<P[BODY][0]: continue
    if re.search(r'w:val="Titolo[1-4]"',pm): continue
    if intab(s) or t.startswith('Sommario') or not t: continue
    ch=False
    for m in re.finditer(r'<w:sz w:val="(\d+)"/>',pm):
        if m.group(1)!='21':
            edits.append((s+m.start(),m.end()-m.start(),'<w:sz w:val="21"/>')); nrun+=1; ch=True
    if ch: npar+=1
d=apply_edits(d,edits)
print('corpo a 10,5: run corretti',nrun,'in',npar,'capoversi')

# ---- B2) stile del corpo a 10,5 (sz 21), titoli di sezione fermi a 11,5 (sz 23)
import os as _o
_st = _o.path.join(_o.path.dirname(_o.path.abspath(DOC)) or '.', 'styles.xml')
if _o.path.exists(_st):
    sx = io.open(_st, encoding='utf-8').read()
    def _stile(t, sz):
        global sx
        m = re.search(r'<w:style [^>]*w:styleId="%s"[^>]*>.*?</w:style>' % t, sx, re.S)
        if not m: return 0
        b = m.group(0)
        if re.search(r'<w:sz w:val="\d+"/>', b):
            nb = re.sub(r'<w:sz w:val="\d+"/>', '<w:sz w:val="%d"/>' % sz, b)
            nb = re.sub(r'<w:szCs w:val="\d+"/>', '<w:szCs w:val="%d"/>' % sz, nb)
        elif '<w:rPr>' in b:
            nb = b.replace('<w:rPr>', '<w:rPr><w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (sz, sz), 1)
        else:
            nb = b.replace('</w:style>', '<w:rPr><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:style>' % (sz, sz))
        sx = sx.replace(b, nb, 1)
        return 1
    n = _stile('Normale', 21) + _stile('Titolo3', 23) + _stile('Titolo4', 23)
    if APPLY: io.open(_st, 'w', encoding='utf-8').write(sx)
    print('stili aggiornati:', n)

if APPLY:
    io.open(DOC,'w',encoding='utf-8').write(d)
    print('APPLICATO; doc',len(d),'byte')

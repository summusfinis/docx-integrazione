import re,sys,io,json,glob
sys.path.insert(0,'/home/user/work/bin')
from xmltext import PARA
from runs import chars
from mk import runs as mkruns

DOC=sys.argv[1]; APPLY='--apply' in sys.argv
d=io.open(DOC,encoding='utf-8').read()

def norm(t):
    t=t.replace('—','–').replace('--','–').replace("'",'’').replace('...','…')
    return re.sub(r'\s+',' ',t).strip()

def plist(s,e):
    out=[]
    for m in PARA.finditer(d,s,e):
        cs=chars(m.group(0))
        out.append((m.start(),m.end(),m.group(0),''.join(c[0] for c in cs)))
    return out

ALL=plist(0,len(d))
BODY=next(i for i,p in enumerate(ALL) if p[3].startswith('Titolo I – I principi generali') and i>0 and
          any(q[3].startswith('Titolo I – I principi generali') for q in ALL[:i]))

def region(n):
    idx=[i for i in range(BODY,len(ALL)) if ALL[i][3].startswith(f'Scheda {n} ') and 'Titolo2' in ALL[i][2]]
    if len(idx)!=1: sys.exit(f'Scheda {n}: intestazione trovata {len(idx)} volte')
    a=idx[0]
    b=next((j for j in range(a+1,len(ALL)) if 'Titolo2' in ALL[j][2] or 'Titolo1' in ALL[j][2]), len(ALL))
    return a,b

ops=[]   # (pos_assoluta, xml_da_inserire)
somm=[]  # (pos_fine_paragrafo_sommario, xml_run_da_aggiungere)
rep=[]
data={}
for f in sorted(glob.glob('/home/user/work/delta/*.json')):
    j=json.load(io.open(f,encoding='utf-8'))
    for k,v in j.items():
        if not k.startswith('Scheda'): continue
        n=int(k[6:]); cur=data.setdefault(n,{'append_sections':[],'inline_inserts':[]})
        cur['append_sections']+= (v.get('append_sections') or [])
        cur['inline_inserts'] += (v.get('inline_inserts') or [])

for n in sorted(data):
    v=data[n]; a,b=region(n)
    seg=ALL[a:b]
    h3=[(i,p) for i,p in enumerate(seg) if 'w:val="Titolo3"' in p[2]]
    nums=[int(m.group(1)) for i,p in h3 if (m:=re.match(r'\s*(\d+)\.',p[3]))]
    start=max(nums)+1 if nums else 1
    # paragrafo base di corpo e di titolo3
    base_b=next((p[2] for i,p in enumerate(seg) if 'Titolo' not in p[2] and len(p[3])>120), None)
    base_h=h3[0][1][2] if h3 else None
    if base_b is None or base_h is None: rep.append(f'Scheda {n}: MANCA MODELLO'); continue
    pprb=re.search(r'<w:pPr>.*?</w:pPr>',base_b,re.S).group(0)
    rprb=re.search(r'<w:r(?:\s[^>]*)?>(<w:rPr>.*?</w:rPr>)',base_b,re.S)
    rprb=rprb.group(1) if rprb else ''
    pprh=re.search(r'<w:pPr>.*?</w:pPr>',base_h,re.S).group(0)
    rprh=re.search(r'<w:r(?:\s[^>]*)?>(<w:rPr>.*?</w:rPr>)',base_h,re.S)
    rprh=rprh.group(1) if rprh else ''
    def P(ppr,rpr_base,md): return '<w:p>'+ppr+mkruns(md,rpr_base)+'</w:p>'
    # punto di inserimento: fine dell'ultimo paragrafo prima della tabella finale
    end=ALL[b-1][1] if b<len(ALL) else len(d)
    tb=d.rfind('<w:tbl>',seg[0][0],end)          # ultima tabella = mappa concettuale
    limit=tb if tb>seg[0][0] else end
    tail=[p for p in seg if p[1]<=limit]
    while tail and (not tail[-1][3].strip() or tail[-1][3].strip()=='Mappa concettuale'):
        tail.pop()
    ip=tail[-1][1]
    secs=v.get('append_sections') or []
    xml=''
    k=start
    added=[]
    for s in secs:
        xml+=P(pprh,rprh,f"{k}. {s['title']}")
        for par in s['paras']: xml+=P(pprb,rprb,par)
        added.append((k,s['title'])); k+=1
    if xml: ops.append((ip,xml))
    if added:
        sp=[p for p in seg if p[3].startswith('Sommario')]
        if len(sp)!=1: rep.append(f'Scheda {n}: SOMMARIO {len(sp)}'); 
        else:
            p=sp[0]
            lastr=list(re.finditer(r'<w:r(?:\s[^>]*)?>.*?</w:r>',p[2],re.S))[-1]
            rp=re.search(r'<w:rPr>.*?</w:rPr>',lastr.group(0),re.S)
            rp=rp.group(0) if rp else ''
            add=''.join(f' – {num}. {t}' for num,t in added)
            somm.append((p[0]+lastr.end(), mkruns(add,rp)))
    nin=0
    for ins in v.get('inline_inserts') or []:
        an=norm(ins['after_anchor'])
        cand=[p for p in seg if an in norm(p[3])]
        if len(cand)!=1:
            rep.append(f'Scheda {n}: ancora {len(cand)} -> sezione di ripiego | {an[:50]}'); continue
        xml2=''.join(P(pprb,rprb,par) for par in ins['paras'])
        ops.append((cand[0][1],xml2)); nin+=1
    rep.append(f'Scheda {n}: +{len(secs)} sez (da {start}), +{nin} inline')

print('\n'.join(rep))
print('inserimenti:',len(ops),'| sommari:',len(somm))
if APPLY:
    for pos,xml in sorted(ops+somm,key=lambda z:-z[0]):
        d=d[:pos]+xml+d[pos:]
    io.open(DOC,'w',encoding='utf-8').write(d)
    print('APPLICATO; doc',len(d),'byte')

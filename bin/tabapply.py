import re,sys,io,glob
sys.path.insert(0,'/home/user/work/bin')
from mk import runs as mkruns
DOC=sys.argv[1]; APPLY='--apply' in sys.argv
d=io.open(DOC,encoding='utf-8').read()
PARAT=re.compile(r'<w:p(?:\s[^>]*)?>(?:(?!<w:p[ >]).)*?</w:p>',re.S)
RUNRX=re.compile(r'<w:r(?:\s[^>]*)?>.*?</w:r>',re.S)
def strip(s): return re.sub(r'\*+','',s)

def load(path):
    out={}; t=None
    for l in io.open(path,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l.strip(): continue
        if l.startswith('#T'): t=int(l[2:]); continue
        if '\t' not in l: continue
        i,tx=l.split('\t',1); out[(t,int(i))]=tx
    return out

edits=[]; nok=0; nbad=0; ntab=set()
for f in sorted(glob.glob('/home/user/work/tab/out_*.txt')):
    n=re.search(r'out_(\d+)',f).group(1)
    src=load(f'/home/user/work/tab/in_{n}.txt'); dst=load(f)
    TAB={}
    for (t,i),tx in src.items():
        if i!=0: continue
        tit=strip(tx).strip()
        hits=[m.start() for m in re.finditer(r'<w:tbl>',d)
              if tit and tit[:60] in ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', d[m.start():d.find('</w:tbl>',m.start())]))[:len(tit)+40]]
        if len(hits)==1: TAB[t]=hits[0]
    for (t,i),tx in dst.items():
        if (t,i) not in src or strip(src[(t,i)])!=strip(tx): nbad+=1; continue
        t0=TAB.get(t)
        if t0 is None: nbad+=1; continue
        e=d.find('</w:tbl>',t0)
        paras=[(m.start()+t0,m.end()+t0,m.group(0)) for m in PARAT.finditer(d[t0:e])]
        if i>=len(paras): nbad+=1; continue
        ps,pe,pm=paras[i]
        rs=list(RUNRX.finditer(pm))
        if not rs: nbad+=1; continue
        base=re.search(r'<w:rPr>.*?</w:rPr>',rs[0].group(0),re.S)
        base=base.group(0) if base else ''
        new=mkruns(tx,base)
        a=ps+rs[0].start(); b=ps+rs[-1].end()
        edits.append((a,b-a,new)); nok+=1; ntab.add(t)
print('righe applicabili:',nok,'| scartate:',nbad,'| tabelle:',len(ntab))
if APPLY:
    for p,L,s in sorted(edits,key=lambda z:-z[0]): d=d[:p]+s+d[p+L:]
    io.open(DOC,'w',encoding='utf-8').write(d)
    print('APPLICATO; doc',len(d),'byte')

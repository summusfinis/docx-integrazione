# Ripara le sei voci d'indice in cui il numero di pagina si era attaccato al titolo.
import io, re, sys
sys.path.insert(0, '/home/user/docx-integrazione/bin')
from xmltext import PARA, nodes

DOC = sys.argv[1]
d = io.open(DOC, encoding='utf-8').read()

# (numero scheda, testo sbagliato in coda al titolo, testo corretto, pagina da mettere dopo il tab)
FIX = [
 (38,  ' alla direttiva CCD233', ' alla direttiva CCD2', '233'),
 (62,  'n. 15895/357',           'n. 15895/2019',        '357'),
 (64,  'n. 8/362',               'n. 8/2023',            '362'),
 (81,  'n. 7513/464',            'n. 7513/2018',         '464'),
 (113, None,                     None,                   '694'),
 (119, None,                     None,                   '721'),
]

P = [(m.start(), m.end(), m.group(0)) for m in PARA.finditer(d)]
TXT = []
for s, e, xml in P:
    t, _ = nodes(d, s, e)
    TXT.append(t)

out = []
for n, bad, good, pag in FIX:
    # la voce d'indice e' il paragrafo che inizia con "Scheda N – " e contiene un hyperlink
    cand = [i for i, t in enumerate(TXT)
            if t.startswith(f'Scheda {n} – ') and 'w:hyperlink' in P[i][2]]
    if len(cand) != 1:
        sys.exit(f'Scheda {n}: voci d indice trovate {len(cand)}')
    i = cand[0]
    s, e, xml = P[i]
    new = xml
    if bad:
        if new.count(bad) != 1:
            sys.exit(f'Scheda {n}: testo "{bad}" trovato {new.count(bad)} volte')
        new = new.replace(bad, good)
    # coda: deve essere <w:tab/><w:t>pagina</w:t>
    new = re.sub(r'<w:t>\.{3,}(\d+)</w:t>', lambda m: f'<w:tab/><w:t>{m.group(1)}</w:t>', new)
    if not re.search(r'<w:tab/><w:t>\d+</w:t>', new):
        if '<w:tab/></w:r>' in new:
            new = new.replace('<w:tab/></w:r>', f'<w:tab/><w:t>{pag}</w:t></w:r>', 1)
        else:
            sys.exit(f'Scheda {n}: niente tab in coda')
    out.append((s, e, new))
    t2, _ = nodes(new + '', 0, len(new))

for s, e, new in sorted(out, key=lambda z: -z[0]):
    d = d[:s] + new + d[e:]
io.open(DOC, 'w', encoding='utf-8').write(d)
print('voci riparate:', len(out))

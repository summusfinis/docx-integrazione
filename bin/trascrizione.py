# Trascrizione continua di un intervallo di pagine del manuale, con marcatori di pagina,
# titoli di capitolo e titoli di paragrafo numerati.
import io, os, re, sys

SRC, OUT = sys.argv[1], sys.argv[2]
OFF = 12
CAP = {3: 'CAPITOLO VII – Contratto e ordinamento giuridico',
       59: 'CAPITOLO VIII – Gli elementi soggettivi del contratto',
       287: 'CAPITOLO IX – Gli elementi oggettivi del contratto',
       495: 'CAPITOLO X – Gli effetti del contratto',
       623: 'CAPITOLO XI – La patologia del contratto',
       801: 'CAPITOLO XII – I contratti del consumatore'}
P0, P1 = int(sys.argv[3]), int(sys.argv[4])

def percorso(p):
    n = (p + OFF) // 2
    s = 'b' if (p + OFF) % 2 else 'a'
    return os.path.join(SRC, 'img-%03d_%s.txt' % (n, s))

def rumore(l):
    if len(l) < 4: return True
    return sum(c.isalpha() or c.isspace() for c in l) < len(l) * 0.6

TIT = re.compile(r'^\d{1,2}(\.\d{1,2}){0,2}\.?\s+[A-ZÀ-Ü][a-zà-ù].{2,55}$')

def blocchi(lines):
    out = []; cur = ''
    lim = max([len(l) for l in lines] or [70]) * 0.80
    for l in lines:
        l = re.sub(r'\s+', ' ', l.strip())
        if not l: continue
        if TIT.match(l):
            if cur: out.append(cur); cur = ''
            out.append('§ ' + l); continue
        if cur.endswith('-'):
            cur = cur[:-1] + l
        elif cur:
            cur += ' ' + l
        else:
            cur = l
        if len(l) < lim:
            out.append(cur); cur = ''
    if cur: out.append(cur)
    return [b for b in out if len(b) > 12 or b.startswith('§')]

res = []
for p in range(P0, P1 + 1):
    f = percorso(p)
    if not os.path.exists(f): continue
    lines = [l.rstrip() for l in io.open(f, encoding='utf-8') if l.strip()]
    while lines and (len(lines[0]) < 55 and (str(p) in lines[0] or re.search(r'(?i)cap\w{0,3}olo|car\w{0,3}olo|cam\w{0,3}olo', lines[0]))):
        lines.pop(0)
    lines = [l for l in lines if not rumore(l)]
    b = blocchi(lines)
    if not b: continue
    if p in CAP: res.append('\n\n# ' + CAP[p])
    res.append('\n[p. %d]' % p)
    res += b
io.open(OUT, 'w', encoding='utf-8').write('\n\n'.join(res) + '\n')
print(OUT, 'pagine', P1 - P0 + 1, '|', sum(len(x.split()) for x in res), 'parole')

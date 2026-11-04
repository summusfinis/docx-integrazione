# Dai file OCR per mezza pagina produce il testo continuo di un intervallo di pagine,
# con marcatori [p. N].  Pagina stampata = 2*indice_immagine + (0|1) - 12.
import io, os, re, sys

SRC, OUT = sys.argv[1], sys.argv[2]
P0, P1 = int(sys.argv[3]), int(sys.argv[4])
OFF = 12

def percorso(p):
    n = (p + OFF) // 2
    s = 'b' if (p + OFF) % 2 else 'a'
    return os.path.join(SRC, 'img-%03d_%s.txt' % (n, s))

def rumore(l):
    if len(l) < 4: return True
    al = sum(c.isalpha() or c.isspace() for c in l)
    return al < len(l) * 0.6

def paragrafi(lines):
    out = []; cur = ''
    for l in lines:
        l = l.strip()
        if not l: continue
        if cur.endswith('-'):
            cur = cur[:-1] + l
        elif cur:
            cur += ' ' + l
        else:
            cur = l
        if re.search(r'[.;:»?!]$', l) and len(l) < 64:
            out.append(cur); cur = ''
    if cur: out.append(cur)
    return [p for p in out if len(p) > 25]

res = []
for p in range(P0, P1 + 1):
    f = percorso(p)
    if not os.path.exists(f): continue
    lines = [l.rstrip() for l in io.open(f, encoding='utf-8') if l.strip()]
    # via l'intestazione corrente: prime righe corte con il numero di pagina
    while lines and (len(lines[0]) < 55 and (str(p) in lines[0] or re.search(r'(?i)cap\w{0,3}olo|car\w{0,3}olo', lines[0]))):
        lines.pop(0)
    lines = [l for l in lines if not rumore(l)]
    t = '\n'.join(paragrafi(lines))
    if t.strip():
        res.append('[p. %d]\n%s' % (p, t))
io.open(OUT, 'w', encoding='utf-8').write('\n\n'.join(res) + '\n')
print(OUT, len(res), 'pagine,', sum(len(x.split()) for x in res), 'parole')

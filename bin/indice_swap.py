import re, sys, io
sys.path.insert(0, '/home/user/work/bin')
from xmltext import paragraphs, nodes, apply_edits, repl_span

DOC = sys.argv[1]; APPLY = '--apply' in sys.argv
d = io.open(DOC, encoding='utf-8').read()
P = paragraphs(d)
def jt(s, e): return nodes(d, s, e)[0].strip()

def find_para(pred, lo=0, hi=None):
    hi = hi if hi is not None else len(d)
    return [(s, e) for s, e in P if s >= lo and s < hi and pred(jt(s, e))]

INDICE_FINE = P[[jt(s,e) for s,e in P].index('Titolo I – I principi generali', 1)][0] if False else None
# confini
t1 = [ (s,e) for s,e in P if jt(s,e).startswith('Titolo I – I principi generali') ]
IDX_END = t1[1][0]                       # inizio corpo
rep = []

def one(pred, lo=0, hi=None, what=''):
    r = find_para(pred, lo, hi)
    if len(r) != 1: sys.exit('AMBIGUO/ASSENTE [%s]: %d' % (what, len(r)))
    return r[0]

# --- paragrafi evidenziati da cancellare
h1 = one(lambda t: t == 'IL TITOLO III DIVENTA IL TITOLO IV E VICEVERSA', 0, IDX_END, 'highlight1')
h2 = one(lambda t: t == '(inverti la scheda 53 con la scheda 54)', 0, IDX_END, 'highlight2')
# --- blocchi indice
i3 = one(lambda t: t.startswith('Titolo III – L’inadempimento'), 0, IDX_END, 'idx T3')
i4 = one(lambda t: t.startswith('Titolo IV – L’estinzione'), 0, IDX_END, 'idx T4')
i5 = one(lambda t: t.startswith('Titolo V – La garanzia patrimoniale'), 0, IDX_END, 'idx T5')
i53 = one(lambda t: t.startswith('Scheda 53 – I patrimoni destinati'), 0, IDX_END, 'idx S53')
i54 = one(lambda t: t.startswith('Scheda 54 – L’azione revocatoria ordinaria e l’azione esecutiva'), 0, IDX_END, 'idx S54')
# --- blocchi corpo
b3 = one(lambda t: t.startswith('Titolo III – L’inadempimento'), IDX_END, None, 'body T3')
b4 = one(lambda t: t.startswith('Titolo IV – L’estinzione'), IDX_END, None, 'body T4')
b5 = one(lambda t: t.startswith('Titolo V – La garanzia patrimoniale'), IDX_END, None, 'body T5')
b53 = one(lambda t: t.startswith('Scheda 53 – I patrimoni destinati'), IDX_END, None, 'body S53')
b54 = one(lambda t: t.startswith('Scheda 54 – L’azione revocatoria ordinaria e l’azione esecutiva'), IDX_END, None, 'body S54')
b55 = one(lambda t: t.startswith('Scheda 55 – Le promesse unilaterali'), IDX_END, None, 'body S55')

blocks = [
    ('corpo 53/54', b53[0], b54[0], b55[0]),
    ('corpo T3/T4', b3[0], b4[0], b5[0]),
    ('indice 53/54', i53[0], i54[0], h2[0]),
    ('indice T3/T4', i3[0], i4[0], i5[0]),
]
for nome, a, b, c in blocks:
    rep.append('%-14s A=[%d,%d) %d byte  B=[%d,%d) %d byte' % (nome, a, b, b-a, b, c, c-b))
rep.append('cancella highlight1 [%d,%d)  highlight2 [%d,%d)' % (h1[0], h1[1], h2[0], h2[1]))

if APPLY:
    # 1) cancellazioni e scambi, dal fondo verso l'inizio
    # ordine decrescente di offset: corpo53/54, corpoT3/T4, h2, indice53/54, indiceT3/T4, h1
    def swap(d, a, b, c): return d[:a] + d[b:c] + d[a:b] + d[c:]
    d = swap(d, b53[0], b54[0], b55[0])
    d = swap(d, b3[0], b4[0], b5[0])
    d = d[:h2[0]] + d[h2[1]:]
    d = swap(d, i53[0], i54[0], h2[0])
    d = swap(d, i3[0], i4[0], i5[0])
    d = d[:h1[0]] + d[h1[1]:]

    # 2) rinumerazione schede e titoli, su testo unito per run
    MAP = {}
    for n in range(22, 29): MAP[n] = n + 17      # 22-28 -> 39-45
    for n in range(29, 46): MAP[n] = n - 7       # 29-45 -> 22-38
    MAP[53] = 54; MAP[54] = 53
    edits = []; nsch = 0; ntit = 0
    for s, e in paragraphs(d):
        t, pos = nodes(d, s, e)
        m = re.search(r'Scheda (\d+)', t)
        if m:
            n = int(m.group(1))
            if n in MAP:
                edits += repl_span(pos, m.start(1), m.end(1), str(MAP[n])); nsch += 1
            continue
        m = re.match(r'\s*Titolo (III|IV) – L’(inadempimento|estinzione)', t)
        if m:
            new = 'IV' if m.group(2) == 'inadempimento' else 'III'
            edits += repl_span(pos, m.start(1), m.end(1), new); ntit += 1
    d = apply_edits(d, edits)
    rep.append('rinumerate %d voci Scheda, %d intestazioni di Titolo' % (nsch, ntit))
    io.open(DOC, 'w', encoding='utf-8').write(d)
    rep.append('APPLICATO; document.xml %d byte' % len(d))
print('\n'.join(rep))

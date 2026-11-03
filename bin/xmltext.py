# utilita': editing del testo di word/document.xml rispettando la frammentazione in run
import re
PARA = re.compile(r'<w:p[ >](?:(?!<w:p[ >]).)*?</w:p>', re.S)
TNODE = re.compile(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>')

def paragraphs(d):
    return [(m.start(), m.end()) for m in PARA.finditer(d)]

def nodes(d, s, e):
    """ritorna (testo_unito, posizioni_assolute)"""
    txt = []; pos = []
    for m in TNODE.finditer(d, s, e):
        base = m.start(1)
        for k, ch in enumerate(m.group(1)):
            txt.append(ch); pos.append(base + k)
    return ''.join(txt), pos

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def apply_edits(d, edits):
    """edits: lista di (abs_pos, old_len, new_str); applicate da destra"""
    for p, L, s in sorted(edits, key=lambda x: -x[0]):
        d = d[:p] + s + d[p + L:]
        
    return d

def repl_span(pos, a, b, new):
    """edits per sostituire i caratteri [a,b) del testo unito con `new`"""
    out = [(pos[i], 1, '') for i in range(a + 1, b)]
    out.append((pos[a], 1, esc(new)))
    return out

# serializza/deserializza i run di un paragrafo in markdown, preservando b/i
import re
RUN = re.compile(r'<w:r(?:\s[^>]*)?>.*?</w:r>', re.S)
TN  = re.compile(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>')
RPR = re.compile(r'<w:rPr>.*?</w:rPr>', re.S)

def chars(pm):
    """[(char, bold, italic, abs_offset_in_pm)] per il paragrafo pm"""
    out = []
    for m in RUN.finditer(pm):
        r = m.group(0)
        pr = RPR.search(r)
        pr = pr.group(0) if pr else ''
        b = ('<w:b/>' in pr); i = ('<w:i/>' in pr)
        for t in TN.finditer(r):
            base = m.start() + t.start(1)
            for k, ch in enumerate(t.group(1)):
                out.append((ch, b, i, base + k))
    return out

def to_md(pm):
    cs = chars(pm)
    out = []; pb = pi = False
    for ch, b, i, _ in cs:
        if i != pi or b != pb:
            if pb and pi: out.append('***')
            elif pb: out.append('**')
            elif pi: out.append('*')
            if b and i: out.append('***')
            elif b: out.append('**')
            elif i: out.append('*')
            pb, pi = b, i
        out.append('&' if ch == '&' else ch)
    if pb and pi: out.append('***')
    elif pb: out.append('**')
    elif pi: out.append('*')
    return ''.join(out)

def italic_spans(pm):
    """estrae i tratti massimali in corsivo (testo piano)"""
    cs = chars(pm); res = []; cur = ''
    for ch, b, i, _ in cs:
        if i: cur += ch
        else:
            if cur.strip(): res.append(cur)
            cur = ''
    if cur.strip(): res.append(cur)
    return res

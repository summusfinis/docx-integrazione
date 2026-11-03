import re
ORDER=['rStyle','rFonts','b','bCs','i','iCs','caps','smallCaps','strike','dstrike','outline','shadow','emboss',
'imprint','noProof','snapToGrid','vanish','webHidden','color','spacing','w','kern','position','sz','szCs',
'highlight','u','effect','bdr','shd','fitText','vertAlign','rtl','cs','em','lang','eastAsianLayout','specVanish','oMath']
TOK=re.compile(r'<w:[a-zA-Z]+[^>]*/>|<w:[a-zA-Z]+[^>]*>(?:(?!</?w:[a-zA-Z]).)*</w:[a-zA-Z]+>',re.S)
def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def rpr(base,b=False,i=False):
    m=re.search(r'<w:rPr>(.*?)</w:rPr>',base,re.S)
    toks=TOK.findall(m.group(1)) if m else []
    toks=[t for t in toks if not re.match(r'<w:(b|i)/>',t)]
    if b: toks.append('<w:b/>')
    if i: toks.append('<w:i/>')
    def k(t):
        n=re.match(r'<w:([a-zA-Z]+)',t).group(1)
        return ORDER.index(n) if n in ORDER else len(ORDER)
    toks.sort(key=k)
    return '<w:rPr>'+''.join(toks)+'</w:rPr>' if toks else ''
def runs(md,base):
    """markdown (**b**, *i*, ***bi***) -> sequenza di <w:r>"""
    md=md.replace('—','–').replace("'",'’')
    out=[];buf='';b=False;i=False;n=0
    def flush():
        nonlocal buf
        if buf: out.append('<w:r>'+rpr(base,b,i)+'<w:t xml:space="preserve">'+esc(buf)+'</w:t></w:r>'); buf=''
    while n<len(md):
        if md[n]=='*':
            c=1
            while n+c<len(md) and md[n+c]=='*' and c<3: c+=1
            flush()
            if c==3: b=not b; i=not i
            elif c==2: b=not b
            else: i=not i
            n+=c
        else: buf+=md[n]; n+=1
    flush()
    return ''.join(out)

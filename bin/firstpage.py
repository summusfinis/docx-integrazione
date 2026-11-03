import re,io,sys
B='/home/user/work/docx/'
# 1) footer vuoto per la prima pagina
ns=re.search(r'<w:ftr[^>]*>',io.open(B+'word/footer1.xml',encoding='utf-8').read()).group(0)
io.open(B+'word/footer2.xml','w',encoding='utf-8').write(
 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'+ns+
 '<w:p><w:pPr><w:pStyle w:val="Pidipagina"/></w:pPr></w:p></w:ftr>')
# 2) relazione
p=B+'word/_rels/document.xml.rels'; s=io.open(p,encoding='utf-8').read()
if 'footer2.xml' not in s:
    rid='rId900'
    s=s.replace('</Relationships>',
      f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer2.xml"/></Relationships>')
    io.open(p,'w',encoding='utf-8').write(s)
# 3) content type
p=B+'[Content_Types].xml'; s=io.open(p,encoding='utf-8').read()
if 'footer2.xml' not in s:
    s=s.replace('</Types>','<Override PartName="/word/footer2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
    io.open(p,'w',encoding='utf-8').write(s)
# 4) sectPr: footerReference first + titlePg
p=B+'word/document.xml'; d=io.open(p,encoding='utf-8').read()
m=list(re.finditer(r'<w:sectPr\b.*?</w:sectPr>',d,re.S))[-1]
sec=m.group(0)
if 'w:type="first"' not in sec:
    sec=sec.replace('<w:footerReference w:type="default"',
        '<w:footerReference w:type="first" r:id="rId900"/><w:footerReference w:type="default"',1)
    sec=re.sub(r'(<w:cols[^>]*/>)',r'\1<w:titlePg/>',sec,count=1)
    d=d[:m.start()]+sec+d[m.end():]
    io.open(p,'w',encoding='utf-8').write(d)
print('prima pagina senza numero: ok')

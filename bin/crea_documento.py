#!/usr/bin/env python3
# Crea la struttura .docx a partire da un file Markdown di contenuto, senza un documento di partenza.
# Output: <DOCX_WORK>/docx/ (pacchetto Word non compresso), che build.sh poi comprime.
#
# Formato di contenuto.md (DOCX_CONTENUTO, default <DOCX_WORK>/contenuto.md):
#   prima della prima intestazione, righe "chiave: valore":  titolo_copertina, sottotitolo
#   "# Titolo I – Nome"           -> titolo (voce d'indice, Titolo1)
#   "## Scheda 1 – Nome"          -> scheda (voce d'indice, Titolo2); il Sommario è generato
#   "### Nome della sezione"      -> sezione (Titolo3), numerata automaticamente
#   "#### Nome"                   -> sottosezione (Titolo4)
#   righe di testo                -> capoversi (una riga vuota separa i capoversi)
#   inline: **grassetto**, *corsivo*, ***grassetto corsivo***
# Le tabelle "Mappa concettuale" non vengono generate: il corpo è solo testo.
import os as _os, sys, io, re
_BIN = _os.path.dirname(_os.path.abspath(__file__))
_WORK = _os.environ.get('DOCX_WORK') or _os.path.join(_os.getcwd(), 'lavoro')
sys.path.insert(0, _BIN)
from mk import runs as mkruns, esc

SRC = _os.environ.get('DOCX_CONTENUTO') or _os.path.join(_WORK, 'contenuto.md')
OUT = _os.path.join(_WORK, 'docx')
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
XMLH = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

# ---------- lettura del contenuto ----------
lines = io.open(SRC, encoding='utf-8').read().split('\n')
meta, items, buf = {}, [], []
def flush():
    if buf:
        items.append(('p', ' '.join(x.strip() for x in buf))); buf.clear()
i = 0
while i < len(lines) and not lines[i].startswith('#'):
    m = re.match(r'^([a-z_]+):\s*(.*)$', lines[i].strip())
    if m: meta[m.group(1)] = m.group(2)
    i += 1
for ln in lines[i:]:
    h = re.match(r'^(#{1,4}) (.*)$', ln)
    if h:
        flush(); items.append((f'h{len(h.group(1))}', h.group(2).strip()))
    elif ln.strip() == '':
        flush()
    else:
        buf.append(ln)
flush()

# ---------- struttura: titoli, schede, sezioni ----------
tree = []   # [('h1', testo, n), ('h2', testo, n, sezioni[]), ...]
for kind, txt in items:
    if kind == 'h1': tree.append({'k': 'h1', 'txt': txt, 'id': f"h{len(tree)+1}", 'blocks': []})
    elif kind == 'h2':
        tree.append({'k': 'h2', 'txt': txt, 'id': f"h{len(tree)+1}", 'blocks': []})
    elif kind == 'h3':
        tree[-1]['blocks'].append(('h3', re.sub(r'^\d+\.\s*', '', txt)))
    elif kind == 'h4':
        tree[-1]['blocks'].append(('h4', txt))
    else:
        if not tree: tree.append({'k': 'h1', 'txt': '', 'id': 'h1', 'blocks': []})
        tree[-1]['blocks'].append(('p', txt))

# ---------- XML ----------
def para(style, runs_xml, extra_ppr=''):
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{extra_ppr}</w:pPr>{runs_xml}</w:p>'
def bm(name, idn, inner):
    return f'<w:bookmarkStart w:id="{idn}" w:name="{name}"/>{inner}<w:bookmarkEnd w:id="{idn}"/>'

body, toc = [], []
body.append(para('Copertina', mkruns(meta.get('titolo_copertina', 'TITOLO'), '')))
if meta.get('sottotitolo'):
    body.append(para('Sottotitolo', mkruns(meta['sottotitolo'], '')))
body.append(para('Titolo1', mkruns('INDICE', ''), '<w:pageBreakBefore/>'))
idn = 1
index_xml = []
for node in tree:
    if node['k'] == 'h1' and node['txt']:
        index_xml.append(('h1', node['txt'], node['id']))
    elif node['k'] == 'h2':
        index_xml.append(('h2', node['txt'], node['id']))
# indice: una riga per titolo e per scheda, con numero di pagina segnaposto (aggiornato da indice_pagine.py)
for kind, txt, anc in index_xml:
    ind = '' if kind == 'h1' else '<w:ind w:left="340"/>'
    rpr_b = '<w:b/>' if kind == 'h1' else ''
    plain = esc(txt.replace('*', '').replace('\u2014', '\u2013'))
    link = (f'<w:hyperlink w:anchor="{anc}" w:history="1"><w:r><w:rPr>{rpr_b}</w:rPr>'
            f'<w:t xml:space="preserve">{plain}</w:t></w:r></w:hyperlink>')
    body.append(f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9071"/></w:tabs>'
                f'<w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/>{ind}</w:pPr>'
                f'{link}<w:r><w:tab/><w:t>0</w:t></w:r></w:p>')
body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

def emit_blocks(blocks):
    n = 0
    for k, t in blocks:
        if k == 'h3':
            n += 1
            body.append(para('Titolo3', mkruns(f'{n}. {t}', ''), '<w:keepNext/>'))
        elif k == 'h4':
            body.append(para('Titolo4', mkruns(t, '')))
        else:
            body.append(para('Normale', mkruns(t, '')))

for node in tree:
    if node['k'] == 'h1':
        if node['txt']:
            body.append(para('Titolo1', bm(node['id'], idn, mkruns(node['txt'], '')), '<w:pageBreakBefore/>')); idn += 1
        emit_blocks([b for b in node['blocks'] if b[0] == 'p'])
        continue
    # scheda
    body.append(para('Titolo2', bm(node['id'], idn, mkruns(node['txt'], '')), '<w:pageBreakBefore/>')); idn += 1
    secs = [t for k, t in node['blocks'] if k == 'h3']
    if secs:
        som = ' – '.join(f'{i}. {t}' for i, t in enumerate(secs, 1))
        body.append(f'<w:p><w:pPr><w:pStyle w:val="Sommario"/></w:pPr>'
                    f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Sommario: </w:t></w:r>'
                    f'{mkruns(som, "")}</w:p>')
    emit_blocks(node['blocks'])

sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rId8"/>'
        '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1417" w:right="1417" w:bottom="1417" '
        'w:left="1417" w:header="720" w:footer="720" w:gutter="0"/><w:cols w:space="720"/></w:sectPr>')
doc = f'{XMLH}<w:document {NS}><w:body>{"".join(body)}{sect}</w:body></w:document>'

FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"/>'
def style(sid, name, ppr, rpr, based='Normale'):
    b = f'<w:basedOn w:val="{based}"/>' if based and sid != 'Normale' else ''
    return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/>{b}'
            f'<w:pPr>{ppr}</w:pPr><w:rPr>{FONT}{rpr}</w:rPr></w:style>')
styles = (XMLH + f'<w:styles {NS}><w:docDefaults><w:rPrDefault><w:rPr>{FONT}<w:color w:val="000000"/>'
          '<w:sz w:val="23"/><w:lang w:val="it-IT"/></w:rPr></w:rPrDefault><w:pPrDefault/></w:docDefaults>'
          + style('Normale', 'Normale', '<w:spacing w:before="0" w:after="0" w:line="276" w:lineRule="auto"/><w:jc w:val="both"/>', '<w:sz w:val="23"/>', None)
          + style('Copertina', 'Copertina', '<w:spacing w:before="2400" w:after="240"/><w:jc w:val="center"/>', '<w:b/><w:sz w:val="36"/>')
          + style('Sottotitolo', 'Sottotitolo', '<w:spacing w:after="240"/><w:jc w:val="center"/>', '<w:b/><w:sz w:val="28"/>')
          + style('Titolo1', 'Titolo 1', '<w:keepNext/><w:spacing w:before="0" w:after="240"/><w:jc w:val="center"/><w:outlineLvl w:val="0"/>', '<w:b/><w:sz w:val="28"/>')
          + style('Titolo2', 'Titolo 2', '<w:keepNext/><w:spacing w:before="0" w:after="160"/><w:jc w:val="both"/><w:outlineLvl w:val="1"/>', '<w:b/><w:sz w:val="25"/>')
          + style('Titolo3', 'Titolo 3', '<w:keepNext/><w:spacing w:before="200" w:after="60"/><w:jc w:val="both"/><w:outlineLvl w:val="2"/>', '<w:b/><w:sz w:val="23"/>')
          + style('Titolo4', 'Titolo 4', '<w:keepNext/><w:spacing w:before="160" w:after="40"/><w:jc w:val="both"/><w:outlineLvl w:val="3"/>', '<w:b/><w:i/><w:sz w:val="23"/>')
          + style('Sommario', 'Sommario', '<w:spacing w:before="40" w:after="160" w:line="264" w:lineRule="auto"/><w:ind w:left="227" w:right="227"/><w:jc w:val="both"/>', '<w:sz w:val="20"/>')
          + style('Pidipagina', 'Pidipagina', '<w:jc w:val="center"/>', '<w:sz w:val="18"/>')
          + '</w:styles>')
footer = (XMLH + f'<w:ftr {NS}><w:p><w:pPr><w:pStyle w:val="Pidipagina"/></w:pPr>'
          '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
          '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>'
          '</w:p></w:ftr>')
rels = (XMLH + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        '</Relationships>')
ctypes = (XMLH + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
          '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
          '</Types>')
pkg_rels = (XMLH + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            '</Relationships>')
core = (XMLH + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f'<dc:title>{esc(meta.get("titolo_copertina", ""))}</dc:title></cp:coreProperties>')
app = (XMLH + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>docx-integrazione</Application></Properties>')

files = {
    '[Content_Types].xml': ctypes, '_rels/.rels': pkg_rels,
    'word/document.xml': doc, 'word/styles.xml': styles, 'word/footer1.xml': footer,
    'word/_rels/document.xml.rels': rels, 'docProps/core.xml': core, 'docProps/app.xml': app,
}
for rel, content in files.items():
    p = _os.path.join(OUT, rel); _os.makedirs(_os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(content)
print('documento creato:', sum(1 for n in tree if n['k'] == 'h2'), 'schede,',
      sum(1 for n in tree if n['k'] == 'h1' and n['txt']), 'titoli')

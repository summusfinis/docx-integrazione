#!/usr/bin/env python3
# Misura le pagine delle schede e dei titoli nel documento e scrive <DOCX_WORK>/pagine.json,
# che indice_pagine.py usa per aggiornare l'indice. Richiede LibreOffice (soffice) e pdftotext.
# Variabili: DOCX_WORK, DOCX_PRIMO_TITOLO (testo di inizio del primo titolo, default 'Titolo I – ')
import os as _os, sys, io, re, json, shutil, subprocess
_BIN = _os.path.dirname(_os.path.abspath(__file__))
_WORK = _os.environ.get('DOCX_WORK') or _os.path.join(_os.getcwd(), 'lavoro')
PRIMO = _os.environ.get('DOCX_PRIMO_TITOLO', 'Titolo I – ')
chk = _os.path.join(_WORK, 'chk'); _os.makedirs(chk, exist_ok=True)
shutil.copy(_os.path.join(_WORK, 'out.docx'), chk)
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', chk,
                _os.path.join(chk, 'out.docx')], check=True, timeout=1800,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(['pdftotext', '-q', _os.path.join(chk, 'out.pdf'), _os.path.join(chk, 'out.txt')], check=True)
pages = io.open(_os.path.join(chk, 'out.txt'), encoding='utf-8').read().split('\f')
start = max(i for i, p in enumerate(pages, 1) if PRIMO in p)
m = {}
for i, p in enumerate(pages, 1):
    if i < start: continue
    for k in re.findall(r'(?:Scheda \d+|Titolo [IVX]+) – ', p):
        k = k[:-3]
        if k not in m: m[k] = i
io.open(_os.path.join(_WORK, 'pagine.json'), 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False))
print('pagine misurate:', len(m), '| totale pagine:', len(pages) - 1)

#!/usr/bin/env bash
# Ricostruisce out.docx a partire dal .docx sorgente.
# Variabili: DOCX_WORK (cartella di lavoro, default ./lavoro), DOCX_SOURCE (default $DOCX_WORK/sorgente.docx)
set -e
BIN="$(cd "$(dirname "$0")" && pwd)"
export DOCX_WORK="${DOCX_WORK:-$PWD/lavoro}"
SRC="${DOCX_SOURCE:-$DOCX_WORK/sorgente.docx}"
mkdir -p "$DOCX_WORK"
cd "$DOCX_WORK"
rm -rf docx out.docx && mkdir docx && unzip -q "$SRC" -d docx
cd docx/word
P="python3 -I"
$P "$BIN/indice_swap.py"  document.xml --apply | tail -1
$P "$BIN/corsivi.py"      document.xml --apply | tail -1
$P "$BIN/tabapply.py"     document.xml --apply | tail -2
$P "$BIN/integra.py"      document.xml --apply | tail -2
$P "$BIN/nuove.py"        document.xml --apply | tail -8
$P "$BIN/sistema.py"      document.xml --apply | tail -3
$P "$BIN/corsivi.py"      document.xml --apply | tail -1
$P "$BIN/firstpage.py"
$P "$BIN/indice_pagine.py" document.xml
$P -c "from xml.etree import ElementTree as ET; ET.parse('document.xml'); print('XML valido')"
cd "$DOCX_WORK/docx" && zip -q -r -X "$DOCX_WORK/out.docx" '[Content_Types].xml' _rels docProps word customXml
ls -la "$DOCX_WORK/out.docx" | awk '{print "out.docx", $5}'

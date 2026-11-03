#!/usr/bin/env bash
# Costruisce <DOCX_WORK>/out.docx.
#  - se esiste <DOCX_WORK>/sorgente.docx (o DOCX_SOURCE), parte da quel documento;
#  - altrimenti crea il documento da <DOCX_WORK>/contenuto.md (o DOCX_CONTENUTO), con crea_documento.py.
# Passi opzionali, solo per il caso del compendio di partenza:
#  DOCX_SCAMBI=1  scambi di titoli e schede (indice_swap.py)
#  DOCX_NUOVE=1   inserimento di schede nuove da delta/*.json (nuove.py)
set -e
BIN="$(cd "$(dirname "$0")" && pwd)"
export DOCX_WORK="${DOCX_WORK:-$PWD/lavoro}"
SRC="${DOCX_SOURCE:-$DOCX_WORK/sorgente.docx}"
mkdir -p "$DOCX_WORK"
cd "$DOCX_WORK"
rm -rf docx out.docx
if [ -f "$SRC" ]; then
  mkdir docx && unzip -q "$SRC" -d docx
else
  python3 -I "$BIN/crea_documento.py"
fi
cd docx/word
P="python3 -I"
[ -n "$DOCX_SCAMBI" ] && $P "$BIN/indice_swap.py" document.xml --apply | tail -1
$P "$BIN/corsivi.py"      document.xml --apply | tail -1
$P "$BIN/tabapply.py"     document.xml --apply | tail -2
$P "$BIN/integra.py"      document.xml --apply | tail -2
[ -n "$DOCX_NUOVE" ] && $P "$BIN/nuove.py" document.xml --apply | tail -8
$P "$BIN/sistema.py"      document.xml --apply | tail -3
$P "$BIN/corsivi.py"      document.xml --apply | tail -1
$P "$BIN/firstpage.py"
$P "$BIN/indice_pagine.py" document.xml
$P -c "from xml.etree import ElementTree as ET; ET.parse('document.xml'); print('XML valido')"
cd "$DOCX_WORK/docx"
parti=()
for x in '[Content_Types].xml' _rels docProps word customXml; do [ -e "$x" ] && parti+=("$x"); done
rm -f "$DOCX_WORK/out.docx"
zip -q -r -X "$DOCX_WORK/out.docx" "${parti[@]}"
ls -la "$DOCX_WORK/out.docx" | awk '{print "out.docx", $5}'

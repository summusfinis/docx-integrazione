set -e
cd /home/user/work
rm -rf docx out.docx && mkdir docx && cd docx && unzip -q /home/user/src/pg.docx
cd word
python3 -I /home/user/work/bin/indice_swap.py document.xml --apply | tail -1
python3 -I /home/user/work/bin/corsivi.py   document.xml --apply | tail -1
python3 -I /home/user/work/bin/tabapply.py  document.xml --apply | tail -2
python3 -I /home/user/work/bin/integra.py   document.xml --apply | tail -2
python3 -I /home/user/work/bin/nuove.py     document.xml --apply | tail -8
python3 -I /home/user/work/bin/sistema.py   document.xml --apply | tail -3
python3 -I /home/user/work/bin/corsivi.py   document.xml --apply | tail -1
python3 -I /home/user/work/bin/firstpage.py
python3 -I /home/user/work/bin/indice_pagine.py document.xml
python3 -I -c "from xml.etree import ElementTree as ET; ET.parse('document.xml'); print('XML valido')"
cd /home/user/work/docx && zip -q -r -X ../out.docx '[Content_Types].xml' _rels docProps word customXml
cd /home/user/work && ls -la out.docx | awk '{print "out.docx", $5}'

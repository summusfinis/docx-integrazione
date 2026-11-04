# Estrae il testo delle schede indicate dal document.xml, in markdown leggero.
import io, re, sys
sys.path.insert(0, '/home/user/docx-integrazione/bin')
from xmltext import PARA, nodes

DOC, OUT = sys.argv[1], sys.argv[2]
nums = set()
for a in sys.argv[3:]:
    if '-' in a:
        x, y = a.split('-'); nums |= set(range(int(x), int(y)+1))
    else:
        nums.add(int(a))

d = io.open(DOC, encoding='utf-8').read()
P = []
for m in PARA.finditer(d):
    t, _ = nodes(d, m.start(), m.end())
    st = re.search(r'w:pStyle w:val="(Titolo\d)"', m.group(0))
    P.append((st.group(1) if st else '', t))

out = []
cur = None
for st, t in P:
    if st == 'Titolo2':
        mm = re.match(r'Scheda (\d+) – ', t)
        cur = int(mm.group(1)) if mm else None
        if cur in nums:
            out.append('\n## ' + t)
        continue
    if st == 'Titolo1':
        cur = None
        continue
    if cur in nums and t.strip():
        if st == 'Titolo3':
            out.append('\n### ' + t.strip())
        elif st == 'Titolo4':
            out.append('\n#### ' + t.strip())
        else:
            out.append(t.strip())
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(OUT, len(out), 'paragrafi')

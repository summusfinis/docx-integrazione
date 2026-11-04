# Mappa: per ogni mezza pagina OCR, numero di pagina stampato e titolo corrente.
import io, os, re, sys, glob
SRC = sys.argv[1]
rows = []
for f in sorted(glob.glob(os.path.join(SRC, 'img-*_[ab].txt'))):
    b = os.path.basename(f)
    n = int(b[4:7]); side = b[8]
    lines = [l.strip() for l in io.open(f, encoding='utf-8') if l.strip()][:4]
    pg = None; hd = ''
    for l in lines:
        if len(l) > 75: continue
        m = re.match(r'^[^\w]{0,4}(\d{1,4})\s+([A-Za-zÀ-ü].{2,45})$', l)
        if m: pg, hd = int(m.group(1)), m.group(2); break
        m = re.match(r'^([A-Za-zÀ-ü].{2,45}?)\s+(\d{1,4})[^\w]{0,4}$', l)
        if m: pg, hd = int(m.group(2)), m.group(1); break
    rows.append((n, side, pg, hd))
io.open(os.path.join(SRC, '..', 'mappa.txt'), 'w', encoding='utf-8').write(
    '\n'.join(f'{n:03d}{s}\t{p if p else ""}\t{h}' for n, s, p, h in rows))
print('righe', len(rows), '| con numero', sum(1 for r in rows if r[2]))

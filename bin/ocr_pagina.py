import sys, os, subprocess
from PIL import Image

src, outdir, tmpdir = sys.argv[1], sys.argv[2], sys.argv[3]
base = os.path.splitext(os.path.basename(src))[0]
im = Image.open(src).convert('L')
W, H = im.size
small = im.resize((300, max(10, int(300*H/W))))
px = small.load(); w, h = small.size
cols = [sum(px[x, y] for y in range(h))/h for x in range(w)]
rows = [sum(px[x, y] for x in range(w))/w for y in range(h)]
thr = max(cols)*0.62
xs = [x for x in range(w) if cols[x] > thr]
ys = [y for y in range(h) if rows[y] > max(rows)*0.62]
if not xs or not ys:
    sys.exit(0)
x0, x1, y0, y1 = xs[0], xs[-1], ys[0], ys[-1]
a = x0 + int((x1-x0)*0.40); b = x0 + int((x1-x0)*0.60)
g = min(range(a, b+1), key=lambda x: cols[x])
sx, sy = W/w, H/h
ins = (x1-x0)*0.015

def run(cx0, cx1, tag):
    L = max(0, int(cx0*sx)); R = min(W, int(cx1*sx))
    T = max(0, int(y0*sy)); B = min(H, int(y1*sy))
    if R-L < 150 or B-T < 150: return
    p0 = os.path.join(tmpdir, base+tag+'_0.png')
    p1 = os.path.join(tmpdir, base+tag+'_1.png')
    p2 = os.path.join(tmpdir, base+tag+'_2.png')
    im.crop((L, T, R, B)).resize(((R-L)*3, (B-T)*3), Image.LANCZOS).save(p0)
    subprocess.run(['convert', p0, '-lat', '50x50-10%', '-negate', p1], check=False)
    subprocess.run(['convert', p1, '-morphology', 'Open', 'Rectangle:45x1', p2], check=False)
    from PIL import ImageChops
    m = Image.open(p1).convert('L'); ln = Image.open(p2).convert('L')
    ImageChops.invert(ImageChops.subtract(m, ln)).save(p0)
    o = os.path.join(outdir, base+tag)
    subprocess.run(['tesseract', p0, o, '-l', 'ita', '--psm', '4'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for p in (p0, p1, p2):
        try: os.remove(p)
        except OSError: pass

run(x0+ins, g, '_a')
run(g, x1-ins, '_b')

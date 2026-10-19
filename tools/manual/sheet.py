import sys, glob
from PIL import Image, ImageDraw
files = sys.argv[2:]
cols = 4; tw, th = 480, 314
rows = (len(files) + cols - 1) // cols
S = Image.new("RGB", (cols * tw, rows * (th + 22)), (255, 255, 255))
d = ImageDraw.Draw(S)
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB"); im.thumbnail((tw, th))
    x, y = (i % cols) * tw, (i // cols) * (th + 22)
    S.paste(im, (x, y + 22)); d.text((x + 6, y + 4), f.split("/")[-1], fill=(0, 0, 0))
S.save(sys.argv[1])

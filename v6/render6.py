"""
Check renders for v6 (one tablet): button reliefs, the plug/loop cavity and the lateral stops.

    V6_TABLET=ipad_pro_11_m5 python render6.py out/renders_ipad_pro_11_m5
"""
import os
import sys

sys.path.insert(0, "/home/claude/ipad-pro-wall-mount/tools/manual")
import mr  # noqa: E402

_orig = mr._stl
mr._stl = lambda s: s if isinstance(s, str) else _orig(s)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import float6 as h  # noqa: E402

tab = h.TAB
dst = sys.argv[1]
os.makedirs(dst, exist_ok=True)
SH = {"_ipad": h.ipad, "_plug": h.plug, "_bracket": h.br, "_hanger": h.hanger_a}
P = lambda n: SH[n]
car = [(h.car_a, "print", 1.0)]
L, W = tab["L"], tab["W"]
Z = h.STANDOFF

# 1. whole carrier + iPad from the front, shell hidden
mr.render(f"{dst}/carrier_front.png", car + [(P("_ipad"), "ipad", 0.35), (P("_plug"), "plug", 1.0)],
          cam=(0, -60, 900), w=1400, h=1000)
# 2. each button relief, close up, iPad ghosted
for i, b in enumerate(tab["buttons"]):
    if b[0] in ("top", "bottom"):
        sy = 1 if b[0] == "top" else -1
        fp = ((b[1] + b[2]) / 2, sy * W / 2, Z + 4)
        cam = (fp[0] - 10, fp[1] + sy * 70, Z + 90)
    else:
        sx = 1 if b[0] == "+x" else -1
        fp = (sx * L / 2, (b[1] + b[2]) / 2, Z + 4)
        cam = (fp[0] + sx * 70, fp[1] - 10, Z + 90)
    clip = h.box(fp[0] - 40, fp[0] + 40, fp[1] - 40, fp[1] + 40, -100, 100)
    mr.render(f"{dst}/button_{i+1}.png", [(h.car_a.intersect(clip), "print", 1.0), (h.ipad.intersect(clip), "ipad", 0.5)],
              cam=cam, w=1200, h=800)
# 3. USB-C end: plug in its cavity
clip = h.box(L / 2 - 20, L / 2 + 50, -35, 35, -100, 100)
mr.render(f"{dst}/usb_end.png", [(h.car_a.intersect(clip), "print", 1.0), (h.ipad.intersect(clip), "ipad", 0.5),
                                 (h.plug, "plug", 1.0), (h.bend, "hw", 1.0)],
          cam=(L / 2 + 60, -90, Z + 140), w=1200, h=800)
# 4. lateral stops: wall bracket + catch rail + hanger, from the front-top
clip = h.box(-90, 90, h.HOOK_Y - 30, h.HOOK_Y + 40, -100, 100)
mr.render(f"{dst}/stops.png", [(h.br.intersect(clip), "active", 1.0), (h.hanger_a.intersect(clip), "print", 1.0)],
          cam=(0, h.HOOK_Y + 160, 260), w=1400, h=900)
print("renders in", dst)

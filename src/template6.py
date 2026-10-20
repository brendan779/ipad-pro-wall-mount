"""
Full-size A3 plasterboard cut-out template for the v6 Flush mount (any tablet in tablets.py).

    V6_TABLET=ipad_mini_a17_pro python template6.py out/flush_ipad_mini_a17_pro/CUTOUT_TEMPLATE_A3.pdf
"""
import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import flush6 as f

PT = 72 / 25.4
W, H = 420.0, 297.0
fig = plt.figure(figsize=(W / 25.4, H / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")
C = (W / 2, H / 2 + 12)


def rr(w, h, r, n=32):
    pts = []
    for qx, qy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        cx, cy = C[0] + qx * (w / 2 - r), C[1] + qy * (h / 2 - r)
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    return zip(*pts)


def T(x, y, s, size=3.0, ha="center", weight="normal", color="#111"):
    ax.text(x, y, s, fontsize=size * PT, ha=ha, va="center", fontweight=weight, color=color, family="DejaVu Sans")


hr = f.BOX_R + f.HOLE_CLR
if f.HOLE_X > W - 8 or f.TRIM_X > W - 4:
    raise SystemExit("cut-out does not fit on A3")
ax.plot(*rr(f.TRIM_X, f.TRIM_Y, f.TRIM_R), lw=0.35 * PT, ls=(0, (6, 3)), color="#999")
ax.plot(*rr(f.HOLE_X, f.HOLE_Y, hr), lw=0.6 * PT, color="#111")
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = C[0] + sx * (f.HOLE_X / 2 - hr), C[1] + sy * (f.HOLE_Y / 2 - hr)
        ax.plot([x - 4, x + 4], [y, y], lw=0.3 * PT, color="#111")
        ax.plot([x, x], [y - 4, y + 4], lw=0.3 * PT, color="#111")
ax.plot([C[0] - 10, C[0] + 10], [C[1], C[1]], lw=0.25 * PT, color="#111")
ax.plot([C[0], C[0]], [C[1] - 10, C[1] + 10], lw=0.25 * PT, color="#111")
cx = C[0] + f.CAT6_X
ax.add_patch(plt.Circle((cx, C[1]), 6, fill=False, lw=0.3 * PT, ls=(0, (2, 2)), color="#111"))
T(cx, C[1] - 10, "Cat6 enters box here", 2.6)
stud_face = f.STUD_CC / 2 - 45.0 / 2
spare = math.floor(stud_face - (f.CLAMP_X + f.ARM_REACH))
T(C[0], C[1] + f.HOLE_Y / 2 - 9, "TOP ↑", 4.0, weight="bold")
T(C[0], C[1] + 22, f"CUT ON SOLID LINE • {f.HOLE_X:.1f} × {f.HOLE_Y:.1f} mm • R{hr:.0f} corners "
  f"(drill Ø{2 * hr:.0f} at the 4 crosses first)", 3.2, weight="bold")
T(C[0], C[1] + 15, "Dashed grey = trim outline (covers the cut edge)", 2.6, color="#555")
T(C[0], C[1] - 22, f"Centre the hole between two studs (450 c/c). Max {spare} mm off-centre so the clamp arms clear the studs.", 2.6)
T(C[0], C[1] - 28, f"Check with a stud finder and look inside before cutting: no cables or pipes in the "
  f"{math.ceil(f.SLEEVE_D + f.BACK_T)} mm deep box zone.", 2.6)
T(W / 2, 20, f"{f.TAB['name']} Flush Mount v6 • plasterboard cut-out template", 3.4, weight="bold")
T(W / 2, 13, "Print at 100% / Actual size on A3. This bar must measure exactly 100 mm.", 2.8)
bx = W / 2 - 50
ax.plot([bx, bx + 100], [7, 7], lw=1.2 * PT, color="#111", solid_capstyle="butt")
for i in range(11):
    ax.plot([bx + 10 * i, bx + 10 * i], [5.5, 8.5 if i % 5 else 9.5], lw=0.3 * PT, color="#111")
out = sys.argv[1] if len(sys.argv) > 1 else "CUTOUT_TEMPLATE_A3.pdf"
fig.savefig(out)
print("wrote", out, f"{f.HOLE_X:.1f} x {f.HOLE_Y:.1f}, max off-centre {spare}")

"""
A3 manufacturing drawing for the Float Mount v4.2 aluminium shell (for JLCCNC or any CNC shop).
Every number comes from hybrid42.py, so the sheet always matches shell_6061.step.

    python drawing42.py out_hybrid_v42/machine/shell_6061_drawing.pdf
"""
import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
from shapely import affinity

import hybrid42 as h

PT = 72 / 25.4                 # points per mm (text sizes are given in mm)
INK, THIN, MID, THICK = "#111111", 0.18, 0.25, 0.5
W_A3, H_A3 = 420, 297

fig = plt.figure(figsize=(W_A3 / 25.4, H_A3 / 25.4))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W_A3)
ax.set_ylim(0, H_A3)
ax.set_aspect("equal")
ax.axis("off")


def T(x, y, s, size=2.5, ha="left", va="baseline", weight="normal", rot=0, color=INK):
    ax.text(x, y, s, fontsize=size * PT, ha=ha, va=va, fontweight=weight, rotation=rot, color=color,
            family="DejaVu Sans")


def line(pts, lw=THICK, ls="-", color=INK):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, lw=lw * PT, ls=ls, color=color, solid_capstyle="butt")


def outline(geom, tf, lw=THICK, ls="-"):
    polys = geom.geoms if hasattr(geom, "geoms") else [geom]
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            line([tf(x, y) for x, y in ring.coords], lw=lw, ls=ls)


def arrow_dim(p0, p1, text, off_text=1.2, size=2.5, rot=None, lw=THIN):
    """dimension line with arrowheads between p0 and p1 (paper mm) and centred text"""
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<|-|>,head_length=0.55,head_width=0.18",
                                                       lw=lw * PT, color=INK, shrinkA=0, shrinkB=0))
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0])) if rot is None else rot
    if ang > 90 or ang < -90:
        ang += 180
    nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
    T(mx + nx * off_text, my + ny * off_text, text, size=size, ha="center", va="center", rot=ang)


def ext(p0, p1):
    line([p0, p1], lw=THIN)


def leader(p_tip, p_text, text, size=2.5, ha="left"):
    ax.annotate("", xy=p_tip, xytext=p_text, arrowprops=dict(arrowstyle="-|>,head_length=0.55,head_width=0.18",
                                                             lw=THIN * PT, color=INK, shrinkA=0, shrinkB=0))
    T(p_text[0] + (0.8 if ha == "left" else -0.8), p_text[1], text, size=size, ha=ha, va="center")


def rrect(w, hgt, r, cx=0.0, cy=0.0, n=24):
    pts = []
    for qx, qy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx, ccy = cx + qx * (w / 2 - r), cy + qy * (hgt / 2 - r)
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return Polygon(pts)


def stadium(cx, cy, length_y, width_x):
    r = width_x / 2
    return unary_union([sbox(cx - r, cy - (length_y / 2 - r), cx + r, cy + (length_y / 2 - r)),
                        Point(cx, cy + length_y / 2 - r).buffer(r, 64), Point(cx, cy - length_y / 2 + r).buffer(r, 64)])


# ------------------------------------------------------------------ geometry (part mm, STEP frame)
L, Wd, R = h.OUT_L, h.OUT_W, h.OUT_R
WL, WW, WR = h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP
NX = -(h.IPAD_L / 2 - h.LIP)
outer = rrect(L, Wd, R)
window = unary_union([rrect(WL, WW, WR), stadium(NX, 0, h.CAM_FRONT_W, 8.4)])
skirt_in = rrect(L - 2 * h.SKIRT, Wd - 2 * h.SKIRT, R - h.SKIRT)
plug_top = h.EDGE_Z + h.PLUG_H / 2 + 0.3
relief = sbox(h.IPAD_L / 2 - 1, -(h.PLUG_W / 2 + 1), h.IPAD_L / 2 + h.PLUG_L + 2, h.PLUG_W / 2 + 1)
relief_d = plug_top - h.PLATE_Z0

holesA = sorted(h.BOSS_PTS, key=lambda p: (p[0] > 0, -p[1]))          # M3 ends
holesB = sorted(h.LONG_PTS, key=lambda p: (-p[1], p[0]))              # M2.5 top/bottom
ids = [(f"A{i+1}", x, y, "A") for i, (x, y) in enumerate(holesA)] + \
      [(f"B{i+1}", x, y, "B") for i, (x, y) in enumerate(holesB)]
bosses = []
for (x, y) in h.BOSS_PTS:
    bosses.append(Point(x, y).buffer(h.BOSS_R, 64))
for (x, y) in h.LONG_PTS:
    sy = 1 if y > 0 else -1
    tie = sbox(x - h.BOSS_R_LONG, min(y, sy * (Wd / 2 - h.SKIRT / 2)), x + h.BOSS_R_LONG, max(y, sy * (Wd / 2 - h.SKIRT / 2)))
    bosses.append(unary_union([Point(x, y).buffer(h.BOSS_R_LONG, 64), tie]).intersection(skirt_in))
boss_geom = unary_union(bosses)

S = 0.5                                         # views at 1:2
FC = (110, 213)                                 # front view centre on paper
BC = (110, 80)                                  # back view centre on paper
tf_front = lambda x, y: (FC[0] + x * S, FC[1] + y * S)
tf_back = lambda x, y: (BC[0] - x * S, BC[1] + y * S)   # seen from behind: X mirrored

# ------------------------------------------------------------------ sheet frame
line([(10, 10), (410, 10), (410, 287), (10, 287), (10, 10)], lw=0.7)
for i in range(1, 8):
    x = 10 + i * 50
    line([(x, 287), (x, 290)], lw=THIN); line([(x, 10), (x, 7)], lw=THIN)

# ------------------------------------------------------------------ FRONT VIEW
outline(outer, tf_front)
outline(window, tf_front)
for g in (outer, window):               # tangent line of the R0.8 front edge
    outline(g.buffer(-0.8 if g is outer else 0.8, 32), tf_front, lw=THIN)
line([tf_front(-L / 2 - 6, 0), tf_front(L / 2 + 6, 0)], lw=THIN, ls=(0, (8, 2, 1, 2)))
line([tf_front(0, -Wd / 2 - 6), tf_front(0, Wd / 2 + 6)], lw=THIN, ls=(0, (8, 2, 1, 2)))
T(FC[0], FC[1] + Wd * S / 2 + 10.5, "FRONT VIEW (FACE A, COSMETIC)  1:2", size=3.2, ha="center", weight="bold")
# overall
y0 = FC[1] + Wd * S / 2
ext(tf_front(-L / 2, Wd / 2 - 20), (tf_front(-L / 2, 0)[0], y0 + 7))
ext(tf_front(L / 2, Wd / 2 - 20), (tf_front(L / 2, 0)[0], y0 + 7))
arrow_dim((tf_front(-L / 2, 0)[0], y0 + 5), (tf_front(L / 2, 0)[0], y0 + 5), f"{L:.1f}")
xl = FC[0] - L * S / 2
ext(tf_front(-L / 2 - 1, -Wd / 2), (xl - 12, tf_front(0, -Wd / 2)[1]))
ext(tf_front(-L / 2 - 1, Wd / 2), (xl - 12, tf_front(0, Wd / 2)[1]))
arrow_dim((xl - 10, tf_front(0, -Wd / 2)[1]), (xl - 10, tf_front(0, Wd / 2)[1]), f"{Wd:.1f}")
# window
arrow_dim(tf_front(-WL / 2, -WW / 2 + 22), tf_front(WL / 2, -WW / 2 + 22), f"WINDOW {WL:.1f}")
arrow_dim(tf_front(WL / 2 - 30, -WW / 2), tf_front(WL / 2 - 30, WW / 2), f"{WW:.1f}")
# frame widths
arrow_dim(tf_front(WL / 2, 60), tf_front(L / 2, 60), f"{(L - WL) / 2:.2f}", off_text=-1.6)
arrow_dim(tf_front(60, -WW / 2), tf_front(60, -Wd / 2), f"{(Wd - WW) / 2:.2f}", off_text=-2.4, rot=90)
leader(tf_front(L / 2 - R * 0.29, Wd / 2 - R * 0.29), (tf_front(L / 2, Wd / 2)[0] + 4, tf_front(0, Wd / 2)[1] + 4), f"R{R:.0f} (4×)")
leader(tf_front(WL / 2 - WR * 0.29, WW / 2 - WR * 0.29), (tf_front(WL / 2, 0)[0] - 42, tf_front(0, WW / 2)[1] - 14),
       f"R{WR:.1f} (4×) WINDOW CORNERS", ha="left")
leader(tf_front(NX - 4.2, 12), (tf_front(NX, 0)[0] + 8, tf_front(0, 40)[1]), "FACE ID SLOT 32 × 8.4, R4.2 ENDS,")
T(tf_front(NX, 0)[0] + 8.8, tf_front(0, 40)[1] - 3.6, f"CENTRED ON WINDOW EDGE X{NX:.1f}", size=2.5)
leader(tf_front(L / 2 - 0.4, -50), (tf_front(L / 2, 0)[0] + 3, tf_front(0, -70)[1]), "R0.8 FRONT EDGES", ha="left")
T(FC[0] - 4, FC[1] - 22, "WINDOW AND OUTLINE CENTRED ON X0 Y0", size=2.2, ha="right")
T(tf_front(L / 2, 0)[0] + 3, FC[1] - 6, "USB-C END", size=2.2)
T(tf_front(L / 2, 0)[0] + 3, FC[1] - 9.5, "(+X)", size=2.2)

# ------------------------------------------------------------------ BACK VIEW
outline(outer, tf_back)
outline(skirt_in, tf_back, lw=MID)
outline(window, tf_back)
outline(boss_geom, tf_back, lw=MID)
outline(relief, tf_back, lw=THIN)
line([tf_back(-L / 2 - 6, 0), tf_back(L / 2 + 6, 0)], lw=THIN, ls=(0, (8, 2, 1, 2)))
line([tf_back(0, -Wd / 2 - 6), tf_back(0, Wd / 2 + 6)], lw=THIN, ls=(0, (8, 2, 1, 2)))
for hid, x, y, typ in ids:
    d_drill = 2.5 if typ == "A" else 2.05
    d_major = 3.0 if typ == "A" else 2.5
    cx, cy = tf_back(x, y)
    ax.add_patch(Circle((cx, cy), d_drill * S / 2, fill=False, lw=MID * PT, color=INK))
    th = matplotlib.patches.Arc((cx, cy), d_major * S, d_major * S, theta1=0, theta2=270, lw=THIN * PT, color=INK)
    ax.add_patch(th)
    dx = 6.5 if x > 0 else -6.5                       # labels toward the inside (X is mirrored)
    dy = -6 if (typ == "B" and y > 0) else (6 if typ == "B" else 0)
    if typ == "A":
        T(cx + dx, cy, hid, size=2.3, ha="center", va="center", weight="bold")
    else:
        T(cx, cy + dy, hid, size=2.3, ha="center", va="center", weight="bold")
T(BC[0], BC[1] + Wd * S / 2 + 5, "BACK VIEW (VIEWED FROM BEHIND, X MIRRORED)  1:2", size=3.2, ha="center", weight="bold")
# axis key
ax.annotate("", xy=(BC[0] - L * S / 2 + 2, BC[1] - Wd * S / 2 - 7), xytext=(BC[0] - L * S / 2 + 14, BC[1] - Wd * S / 2 - 7),
            arrowprops=dict(arrowstyle="-|>", lw=MID * PT, color=INK))
T(BC[0] - L * S / 2 + 16, BC[1] - Wd * S / 2 - 7, "+X (STEP)", size=2.3, va="center")
ax.annotate("", xy=(BC[0] - L * S / 2 - 6, BC[1] - Wd * S / 2 + 10), xytext=(BC[0] - L * S / 2 - 6, BC[1] - Wd * S / 2 - 2),
            arrowprops=dict(arrowstyle="-|>", lw=MID * PT, color=INK))
T(BC[0] - L * S / 2 - 6, BC[1] - Wd * S / 2 + 12, "+Y", size=2.3, ha="center")
# pocket and relief callouts
leader(tf_back(-60, -60), (BC[0] + 8, BC[1] - 18), f"POCKET {h.PLATE_Z0:.1f} DEEP FROM BACK FACE", ha="left")
T(BC[0] + 8.8, BC[1] - 21.6, f"(LEAVES {h.FT:.1f} FRONT PLATE), SKIRT {h.SKIRT:.1f} WALL", size=2.5)
rx, ry = tf_back(h.IPAD_L / 2 + 8, 0)
leader((rx, ry + 2.5), (rx + 30, ry + 30), f"PLUG RELIEF {relief.bounds[2]-relief.bounds[0]:.1f} × "
       f"{relief.bounds[3]-relief.bounds[1]:.1f} × {relief_d:.2f} DEEP", ha="left")
T(rx + 30.8, ry + 26.4, "IN POCKET FLOOR (USB-C END, +X)", size=2.5)
# section line B-B through A-hole at +X, y = 25
secy = 25.0
pa, pb = tf_back(h.OUT_L / 2 + 4, secy), tf_back(h.IPAD_L / 2 - 6, secy)
line([pa, pb], lw=THIN, ls=(0, (8, 2, 1, 2)))
for p, d in ((pa, -1), (pb, 1)):
    line([p, (p[0], p[1] + 4)], lw=0.7)
    T(p[0], p[1] + 5, "B", size=3.2, ha="center", weight="bold")

# ------------------------------------------------------------------ SECTION B-B (4:1) through A hole (x = +154.68)
SC = 4.0
xa = h.BOSS_PTS[[i for i, p in enumerate(h.BOSS_PTS) if p[0] > 0 and abs(p[1] - secy) < 1e-6][0]][0]
X0, X1 = h.IPAD_L / 2 - h.LIP - 0.0, h.OUT_L / 2                 # window edge to outside
ORG = (232, 200)
tf_s = lambda x, z: (ORG[0] + (x - X0) * SC, ORG[1] + z * SC)
rt = 1.25
cone = h.drill_cone_h(rt)
plate = sbox(X0, h.PLATE_Z0, X1, h.SHELL_H)
skirt = sbox(X1 - h.SKIRT, 0, X1, h.SHELL_H)
boss = sbox(xa - h.BOSS_R, h.BOSS_Z0, xa + h.BOSS_R, h.PLATE_Z0 + 0.01)
sect = unary_union([plate, skirt, boss])
# R0.8 on both front edges
for cx_, sgn in ((X1 - 0.8, 1), (X0 + 0.8, -1)):
    corner = sbox(min(cx_, cx_ + sgn * 0.8), h.SHELL_H - 0.8, max(cx_, cx_ + sgn * 0.8), h.SHELL_H)
    sect = sect.difference(corner).union(Point(cx_, h.SHELL_H - 0.8).buffer(0.8, 32).intersection(corner))
zfull = h.BOSS_Z0 + h.DRILL_DEPTH
hole = Polygon([(xa - rt, h.BOSS_Z0 - 1), (xa + rt, h.BOSS_Z0 - 1), (xa + rt, zfull), (xa, zfull + cone), (xa - rt, zfull)])
sect = sect.difference(hole)
for p in (sect.geoms if hasattr(sect, "geoms") else [sect]):
    ax.add_patch(MPoly([tf_s(x, z) for x, z in p.exterior.coords], closed=True, fill=False, hatch="////",
                       lw=THICK * PT, edgecolor=INK))
# thread: major diameter thin lines over the threaded length
for sx in (-1, 1):
    line([tf_s(xa + sx * 1.5, h.BOSS_Z0), tf_s(xa + sx * 1.5, h.BOSS_Z0 + h.THREAD_DEPTH)], lw=THIN)
line([tf_s(xa - 1.5, h.BOSS_Z0 + h.THREAD_DEPTH), tf_s(xa + 1.5, h.BOSS_Z0 + h.THREAD_DEPTH)], lw=MID)
line([tf_s(xa, h.BOSS_Z0 - 2), tf_s(xa, h.SHELL_H + 2)], lw=THIN, ls=(0, (8, 2, 1, 2)))
T(ORG[0] + (X1 - X0) * SC / 2, ORG[1] + h.SHELL_H * SC + 12, "SECTION B–B  4:1  (TYPICAL A1–A8)", size=3.2, ha="center", weight="bold")
T(ORG[0], ORG[1] + h.SHELL_H * SC + 3, "FACE A UP", size=2.3)
# section dims
xr = tf_s(X1, 0)[0] + 6
arrow_dim((xr, tf_s(0, 0)[1]), (xr, tf_s(0, h.SHELL_H)[1]), f"{h.SHELL_H:.1f}", off_text=-2.4)
arrow_dim((xr + 9, tf_s(0, h.PLATE_Z0)[1]), (xr + 9, tf_s(0, h.SHELL_H)[1]), f"{h.FT:.1f}", off_text=-2.4)
arrow_dim(tf_s(X1 - h.SKIRT, -2.5), tf_s(X1, -2.5), f"{h.SKIRT:.1f}", off_text=-2.0)
xl_ = tf_s(xa - h.BOSS_R, 0)[0] - 4
arrow_dim((xl_, tf_s(0, h.BOSS_Z0)[1]), (xl_, tf_s(0, h.SHELL_H)[1]), f"{h.SHELL_H - h.BOSS_Z0:.1f}", off_text=2.4)
arrow_dim((xl_ - 9, tf_s(0, h.BOSS_Z0)[1]), (xl_ - 9, tf_s(0, h.PLATE_Z0)[1]), f"{h.PLATE_Z0 - h.BOSS_Z0:.1f}", off_text=2.4)
arrow_dim(tf_s(xa - h.BOSS_R, h.BOSS_Z0 - 2.2), tf_s(xa + h.BOSS_R, h.BOSS_Z0 - 2.2), f"Ø{2*h.BOSS_R:.0f}", off_text=-2.0)
skin = h.SHELL_H - zfull - cone
xs_ = tf_s(xa, 0)[0] + 9
arrow_dim((xs_, tf_s(0, zfull + cone)[1]), (xs_, tf_s(0, h.SHELL_H)[1]), "", off_text=0)
leader((xs_, tf_s(0, h.SHELL_H - skin / 2)[1]), (xs_ + 10, tf_s(0, h.SHELL_H)[1] + 5), f"{skin:.2f} MIN SKIN UNDER POINT", ha="left")
leader(tf_s(xa + rt, h.BOSS_Z0 + 1.5), (tf_s(xa, 0)[0] + 14, tf_s(0, h.BOSS_Z0 - 4.5)[1]),
       f"M3×0.5-6H ↧{h.THREAD_DEPTH:.1f} MIN FULL THREAD", ha="left")
T(tf_s(xa, 0)[0] + 14.8, tf_s(0, h.BOSS_Z0 - 4.5)[1] - 3.6, f"TAP DRILL Ø2.5 ↧{h.DRILL_DEPTH:.1f} (118° POINT)", size=2.5)
leader(tf_s(X0 + 3, h.PLATE_Z0 - 0.1), (tf_s(X0, 0)[0] + 2, tf_s(0, 2.5)[1]), f"POCKET FLOOR {h.PLATE_Z0:.1f} FROM BACK", ha="left")
T(ORG[0], ORG[1] - 20, f"B1–B8 (M2.5): SAME DEPTHS ON A Ø{2*h.BOSS_R_LONG:.0f} BOSS TIED INTO THE SKIRT,", size=2.3)
T(ORG[0], ORG[1] - 23.4, f"TAP DRILL Ø2.05 ↧{h.DRILL_DEPTH:.1f}, M2.5×0.45-6H ↧{h.THREAD_DEPTH:.1f}, "
  f"{h.SHELL_H - zfull - h.drill_cone_h(1.025):.2f} MIN SKIN", size=2.3)

# ------------------------------------------------------------------ HOLE TABLE
tx, ty = 232, 168
cols = [("HOLE", 12), ("X", 18), ("Y", 18), ("THREAD", 30), ("TAP DRILL", 22), ("DRILL ↧", 16), ("THREAD ↧", 18)]
rowh = 4.3
T(tx, ty + 3, "HOLE TABLE  (X/Y FROM PART CENTRE, STEP FRAME; BLIND FROM BOSS TIP, BACK SIDE)", size=2.4, weight="bold")
line([(tx, ty), (tx + sum(c[1] for c in cols), ty)], lw=MID)
cx = tx
for nm, w in cols:
    T(cx + 1, ty - 3.1, nm, size=2.3, weight="bold")
    cx += w
line([(tx, ty - rowh), (tx + sum(c[1] for c in cols), ty - rowh)], lw=MID)
for i, (hid, x, y, typ) in enumerate(ids):
    yy = ty - rowh * (i + 2) + 1.2
    vals = [hid, f"{x:+.2f}", f"{y:+.2f}", "M3×0.5-6H" if typ == "A" else "M2.5×0.45-6H",
            "Ø2.5" if typ == "A" else "Ø2.05", f"{h.DRILL_DEPTH:.1f}", f"{h.THREAD_DEPTH:.1f} MIN"]
    cx = tx
    for (nm, w), v in zip(cols, vals):
        T(cx + 1, yy, v, size=2.3)
        cx += w
    if i == 7:
        line([(tx, yy - 1.3), (tx + sum(c[1] for c in cols), yy - 1.3)], lw=THIN)
line([(tx, ty - rowh * 17 - 0.4), (tx + sum(c[1] for c in cols), ty - rowh * 17 - 0.4)], lw=MID)

# ------------------------------------------------------------------ NOTES
nx, ny = 232, 88
notes = [
    "NOTES",
    "1. 3D MODEL shell_6061.step DEFINES ALL GEOMETRY NOT DIMENSIONED HERE. THREADED HOLES ARE",
    "    MODELLED AT TAP DRILL DIAMETER; THREAD PER THIS DRAWING.",
    f"2. 8× M3×0.5-6H ↧{h.THREAD_DEPTH:.1f} (A1–A8) AND 8× M2.5×0.45-6H ↧{h.THREAD_DEPTH:.1f} (B1–B8). BLIND HOLES:",
    "    DO NOT BREAK THROUGH OR MARK FACE A. 1.4 MIN METAL UNDER DRILL POINT.",
    "3. FACE A IS COSMETIC: NO TOOL, CLAMP OR FIXTURE MARKS. FRONT EDGES R0.8 AS MODELLED.",
    "4. DEBURR ALL EDGES, BREAK SHARP EDGES 0.2 MAX UNLESS NOTED.",
    "5. FINISH: FINE GLASS BEAD BLAST, THEN TYPE II ANODISE (COLOUR PER ORDER: CLEAR OR BLACK).",
    "    MASK THREADS OR CHASE AFTER ANODISING.",
    "6. GENERAL TOLERANCES ISO 2768-mK. FLATNESS OF FACE A 0.2 OVER FULL LENGTH.",
]
for i, s in enumerate(notes):
    T(nx, ny - i * 3.9, s, size=2.4 if i else 2.8, weight="bold" if i == 0 else "normal")

# ------------------------------------------------------------------ TITLE BLOCK
bx0, by0, bx1, by1 = 232, 10, 410, 46
line([(bx0, by0), (bx0, by1), (bx1, by1)], lw=0.7)
for yv in (by0 + 9, by0 + 18, by0 + 27):
    line([(bx0, yv), (bx1, yv)], lw=THIN)
for xv in (bx0 + 60, bx0 + 120):
    line([(xv, by0), (xv, by0 + 27)], lw=THIN)
T(bx0 + 2, by1 - 4.6, "FLOAT MOUNT v4.2 · SHELL (iPad Pro 12.9″ 3rd gen)", size=3.6, weight="bold")
cells = [
    ("PART No.", "FM42-SHELL-01", "MATERIAL", "6061-T6 AL, 12 mm PLATE", "QTY", "1"),
    ("FINISH", "BEAD BLAST + ANODISE", "MASS", f"≈{h.shell.val().Volume()*2.70e-3:.0f} g", "UNITS", "mm"),
    ("SCALE", "1:2 (U.N.O.)", "TOLERANCE", "ISO 2768-mK", "REV / DATE", "A · 2026-10-20"),
]
for r, row in enumerate(cells):
    yv = by0 + 27 - (r + 1) * 9
    for c in range(3):
        T(bx0 + 60 * c + 1.5, yv + 6.2, row[2 * c], size=1.9, color="#555555")
        T(bx0 + 60 * c + 1.5, yv + 1.8, row[2 * c + 1], size=2.6, weight="bold")
T(bx0 + 2, by1 - 8.0, "DESIGN: BRENDAN · FILE: shell_6061.step · github.com/brendan779/ipad-pro-wall-mount", size=2.0)
# first-angle projection symbol
sx0, sy0 = 395, 52
ax.add_patch(Circle((sx0 + 8, sy0 + 4), 3.0, fill=False, lw=MID * PT, color=INK))
ax.add_patch(Circle((sx0 + 8, sy0 + 4), 1.5, fill=False, lw=MID * PT, color=INK))
line([(sx0 - 6, sy0 + 2.2), (sx0 - 6, sy0 + 5.8), (sx0 + 1, sy0 + 7), (sx0 + 1, sy0 + 1), (sx0 - 6, sy0 + 2.2)], lw=MID)
T(sx0 + 1, sy0 - 2.5, "FIRST-ANGLE", size=1.9, ha="center")

out = sys.argv[1] if len(sys.argv) > 1 else "shell_6061_drawing.pdf"
fig.savefig(out)
fig.savefig(out.replace(".pdf", ".png"), dpi=150)
print("wrote", out, "| ids:", ", ".join(f"{i}({x:.1f},{y:.1f})" for i, x, y, _ in ids))

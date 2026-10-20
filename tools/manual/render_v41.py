import sys, os
sys.path[:0] = ["../../previous-releases/float-v4.1", "../../previous-releases/flush-v5.1"]
import cadquery as cq
import mr
from mr import render, C
import hybrid as h

OUT = "v41"
os.makedirs(OUT, exist_ok=True)
S = h.STANDOFF
TOP = S + h.SHELL_H                      # front face of the shell (assembled)
box, zcyl, rrect = h.box, h.zcyl, h.rrect


def bench(p):
    """Bench frame: panel face-down on the bench (front face on Z0, back facing up)."""
    return p.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, TOP))


def cap(x, y, z_head, head_d, head_t, d, length, up=True):
    """Cap/countersunk screw marker: head starts at z_head, shank runs away from it."""
    if up:
        return zcyl(x, y, head_d / 2, z_head, z_head + head_t).union(zcyl(x, y, d / 2, z_head + head_t, z_head + head_t + length))
    return zcyl(x, y, head_d / 2, z_head - head_t, z_head).union(zcyl(x, y, d / 2, z_head - head_t - length, z_head - head_t))


def U(parts):
    u = parts[0]
    for p in parts[1:]:
        u = u.union(p)
    return u


wall = box(-245, 245, -175, 175, -10, 0)
ipad = h.ipad
plug = h.plug
# simple cable: plug end -> down into the gap -> along to the bracket cut-out
cx = h.IPAD_L / 2 + h.PLUG_L + h.BEND_R / 2
cable = (zcyl(cx, 0, h.CABLE_D / 2, 8.0, S + h.EDGE_Z)
         .union(cq.Workplane("YZ").circle(h.CABLE_D / 2).extrude(cx - 12).translate((12, 0, 8.0))))
tape = (rrect(h.IPAD_L, h.IPAD_W, h.IPAD_R, 0.3, z0=0)
        .cut(rrect(h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP, 2, z0=-1))
        .translate((0, 0, S + h.PLATE_Z0 - 0.3)))
car = h.car_a
qTL, qTR = h.up(h.quad(h.car, -1, 1)), h.up(h.quad(h.car, 1, 1))
qBL, qBR = h.up(h.quad(h.car, -1, -1)), h.up(h.quad(h.car, 1, -1))

ISO = (560, -460, 620)        # front-right, slightly below eye level of the wall
jobs = []

# ---------------------------------------------------------------- overview
jobs.append(("hero", [(wall, "wall", 1), (h.br, "print2", 1), (car, "print", 1), (h.hanger_a, "print", 1),
                      (h.lock_a, "print", 1), (ipad, "ipad", 1), (h.shell_a, "alu", 1)], dict(cam=(420, -300, 900), zoom=1.15)))
jobs.append(("exploded", [(wall, "wall", 1), (h.br, "print2", 1),
                          (car.translate((0, 0, 70)), "print", 1), (h.hanger_a.translate((0, 0, 70)), "print2", 1),
                          (h.lock_a.translate((0, 0, 70)), "print2", 1), (ipad.translate((0, 0, 120)), "ipad", 1),
                          (plug.translate((0, 0, 120)), "plug", 1), (h.shell_a.translate((0, 0, 175)), "alu", 1)],
             dict(cam=(760, -560, 640), zoom=1.05)))
jobs.append(("rear_view", [(car, "print", 1), (h.hanger_a, "active", 1), (h.lock_a, "active", 1), (h.shell_a, "alu", 1),
                           (cable, "plug", 1)], dict(cam=(-320, -300, -700), zoom=1.3)))

# ---------------------------------------------------------------- print orientation
def plate_grid(parts, gap=24.0):
    items = []
    for i, p in enumerate(parts):
        pp, _ = mr.on_plate(p)
        ox, oy = (i % 2) * (256 + gap), -(i // 2) * (256 + gap)
        items += [(pp.translate((ox, oy, 0)), "active", 1),
                  (mr.plate(ox - 128, ox + 128, oy - 128, oy + 128), (0.80, 0.80, 0.78), 1)]
    return items


jobs.append(("po_carrier", plate_grid([h.quad(h.car, -1, 1), h.quad(h.car, 1, 1), h.quad(h.car, -1, -1), h.quad(h.car, 1, -1)]),
             dict(cam=(420, -700, 760), zoom=1.15)))
small = [h.hanger, h.flip(h.lock_boss), h.flip(h.catch_rail)]
items, y = [], -80.0
for p in small:
    pp, _ = mr.on_plate(p)
    items.append((pp.translate((0, y, 0)), "active", 1))
    y += 70
items.append((mr.plate(-128, 128, -128, 128), (0.80, 0.80, 0.78), 1))
jobs.append(("po_small", items, dict(cam=(160, -330, 300), zoom=1.15)))
bp, plt_ = mr.on_plate(h.br_plate)
jobs.append(("po_bracket", [(bp, "active", 1), (plt_, (0.80, 0.80, 0.78), 1)], dict(cam=(180, -320, 330), zoom=1.1)))
jobs.append(("po_shellproto", plate_grid([h.flip(h.quad(h.shell, -1, 1)), h.flip(h.quad(h.shell, 1, 1)),
                                          h.flip(h.quad(h.shell, -1, -1)), h.flip(h.quad(h.shell, 1, -1))]),
             dict(cam=(420, -700, 760), zoom=1.15)))

# ---------------------------------------------------------------- machining
sh_back = h.shell.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, h.SHELL_H))
stock = box(-h.OUT_L / 2 - 8, h.OUT_L / 2 + 8, -h.OUT_W / 2 - 8, h.OUT_W / 2 + 8, -12, 0)
jobs.append(("mach_op1", [(stock, (0.86, 0.86, 0.84), 1), (sh_back.translate((0, 0, 0)), "alu", 1)],
             dict(cam=(300, -380, 520), zoom=1.25)))
jobs.append(("mach_op2", [(stock, (0.86, 0.86, 0.84), 1), (h.shell.translate((0, 0, 0)), "alu", 1)],
             dict(cam=(300, -380, 520), zoom=1.25)))
jobs.append(("mach_bosses", [(sh_back, "alu", 1)] + [(zcyl(x, -y, r, h.SHELL_H - h.PLATE_Z0 - 0.01, h.SHELL_H - h.BOSS_Z0), "active", 1)
                                                     for (x, y, r) in h.ALL_BOSSES],
             dict(cam=(240, -260, 420), zoom=1.3)))

# ---------------------------------------------------------------- A1 heat-set inserts
def centred(p, y_target):
    bb = p.val().BoundingBox()
    return (-(bb.xmin + bb.xmax) / 2, y_target - (bb.ymin + bb.ymax) / 2, -bb.zmin)


ins = []
dx, dy, dz = centred(h.hanger, 55)
ins += [(h.hanger.translate((dx, dy, dz)), "print", 1)]
ins += [(zcyl(x + dx, y + dy, 2.1, -5.0 + dz, 0.8 + dz), "hw", 1) for (x, y) in h.HANG_BOLTS]
dx, dy, dz = centred(h.lock_boss, 0)
ins += [(h.lock_boss.translate((dx, dy, dz)), "print", 1),
        (h.ycyl(0 + dx, h.LOCK_Z + dz, 2.1, h.LOCK_Y + 8 + dy - 0.8, h.LOCK_Y + 16 + dy), "hw", 1)]
rl = h.flip(h.catch_rail)
dx, dy, dz = centred(rl, -55)
rb = rl.translate((dx, dy, dz)).val().BoundingBox()
ins += [(rl.translate((dx, dy, dz)), "print", 1)]
for (x, y) in h.RAIL_BOLTS:
    ins.append((zcyl(x + dx, -y + dy, 2.1, rb.zmax - 5.5, rb.zmax + 0.8), "hw", 1))
jobs.append(("a1_inserts", ins, dict(cam=(150, -230, 260), zoom=1.0)))

# ---------------------------------------------------------------- A2 rail to bracket
rail_scr = [cap(x, y, -2.0, 6.0, 1.6, 3.0, 8.0, up=True).translate((0, 0, -10)) for (x, y) in h.RAIL_BOLTS]
jobs.append(("a2_rail", [(h.br_plate, "print2", 1), (h.catch_rail.translate((0, 0, 25)), "active", 1)] +
             [(s, "hw", 1) for s in rail_scr], dict(cam=(300, -260, -420), zoom=1.3)))

# ---------------------------------------------------------------- A3/A4 hanger + lock onto carrier pairs
def pocket_screws(pts):
    return [cap(x, y, S + h.CB + 18, 6.6, 1.6, 3.0, 8.0, up=False) for (x, y) in pts]


jobs.append(("a3_hanger", [(qTL, "print", 1), (qTR, "print2", 1), (h.hanger_a.translate((0, 0, -35)), "active", 1)] +
             [(s, "hw", 1) for s in pocket_screws(h.HANG_BOLTS)], dict(cam=(260, -120, 520), zoom=1.45,
                                                                      focal=(0, 60, 10))))
jobs.append(("a4_lock", [(qBL, "print", 1), (qBR, "print2", 1), (h.lock_a.translate((0, 0, -35)), "active", 1)] +
             [(s, "hw", 1) for s in pocket_screws(h.LOCK_BOLTS)], dict(cam=(260, -420, 420), zoom=1.45,
                                                                      focal=(0, -70, 10))))

# ---------------------------------------------------------------- bench steps (face-down)
B = bench
jobs.append(("a5_tape", [(B(h.shell_a), "alu", 1), (B(tape).translate((0, 0, 1.5)), "tape", 1)],
             dict(cam=(300, -380, 520), zoom=1.25)))
jobs.append(("a6_ipad", [(B(h.shell_a), "alu", 1), (B(tape), "tape", 1), (B(ipad).translate((0, 0, 40)), "active", 1),
                         (B(plug).translate((0, 0, 40)), "plug", 1)], dict(cam=(300, -380, 520), zoom=1.25)))
top_pair = qTL.union(qTR).union(h.hanger_a)
bot_pair = qBL.union(qBR).union(h.lock_a)
jobs.append(("a7_carrier", [(B(h.shell_a), "alu", 1), (B(ipad), "ipad", 1), (B(plug), "plug", 1),
                            (B(top_pair).translate((0, 0, 45)), "active", 1), (B(bot_pair).translate((0, 0, 45)), "active", 1)],
             dict(cam=(300, -380, 560), zoom=1.2)))
boss_screws = []
for (x, y, r) in h.ALL_BOSSES:
    m3 = (x, y) not in h.LONG_PTS
    boss_screws.append(cap(x, y, S + 0.0, 5.5 if m3 else 4.5, 3.0, 3.0 if m3 else 2.5, 6.0, up=True))
jobs.append(("a8_screws", [(B(h.shell_a), "alu", 1), (B(ipad), "ipad", 1), (B(car), "print", 1),
                           (B(h.hanger_a), "print2", 1), (B(h.lock_a), "print2", 1)] +
             [(B(s).translate((0, 0, 14)), "hw", 1) for s in boss_screws],
             dict(cam=(300, -380, 520), zoom=1.25)))
jobs.append(("a9_cable", [(B(h.shell_a), "alu", 1), (B(car), "print", 1), (B(h.hanger_a), "print2", 1),
                          (B(h.lock_a), "print2", 1), (B(cable), "active", 1), (B(plug), "plug", 1)],
             dict(cam=(330, 120, 300), zoom=1.9, focal=(110, 0, 10))))

# ---------------------------------------------------------------- wall steps
cut = box(-h.CUTOUT[0] / 2, h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2, h.CUTOUT[1] / 2, -11, 1)
wall_cut = wall.cut(cut)
poe = box(-24, 24, -30, 30, -45, -15)
cat6 = (cq.Workplane("XY").circle(3.0).extrude(30).translate((0, -30, -40))
        .rotate((0, -30, -40), (1, -30, -40), 90))
anchors = [cap(sx * (h.BR_L / 2 - 18), sy * (h.BR_W / 2 - 18), h.BR_T + 25, 8.0, 2.0, 4.0, 30, up=False)
           for sx in (-1, 1) for sy in (-1, 1)]
jobs.append(("w2_bracket", [(wall_cut, "wall", 1), (h.br.translate((0, 0, 25)), "active", 1)] +
             [(a, "hw", 1) for a in anchors], dict(cam=(300, -330, 560), zoom=1.15)))
jobs.append(("w3_poe", [(wall_cut, "wall", 0.35), (h.br, "print2", 1), (poe, "active", 1),
                        (zcyl(0, 0, 3, -60, -45), "hw", 1), (zcyl(0, 0, 2.25, -15, 6), "plug", 1)],
             dict(cam=(260, -240, -420), zoom=2.2, focal=(0, 0, -20))))
offered = [(p.translate((0, 10, 30)), c, 1) for p, c in ((car, "active"), (h.hanger_a, "active"), (h.lock_a, "active"),
                                                         (ipad, "ipad"), (h.shell_a, "alu"))]
jobs.append(("w4_hang", [(wall, "wall", 1), (h.br, "print2", 1)] + offered, dict(cam=(620, -380, 520), zoom=1.1)))
lock_scr = (cq.Workplane("XZ").circle(1.5).extrude(-12).translate((0, h.LOCK_Y - 3, h.LOCK_Z + S))
            .union(cq.Workplane("XZ").circle(2.75).extrude(-3).translate((0, h.LOCK_Y - 6, h.LOCK_Z + S))))
jobs.append(("_skip_w5_lock", [(wall, "wall", 1), (h.br, "print2", 1), (car, "print", 1), (h.lock_a, "print2", 1),
                         (h.shell_a, "alu", 1), (lock_scr.translate((0, -12, 0)), "hw", 1)],
             dict(cam=(140, -520, -60), up=(0, 0, 1), zoom=3.0, focal=(0, h.LOCK_Y, 10))))
jobs.append(("final", [(wall, "wall", 1), (h.br, "print2", 1), (car, "print", 1), (ipad, "ipad", 1),
                       (h.shell_a, "alu", 1)], dict(cam=(0, -60, 900), zoom=1.2)))

only = set(sys.argv[1:])
for name, items, kw in jobs:
    if name.startswith("_skip") or (only and name not in only):
        continue
    render(f"{OUT}/{name}.png", items, **kw)
    print("rendered", name, flush=True)

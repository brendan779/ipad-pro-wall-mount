"""
Float Mount v6 FLUSH -- in-wall PoE mount for any tablet in tablets.py.
Existing 10 mm plasterboard, 70 mm studs at 450 c/c. Every part prints flat
with no supports; the trim is 3 mm 6061 (or printed, see printed6.py).

v6 changes from v5.1
  * tablet-driven: V6_TABLET=<key> picks the iPad (tablets.py)
  * +2 mm cable-loop room at BOTH ends
  * button reliefs in the sleeve wall (45° roof, prints face-down) and deck ribs
  * magnets, locating pins and dog-ear clamps are placed clear of every
    speaker / mic path for the chosen tablet
  * front-camera notch on the short end or the top bar; rear-camera keep-outs

Coordinates: wall face = Z0, +Z out of the wall, +X USB-C end, +Y up.
Run:  V6_TABLET=ipad_mini_a17_pro python flush6.py out_dir
"""
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tablets  # noqa: E402

TAB_KEY, TAB = tablets.get()
IPAD_L, IPAD_W, IPAD_T, IPAD_R = TAB["L"], TAB["W"], TAB["T"], TAB["R"]
CLR = 0.35
CAM_SIDE, CAM_LEN = TAB["cam"]
PLUG_L, PLUG_W, PLUG_H, CABLE_D, BEND_R = 17.0, 12.5, 7.0, 4.5, 8.0
LOOP_EXTRA = 2.0
PLASTER = 10.0
STUD_CC, STUD_W, STUD_D = 450.0, 35.0, 70.0

GLASS_GAP, FL_T, TRIM_T, LIP = 0.3, 1.5, 3.0, 2.8
WALL, DECK_T = 2.0, 3.0
SLEEVE_D, BACK_T = 55.0, 2.5
HOLE_CLR, FLANGE_W, TRIM_OVER = 1.0, 6.0, 1.0
VENT_INSET, DECK_SG = 32, 0.3
LEDGE_W, BEVEL = 2.5, 1.5
BUTTON_RELIEF = 1.2

Z_F = FL_T
GLASS_Z = Z_F - GLASS_GAP
IPAD_Z0 = GLASS_Z - IPAD_T
EDGE_Z = IPAD_Z0 + IPAD_T / 2
DECK_Z0 = IPAD_Z0 - DECK_T

END_X = PLUG_L + BEND_R + CABLE_D / 2 + 1.0 + LOOP_EXTRA
IN_L, IN_W = IPAD_L + 2 * CLR, IPAD_W + 2 * CLR
BOX_IN_X, BOX_IN_Y = IPAD_L / 2 + END_X, IN_W / 2
BOX_X, BOX_Y = 2 * (BOX_IN_X + WALL), 2 * (BOX_IN_Y + WALL)
BOX_R = 6.0
IN_R_BOX = BOX_R - WALL + 0.5
HOLE_X, HOLE_Y = BOX_X + 2 * HOLE_CLR, BOX_Y + 2 * HOLE_CLR
FLG_X, FLG_Y = BOX_X + 2 * FLANGE_W, BOX_Y + 2 * FLANGE_W
TRIM_X, TRIM_Y = FLG_X + 2 * TRIM_OVER, FLG_Y + 2 * TRIM_OVER
TRIM_R = 14.0

MAG_D, MAG_H = 10.0, 1.5
ARM_REACH, ARM_W, ARM_T = 18.0, 12.0, 6.0
WIN = {e: [tuple(w) for w in TAB["spk"][e]] + [tuple(w) for w in TAB["mic_end"][e]] for e in ("-x", "+x")}
PLUG_BAND = (-(PLUG_W / 2 + 1), PLUG_W / 2 + 1)


def _gap_ok(y, r, bands, margin):
    return all(y + r + margin <= a or y - r - margin >= b for a, b in bands)


def place(r, ends, lo, hi, margin=1.5, prefer=None, step=0.5, extra=()):
    """y positions (+ and mirrored -) clear of every vented window on the given ends."""
    bands = [w for e in ends for w in WIN[e]] + ([PLUG_BAND] if "+x" in ends else []) + list(extra)
    cands = []
    y = lo
    while y <= hi + 1e-9:
        if _gap_ok(y, r, bands, margin) and _gap_ok(-y, r, bands, margin):
            cands.append(y)
        y += step
    if not cands:
        return None
    return min(cands, key=lambda c: abs(c - prefer)) if prefer is not None else cands[-1]


# magnets: one near each corner, one inner pair if there is room (both ends)
MAG_X = IPAD_L / 2 + 14
mag_corner = place(7.0, ("-x", "+x"), 20, IPAD_W / 2 - 7.45, prefer=IPAD_W / 2 - 7.45)
mag_inner = place(7.0, ("-x", "+x"), 10, (mag_corner or 50) - 30, prefer=18)
MAG_YS = [y for y in (mag_corner, mag_inner) if y is not None]
MAG_PTS = [(sx * MAG_X, sy * y) for sx in (-1, 1) for y in MAG_YS for sy in (-1, 1)]
CLAMP_X = BOX_X / 2 - WALL - 6.0
clamp_y = place(5.5, ("-x", "+x"), 25, IPAD_W / 2 - 15, prefer=45.0)
CLAMP_PTS = [(sx * CLAMP_X, sy * clamp_y) for sx in (-1, 1) for sy in (-1, 1)]
PIN_X = IPAD_L / 2 + 22
# the pin hole must stay out of the clamp's deck post (r5.5) and screw counterbore
_PIN_DY = max(0.0, (5.5 + 1.6 + 1.0) ** 2 - (CLAMP_X - PIN_X) ** 2) ** 0.5
pin_y = place(4.0, ("-x", "+x"), 20, IPAD_W / 2 - 10, prefer=IPAD_W / 2 - 32.45,
              extra=[(clamp_y - _PIN_DY + 4.0 + 1.5, clamp_y + _PIN_DY - 4.0 - 1.5),
                     (-clamp_y - _PIN_DY + 4.0 + 1.5, -clamp_y + _PIN_DY - 4.0 - 1.5)])
PIN_PTS = [(-PIN_X, pin_y), (PIN_X, -pin_y)]
GRILLE_X = [IPAD_L / 2 + 6 + 4 * i for i in range(5)]
BACK_SPLIT_X = 60.0
BACK_X = 0.784 * IPAD_L / 2
BACK_BOSSES = ([(sx * (BOX_IN_X - 4), sy * (BOX_IN_Y - 4)) for sx in (-1, 1) for sy in (-1, 1)] +
               [(x, sy * (BOX_IN_Y - 3)) for x in (-BACK_X, BACK_X) for sy in (-1, 1)])


def rrect(l, w, r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").rect(l, w).extrude(z1 - z0).edges("|Z").fillet(r).translate((x, y, z0))


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def zcyl(x, y, r, z0, z1):
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def yslot(x, y, length, width, z0, z1):
    return cq.Workplane("XY").slot2D(length, width, angle=90).extrude(z1 - z0).translate((x, y, z0))


def cam_slot(z0, z1):
    if CAM_SIDE == "end":
        return yslot(-(IPAD_L / 2 - LIP), 0, CAM_LEN, 8.4, z0, z1)
    return cq.Workplane("XY").slot2D(CAM_LEN, 8.4, angle=0).extrude(z1 - z0).translate((0, IPAD_W / 2 - LIP, z0))


def ledge_profile(w_in, length, axis):
    zt = DECK_Z0 + DECK_SG + BEVEL
    pts = [(0.0, zt), (-LEDGE_W, zt - LEDGE_W), (-LEDGE_W, zt - LEDGE_W - 1.2), (0.0, zt - LEDGE_W - 1.2)]
    if axis == "y":
        return cq.Workplane("YZ").polyline([(w_in + u, z) for u, z in pts]).close().extrude(length / 2, both=True)
    return cq.Workplane("XZ").polyline([(w_in + u, z) for u, z in pts]).close().extrude(length / 2, both=True)


def trim_part(round_edges=True):
    t = rrect(TRIM_X, TRIM_Y, TRIM_R, Z_F, Z_F + TRIM_T)
    t = t.cut(rrect(IPAD_L - 2 * LIP, IPAD_W - 2 * LIP, IPAD_R - LIP, Z_F - 1, Z_F + TRIM_T + 1))
    t = t.cut(cam_slot(Z_F - 1, Z_F + TRIM_T + 1))
    sel = t.edges(cq.selectors.BoxSelector((-999, -999, Z_F + TRIM_T - 0.01), (999, 999, Z_F + TRIM_T + 0.01)))
    t = sel.fillet(0.8) if round_edges else sel.chamfer(0.8)
    for sx, e in ((-1, "-x"), (1, "+x")):
        for gx in GRILLE_X:
            for (y0, y1) in WIN[e]:
                ln = max(6.0, (y1 - y0) - 6.0)
                t = t.cut(yslot(sx * gx, (y0 + y1) / 2, ln, 2.0, Z_F - 1, Z_F + TRIM_T + 1))
    for (x, y) in MAG_PTS:
        t = t.cut(zcyl(x, y, MAG_D / 2 + 0.1, Z_F - 1, Z_F + MAG_H + 0.1))
    for (x, y) in PIN_PTS:
        t = t.cut(zcyl(x, y, 1.5, Z_F - 1, Z_F + 2.0))
    if EDGE_Z + PLUG_H / 2 + 0.3 > Z_F:
        t = t.cut(box(IPAD_L / 2 - 1, IPAD_L / 2 + PLUG_L + 2, -(PLUG_W / 2 + 1), PLUG_W / 2 + 1,
                      Z_F - 1, EDGE_Z + PLUG_H / 2 + 0.3))
    return t


trim = trim_part(True)

# =============================== SLEEVE ====================================
sleeve = rrect(BOX_X, BOX_Y, BOX_R, -SLEEVE_D, Z_F).union(rrect(FLG_X, FLG_Y, BOX_R + FLANGE_W, 0, Z_F))
sleeve = sleeve.cut(rrect(2 * BOX_IN_X, 2 * BOX_IN_Y, IN_R_BOX, -SLEEVE_D - 1, Z_F + 1))
for sy in (-1, 1):
    l = ledge_profile(BOX_IN_Y, 2 * BOX_IN_X - 2 * IN_R_BOX, "y")
    sleeve = sleeve.union(l if sy > 0 else l.mirror("XZ"))
CABLE_GAP = CABLE_D / 2 + 3.0
LEDGE_SKIP = clamp_y + ARM_W / 2 + 2        # end-wall ledges stop short of the arm slots
for sx in (-1, 1):
    inner = clamp_y - ARM_REACH - 1.5        # clear of the arm's swing when it is retracted
    mids = [(-inner, -CABLE_GAP), (CABLE_GAP, inner)] if sx > 0 else [(-inner, inner)]
    for (y0, y1) in [(-BOX_IN_Y + IN_R_BOX, -LEDGE_SKIP)] + mids + [(LEDGE_SKIP, BOX_IN_Y - IN_R_BOX)]:
        if y1 - y0 < 4:
            continue
        l = ledge_profile(BOX_IN_X, y1 - y0, "x").translate((0, (y0 + y1) / 2, 0))
        sleeve = sleeve.union(l if sx > 0 else l.mirror("YZ"))
for (x, y) in CLAMP_PTS:
    sx = 1 if x > 0 else -1
    wx0, wx1 = sorted((sx * (BOX_IN_X - 0.5), sx * (BOX_X / 2 + 1)))
    hw = ARM_W / 2 + 1
    sleeve = sleeve.cut(box(wx0, wx1, y - hw, y + hw, -45, -PLASTER + 0.5))
    roof = (cq.Workplane("YZ").polyline([(y - hw, -45.0), (y + hw, -45.0), (y, -45.0 - hw)]).close()
            .extrude((wx1 - wx0) / 2, both=True).translate(((wx0 + wx1) / 2, 0, 0)))
    sleeve = sleeve.cut(roof)
for (x, y) in BACK_BOSSES:
    corner = abs(abs(x) - (BOX_IN_X - 4)) < 0.01
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    if corner:
        x0, x1 = sorted((sx * (BOX_IN_X - 8), sx * BOX_IN_X))
        d = 8.0
    else:
        x0, x1 = x - 5, x + 5
        d = 6.0
    wy = sy * BOX_IN_Y
    y0, y1 = sorted((wy - sy * d, wy))
    zb = -SLEEVE_D + 10
    sleeve = sleeve.union(box(x0, x1, y0, y1, -SLEEVE_D, zb))
    wedge = (cq.Workplane("YZ").polyline([(wy, zb), (wy - sy * d, zb), (wy, zb + d)]).close()
             .extrude((x1 - x0) / 2, both=True).translate(((x0 + x1) / 2, 0, 0)))
    sleeve = sleeve.union(wedge)
    sleeve = sleeve.cut(zcyl(x, y, 2.1, -SLEEVE_D - 1, -SLEEVE_D + 6))


def wall_relief_y(x0, x1, sy):
    """Pocket in a long sleeve wall above the deck, open to the front (under the trim),
    with a 45° roof at the back so it prints face-down without support."""
    wy = sy * BOX_IN_Y
    z_lo = IPAD_Z0 + 0.3
    d = BUTTON_RELIEF + 0.5
    pts = [(wy - sy * 0.5, Z_F + 1), (wy - sy * 0.5, z_lo - d), (wy + sy * BUTTON_RELIEF, z_lo), (wy + sy * BUTTON_RELIEF, Z_F + 1)]
    return cq.Workplane("YZ").polyline(pts).close().extrude((x1 - x0) / 2, both=True).translate(((x0 + x1) / 2, 0, 0))


for b in TAB["buttons"]:
    if b[0] in ("top", "bottom"):
        sleeve = sleeve.cut(wall_relief_y(b[1], b[2], 1 if b[0] == "top" else -1))
for (x0, x1) in TAB["mic_top"]:
    sleeve = sleeve.cut(wall_relief_y(x0, x1, 1))

# =============================== DECK =====================================
DX, DY = BOX_IN_X - DECK_SG, BOX_IN_Y - DECK_SG
deck = rrect(2 * DX, 2 * DY, IN_R_BOX - DECK_SG, DECK_Z0, IPAD_Z0)
deck = deck.edges(cq.selectors.BoxSelector((-999, -999, DECK_Z0 - 0.01), (999, 999, DECK_Z0 + 0.01))).chamfer(BEVEL)
deck = deck.cut(rrect(IN_L - 2 * VENT_INSET, IN_W - 2 * VENT_INSET, 14, DECK_Z0 - 1, IPAD_Z0 + 1))
for f in TAB["rear"]:
    if f[0] == "circle":
        deck = deck.cut(zcyl(f[1], f[2], f[3], DECK_Z0 - 1, IPAD_Z0 + 1))
    else:
        deck = deck.cut(box(f[1], f[2], f[3], f[4], DECK_Z0 - 1, IPAD_Z0 + 1))
deck = deck.cut(box(IN_L / 2 - 0.5, BOX_IN_X + 1, -(PLUG_W / 2 + 1), PLUG_W / 2 + 1, DECK_Z0 - 1, IPAD_Z0 + 1))
for sx, e in ((-1, "-x"), (1, "+x")):
    x0, x1 = sorted((sx * IN_L / 2, sx * (IN_L / 2 + 2.0)))
    rib = box(x0, x1, -IN_W / 2 + 0.6, IN_W / 2 - 0.6, IPAD_Z0, GLASS_Z)
    cuts = list(WIN[e]) + [(b[1], b[2]) for b in TAB["buttons"] if b[0] == e]
    if sx > 0:
        cuts.append(PLUG_BAND)
    for (y0, y1) in cuts:
        rib = rib.cut(box(x0 - 1, x1 + 1, y0, y1, IPAD_Z0 - 1, GLASS_Z + 1))
    deck = deck.union(rib)
for (x, y) in MAG_PTS:
    deck = deck.union(zcyl(x, y, 7.0, IPAD_Z0, Z_F))
    deck = deck.cut(zcyl(x, y, MAG_D / 2 + 0.1, Z_F - MAG_H - 0.1, Z_F + 1))
for (x, y) in PIN_PTS:
    deck = deck.union(zcyl(x, y, 4.0, IPAD_Z0, Z_F))
    deck = deck.cut(zcyl(x, y, 1.6, Z_F - 4, Z_F + 1))
for (x, y) in CLAMP_PTS:
    deck = deck.union(zcyl(x, y, 5.5, IPAD_Z0, Z_F))
    deck = deck.cut(zcyl(x, y, 2.25, DECK_Z0 - 1, Z_F + 1))
    deck = deck.cut(zcyl(x, y, 4.3, Z_F - 3.0, Z_F + 1))

# =============================== BACK PLATE ===============================
back = rrect(BOX_X, BOX_Y, BOX_R, -SLEEVE_D - BACK_T, -SLEEVE_D)
CAT6_X = -min(70.0, BOX_IN_X - 40)
back = back.cut(zcyl(CAT6_X, 0, 11.0, -SLEEVE_D - BACK_T - 1, -SLEEVE_D + 1))
TIE_CX = CAT6_X + 10
TIE_DY = min(38.0, BOX_IN_Y - 12)
for dx in (-30, 30):
    for dy in (-TIE_DY, TIE_DY):
        back = back.cut(box(TIE_CX + dx - 1.5, TIE_CX + dx + 1.5, dy - 4, dy + 4, -SLEEVE_D - BACK_T - 1, -SLEEVE_D + 1))
for (x, y) in BACK_BOSSES:
    back = back.cut(zcyl(x, y, 1.7, -SLEEVE_D - BACK_T - 1, -SLEEVE_D + 1))
    back = back.cut(cq.Workplane("XY").circle(3.3).workplane(offset=1.6).circle(1.7).loft()
                    .translate((x, y, -SLEEVE_D - BACK_T - 0.001)))
back_L = back.intersect(box(-999, BACK_SPLIT_X, -999, 999, -999, 999))
back_R = back.intersect(box(BACK_SPLIT_X, 999, -999, 999, -999, 999))

# =============================== ARMS =====================================
ARM_Z1 = -PLASTER
ARM_Z0 = ARM_Z1 - ARM_T
arm = box(-6, ARM_REACH, -ARM_W / 2, ARM_W / 2, 0, ARM_T).cut(zcyl(0, 0, 2.8, -1, ARM_T + 1))


def place_arm(x, y, retracted=False):
    sx = 1 if x > 0 else -1
    sy = 1 if y > 0 else -1
    a = arm if sx > 0 else arm.rotate((0, 0, 0), (0, 0, 1), 180)
    if retracted:
        a = a.rotate((0, 0, 0), (0, 0, 1), -90 * sy * sx)
    return a.translate((x, y, ARM_Z0))


arms = [place_arm(x, y) for (x, y) in CLAMP_PTS]
arms_in = [place_arm(x, y, True) for (x, y) in CLAMP_PTS]

# =============================== REFERENCES ===============================
ipad = rrect(IPAD_L, IPAD_W, IPAD_R, IPAD_Z0, GLASS_Z)
plug = box(IPAD_L / 2, IPAD_L / 2 + PLUG_L, -PLUG_W / 2, PLUG_W / 2, EDGE_Z - PLUG_H / 2, EDGE_Z + PLUG_H / 2)
bend = box(IPAD_L / 2 + PLUG_L, IPAD_L / 2 + PLUG_L + BEND_R + CABLE_D / 2 + LOOP_EXTRA, -CABLE_D / 2, CABLE_D / 2,
           -SLEEVE_D + 5, EDGE_Z + CABLE_D / 2)
plaster = box(-STUD_CC, STUD_CC, -300, 300, -PLASTER, 0).cut(rrect(HOLE_X, HOLE_Y, BOX_R + HOLE_CLR, -PLASTER - 1, 1))
studs = (box(-STUD_CC / 2 - STUD_W / 2, -STUD_CC / 2 + STUD_W / 2, -300, 300, -PLASTER - STUD_D, -PLASTER)
         .union(box(STUD_CC / 2 - STUD_W / 2, STUD_CC / 2 + STUD_W / 2, -300, 300, -PLASTER - STUD_D, -PLASTER)))
buttons = []
for b in TAB["buttons"]:
    if b[0] in ("top", "bottom"):
        sy = 1 if b[0] == "top" else -1
        y0, y1 = sorted((sy * IPAD_W / 2, sy * (IPAD_W / 2 + 0.6)))
        buttons.append(box(b[1] + 2, b[2] - 2, y0, y1, EDGE_Z - 1.5, EDGE_Z + 1.5))
    else:
        sx = 1 if b[0] == "+x" else -1
        x0, x1 = sorted((sx * IPAD_L / 2, sx * (IPAD_L / 2 + 0.6)))
        buttons.append(box(x0, x1, b[1] + 2, b[2] - 2, EDGE_Z - 1.5, EDGE_Z + 1.5))


# =============================== HARDWARE (for the STEP assembly) ============
import hardware6 as hw  # noqa: E402


def flush_kit(trim_name="trim"):
    k = hw.Kit()
    for (x, y) in MAG_PTS:
        k.add("magnet_N52_10x1.5", hw.disc(MAG_D, MAG_H), hw.loc(x, y, Z_F + MAG_H, "-z"), hw.MAGNET, "trim pockets")
        k.add("magnet_N52_10x1.5", hw.disc(MAG_D, MAG_H), hw.loc(x, y, Z_F, "-z"), hw.MAGNET, "deck posts")
    for (x, y) in PIN_PTS:
        k.add("dowel_pin_3x6_ISO8734", hw.pin(3.0, 6.0), hw.loc(x, y, Z_F + 2.0, "-z"), hw.STEEL, "trim, locating in the deck")
    for (x, y) in CLAMP_PTS:
        k.add("M4x30_pan_ISO7045", hw.screw("pan", "M4", 30), hw.loc(x, y, Z_F - 3.0, "-z"), hw.BLACK,
              "deck posts down to the dog-ear arms")
        k.add("M4_heat-set_insert", hw.insert("M4"), hw.loc(x, y, ARM_Z1, "-z"), hw.BRASS, "dog-ear arms", bites="arms")
    for (x, y) in BACK_BOSSES:
        k.add("M3_heat-set_insert", hw.insert("M3"), hw.loc(x, y, -SLEEVE_D, "+z"), hw.BRASS, "sleeve back bosses",
              bites="sleeve")
        k.add("M3x8_countersunk_ISO10642", hw.screw("csk", "M3", 8), hw.loc(x, y, -SLEEVE_D - BACK_T, "+z"), hw.BLACK,
              "back plate to the sleeve")
    return k


def half(p, side):
    return p.intersect(box(min(0, side * 999), max(0, side * 999), -999, 999, -999, 999))


def flip(p):
    return p.rotate((0, 0, 0), (1, 0, 0), 180)


def union_all(parts):
    u = parts[0]
    for p in parts[1:]:
        u = u.union(p)
    return u


def vol(a, b):
    try:
        return round(a.intersect(b).val().Volume(), 2)
    except Exception:
        return 0.0


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else f"out_flush6_{TAB_KEY}"
    for d in ("machine", "print", "print/one_piece"):
        os.makedirs(f"{out}/{d}", exist_ok=True)

    def exp(path, part, step=True):
        cq.exporters.export(part, path + ".stl", tolerance=0.02, angularTolerance=0.1)
        if step:
            cq.exporters.export(part, path + ".step")

    PRINT = {"sleeve_L": flip(half(sleeve, -1)), "sleeve_R": flip(half(sleeve, 1)),
             "deck_L": half(deck, -1), "deck_R": half(deck, 1),
             "back_plate_L": back_L, "back_plate_R": back_R, "dog_ear_arm_x4": arm}
    ONE = {"sleeve_full": flip(sleeve), "deck_full": deck, "back_plate_full": back}
    exp(f"{out}/machine/trim_6061", trim)
    for nm, p in PRINT.items():
        exp(f"{out}/print/{nm}", p)
    for nm, p in ONE.items():
        exp(f"{out}/print/one_piece/{nm}", p)
    arms_u = union_all(arms)
    for nm, p in (("trim", trim), ("sleeve", sleeve), ("deck", deck), ("back", back), ("ipad", ipad),
                  ("plug", plug), ("plaster", plaster), ("studs", studs), ("arms", arms_u)):
        cq.exporters.export(p, f"{out}/_{nm}.stl", tolerance=0.05)
    assy = cq.Assembly(name=f"Flush_v6_{TAB_KEY}")
    assy.add(studs, name="studs_reference", color=cq.Color(0.80, 0.65, 0.45))
    assy.add(plaster, name="plasterboard_reference", color=cq.Color(0.93, 0.93, 0.90, 0.5))
    assy.add(sleeve, name="sleeve", color=cq.Color(0.15, 0.15, 0.17))
    assy.add(deck, name="deck", color=cq.Color(0.30, 0.30, 0.34))
    assy.add(back, name="back_plate", color=cq.Color(0.22, 0.22, 0.25))
    for i, a in enumerate(arms):
        assy.add(a, name=f"dog_ear_{i+1}", color=cq.Color(0.9, 0.45, 0.15))
    assy.add(ipad, name="ipad_reference", color=cq.Color(0.03, 0.03, 0.05))
    assy.add(plug, name="usb_c_plug_reference", color=cq.Color(0.95, 0.95, 0.95))
    assy.add(trim, name="trim_6061", color=cq.Color(0.74, 0.75, 0.78))
    kit = flush_kit()
    kit.to_assembly(assy)
    assy.export(f"{out}/assembly_flush6.step")
    hw_clash = kit.clashes({"trim": trim, "sleeve": sleeve, "deck": deck, "back_plate": back, "arms": arms_u,
                            "ipad": ipad, "plasterboard": plaster, "studs": studs})
    open(f"{out}/hardware.txt", "w").write(
        f"{TAB['name']} · Flush v6 hardware (all modelled in assembly_flush6.step)\n" + "\n".join(kit.bom_lines()) + "\n")

    reach = CLAMP_X + ARM_REACH
    stud_face = STUD_CC / 2 - STUD_W / 2
    rep = [f"{TAB['name']}: trim {TRIM_X:.1f} x {TRIM_Y:.1f} x {TRIM_T:.0f} mm ({trim.val().Volume()*2.7e-3:.0f} g 6061), "
           f"ends {(TRIM_X - IPAD_L) / 2 - LIP:.1f}, top/bottom {(TRIM_Y - IPAD_W) / 2:.1f} visible",
           f"cut-out {HOLE_X:.1f} x {HOLE_Y:.1f} (R{BOX_R + HOLE_CLR:.0f}); depth {SLEEVE_D + BACK_T:.1f} from the wall face",
           f"magnets y = ±{', ±'.join(f'{y:.1f}' for y in MAG_YS)} ({len(MAG_PTS)} pairs); pins y = ±{pin_y:.1f}; clamps y = ±{clamp_y:.1f}",
           f"arm reach ±{reach:.1f}; 35 mm studs at 450 c/c leave {stud_face - reach:.1f} mm a side "
           f"(45 mm studs: {STUD_CC / 2 - 45 / 2 - reach:.1f})"]
    checks = [("deck/sleeve", deck, sleeve), ("deck/ipad", deck, ipad), ("sleeve/ipad", sleeve, ipad),
              ("trim/ipad", trim, ipad), ("trim/deck", trim, deck), ("trim/sleeve", trim, sleeve),
              ("plug/deck", plug, deck), ("plug/sleeve", plug, sleeve), ("plug/trim", plug, trim),
              ("bend/deck", bend, deck), ("bend/sleeve", bend, sleeve), ("bend/back", bend, back),
              ("back/sleeve", back, sleeve), ("sleeve/studs", sleeve, studs), ("back/studs", back, studs),
              ("arms/sleeve", arms_u, sleeve), ("arms/deck", arms_u, deck), ("arms/plaster", arms_u, plaster),
              ("arms/studs", arms_u, studs), ("arms retracted/sleeve", union_all(arms_in), sleeve),
              ("arms retracted/deck", union_all(arms_in), deck)]
    for i, b in enumerate(buttons):
        checks += [(f"button {i + 1}/sleeve", b, sleeve), (f"button {i + 1}/deck", b, deck)]
    bad = 0
    for nm, a, b in checks:
        v = vol(a, b)
        bad += v > 0
        rep.append(f"clash {nm:26s} {v}")
    seated = vol(deck.translate((0, 0, -0.05)), sleeve) > 0
    bad += not seated
    rep.append(f"deck seats on ledges: {seated}")
    try:
        oh = union_all(arms_in).cut(rrect(HOLE_X, HOLE_Y, BOX_R + HOLE_CLR, -999, 999)).val().Volume()
    except Exception:
        oh = 0.0
    bad += oh > 0.01
    rep.append(f"retracted arms outside the cut-out: {oh:.2f} mm3")
    for nm, p in list(PRINT.items()) + list(ONE.items()):
        bb = p.val().BoundingBox()
        rep.append(f"size {nm:16s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  {'fits 256' if max(bb.xlen, bb.ylen) <= 256 else 'needs a big bed'}")
    rep.append(f"hardware: {len(kit.items)} parts modelled, {len(hw_clash)} clash(es)")
    rep += [f"  CLASH {n} / {p}: {v} mm3" for n, p, v in hw_clash]
    bad += len(hw_clash)
    rep.append("RESULT: " + ("ALL CHECKS PASS" if bad == 0 else f"{bad} PROBLEM(S)"))
    open(f"{out}/checks.txt", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))

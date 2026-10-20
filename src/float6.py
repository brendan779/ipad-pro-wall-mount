"""
Float Mount v6 -- surface PoE wall mount, any tablet in tablets.py.
Machined 6061 shell (or a printed shell, see printed6.py) + printed carrier,
hanger, lock boss, catch rail and wall bracket.

v6 changes from v4.2
  * tablet-driven: V6_TABLET=<key> picks the iPad (tablets.py)
  * +2 mm cable-loop room at BOTH ends (end frames 2 mm wider each side)
  * button reliefs in the carrier wall / end ribs, so the carrier can't press
    the volume or top buttons
  * the catch rail has END STOPS: the hanger drops between them with 0.4 mm a side,
    so the panel can't slide left/right on the bracket
  * front-camera notch on the short end or the top bar, rear-camera keep-outs,
    bosses / hanger / bracket scale with the tablet

Coordinates: carrier back = Z0, +Z toward the room, +X USB-C end, +Y up.
Run:  V6_TABLET=ipad_pro_13_m5 python float6.py out_dir
"""
import math
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tablets  # noqa: E402

TAB_KEY, TAB = tablets.get()

# ---------------- tablet --------------------------------------------------
IPAD_L, IPAD_W, IPAD_T, IPAD_R = TAB["L"], TAB["W"], TAB["T"], TAB["R"]
CLR = 0.35
CAM_SIDE, CAM_LEN = TAB["cam"]
CAM_SLOT_W = 8.4

# ---------------- USB-C cable (MEASURE YOURS) -----------------------------
PLUG_L, PLUG_W, PLUG_H, CABLE_D, BEND_R = 17.0, 12.5, 7.0, 4.5, 8.0
LOOP_EXTRA = 2.0          # v6: extra room for the cable to loop back (each end)

# ---------------- Mount ---------------------------------------------------
CB, GLASS_GAP, FT, SKIRT, SG, LIP = 3.0, 0.3, 2.5, 2.0, 0.3, 2.8
STANDOFF, VENT_INSET, CARRIER_WALL, END_RIB = 14.0, 32, 1.2, 2.0
BUTTON_RELIEF = 1.2       # v6: depth cut into the carrier wall at each button

CAVITY_X = PLUG_L + BEND_R + CABLE_D / 2 + 1.0 + LOOP_EXTRA
FRAME_X = CAVITY_X + CARRIER_WALL + SG + SKIRT
FRAME_Y = 12.0
OUT_L, OUT_W = IPAD_L + 2 * FRAME_X, IPAD_W + 2 * FRAME_Y
OUT_R = 24.0
IN_L, IN_W = IPAD_L + 2 * CLR, IPAD_W + 2 * CLR
IN_R = IPAD_R + CLR
PLATE_Z0 = CB + IPAD_T + GLASS_GAP
SHELL_H = PLATE_Z0 + FT
EDGE_Z = CB + IPAD_T / 2
CAR_L, CAR_W = OUT_L - 2 * (SKIRT + SG), OUT_W - 2 * (SKIRT + SG)
CAR_R = OUT_R - SKIRT - SG

# ---------------- holes (v4.2 rules: real 118° tap drill, JLCCNC guidance) --
THREAD_DEPTH, DRILL_DEPTH, DRILL_POINT, SCREW_LEN = 3.0, 4.5, 118.0, 5.0
BOSS_R, BOSS_R_LONG = 4.0, 3.0
TIP_TO_FACE = 6.7                     # metal from boss tip to the front face (v4.2: 1.45 mm skin)
BOSS_Z0 = SHELL_H - TIP_TO_FACE        # boss tip height: thinner iPads get taller bosses
CLAMP_T = 2.0                          # carrier thickness clamped under each screw head
CB_FLOOR = BOSS_Z0 - CLAMP_T           # head counterbore floor (from the carrier back)
LONG_BOSS_OFF = IPAD_W / 2 + CLR + 2.0 + BOSS_R_LONG + 0.3


def drill_cone_h(r):
    return r / math.tan(math.radians(DRILL_POINT / 2))


# sound/mic windows on each end (these vent through the carrier back)
WIN = {e: [tuple(w) for w in TAB["spk"][e]] + [tuple(w) for w in TAB["mic_end"][e]] for e in ("-x", "+x")}
END_BOSS_X = IPAD_L / 2 + FRAME_X / 2 - 1.5


def _end_boss_ys():
    """Two end bosses per corner side: one near the corner, and an inner one clear of every
    vented window, the plug cavity on +X and the corner boss, as close as it can get to
    40% of the way out from the centre (so the end is clamped along its length)."""
    corner = IPAD_W / 2 - 6.45
    bad = [w for e in ("-x", "+x") for w in WIN[e]] + [(-(PLUG_W / 2 + 1), PLUG_W / 2 + 1)]
    bad += [(corner - BOSS_R, corner + BOSS_R), (-corner - BOSS_R, -corner + BOSS_R)]
    need = BOSS_R + 1.5
    ok = []
    y = 6.0
    while y < corner:
        if all(y + need <= a or y - need >= b for a, b in bad) and all(-y + need <= a or -y - need >= b for a, b in bad):
            ok.append(y)
        y += 0.5
    if not ok:
        raise SystemExit("no room for an inner end boss")
    return [corner, min(ok, key=lambda c: abs(c - 0.4 * corner))]


BOSS_YS = _end_boss_ys()
BOSS_PTS = [(sx * END_BOSS_X, sy * yy) for sx in (-1, 1) for sy in (-1, 1) for yy in BOSS_YS]
_LX_IN = 0.285 * IPAD_L / 2
if CAM_SIDE == "top":                   # keep the inner B bosses clear of the printed shell's seam key
    _LX_IN = max(_LX_IN, CAM_LEN / 2 + 13.0)
LONG_X = [-0.784 * IPAD_L / 2, -_LX_IN, _LX_IN, 0.784 * IPAD_L / 2]
LONG_PTS = [(x, sy * LONG_BOSS_OFF) for x in LONG_X for sy in (-1, 1)]
ALL_BOSSES = [(x, y, BOSS_R) for x, y in BOSS_PTS] + [(x, y, BOSS_R_LONG) for x, y in LONG_PTS]


def screw(x, y):
    return (1.025, 1.4, 2.6) if (x, y) in LONG_PTS else (1.25, 1.7, 3.1)   # M2.5 / M3


# ---------------- bracket / hook / lock (scaled to the panel) ---------------
HOOK_LEN, GAP, RAIL_SP = 8.0, 3.6, 8.0
HOOK_Y = IPAD_W / 2 - 27.45
LOCK_Y = -(OUT_W / 2) + 5.0
BR_T = 3.0
BR_L = min(200.0, OUT_L - 60.0)
BR_W = OUT_W - 38.9
AU_PLATE_CTRS = 84.0
AU_HOLES = AU_PLATE_CTRS / 2 + 4 < HOOK_Y - RAIL_SP - 2      # room above/below for the AU plate screws?
CUTOUT = (46.0, min(68.0, 2 * (HOOK_Y - RAIL_SP) - 8.0))
HANGER_HALF = 55.0
STOP_CLR, STOP_T, STOP_RISE = 0.4, 5.0, 12.0                 # v6 lateral stops


def rrect(l, w, r, h, z0=0.0, x=0.0, y=0.0):
    return cq.Workplane("XY").rect(l, w).extrude(h).edges("|Z").fillet(r).translate((x, y, z0))


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def zcyl(x, y, r, z0, z1):
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def ycyl(x, z, r, y0, y1):
    return cq.Workplane("XZ").circle(r).extrude(-(y1 - y0)).translate((x, y0, z))


def csk(x, y, z_face, r_hole, r_head, depth, up=True):
    if up:
        return (cq.Workplane("XY").circle(r_hole).workplane(offset=depth)
                .circle(r_head).loft().translate((x, y, z_face - depth + 0.001)))
    return (cq.Workplane("XY").circle(r_head).workplane(offset=depth)
            .circle(r_hole).loft().translate((x, y, z_face - 0.001)))


def cam_slot(z0, z1):
    """Front-camera stadium slot, centred on the window edge."""
    if CAM_SIDE == "end":
        return (cq.Workplane("XY").slot2D(CAM_LEN, CAM_SLOT_W, angle=90).extrude(z1 - z0)
                .translate((-(IPAD_L / 2 - LIP), 0, z0)))
    return (cq.Workplane("XY").slot2D(CAM_LEN, CAM_SLOT_W, angle=0).extrude(z1 - z0)
            .translate((0, IPAD_W / 2 - LIP, z0)))


# =========================== SHELL (6061) ===================================
shell = rrect(OUT_L, OUT_W, OUT_R, SHELL_H)
shell = shell.cut(rrect(OUT_L - 2 * SKIRT, OUT_W - 2 * SKIRT, OUT_R - SKIRT, PLATE_Z0 + 1, z0=-1)
                  .intersect(box(-999, 999, -999, 999, -1, PLATE_Z0)))
shell = shell.cut(rrect(IPAD_L - 2 * LIP, IPAD_W - 2 * LIP, IPAD_R - LIP, SHELL_H + 2, z0=-1))
shell = shell.cut(cam_slot(-1, SHELL_H + 1))
shell_front_edges = cq.selectors.BoxSelector((-999, -999, SHELL_H - 0.01), (999, 999, SHELL_H + 0.01))
shell = shell.edges(shell_front_edges).fillet(0.8)
for (x, y, r) in ALL_BOSSES:
    shell = shell.union(zcyl(x, y, r, BOSS_Z0, PLATE_Z0 + 0.01))
    if (x, y) in LONG_PTS:
        sy = 1 if y > 0 else -1
        y0, y1 = sorted((y, sy * (OUT_W / 2 - SKIRT / 2)))
        shell = shell.union(box(x - r, x + r, y0, y1, BOSS_Z0, PLATE_Z0 + 0.01))
    rt = screw(x, y)[0]
    zf = BOSS_Z0 + DRILL_DEPTH
    shell = shell.cut(zcyl(x, y, rt, BOSS_Z0 - 1, zf))
    shell = shell.cut(cq.Workplane().add(cq.Solid.makeCone(rt, 0.0, drill_cone_h(rt), cq.Vector(x, y, zf), cq.Vector(0, 0, 1))))
plug_top = EDGE_Z + PLUG_H / 2 + 0.3
if plug_top > PLATE_Z0:
    shell = shell.cut(box(IPAD_L / 2 - 1, IPAD_L / 2 + PLUG_L + 2, -(PLUG_W / 2 + 1), PLUG_W / 2 + 1,
                          PLATE_Z0 - 0.01, plug_top))

# =========================== CARRIER ========================================
car = rrect(CAR_L, CAR_W, CAR_R, PLATE_Z0)
car = car.cut(rrect(IN_L, IN_W, IN_R, PLATE_Z0, z0=CB))
car = car.cut(rrect(IN_L - 2 * VENT_INSET, IN_W - 2 * VENT_INSET, 14, CB + 2, z0=-1))
for f in TAB["rear"]:                                               # rear-camera keep-outs
    if f[0] == "circle":
        car = car.cut(zcyl(f[1], f[2], f[3], -1, CB + 0.01))
    else:
        # clipped to the iPad pocket, so the cut never undercuts the carrier wall
        car = car.cut(box(f[1], f[2], f[3], f[4], -1, CB + 0.01).intersect(rrect(IN_L, IN_W, IN_R, CB + 3, z0=-2)))
car = car.cut(box(IN_L / 2 - 0.5, IPAD_L / 2 + CAVITY_X, -(PLUG_W / 2 + 1.0), PLUG_W / 2 + 1.0, -1, PLATE_Z0 + 0.01))
for sx, e in ((-1, "-x"), (1, "+x")):                              # open-top sound chambers
    cx0, cx1 = sorted((sx * (IN_L / 2 + END_RIB), sx * (IPAD_L / 2 + CAVITY_X)))
    car = car.cut(box(cx0, cx1, -(IN_W / 2 - 12), IN_W / 2 - 12, EDGE_Z - 1.3, PLATE_Z0 + 1))
    rx0, rx1 = sorted((sx * (IN_L / 2 - 0.5), sx * (IN_L / 2 + END_RIB + 0.1)))
    vx0, vx1 = sorted((sx * (IPAD_L / 2 + 8), sx * (IPAD_L / 2 + CAVITY_X - 2)))
    for (y0, y1) in WIN[e]:
        car = car.cut(box(rx0, rx1, y0, y1, EDGE_Z - 1.3, PLATE_Z0 + 1))
        car = car.cut(box(vx0, vx1, y0, y1, -1, EDGE_Z))
# v6: button reliefs (open-top pockets in the wall / rib, no venting)
for b in TAB["buttons"]:
    if b[0] in ("top", "bottom"):
        sy = 1 if b[0] == "top" else -1
        y0, y1 = sorted((sy * (IN_W / 2 - 0.5), sy * (IN_W / 2 + BUTTON_RELIEF)))
        car = car.cut(box(b[1], b[2], y0, y1, CB + 0.3, PLATE_Z0 + 1))
    else:
        sx = 1 if b[0] == "+x" else -1
        x0, x1 = sorted((sx * (IN_L / 2 - 0.5), sx * (IN_L / 2 + BUTTON_RELIEF)))
        car = car.cut(box(x0, x1, b[1], b[2], CB + 0.3, PLATE_Z0 + 1))
for (x0, x1) in TAB["mic_top"]:                                     # side mics: relief + vent
    car = car.cut(box(x0, x1, IN_W / 2 - 0.5, IN_W / 2 + BUTTON_RELIEF, -1, PLATE_Z0 + 1))
for (x, y, r) in ALL_BOSSES:
    car = car.cut(zcyl(x, y, r + 0.3, BOSS_Z0 - 0.2, PLATE_Z0 + 1))
    if (x, y) in LONG_PTS:
        sy = 1 if y > 0 else -1
        y0, y1 = sorted((y, sy * (CAR_W / 2 + 1)))
        car = car.cut(box(x - r - 0.3, x + r + 0.3, y0, y1, BOSS_Z0 - 0.2, PLATE_Z0 + 1))
    _, rc, rh = screw(x, y)
    car = car.cut(zcyl(x, y, rc, -1, BOSS_Z0))
    car = car.cut(zcyl(x, y, rh, -1, CB_FLOOR))

# hanger + lock boss (they also splice the carrier quarters)
W0 = -STANDOFF
LOCK_Z = W0 + BR_T + 5.0
PAD_T = 3.0
HANG_BOLTS = [(x, HOOK_Y + HOOK_LEN + 8.0) for x in (-45, -20, 20, 45)]
LOCK_BOLTS = [(x, LOCK_Y + 22.0) for x in (-22, 22)]
H = HANGER_HALF
stem = box(-H, H, HOOK_Y + HOOK_LEN + 0.8, HOOK_Y + HOOK_LEN + 4.8, W0 + BR_T + 0.4, -PAD_T)
foot = box(-H, H, HOOK_Y + 0.6, HOOK_Y + HOOK_LEN + 4.8, W0 + BR_T + 0.4, W0 + BR_T + GAP - 0.4)
hanger = box(-H, H, HOOK_Y + HOOK_LEN + 0.8, HOOK_Y + HOOK_LEN + 14.0, W0 + BR_T + 0.4, 0).union(stem).union(foot)
boss = box(-12, 12, LOCK_Y + 8.5, LOCK_Y + 17.5, W0 + BR_T + 1.0, -PAD_T)
lock_boss = (box(-30, 30, LOCK_Y + 8.5, LOCK_Y + 26.0, -PAD_T, 0).union(boss)
             .cut(ycyl(0, LOCK_Z, 2.1, LOCK_Y + 8, LOCK_Y + 16)))


def nut_trap(x, y):
    return cq.Workplane("XY").polygon(6, 6.7).extrude(2.6).translate((x, y, -PAD_T - 0.01))


for (x, y) in HANG_BOLTS:
    hanger = hanger.cut(zcyl(x, y, 2.1, -6.0, 1))
    car = car.cut(zcyl(x, y, 1.7, -1, CB + 1)).cut(csk(x, y, CB, 1.7, 3.3, 1.6))
for (x, y) in LOCK_BOLTS:
    lock_boss = lock_boss.cut(zcyl(x, y, 1.7, -PAD_T - 1, 1)).cut(nut_trap(x, y))
    if abs(y) < IN_W / 2:
        car = car.cut(zcyl(x, y, 1.7, -1, CB + 1)).cut(csk(x, y, CB, 1.7, 3.3, 1.6))
    else:
        car = car.cut(zcyl(x, y, 1.7, -1, PLATE_Z0 + 1)).cut(csk(x, y, PLATE_Z0, 1.7, 3.3, 1.6))

# =========================== WALL BRACKET + CATCH RAIL ======================
br = rrect(BR_L, BR_W, 14, BR_T)
br = br.cut(rrect(*CUTOUT, 6, BR_T + 2, z0=-1))
if AU_HOLES:
    for sy in (1, -1):
        br = br.cut(zcyl(0, sy * AU_PLATE_CTRS / 2, 2.0, -1, BR_T + 1))
for sx in (-1, 1):
    for sy in (-1, 1):
        br = br.cut(cq.Workplane("XY").slot2D(16, 5.2).extrude(BR_T + 2)
                    .translate((sx * (BR_L / 2 - 18), sy * (BR_W / 2 - 18), -1)))
RAIL_HALF = H + STOP_CLR + STOP_T
catch_rail = (box(-RAIL_HALF, RAIL_HALF, HOOK_Y - RAIL_SP, HOOK_Y, BR_T, BR_T + GAP)
              .union(box(-RAIL_HALF, RAIL_HALF, HOOK_Y - RAIL_SP, HOOK_Y + HOOK_LEN, BR_T + GAP, BR_T + GAP + 3.0)))
# v6 lateral stops: cheeks at both ends, full rail height, rising STOP_RISE above the lip
for sx in (-1, 1):
    x0, x1 = sorted((sx * (H + STOP_CLR), sx * RAIL_HALF))
    catch_rail = catch_rail.union(box(x0, x1, HOOK_Y - RAIL_SP, HOOK_Y + HOOK_LEN + STOP_RISE, BR_T, BR_T + GAP + 3.0))
RAIL_BOLTS = [(x, HOOK_Y - RAIL_SP / 2) for x in (-48, -16, 16, 48)]
for (x, y) in RAIL_BOLTS:
    catch_rail = catch_rail.cut(zcyl(x, y, 2.1, BR_T - 0.1, BR_T + 5.5))
    br = br.cut(zcyl(x, y, 1.7, -1, BR_T + 1)).cut(csk(x, y, 0, 1.7, 3.3, 1.6, up=False))
br = br.union(box(-20, 20, LOCK_Y, -BR_W / 2 + 6, 0, BR_T))
br = br.union(box(-12, 12, LOCK_Y, LOCK_Y + 8.0, BR_T, BR_T + 9.0))
br = br.cut(ycyl(0, LOCK_Z + STANDOFF, 1.7, LOCK_Y - 1, LOCK_Y + 9))
br = br.cut(ycyl(0, LOCK_Z + STANDOFF, 3.0, LOCK_Y - 1, LOCK_Y + 3.0))

# =========================== ASSEMBLY / REFERENCES ===========================


def up(p, dz=STANDOFF):
    return p.translate((0, 0, dz))


shell_a, car_a, hanger_a, lock_a = up(shell), up(car), up(hanger), up(lock_boss)
br_plate = br
br = br_plate.union(catch_rail)
rear_a = car_a.union(hanger_a).union(lock_a)
ipad = rrect(IPAD_L, IPAD_W, IPAD_R, IPAD_T, z0=STANDOFF + CB)
plug = up(box(IPAD_L / 2, IPAD_L / 2 + PLUG_L, -PLUG_W / 2, PLUG_W / 2, EDGE_Z - PLUG_H / 2, EDGE_Z + PLUG_H / 2))
bend = up(box(IPAD_L / 2 + PLUG_L, IPAD_L / 2 + PLUG_L + BEND_R + CABLE_D / 2 + LOOP_EXTRA,
              -CABLE_D / 2, CABLE_D / 2, -STANDOFF + BR_T + 2, EDGE_Z + CABLE_D / 2))
# button bodies (0.6 mm proud of the edge, 3 mm tall) to prove the reliefs clear them
buttons = []
for b in TAB["buttons"]:
    if b[0] in ("top", "bottom"):
        sy = 1 if b[0] == "top" else -1
        y0, y1 = sorted((sy * IPAD_W / 2, sy * (IPAD_W / 2 + 0.6)))
        buttons.append(up(box(b[1] + 2, b[2] - 2, y0, y1, EDGE_Z - 1.5, EDGE_Z + 1.5)))
    else:
        sx = 1 if b[0] == "+x" else -1
        x0, x1 = sorted((sx * IPAD_L / 2, sx * (IPAD_L / 2 + 0.6)))
        buttons.append(up(box(x0, x1, b[1] + 2, b[2] - 2, EDGE_Z - 1.5, EDGE_Z + 1.5)))
BIG = 2000

# =========================== HARDWARE (for the STEP assembly) ================
import hardware6 as hw  # noqa: E402

LOW_HEAD = CB_FLOOR < hw.CAP["M3"][1] - 1e-6        # thin iPads: cap heads would stand proud


def float_kit(shell_name="shell"):
    k = hw.Kit()
    kind = "button" if LOW_HEAD else "cap"
    std = "ISO7380" if LOW_HEAD else "ISO4762"
    for (x, y) in BOSS_PTS:
        k.add(f"M3x5_{kind}_{std}", hw.screw(kind, "M3", 5), hw.loc(x, y, STANDOFF + CB_FLOOR, "+z"), hw.BLACK,
              "carrier to shell, end bosses", bites=shell_name)
    for (x, y) in LONG_PTS:
        k.add(f"M2.5x5_{kind}_{std}", hw.screw(kind, "M2.5", 5), hw.loc(x, y, STANDOFF + CB_FLOOR, "+z"), hw.BLACK,
              "carrier to shell, top/bottom bosses", bites=shell_name)
    for (x, y) in HANG_BOLTS:
        k.add("M3_heat-set_insert", hw.insert("M3"), hw.loc(x, y, STANDOFF, "-z"), hw.BRASS, "hanger", bites="hanger")
        k.add("M3x8_countersunk_ISO10642", hw.screw("csk", "M3", 8), hw.loc(x, y, STANDOFF + CB, "-z"), hw.BLACK,
              "carrier to hanger")
    for (x, y) in LOCK_BOLTS:
        k.add("M3_nut_ISO4032", hw.nut("M3"), hw.loc(x, y, STANDOFF - PAD_T + 0.1, "-z"), hw.STEEL, "lock boss hex pockets")
        k.add("M3x8_countersunk_ISO10642", hw.screw("csk", "M3", 8), hw.loc(x, y, STANDOFF + CB, "-z"), hw.BLACK,
              "carrier to lock boss")
    k.add("M3_heat-set_insert", hw.insert("M3"), hw.loc(0, LOCK_Y + 8.5, STANDOFF + LOCK_Z, "+y"), hw.BRASS,
          "lock boss (end-on)", bites="lock_boss")
    k.add("M3x12_cap_ISO4762", hw.screw("cap", "M3", 12), hw.loc(0, LOCK_Y + 3.0, STANDOFF + LOCK_Z, "+y"), hw.BLACK,
          "lock screw, up from below")
    for (x, y) in RAIL_BOLTS:
        k.add("M3_heat-set_insert", hw.insert("M3"), hw.loc(x, y, BR_T, "+z"), hw.BRASS, "catch rail", bites="catch_rail")
        k.add("M3x8_countersunk_ISO10642", hw.screw("csk", "M3", 8), hw.loc(x, y, 0.0, "+z"), hw.BLACK,
              "bracket to catch rail, from the wall side")
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.add("wall_screw_M4x30_pan_reference", hw.screw("pan", "M4", 30),
                  hw.loc(sx * (BR_L / 2 - 18), sy * (BR_W / 2 - 18), BR_T, "-z"), hw.STEEL,
                  "bracket slots (use anchors or wood screws to suit the wall)")
    return k



def quad(p, sx, sy):
    return p.intersect(box(min(0, sx * BIG), max(0, sx * BIG), min(0, sy * BIG), max(0, sy * BIG), -BIG, BIG))


def flip(p):
    return p.rotate((0, 0, 0), (1, 0, 0), 180)


def vol(a, b):
    try:
        return round(a.intersect(b).val().Volume(), 2)
    except Exception:
        return 0.0


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else f"out_float6_{TAB_KEY}"
    for d in ("print", "print/one_piece", "machine"):
        os.makedirs(f"{out}/{d}", exist_ok=True)

    def exp(path, part, step=True):
        cq.exporters.export(part, path + ".stl", tolerance=0.02, angularTolerance=0.1)
        if step:
            cq.exporters.export(part, path + ".step")

    exp(f"{out}/machine/shell_6061", shell)
    PRINT = {f"carrier_{nm}": quad(car, sx, sy) for (sx, sy), nm in
             {(-1, 1): "TL", (1, 1): "TR", (-1, -1): "BL", (1, -1): "BR"}.items()}
    PRINT.update({"hanger": hanger, "lock_boss": flip(lock_boss), "wall_bracket": br_plate,
                  "catch_rail": flip(catch_rail)})
    for nm, p in PRINT.items():
        exp(f"{out}/print/{nm}", p)
    exp(f"{out}/print/one_piece/carrier_full", car)
    for nm, p in (("rear", rear_a), ("shell", shell_a), ("ipad", ipad), ("bracket", br), ("plug", plug)):
        cq.exporters.export(p, f"{out}/_{nm}.stl", tolerance=0.05)
    assy = cq.Assembly(name=f"Float_v6_{TAB_KEY}")
    assy.add(br, name="wall_bracket", color=cq.Color(0.62, 0.63, 0.66))
    assy.add(car_a, name="carrier", color=cq.Color(0.15, 0.15, 0.17))
    assy.add(hanger_a, name="hanger", color=cq.Color(0.85, 0.45, 0.15))
    assy.add(lock_a, name="lock_boss", color=cq.Color(0.85, 0.45, 0.15))
    assy.add(ipad, name="ipad_reference", color=cq.Color(0.03, 0.03, 0.05))
    assy.add(plug, name="usb_c_plug_reference", color=cq.Color(0.9, 0.9, 0.9))
    assy.add(shell_a, name="shell_6061", color=cq.Color(0.72, 0.73, 0.76))
    kit = float_kit()
    kit.to_assembly(assy)
    assy.export(f"{out}/assembly_float6.step")
    hw_parts = {"shell": shell_a, "carrier": car_a, "hanger": hanger_a, "lock_boss": lock_a,
                "wall_bracket": up(br_plate, 0), "catch_rail": up(catch_rail, 0), "ipad": ipad}
    hw_clash = kit.clashes(hw_parts)
    open(f"{out}/hardware.txt", "w").write(
        f"{TAB['name']} · Float v6 hardware (all modelled in assembly_float6.step)\n" + "\n".join(kit.bom_lines()) + "\n")

    rep = []
    rep.append(f"{TAB['name']}: shell {OUT_L:.1f} x {OUT_W:.1f} x {SHELL_H:.1f} mm, ends {FRAME_X:.1f}, top/bottom {FRAME_Y:.1f}, "
               f"{STANDOFF + SHELL_H:.1f} off the wall, {shell.val().Volume()*2.70e-3:.0f} g 6061")
    rep.append(f"end bosses at y = ±{BOSS_YS[0]:.2f}, ±{BOSS_YS[1]:.2f}; long bosses at x = " + ", ".join(f"{x:.1f}" for x in LONG_X))
    rep.append(f"bracket {BR_L:.1f} x {BR_W:.1f}, cut-out {CUTOUT[0]:.0f} x {CUTOUT[1]:.0f}, AU plate holes: {'yes' if AU_HOLES else 'no (no room)'}")
    checks = [("rear/bracket", rear_a, br), ("rear/bracket +10 mm (offered high)", rear_a.translate((0, 10, 0)), br),
              ("shell/bracket +10", shell_a.translate((0, 10, 0)), br), ("carrier/ipad", car_a, ipad),
              ("shell/ipad", shell_a, ipad), ("shell/carrier", shell_a, car_a), ("shell/hanger,lock", shell_a, hanger_a.union(lock_a)),
              ("plug/carrier", plug, car_a), ("plug/shell", plug, shell_a), ("bend/carrier", bend, car_a), ("bend/shell", bend, shell_a)]
    for i, b in enumerate(buttons):
        checks.append((f"button {i + 1}/carrier", b, car_a))
        checks.append((f"button {i + 1}/shell", b, shell_a))
    # lateral stops: hanger shifted 0.5 mm sideways must hit the rail cheeks
    checks_hit = [("hanger +0.5 mm X hits stop", hanger_a.translate((0.5, 0, 0)), br),
                  ("hanger -0.5 mm X hits stop", hanger_a.translate((-0.5, 0, 0)), br)]
    bad = 0
    for nm, a, b in checks:
        v = vol(a, b)
        bad += v > 0
        rep.append(f"clash {nm:36s} {v}")
    for nm, a, b in checks_hit:
        v = vol(a, b)
        bad += v <= 0
        rep.append(f"stop  {nm:36s} {v} {'OK' if v > 0 else 'NO CONTACT'}")
    rep.append(f"boss tip z {BOSS_Z0:.2f}; screw head counterbore {CB_FLOOR:.2f} deep "
               f"({'ISO 4762 cap heads sit flush' if not LOW_HEAD else f'a cap head would sit {3.0 - CB_FLOOR:.1f} proud: ISO 7380 button heads (1.65 mm) used'}); "
               f"engagement {SCREW_LEN - CLAMP_T:.1f} mm")
    rep.append(f"hardware: {len(kit.items)} parts modelled, {len(hw_clash)} clash(es)")
    rep += [f"  CLASH {n} / {p}: {v} mm3" for n, p, v in hw_clash]
    bad += len(hw_clash)
    for nm, r in (("M3", 1.25), ("M2.5", 1.025)):
        rep.append(f"{nm}: skin under drill point {SHELL_H - (BOSS_Z0 + DRILL_DEPTH + drill_cone_h(r)):.2f} mm")
    for nm, p in list(PRINT.items()) + [("carrier one piece", car)]:
        bb = p.val().BoundingBox()
        rep.append(f"size {nm:18s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  {'fits 256' if max(bb.xlen, bb.ylen) <= 256 else 'needs a big bed'}")
    rep.append("RESULT: " + ("ALL CHECKS PASS" if bad == 0 else f"{bad} PROBLEM(S)"))
    open(f"{out}/checks.txt", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))

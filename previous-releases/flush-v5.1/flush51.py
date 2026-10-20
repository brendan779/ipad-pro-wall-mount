"""
iPad Pro 12.9" (3rd gen) FLUSH in-wall mount -- v5.1 (printable)
Existing 10 mm plasterboard, 70 mm studs at 450 c/c.

v5.1 splits the v5 back box so EVERY part prints flat with no supports:
  * SLEEVE (2 halves)   walls + flange only, open back. Printed face-down: the
                        wall-contact face comes off the bed dead flat. 45-degree
                        ledges inside carry the deck.
  * DECK (2 halves)     flat insert: iPad bed, end ribs, magnet/pin posts and the
                        4 dog-ear screw posts. Printed bottom-down. Its 45-degree
                        bevelled edges seat on the sleeve ledges (self-centring).
  * BACK PLATE (2 pcs)  flat; PoE adapter + Cat6 entry. Split off-centre so it
                        spans the sleeve seam and ties the halves together.
  * DOG-EAR ARMS x4     unchanged. Their M4 screws run through the DECK posts, so
                        tightening them clamps plasterboard between the arms and
                        the sleeve flange AND locks the deck in.
  * TRIM (6061)         unchanged from v5 (magnets in the deck posts).

Coordinates: wall face = Z0, +Z out of the wall, +X long edge, +Y up.
>>> Feature positions and plug sizes are approximations: measure them.
"""
import os
import cadquery as cq

# ---------------- iPad / cable / wall (as v5) -----------------------------
IPAD_L, IPAD_W, IPAD_T, IPAD_R = 280.6, 214.9, 5.9, 10.3
CLR = 0.35
CAM_FRONT_W = 32.0
SPK_LEN, SPK_FROM_CORNER = 36, 20
REAR_CAM, REAR_CAM_R = (-IPAD_L / 2 + 16, IPAD_W / 2 - 16), 11.0
PLUG_L, PLUG_W, PLUG_H, CABLE_D, BEND_R = 17.0, 12.5, 7.0, 4.5, 8.0
PLASTER = 10.0
STUD_CC, STUD_W, STUD_D = 450.0, 35.0, 70.0

# ---------------- Mount --------------------------------------------------
GLASS_GAP, FL_T, TRIM_T, LIP = 0.3, 1.5, 3.0, 2.8
WALL, DECK_T = 2.0, 3.0
SLEEVE_D = 55.0          # sleeve depth behind the wall face
BACK_T = 2.5             # back plate (sits on the sleeve's back edge)
HOLE_CLR, FLANGE_W, TRIM_OVER = 1.0, 6.0, 1.0
VENT_INSET = 32
DECK_SG = 0.3            # deck-to-wall gap
LEDGE_W, BEVEL = 2.5, 1.5

Z_F = FL_T
GLASS_Z = Z_F - GLASS_GAP
IPAD_Z0 = GLASS_Z - IPAD_T
EDGE_Z = IPAD_Z0 + IPAD_T / 2
DECK_Z0 = IPAD_Z0 - DECK_T

END_X = PLUG_L + BEND_R + CABLE_D / 2 + 1.0
IN_L, IN_W = IPAD_L + 2 * CLR, IPAD_W + 2 * CLR
BOX_IN_X, BOX_IN_Y = IPAD_L / 2 + END_X, IN_W / 2           # sleeve inner half-sizes
BOX_X, BOX_Y = 2 * (BOX_IN_X + WALL), 2 * (BOX_IN_Y + WALL)
BOX_R = 6.0
IN_R_BOX = BOX_R - WALL + 0.5
HOLE_X, HOLE_Y = BOX_X + 2 * HOLE_CLR, BOX_Y + 2 * HOLE_CLR
FLG_X, FLG_Y = BOX_X + 2 * FLANGE_W, BOX_Y + 2 * FLANGE_W
TRIM_X, TRIM_Y = FLG_X + 2 * TRIM_OVER, FLG_Y + 2 * TRIM_OVER
TRIM_R = 14.0

MAG_D, MAG_H = 10.0, 1.5
MAG_PTS = [(sx * (IPAD_L / 2 + 14), y) for sx in (-1, 1) for y in (-100, -18, 18, 100)]
PIN_PTS = [(-(IPAD_L / 2 + 22), 75.0), (IPAD_L / 2 + 22, -75.0)]
CLAMP_PTS = [(sx * (BOX_X / 2 - WALL - 6.0), sy * 45.0) for sx in (-1, 1) for sy in (-1, 1)]
ARM_REACH, ARM_W, ARM_T = 18.0, 12.0, 6.0
GRILLE_X = [IPAD_L / 2 + 6 + 4 * i for i in range(5)]
SPK_Y = IN_W / 2 - SPK_FROM_CORNER - SPK_LEN / 2
BACK_SPLIT_X = 60.0
BACK_BOSSES = ([(sx * (BOX_IN_X - 4), sy * (BOX_IN_Y - 4)) for sx in (-1, 1) for sy in (-1, 1)] +
               [(x, sy * (BOX_IN_Y - 3)) for x in (-110, 110) for sy in (-1, 1)])


def rrect(l, w, r, z0, z1, x=0.0, y=0.0):
    return (cq.Workplane("XY").rect(l, w).extrude(z1 - z0).edges("|Z").fillet(r)
            .translate((x, y, z0)))


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def zcyl(x, y, r, z0, z1):
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def yslot(x, y, length, width, z0, z1):
    return (cq.Workplane("XY").slot2D(length, width, angle=90).extrude(z1 - z0)
            .translate((x, y, z0)))


def ledge_profile(w_in, length, axis):
    """45-degree deck ledge on the inside of a wall whose inner face is at w_in.
    axis='y': runs along X on a long wall (+Y side); axis='x': along Y on an end wall (+X)."""
    zt = DECK_Z0 + DECK_SG + BEVEL                     # tip where the slope meets the wall
    pts = [(0.0, zt), (-LEDGE_W, zt - LEDGE_W), (-LEDGE_W, zt - LEDGE_W - 1.2), (0.0, zt - LEDGE_W - 1.2)]
    if axis == "y":       # profile in YZ, extruded along X
        wp = cq.Workplane("YZ").polyline([(w_in + u, z) for u, z in pts]).close().extrude(length / 2, both=True)
    else:                 # profile in XZ, extruded along Y
        wp = (cq.Workplane("XZ").polyline([(w_in + u, z) for u, z in pts]).close()
              .extrude(length / 2, both=True))
    return wp


# =============================== TRIM (6061, unchanged) =====================
trim = rrect(TRIM_X, TRIM_Y, TRIM_R, Z_F, Z_F + TRIM_T)
trim = trim.cut(rrect(IPAD_L - 2 * LIP, IPAD_W - 2 * LIP, IPAD_R - LIP, Z_F - 1, Z_F + TRIM_T + 1))
trim = trim.cut(yslot(-(IPAD_L / 2 - LIP), 0, CAM_FRONT_W, 8.4, Z_F - 1, Z_F + TRIM_T + 1))
trim = trim.edges(cq.selectors.BoxSelector((-999, -999, Z_F + TRIM_T - 0.01),
                                           (999, 999, Z_F + TRIM_T + 0.01))).fillet(0.8)
for sx in (-1, 1):
    for gx in GRILLE_X:
        for yc, ln in ((SPK_Y, SPK_LEN - 6), (-SPK_Y, SPK_LEN - 6), (0.0, 16.0)):
            trim = trim.cut(yslot(sx * gx, yc, ln, 2.0, Z_F - 1, Z_F + TRIM_T + 1))
for (x, y) in MAG_PTS:
    trim = trim.cut(zcyl(x, y, MAG_D / 2 + 0.1, Z_F - 1, Z_F + MAG_H + 0.1))
for (x, y) in PIN_PTS:
    trim = trim.cut(zcyl(x, y, 1.5, Z_F - 1, Z_F + 2.0))
plug_top = EDGE_Z + PLUG_H / 2 + 0.3
if plug_top > Z_F:
    trim = trim.cut(box(IPAD_L / 2 - 1, IPAD_L / 2 + PLUG_L + 2, -(PLUG_W / 2 + 1), PLUG_W / 2 + 1,
                        Z_F - 1, plug_top))

# =============================== SLEEVE ====================================
sleeve = rrect(BOX_X, BOX_Y, BOX_R, -SLEEVE_D, Z_F).union(rrect(FLG_X, FLG_Y, BOX_R + FLANGE_W, 0, Z_F))
sleeve = sleeve.cut(rrect(2 * BOX_IN_X, 2 * BOX_IN_Y, IN_R_BOX, -SLEEVE_D - 1, Z_F + 1))
# 45-degree deck ledges: long walls full length, end walls with gaps for the arm slots
for sy in (-1, 1):
    l = ledge_profile(BOX_IN_Y, 2 * BOX_IN_X - 2 * IN_R_BOX, "y")
    sleeve = sleeve.union(l if sy > 0 else l.mirror("XZ"))
CABLE_GAP = CABLE_D / 2 + 3.0                     # keep the +X ledge clear of the cable bend
for sx in (-1, 1):
    mids = [(-37.0, -CABLE_GAP), (CABLE_GAP, 37.0)] if sx > 0 else [(-37.0, 37.0)]
    for (y0, y1) in [(-BOX_IN_Y + IN_R_BOX, -53.0)] + mids + [(53.0, BOX_IN_Y - IN_R_BOX)]:
        l = ledge_profile(BOX_IN_X, y1 - y0, "x").translate((0, (y0 + y1) / 2, 0))
        sleeve = sleeve.union(l if sx > 0 else l.mirror("YZ"))
# Dog-ear arm slots through the end walls
for (x, y) in CLAMP_PTS:
    sx = 1 if x > 0 else -1
    wx0, wx1 = sorted((sx * (BOX_IN_X - 0.5), sx * (BOX_X / 2 + 1)))
    hw = ARM_W / 2 + 1
    sleeve = sleeve.cut(box(wx0, wx1, y - hw, y + hw, -45, -PLASTER + 0.5))
    # pointed 45-degree roof at the back end of the slot (prints without a bridge)
    roof = (cq.Workplane("YZ").polyline([(y - hw, -45.0), (y + hw, -45.0), (y, -45.0 - hw)]).close()
            .extrude((wx1 - wx0) / 2, both=True).translate(((wx0 + wx1) / 2, 0, 0)))
    sleeve = sleeve.cut(roof)
# Back-plate bosses (wall-attached, 45-degree lead-in on the front so they print
# face-down without support); M3 heat-set inserts from the back edge
for (x, y) in BACK_BOSSES:
    corner = abs(abs(x) - (BOX_IN_X - 4)) < 0.01
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    if corner:
        x0, x1 = sorted((sx * (BOX_IN_X - 8), sx * BOX_IN_X))
        d = 8.0
    else:
        x0, x1 = x - 5, x + 5
        d = 6.0
    wy = sy * BOX_IN_Y                               # long-wall inner face
    y0, y1 = sorted((wy - sy * d, wy))
    zb = -SLEEVE_D + 10
    sleeve = sleeve.union(box(x0, x1, y0, y1, -SLEEVE_D, zb))
    # 45-degree wedge on the boss's front so it grows out of the wall when printed face-down
    wedge = (cq.Workplane("YZ").polyline([(wy, zb), (wy - sy * d, zb), (wy, zb + d)]).close()
             .extrude((x1 - x0) / 2, both=True).translate(((x0 + x1) / 2, 0, 0)))
    sleeve = sleeve.union(wedge)
    sleeve = sleeve.cut(zcyl(x, y, 2.1, -SLEEVE_D - 1, -SLEEVE_D + 6))     # M3 heat-set

# =============================== DECK =====================================
DX, DY = BOX_IN_X - DECK_SG, BOX_IN_Y - DECK_SG
deck = rrect(2 * DX, 2 * DY, IN_R_BOX - DECK_SG, DECK_Z0, IPAD_Z0)
# 45-degree bevel on the back edges -> seats on the ledges
deck = deck.edges(cq.selectors.BoxSelector((-999, -999, DECK_Z0 - 0.01), (999, 999, DECK_Z0 + 0.01))).chamfer(BEVEL)
deck = deck.cut(rrect(IN_L - 2 * VENT_INSET, IN_W - 2 * VENT_INSET, 14, DECK_Z0 - 1, IPAD_Z0 + 1))
deck = deck.cut(zcyl(*REAR_CAM, REAR_CAM_R, DECK_Z0 - 1, IPAD_Z0 + 1))
deck = deck.cut(box(IN_L / 2 - 0.5, BOX_IN_X + 1, -(PLUG_W / 2 + 1), PLUG_W / 2 + 1, DECK_Z0 - 1, IPAD_Z0 + 1))
for sx in (-1, 1):                                  # end ribs (locate the iPad in X)
    x0, x1 = sorted((sx * IN_L / 2, sx * (IN_L / 2 + 2.0)))
    rib = box(x0, x1, -IN_W / 2 + 0.6, IN_W / 2 - 0.6, IPAD_Z0, GLASS_Z)
    for yc in (SPK_Y, -SPK_Y):
        rib = rib.cut(box(x0 - 1, x1 + 1, yc - SPK_LEN / 2, yc + SPK_LEN / 2, IPAD_Z0 - 1, GLASS_Z + 1))
    gap = PLUG_W / 2 + 1 if sx > 0 else 11.0
    rib = rib.cut(box(x0 - 1, x1 + 1, -gap, gap, IPAD_Z0 - 1, GLASS_Z + 1))
    deck = deck.union(rib)
for (x, y) in MAG_PTS:
    deck = deck.union(zcyl(x, y, 7.0, IPAD_Z0, Z_F))
    deck = deck.cut(zcyl(x, y, MAG_D / 2 + 0.1, Z_F - MAG_H - 0.1, Z_F + 1))
for (x, y) in PIN_PTS:
    deck = deck.union(zcyl(x, y, 4.0, IPAD_Z0, Z_F))
    deck = deck.cut(zcyl(x, y, 1.6, Z_F - 4, Z_F + 1))
for (x, y) in CLAMP_PTS:                            # dog-ear screw posts
    deck = deck.union(zcyl(x, y, 5.5, IPAD_Z0, Z_F))
    deck = deck.cut(zcyl(x, y, 2.25, DECK_Z0 - 1, Z_F + 1))
    deck = deck.cut(zcyl(x, y, 4.3, Z_F - 3.0, Z_F + 1))

# =============================== BACK PLATE ===============================
back = rrect(BOX_X, BOX_Y, BOX_R, -SLEEVE_D - BACK_T, -SLEEVE_D)
back = back.cut(zcyl(-70, 0, 11.0, -SLEEVE_D - BACK_T - 1, -SLEEVE_D + 1))   # Cat6
for dx in (-30, 30):
    for dy in (-38, 38):
        back = back.cut(box(-60 + dx - 1.5, -60 + dx + 1.5, dy - 4, dy + 4, -SLEEVE_D - BACK_T - 1, -SLEEVE_D + 1))
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
bend = box(IPAD_L / 2 + PLUG_L, IPAD_L / 2 + PLUG_L + BEND_R + CABLE_D / 2, -CABLE_D / 2, CABLE_D / 2,
           -SLEEVE_D + 5, EDGE_Z + CABLE_D / 2)
plaster = (box(-STUD_CC, STUD_CC, -300, 300, -PLASTER, 0)
           .cut(rrect(HOLE_X, HOLE_Y, BOX_R + HOLE_CLR, -PLASTER - 1, 1)))
studs = (box(-STUD_CC / 2 - STUD_W / 2, -STUD_CC / 2 + STUD_W / 2, -300, 300, -PLASTER - STUD_D, -PLASTER)
         .union(box(STUD_CC / 2 - STUD_W / 2, STUD_CC / 2 + STUD_W / 2, -300, 300, -PLASTER - STUD_D, -PLASTER)))


def half(p, side):
    return p.intersect(box(min(0, side * 999), max(0, side * 999), -999, 999, -999, 999))


def flip(p):
    return p.rotate((0, 0, 0), (1, 0, 0), 180)


def union_all(parts):
    u = parts[0]
    for p in parts[1:]:
        u = u.union(p)
    return u


if __name__ == "__main__":
    import sys
    from overhang_audit import audit
    out = sys.argv[1] if len(sys.argv) > 1 else "out_flush51"
    for d in ("machine", "print"):
        os.makedirs(f"{out}/{d}", exist_ok=True)

    def exp(path, part, step=True):
        cq.exporters.export(part, path + ".stl", tolerance=0.02, angularTolerance=0.1)
        if step:
            cq.exporters.export(part, path + ".step")

    PRINT = {   # name: (part in its print orientation)
        "sleeve_L": flip(half(sleeve, -1)), "sleeve_R": flip(half(sleeve, 1)),
        "deck_L": half(deck, -1), "deck_R": half(deck, 1),
        "back_plate_L": back_L, "back_plate_R": back_R,
        "dog_ear_arm_x4": arm,
    }
    exp(f"{out}/machine/trim_6061", trim)
    for nm, p in PRINT.items():
        exp(f"{out}/print/{nm}", p)

    arms_u = union_all(arms)
    for nm, p in (("trim", trim), ("sleeve", sleeve), ("deck", deck), ("back", back), ("ipad", ipad),
                  ("plug", plug), ("plaster", plaster), ("studs", studs), ("arms", arms_u)):
        cq.exporters.export(p, f"{out}/_{nm}.stl", tolerance=0.05)
    assy = cq.Assembly(name="iPadPro129_Flush_v5_1")
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
    assy.export(f"{out}/assembly_flush_v5_1.step")

    def vol(a, b):
        try:
            return round(a.intersect(b).val().Volume(), 2)
        except Exception:
            return 0.0

    print(f"Trim {TRIM_X:.1f} x {TRIM_Y:.1f} | cut-out {HOLE_X:.1f} x {HOLE_Y:.1f} | depth {SLEEVE_D + BACK_T:.1f} mm")
    checks = [("deck/sleeve", deck, sleeve), ("deck/ipad", deck, ipad), ("sleeve/ipad", sleeve, ipad),
              ("trim/ipad", trim, ipad), ("trim/deck", trim, deck), ("trim/sleeve", trim, sleeve),
              ("plug/deck", plug, deck), ("plug/sleeve", plug, sleeve), ("plug/trim", plug, trim),
              ("bend/deck", bend, deck), ("bend/sleeve", bend, sleeve), ("bend/back", bend, back),
              ("back/sleeve", back, sleeve), ("sleeve-in-wall/plaster", sleeve.intersect(box(-999, 999, -999, 999, -PLASTER, -0.01)), plaster),
              ("sleeve/studs", sleeve, studs), ("back/studs", back, studs),
              ("arms/sleeve", arms_u, sleeve), ("arms/deck", arms_u, deck), ("arms/plaster", arms_u, plaster),
              ("arms/studs", arms_u, studs), ("arms retracted/sleeve", union_all(arms_in), sleeve),
              ("arms retracted/deck", union_all(arms_in), deck)]
    for nm, a, b in checks:
        print(f"clash {nm:24s} {vol(a, b)}")
    # deck must actually SIT on the ledges: push it 0.05 mm into the wall and it must touch
    print("deck seats on ledges (contact when pushed 0.05 mm):", vol(deck.translate((0, 0, -0.05)), sleeve) > 0)
    # retracted arms inside the cut-out?
    out_of_hole = union_all(arms_in).cut(rrect(HOLE_X, HOLE_Y, BOX_R + HOLE_CLR, -999, 999))
    try:
        oh = out_of_hole.val().Volume()
    except Exception:
        oh = 0.0
    print("retracted arms outside the cut-out mm3:", round(oh, 2))
    print("--- print-orientation overhang audit ---")
    for nm, p in PRINT.items():
        bb = p.val().BoundingBox()
        fit = "OK " if max(bb.xlen, bb.ylen) <= 256 and bb.zlen <= 256 else "BIG"
        print(f"[{fit} {bb.xlen:5.1f} x {bb.ylen:5.1f} x {bb.zlen:4.1f}] ", end="")
        audit(nm, p)
    print(f"trim {trim.val().Volume()*2.7e-3:.0f} g")

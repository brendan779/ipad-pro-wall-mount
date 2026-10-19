"""
iPad Pro 12.9" (3rd gen) "Float" PoE wall mount -- HYBRID v3
  * Aluminium SHELL  : the only visible part. Front frame + side skirt, machined
                       from 12 mm 6061 plate. No visible screws: the printed
                       carrier screws into blind M3 bosses from behind.
  * Printed CARRIER  : everything hidden. Holds the iPad, hides a STANDARD
                       straight USB-C plug + its bend, routes speaker/mic sound
                       to the shadow gap, carries the hook + lock. Printed in
                       4 quarters (Bambu P1S 256 mm bed); the alu shell is the
                       jig that aligns them.
  * Printed HANGER, LOCK_BOSS, WALL_BRACKET : as v2.

Frame: the two short ends (left/right in landscape) are sized for the USB-C plug +
cable bend and match each other; top/bottom are slim (FRAME_Y).

Coordinates (assembled): +X long edge, +Y up the wall, +Z out of the wall.
Landscape: Face ID camera LEFT (-X), USB-C RIGHT (+X).
Carrier-local Z: 0 = carrier back face. Assembly lifts it by STANDOFF.

>>> iPad feature positions and plug sizes are approximations: measure them.
"""
import os
import cadquery as cq

# ---------------- iPad Pro 12.9 (3rd gen) ---------------------------------
IPAD_L, IPAD_W, IPAD_T = 280.6, 214.9, 5.9
IPAD_R = 10.3
CLR = 0.35                       # printed carrier fit, per side

CAM_FRONT_W = 32.0               # Face ID array width (along Y)
SPK_LEN, SPK_FROM_CORNER = 36, 20
REAR_CAM = (-IPAD_L / 2 + 16, IPAD_W / 2 - 16)
REAR_CAM_R = 11.0

# ---------------- USB-C cable (MEASURE YOURS) -----------------------------
PLUG_L = 17.0    # overmold length from the iPad edge (port face) outward
PLUG_W = 12.5    # overmold width  (along Y)
PLUG_H = 7.0     # overmold height (along Z, may exceed iPad thickness)
CABLE_D = 4.5    # cable diameter
BEND_R = 8.0     # bend radius as it turns back toward the wall

# ---------------- Mount -------------------------------------------------
CB = 3.0         # carrier back thickness
GLASS_GAP = 0.3  # glass to shell lip (fill with 0.3 mm PORON / felt tape)
FT = 2.5         # alu front plate thickness
SKIRT = 2.0      # alu side skirt thickness
SG = 0.3         # side gap shell <-> carrier
LIP = 2.8        # how far the alu lip overlaps the glass
STANDOFF = 14.0  # wall -> carrier back (shadow gap, cable route)
VENT_INSET = 32  # carrier rim left around the rear vent behind the iPad
CARRIER_WALL = 1.2
GRILLE = "rear"  # "rear": sound exits into the shadow gap (no side machining)
                 # "skirt": visible slots machined in the alu skirt ends

CAVITY_X = PLUG_L + BEND_R + CABLE_D / 2 + 1.0         # beyond the iPad edge
FRAME_X = CAVITY_X + CARRIER_WALL + SG + SKIRT         # short ends (cable side + its twin)
FRAME_Y = 12.0   # top & bottom (landscape). Minimum ~11 with the long-edge
                 # bosses; set LONG_BOSSES = False to go down to ~8.
LONG_BOSSES = True
FRAME = FRAME_X
OUT_L, OUT_W = IPAD_L + 2 * FRAME_X, IPAD_W + 2 * FRAME_Y
OUT_R = 24.0
IN_L, IN_W = IPAD_L + 2 * CLR, IPAD_W + 2 * CLR
IN_R = IPAD_R + CLR
PLATE_Z0 = CB + IPAD_T + GLASS_GAP                     # underside of alu plate
SHELL_H = PLATE_Z0 + FT
EDGE_Z = CB + IPAD_T / 2
CAR_L, CAR_W = OUT_L - 2 * (SKIRT + SG), OUT_W - 2 * (SKIRT + SG)
CAR_R = OUT_R - SKIRT - SG

# Shell bosses (blind M3, carrier screws in from behind)
BOSS_R, BOSS_Z0 = 4.0, 5.0          # short-end bosses (room to spare)
BOSS_R_LONG = 3.0                   # slim top/bottom bosses, M2.5
LONG_BOSS_OFF = IPAD_W / 2 + CLR + 2.0 + BOSS_R_LONG + 0.3   # 2 mm carrier wall to the iPad
BOSS_PTS = [(sx * (IPAD_L / 2 + FRAME_X / 2 - 1.5), sy * yy)
            for sx in (-1, 1) for sy in (-1, 1) for yy in (25.0, 101.0)]
LONG_PTS = ([(x, sy * LONG_BOSS_OFF) for x in (-110, -40, 40, 110) for sy in (-1, 1)]
            if LONG_BOSSES else [])
ALL_BOSSES = [(x, y, BOSS_R) for x, y in BOSS_PTS] + [(x, y, BOSS_R_LONG) for x, y in LONG_PTS]
# screw sizes per boss: (tap drill r, clearance r, head counterbore r)
def screw(x, y):
    return (1.025, 1.4, 2.6) if (x, y) in LONG_PTS else (1.25, 1.7, 3.1)   # M2.5 / M3

# Bracket / hook / lock (same interface as v2)
BR_L, BR_W, BR_T = 200.0, 200.0, 3.0
AU_PLATE_CTRS = 84.0
CUTOUT = (46.0, 68.0)
HOOK_Y, HOOK_LEN, GAP = 80.0, 8.0, 3.6
LOCK_Y = -(OUT_W / 2) + 5.0


def rrect(l, w, r, h, z0=0.0, x=0.0, y=0.0):
    return (cq.Workplane("XY").rect(l, w).extrude(h).edges("|Z").fillet(r)
            .translate((x, y, z0)))


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def zcyl(x, y, r, z0, z1):
    return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((x, y, z0))


def ycyl(x, z, r, y0, y1):
    return cq.Workplane("XZ").circle(r).extrude(-(y1 - y0)).translate((x, y0, z))


def csk(x, y, z_face, r_hole, r_head, depth, up=True):
    """Countersink cone opening toward +Z at z_face (up=True) or -Z."""
    if up:
        return (cq.Workplane("XY").circle(r_hole).workplane(offset=depth)
                .circle(r_head).loft().translate((x, y, z_face - depth + 0.001)))
    return (cq.Workplane("XY").circle(r_head).workplane(offset=depth)
            .circle(r_hole).loft().translate((x, y, z_face - 0.001)))


# =========================== ALUMINIUM SHELL ================================
shell = rrect(OUT_L, OUT_W, OUT_R, SHELL_H)
shell = shell.cut(rrect(OUT_L - 2 * SKIRT, OUT_W - 2 * SKIRT, OUT_R - SKIRT, PLATE_Z0 + 1, z0=-1)
                  .translate((0, 0, 0)).intersect(box(-999, 999, -999, 999, -1, PLATE_Z0)))
shell = shell.cut(rrect(IPAD_L - 2 * LIP, IPAD_W - 2 * LIP, IPAD_R - LIP, SHELL_H + 2, z0=-1))
# Face ID notch: stadium shape so a 6 mm end mill can cut it
notch = (cq.Workplane("XY").slot2D(CAM_FRONT_W, 8.4, angle=90).extrude(SHELL_H + 2)
         .translate((-(IPAD_L / 2 - LIP), 0, -1)))
shell = shell.cut(notch)
# Front edges: soft outer radius, crisp small chamfer on the window
shell = shell.edges(cq.selectors.BoxSelector((-999, -999, SHELL_H - 0.01), (999, 999, SHELL_H + 0.01))).fillet(0.8)
# Blind bosses + M3 tap drill (2.5) into the plate, 1.2 mm skin left on the face
for (x, y, r) in ALL_BOSSES:
    shell = shell.union(zcyl(x, y, r, BOSS_Z0, PLATE_Z0 + 0.01))
    if (x, y) in LONG_PTS:     # tie slim bosses into the skirt (no tool gap)
        sy = 1 if y > 0 else -1
        y0, y1 = sorted((y, sy * (OUT_W / 2 - SKIRT / 2)))
        shell = shell.union(box(x - r, x + r, y0, y1, BOSS_Z0, PLATE_Z0 + 0.01))
    shell = shell.cut(zcyl(x, y, screw(x, y)[0], BOSS_Z0 - 1, SHELL_H - 1.2))
# Plug relief on the plate underside (only if the plug is taller than the iPad)
plug_top = EDGE_Z + PLUG_H / 2 + 0.3
if plug_top > PLATE_Z0:
    shell = shell.cut(box(IPAD_L / 2 - 1, IPAD_L / 2 + PLUG_L + 2, -(PLUG_W / 2 + 1), PLUG_W / 2 + 1,
                          PLATE_Z0 - 0.01, plug_top))
if GRILLE == "skirt":
    for sx in (-1, 1):
        for sy in (-1, 1):
            yc = sy * (IN_W / 2 - SPK_FROM_CORNER - SPK_LEN / 2)
            shell = shell.cut(cq.Workplane("YZ").slot2D(SPK_LEN - 2, 2.2).extrude(SKIRT + 2)
                              .translate((sx * OUT_L / 2 - (1 if sx > 0 else SKIRT + 1), yc, EDGE_Z)))

# =========================== PRINTED CARRIER ===============================
car = rrect(CAR_L, CAR_W, CAR_R, PLATE_Z0)
car = car.cut(rrect(IN_L, IN_W, IN_R, PLATE_Z0, z0=CB))                      # iPad pocket
car = car.cut(rrect(IN_L - 2 * VENT_INSET, IN_W - 2 * VENT_INSET, 14, CB + 2, z0=-1))  # vent
car = car.cut(zcyl(*REAR_CAM, REAR_CAM_R, -1, CB + 0.01))                    # rear camera

# Straight USB-C plug + bend cavity, open through the back into the shadow gap
car = car.cut(box(IN_L / 2 - 0.5, IPAD_L / 2 + CAVITY_X, -(PLUG_W / 2 + 1.0), PLUG_W / 2 + 1.0,
                  -1, PLATE_Z0 + 0.01))

# Sound chambers along both short ends (v4.1: OPEN-TOP so they print with no
# overhang; the alu plate is their ceiling). A 2 mm end rib still locates the
# iPad in X, with windows in front of the speakers / mics / plug.
END_RIB = 2.0
for sx in (-1, 1):
    cx0, cx1 = sorted((sx * (IN_L / 2 + END_RIB), sx * (IPAD_L / 2 + CAVITY_X)))
    car = car.cut(box(cx0, cx1, -(IN_W / 2 - 12), IN_W / 2 - 12, EDGE_Z - 1.3, PLATE_Z0 + 1))
    rx0, rx1 = sorted((sx * (IN_L / 2 - 0.5), sx * (IN_L / 2 + END_RIB + 0.1)))
    windows = [(sy * (IN_W / 2 - SPK_FROM_CORNER - SPK_LEN / 2), SPK_LEN / 2) for sy in (-1, 1)]
    if sx < 0:
        windows.append((0.0, 11.0))                     # mics
    for yc, hw in windows:
        car = car.cut(box(rx0, rx1, yc - hw, yc + hw, EDGE_Z - 1.3, PLATE_Z0 + 1))
    if GRILLE == "rear":
        vx0, vx1 = sorted((sx * (IPAD_L / 2 + 8), sx * (IPAD_L / 2 + CAVITY_X - 2)))
        for yc, hw in windows:
            car = car.cut(box(vx0, vx1, yc - hw, yc + hw, -1, EDGE_Z))

# Boss clearance from the top, M3 x 6 cap screws from the back
for (x, y, r) in ALL_BOSSES:
    car = car.cut(zcyl(x, y, r + 0.3, BOSS_Z0 - 0.2, PLATE_Z0 + 1))
    if (x, y) in LONG_PTS:     # slim edge: open the boss pocket out to the skirt
        sy = 1 if y > 0 else -1
        y0, y1 = sorted((y, sy * (CAR_W / 2 + 1)))
        car = car.cut(box(x - r - 0.3, x + r + 0.3, y0, y1, BOSS_Z0 - 0.2, PLATE_Z0 + 1))
    _, rc, rh = screw(x, y)
    car = car.cut(zcyl(x, y, rc, -1, BOSS_Z0))
    car = car.cut(zcyl(x, y, rh, -1, 3.0))        # head counterbore

# Bolt-on hanger + lock boss (they also splice the carrier quarters)
W0 = -STANDOFF
LOCK_Z = W0 + BR_T + 5.0
PAD_T = 3.0
HANG_BOLTS = [(x, HOOK_Y + HOOK_LEN + 8.0) for x in (-45, -20, 20, 45)]
LOCK_BOLTS = [(x, LOCK_Y + 22.0) for x in (-22, 22)]

stem = box(-55, 55, HOOK_Y + HOOK_LEN + 0.8, HOOK_Y + HOOK_LEN + 4.8, W0 + BR_T + 0.4, -PAD_T)
foot = box(-55, 55, HOOK_Y + 0.6, HOOK_Y + HOOK_LEN + 4.8, W0 + BR_T + 0.4, W0 + BR_T + GAP - 0.4)
# v4.1: the pad is filled solid down to the foot's level, so the hanger prints
# foot-down with nothing hanging in the air
hanger = (box(-55, 55, HOOK_Y + HOOK_LEN + 0.8, HOOK_Y + HOOK_LEN + 14.0, W0 + BR_T + 0.4, 0)
          .union(stem).union(foot))
boss = box(-12, 12, LOCK_Y + 8.5, LOCK_Y + 17.5, W0 + BR_T + 1.0, -PAD_T)
lock_boss = (box(-30, 30, LOCK_Y + 8.5, LOCK_Y + 26.0, -PAD_T, 0).union(boss)
             .cut(ycyl(0, LOCK_Z, 2.1, LOCK_Y + 8, LOCK_Y + 16)))      # M3 heat-set 4.2


def nut_trap(x, y):
    return cq.Workplane("XY").polygon(6, 6.7).extrude(2.6).translate((x, y, -PAD_T - 0.01))


for (x, y) in HANG_BOLTS:
    hanger = hanger.cut(zcyl(x, y, 2.1, -6.0, 1))       # M3 heat-set insert from the top
    car = car.cut(zcyl(x, y, 1.7, -1, CB + 1)).cut(csk(x, y, CB, 1.7, 3.3, 1.6))     # flush under iPad
for (x, y) in LOCK_BOLTS:
    lock_boss = lock_boss.cut(zcyl(x, y, 1.7, -PAD_T - 1, 1)).cut(nut_trap(x, y))
    if abs(y) < IN_W / 2:      # behind the iPad: flush under the iPad back
        car = car.cut(zcyl(x, y, 1.7, -1, CB + 1)).cut(csk(x, y, CB, 1.7, 3.3, 1.6))
    else:                      # in the frame: flush under the alu plate
        car = car.cut(zcyl(x, y, 1.7, -1, PLATE_Z0 + 1)).cut(csk(x, y, PLATE_Z0, 1.7, 3.3, 1.6))

# =========================== WALL BRACKET =================================
br = rrect(BR_L, BR_W, 14, BR_T)
br = br.cut(rrect(*CUTOUT, 6, BR_T + 2, z0=-1))
for sy in (1, -1):
    br = br.cut(zcyl(0, sy * AU_PLATE_CTRS / 2, 2.0, -1, BR_T + 1))
for sx in (-1, 1):
    for sy in (-1, 1):
        br = br.cut(cq.Workplane("XY").slot2D(16, 5.2).extrude(BR_T + 2)
                    .translate((sx * (BR_L / 2 - 18), sy * (BR_W / 2 - 18), -1)))
# v4.1: catch rail is a separate part, printed flange-down (no overhang), bolted
# to the plate with M3 countersunk screws from the wall side into heat-set inserts
RAIL_SP = 8.0
catch_rail = (box(-60, 60, HOOK_Y - RAIL_SP, HOOK_Y, BR_T, BR_T + GAP)
              .union(box(-60, 60, HOOK_Y - RAIL_SP, HOOK_Y + HOOK_LEN, BR_T + GAP, BR_T + GAP + 3.0)))
RAIL_BOLTS = [(x, HOOK_Y - RAIL_SP / 2) for x in (-48, -16, 16, 48)]
for (x, y) in RAIL_BOLTS:
    catch_rail = catch_rail.cut(zcyl(x, y, 2.1, BR_T - 0.1, BR_T + 5.5))
    br = br.cut(zcyl(x, y, 1.7, -1, BR_T + 1)).cut(csk(x, y, 0, 1.7, 3.3, 1.6, up=False))
br = br.union(box(-20, 20, LOCK_Y, -BR_W / 2 + 6, 0, BR_T))
br = br.union(box(-12, 12, LOCK_Y, LOCK_Y + 8.0, BR_T, BR_T + 9.0))
br = br.cut(ycyl(0, LOCK_Z + STANDOFF, 1.7, LOCK_Y - 1, LOCK_Y + 9))
br = br.cut(ycyl(0, LOCK_Z + STANDOFF, 3.0, LOCK_Y - 1, LOCK_Y + 3.0))

# =========================== ASSEMBLY / CHECKS ============================
def up(p, dz=STANDOFF):
    return p.translate((0, 0, dz))


shell_a, car_a, hanger_a, lock_a = up(shell), up(car), up(hanger), up(lock_boss)
br_plate = br
br = br_plate.union(catch_rail)          # assembled bracket for checks / renders
rear_a = car_a.union(hanger_a).union(lock_a)
ipad = rrect(IPAD_L, IPAD_W, IPAD_R, IPAD_T, z0=STANDOFF + CB)
plug = up(box(IPAD_L / 2, IPAD_L / 2 + PLUG_L, -PLUG_W / 2, PLUG_W / 2,
              EDGE_Z - PLUG_H / 2, EDGE_Z + PLUG_H / 2))
# cable bend envelope: from plug end, down through the carrier into the gap
bend = up(box(IPAD_L / 2 + PLUG_L, IPAD_L / 2 + PLUG_L + BEND_R + CABLE_D / 2,
              -CABLE_D / 2, CABLE_D / 2, -STANDOFF + BR_T + 2, EDGE_Z + CABLE_D / 2))

BIG = 2000


def quad(p, sx, sy):
    return p.intersect(box(min(0, sx * BIG), max(0, sx * BIG), min(0, sy * BIG), max(0, sy * BIG), -BIG, BIG))


def flip(p):
    return p.rotate((0, 0, 0), (1, 0, 0), 180)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "out_hybrid"
    os.makedirs(f"{out}/print", exist_ok=True)
    os.makedirs(f"{out}/machine", exist_ok=True)
    os.makedirs(f"{out}/print/optional_shell_prototype", exist_ok=True)

    def exp(path, part, step=True):
        cq.exporters.export(part, path + ".stl", tolerance=0.02, angularTolerance=0.1)
        if step:
            cq.exporters.export(part, path + ".step")

    exp(f"{out}/machine/shell_6061", shell)
    names = {(-1, 1): "TL", (1, 1): "TR", (-1, -1): "BL", (1, -1): "BR"}
    for (sx, sy), nm in names.items():
        exp(f"{out}/print/carrier_{nm}", quad(car, sx, sy))
        exp(f"{out}/print/optional_shell_prototype/shell_print_{nm}", flip(quad(shell, sx, sy)), step=False)
    exp(f"{out}/print/hanger", hanger)
    exp(f"{out}/print/lock_boss", flip(lock_boss))
    exp(f"{out}/print/wall_bracket", br_plate)
    exp(f"{out}/print/catch_rail", flip(catch_rail))   # flange-down
    cq.exporters.export(car, f"{out}/carrier_full_reference.step")

    for nm, p in (("rear", rear_a), ("shell", shell_a), ("ipad", ipad), ("bracket", br), ("plug", plug)):
        cq.exporters.export(p, f"{out}/_{nm}.stl", tolerance=0.05)

    assy = cq.Assembly(name="iPadPro129_Float_Hybrid_v4_1")
    assy.add(br, name="wall_bracket", color=cq.Color(0.62, 0.63, 0.66))
    assy.add(car_a, name="carrier", color=cq.Color(0.15, 0.15, 0.17))
    assy.add(hanger_a, name="hanger", color=cq.Color(0.85, 0.45, 0.15))
    assy.add(lock_a, name="lock_boss", color=cq.Color(0.85, 0.45, 0.15))
    assy.add(ipad, name="ipad_reference", color=cq.Color(0.03, 0.03, 0.05))
    assy.add(plug, name="usb_c_plug_reference", color=cq.Color(0.9, 0.9, 0.9))
    assy.add(shell_a, name="shell_6061", color=cq.Color(0.72, 0.73, 0.76))
    assy.export(f"{out}/assembly_hybrid_v4_1.step")

    def vol(a, b):
        try:
            return round(a.intersect(b).val().Volume(), 2)
        except Exception:
            return 0.0

    print(f"Frame ends {FRAME_X:.1f} mm, top/bottom {FRAME_Y:.1f} mm | overall {OUT_L:.1f} x {OUT_W:.1f} mm | "
          f"{STANDOFF + SHELL_H:.1f} mm off wall | shell height {SHELL_H:.1f}")
    print("clash rear/bracket      ", vol(rear_a, br))
    print("clash rear/bracket +10mm", vol(rear_a.translate((0, 10, 0)), br))
    print("clash shell/bracket +10 ", vol(shell_a.translate((0, 10, 0)), br))
    print("clash carrier/ipad      ", vol(car_a, ipad))
    print("clash shell/ipad        ", vol(shell_a, ipad))
    print("clash shell/carrier     ", vol(shell_a, car_a))
    print("clash shell/hanger,lock ", vol(shell_a, hanger_a.union(lock_a)))
    print("clash plug/carrier      ", vol(plug, car_a), " plug/shell", vol(plug, shell_a))
    print("clash bend/carrier      ", vol(bend, car_a), " bend/shell", vol(bend, shell_a))
    for nm, p in (("carrier quarter", quad(car, 1, 1)), ("bracket", br),
                  ("shell print quarter", quad(shell, 1, 1)), ("hanger", hanger)):
        bb = p.val().BoundingBox()
        print(f"bed fit {nm:20s} {bb.xlen:6.1f} x {bb.ylen:6.1f}  {'OK' if max(bb.xlen, bb.ylen) <= 256 else 'TOO BIG'}")
    sv = shell.val().Volume()
    print(f"shell volume {sv/1000:.0f} cm3 -> {sv*2.70e-3:.0f} g in 6061")

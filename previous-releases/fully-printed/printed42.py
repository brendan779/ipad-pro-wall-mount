"""
Fully printed Float Mount v4.2 face (shell), one-piece and split.

The only machined part in each design is the visible face (v4.1 shell, v5.1 trim).
Here that face is rebuilt for FDM:

* split into two halves at the centreline so each half fits a 256 x 256 bed
  (neither face fits whole on an H2S/H2D either: 344.1 / 355.1 mm long),
* a dovetail key across each slim top/bottom bar aligns and locks the halves,
* printed face-down, so the visible side is the textured build plate,
* v4.1 only: the tapped holes become self-tapping pilot holes (Ø2.5 for M3,
  Ø2.1 for M2.5) and the skin over them grows from 1.2 to 1.6 mm so screw
  tips can't print through to the face.

Everything else in both designs was already printed and is reused unchanged.
Run:  python printed.py [out_dir]
"""
import os
import sys
import cadquery as cq

sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "float-v4.2")]
import hybrid42 as h  # noqa: E402

DOVE_CLR = 0.15      # per flank, socket vs key
DOVE_DEPTH = 5.0     # how far the key reaches across the seam


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def dovetail(yc, neck, head, depth, z0, z1, grow=0.0):
    """Key from the left half (x<0) reaching into the right half, centred on y=yc."""
    n, hd, d = neck / 2 + grow, head / 2 + grow, depth + grow
    pts = [(-1.0, yc - n), (0.0, yc - n), (d, yc - hd), (d, yc + hd), (0.0, yc + n), (-1.0, yc + n)]
    return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))


def split_with_keys(part, keys, zmin, zmax):
    """Return (left, right). keys = [(yc, neck, head)] dovetails across x = 0."""
    big = 2000
    left_zone = box(-big, 0, -big, big, -big, big)
    left_cut = left_zone
    for yc, neck, head in keys:
        left_zone = left_zone.union(dovetail(yc, neck, head, DOVE_DEPTH, zmin, zmax))
        left_cut = left_cut.union(dovetail(yc, neck, head, DOVE_DEPTH, zmin, zmax, grow=DOVE_CLR))
    return part.intersect(left_zone), part.cut(left_cut)


# =========================== v4.1 printed shell ==============================
PILOT = {"M3": 1.25, "M2.5": 1.05}   # radii: Ø2.5 / Ø2.1 self-tapping pilots in PETG
SKIN = 1.6

shell = h.rrect(h.OUT_L, h.OUT_W, h.OUT_R, h.SHELL_H)
shell = shell.cut(h.rrect(h.OUT_L - 2 * h.SKIRT, h.OUT_W - 2 * h.SKIRT, h.OUT_R - h.SKIRT, h.PLATE_Z0 + 1, z0=-1)
                  .intersect(h.box(-999, 999, -999, 999, -1, h.PLATE_Z0)))
shell = shell.cut(h.rrect(h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP, h.SHELL_H + 2, z0=-1))
shell = shell.cut(cq.Workplane("XY").slot2D(h.CAM_FRONT_W, 8.4, angle=90).extrude(h.SHELL_H + 2)
                  .translate((-(h.IPAD_L / 2 - h.LIP), 0, -1)))
# printed face-down: a 45° chamfer prints crisply where the alu part has a 0.8 mm round
shell = shell.edges(cq.selectors.BoxSelector((-999, -999, h.SHELL_H - 0.01), (999, 999, h.SHELL_H + 0.01))).chamfer(0.8)
for (x, y, r) in h.ALL_BOSSES:
    shell = shell.union(h.zcyl(x, y, r, h.BOSS_Z0, h.PLATE_Z0 + 0.01))
    long_ = (x, y) in h.LONG_PTS
    if long_:
        sy = 1 if y > 0 else -1
        y0, y1 = sorted((y, sy * (h.OUT_W / 2 - h.SKIRT / 2)))
        shell = shell.union(h.box(x - r, x + r, y0, y1, h.BOSS_Z0, h.PLATE_Z0 + 0.01))
    shell = shell.cut(h.zcyl(x, y, PILOT["M2.5" if long_ else "M3"], h.BOSS_Z0 - 1, h.SHELL_H - SKIN))
plug_top = h.EDGE_Z + h.PLUG_H / 2 + 0.3
if plug_top > h.PLATE_Z0:
    shell = shell.cut(h.box(h.IPAD_L / 2 - 1, h.IPAD_L / 2 + h.PLUG_L + 2, -(h.PLUG_W / 2 + 1), h.PLUG_W / 2 + 1,
                            h.PLATE_Z0 - 0.01, plug_top))

# key sits in the slim top/bottom bar, between the window edge and the skirt
bar_in, bar_out = h.IPAD_W / 2 - h.LIP, h.OUT_W / 2 - h.SKIRT
yc41 = (bar_in + bar_out) / 2
KEYS41 = [(sy * yc41, 5.0, 8.0) for sy in (1, -1)]
shell_L, shell_R = split_with_keys(shell, KEYS41, h.PLATE_Z0 - 0.01, h.SHELL_H + 1)



def face_down(p):
    """Flip so the visible face is on the bed, and drop to z = 0."""
    q = p.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = q.val().BoundingBox()
    return q.translate((0, 0, -bb.zmin))


PARTS = {"shell_print_full": face_down(shell), "shell_print_L": face_down(shell_L), "shell_print_R": face_down(shell_R)}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out_printed42"
    os.makedirs(f"{out}/print/one_piece", exist_ok=True)
    for nm, p in PARTS.items():
        path = f"{out}/print/one_piece/{nm}" if nm.endswith("full") else f"{out}/print/{nm}"
        cq.exporters.export(p, path + ".stl", tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(p, path + ".step")
        b = p.val().BoundingBox()
        print(f"{nm:17s} {b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.2f}  solids={len(p.solids().vals())}")
    print(f"pilot depth from boss tip {h.SHELL_H - SKIN - h.BOSS_Z0:.1f} mm; M3/M2.5 x {h.SCREW_LEN:.0f} engage {h.SCREW_LEN - (h.BOSS_Z0 - 3.0):.1f} mm")

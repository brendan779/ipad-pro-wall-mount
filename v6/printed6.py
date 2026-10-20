"""
Printed faces for v6: the Float shell and the Flush trim, for any tablet in tablets.py.
Each comes as two dovetailed halves (256 mm beds) and as one piece (big beds).

* printed face-down; the 0.8 mm front round becomes a 0.8 mm 45° chamfer
* Float shell: self-tapping pilot holes (Ø2.5 M3 / Ø2.1 M2.5), 1.6 mm skin over them
* the seam sits at X0, except where the front camera notch is in the top bar (M5):
  then it moves 3 mm past the notch, with the inner long bosses kept clear of its keys

Run:  V6_TABLET=ipad_pro_11_m5 python printed6.py out_dir
"""
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import float6 as h  # noqa: E402
import flush6 as f  # noqa: E402

DOVE_CLR, DOVE_DEPTH = 0.15, 5.0
PILOT = {"M3": 1.25, "M2.5": 1.05}
SKIN = 1.6
SPLIT_X = 0.0 if h.CAM_SIDE == "end" else h.CAM_LEN / 2 + 3.0   # just past the top camera notch


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
            .translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def dovetail(xs, yc, neck, head, depth, z0, z1, grow=0.0):
    n, hd, d = neck / 2 + grow, head / 2 + grow, depth + grow
    pts = [(xs - 1.0, yc - n), (xs, yc - n), (xs + d, yc - hd), (xs + d, yc + hd), (xs, yc + n), (xs - 1.0, yc + n)]
    return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))


def split_with_keys(part, xs, keys, zmin, zmax):
    big = 2000
    left_zone = box(-big, xs, -big, big, -big, big)
    left_cut = left_zone
    for yc, neck, head in keys:
        left_zone = left_zone.union(dovetail(xs, yc, neck, head, DOVE_DEPTH, zmin, zmax))
        left_cut = left_cut.union(dovetail(xs, yc, neck, head, DOVE_DEPTH, zmin, zmax, grow=DOVE_CLR))
    return part.intersect(left_zone), part.cut(left_cut)


def face_down(p):
    q = p.rotate((0, 0, 0), (1, 0, 0), 180)
    return q.translate((0, 0, -q.val().BoundingBox().zmin))


# ------------------------------------------------------------- Float shell
shell = h.rrect(h.OUT_L, h.OUT_W, h.OUT_R, h.SHELL_H)
shell = shell.cut(h.rrect(h.OUT_L - 2 * h.SKIRT, h.OUT_W - 2 * h.SKIRT, h.OUT_R - h.SKIRT, h.PLATE_Z0 + 1, z0=-1)
                  .intersect(h.box(-999, 999, -999, 999, -1, h.PLATE_Z0)))
shell = shell.cut(h.rrect(h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP, h.SHELL_H + 2, z0=-1))
shell = shell.cut(h.cam_slot(-1, h.SHELL_H + 1))
shell = shell.edges(cq.selectors.BoxSelector((-999, -999, h.SHELL_H - 0.01), (999, 999, h.SHELL_H + 0.01))).chamfer(0.8)
for (x, y, r) in h.ALL_BOSSES:
    shell = shell.union(h.zcyl(x, y, r, h.BOSS_Z0, h.PLATE_Z0 + 0.01))
    long_ = (x, y) in h.LONG_PTS
    if long_:
        sy = 1 if y > 0 else -1
        y0, y1 = sorted((y, sy * (h.OUT_W / 2 - h.SKIRT / 2)))
        shell = shell.union(h.box(x - r, x + r, y0, y1, h.BOSS_Z0, h.PLATE_Z0 + 0.01))
    shell = shell.cut(h.zcyl(x, y, PILOT["M2.5" if long_ else "M3"], h.BOSS_Z0 - 1, h.SHELL_H - SKIN))
if h.plug_top > h.PLATE_Z0:
    shell = shell.cut(h.box(h.IPAD_L / 2 - 1, h.IPAD_L / 2 + h.PLUG_L + 2, -(h.PLUG_W / 2 + 1), h.PLUG_W / 2 + 1,
                            h.PLATE_Z0 - 0.01, h.plug_top))
bar_in, bar_out = h.IPAD_W / 2 - h.LIP, h.OUT_W / 2 - h.SKIRT
KEYS_S = [(sy * (bar_in + bar_out) / 2, 5.0, 8.0) for sy in (1, -1)]
shell_L, shell_R = split_with_keys(shell, SPLIT_X, KEYS_S, h.PLATE_Z0 - 0.01, h.SHELL_H + 1)

# ------------------------------------------------------------- Flush trim
trim = f.trim_part(round_edges=False)
tb_in, tb_out = f.IPAD_W / 2 - f.LIP, f.TRIM_Y / 2
KEYS_T = [(sy * (tb_in + tb_out) / 2, 4.0, 6.5) for sy in (1, -1)]
trim_L, trim_R = split_with_keys(trim, SPLIT_X, KEYS_T, f.Z_F - 1, f.Z_F + f.TRIM_T + 1)

PARTS = {"float": {"shell_print_L": face_down(shell_L), "shell_print_R": face_down(shell_R), "shell_print_full": face_down(shell)},
         "flush": {"trim_print_L": face_down(trim_L), "trim_print_R": face_down(trim_R), "trim_print_full": face_down(trim)}}

if __name__ == "__main__":
    from overhang_audit import audit
    out = sys.argv[1] if len(sys.argv) > 1 else f"out_printed6_{h.TAB_KEY}"
    rep = [f"{h.TAB['name']}: seam at X{SPLIT_X:+.1f}"]
    for style, parts in PARTS.items():
        os.makedirs(f"{out}/{style}/print/one_piece", exist_ok=True)
        for nm, p in parts.items():
            path = f"{out}/{style}/print/one_piece/{nm}" if nm.endswith("full") else f"{out}/{style}/print/{nm}"
            cq.exporters.export(p, path + ".stl", tolerance=0.02, angularTolerance=0.1)
            cq.exporters.export(p, path + ".step")
            b = p.val().BoundingBox()
            n = len(p.solids().vals())
            fit = "fits 256" if max(b.xlen, b.ylen) <= 256 else "needs a big bed"
            rep.append(f"{nm:17s} {b.xlen:6.1f} x {b.ylen:6.1f} x {b.zlen:5.2f}  solids={n}  {fit}  overhang {audit(nm, p):.1f} mm2")
    for nm, a, b in (("shell halves", shell_L, shell_R), ("trim halves", trim_L, trim_R)):
        try:
            v = a.intersect(b).val().Volume()
        except Exception:
            v = 0.0
        rep.append(f"overlap {nm}: {v:.3f}")
    open(f"{out}/printed_checks.txt", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))

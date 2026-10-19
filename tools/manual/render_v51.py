import sys, os
sys.path[:0] = ["../../float-v4.1", "../../flush-v5.1"]
import cadquery as cq
import mr
from mr import render
import flush51 as f

OUT = "v51"
os.makedirs(OUT, exist_ok=True)
box, zcyl, rrect = f.box, f.zcyl, f.rrect


def U(parts):
    u = parts[0]
    for p in parts[1:]:
        u = u.union(p)
    return u


def cap(x, y, z_head, head_d, head_t, d, length, up=True):
    if up:
        return zcyl(x, y, head_d / 2, z_head, z_head + head_t).union(zcyl(x, y, d / 2, z_head + head_t, z_head + head_t + length))
    return zcyl(x, y, head_d / 2, z_head - head_t, z_head).union(zcyl(x, y, d / 2, z_head - head_t - length, z_head - head_t))


plaster = box(-300, 300, -200, 200, -f.PLASTER, 0).cut(rrect(f.HOLE_X, f.HOLE_Y, f.BOX_R + f.HOLE_CLR, -f.PLASTER - 1, 1))
plaster_full = box(-300, 300, -200, 200, -f.PLASTER, 0)
studs = (box(-f.STUD_CC / 2 - f.STUD_W / 2, -f.STUD_CC / 2 + f.STUD_W / 2, -200, 200, -f.PLASTER - f.STUD_D, -f.PLASTER)
         .union(box(f.STUD_CC / 2 - f.STUD_W / 2, f.STUD_CC / 2 + f.STUD_W / 2, -200, 200, -f.PLASTER - f.STUD_D, -f.PLASTER)))
arms = U(f.arms)
arms_in = U(f.arms_in)
unit = f.sleeve.union(f.deck).union(f.back)
poe = box(-60 - 26, -60 + 26, -32, 32, -f.SLEEVE_D, -f.SLEEVE_D + 24)
cat6 = zcyl(-70, 0, 3.0, -f.SLEEVE_D - 40, -f.SLEEVE_D + 4)
clamp_scr = [cap(x, y, f.Z_F - 3.0, 7.5, 2.8, 4.0, 26.0, up=False) for (x, y) in f.CLAMP_PTS]
tape = (rrect(f.IPAD_L, f.IPAD_W, f.IPAD_R, f.Z_F - 0.3, f.Z_F)
        .cut(rrect(f.IPAD_L - 2 * f.LIP, f.IPAD_W - 2 * f.LIP, f.IPAD_R - f.LIP, f.Z_F - 1, f.Z_F + 1)))
GREY = (0.80, 0.80, 0.78)
jobs = []

# ---------------------------------------------------------------- overview
jobs.append(("hero", [(plaster_full.cut(rrect(f.HOLE_X, f.HOLE_Y, 7, -11, 1)), "wall", 1), (unit, "print", 1),
                      (f.ipad, "ipad", 1), (f.trim, "alu", 1)], dict(cam=(420, -300, 900), zoom=1.15)))
jobs.append(("exploded", [(studs, "stud", 1), (plaster, "wall", 0.35), (f.back.translate((0, 0, -50)), "print2", 1),
                          (f.sleeve, "print", 1), (arms, "active", 1), (f.deck.translate((0, 0, 60)), "print2", 1),
                          (f.ipad.translate((0, 0, 110)), "ipad", 1), (f.plug.translate((0, 0, 110)), "plug", 1),
                          (f.trim.translate((0, 0, 165)), "alu", 1)], dict(cam=(700, -560, 480), zoom=1.15)))
jobs.append(("behind_wall", [(plaster, "wall", 1), (studs, "stud", 1), (unit, "print", 1), (arms, "active", 1),
                             (cat6, "hw", 1)], dict(cam=(-320, -300, -700), zoom=1.3)))

# ---------------------------------------------------------------- print orientation
def plate_grid(parts, gap=24.0, cols=2):
    items = []
    for i, p in enumerate(parts):
        pp, _ = mr.on_plate(p)
        ox, oy = (i % cols) * (256 + gap), -(i // cols) * (256 + gap)
        items += [(pp.translate((ox, oy, 0)), "active", 1), (mr.plate(ox - 128, ox + 128, oy - 128, oy + 128), GREY, 1)]
    return items


jobs.append(("po_sleeve", plate_grid([f.flip(f.half(f.sleeve, -1)), f.flip(f.half(f.sleeve, 1))]),
             dict(cam=(300, -520, 420), zoom=1.2)))
jobs.append(("po_deck", plate_grid([f.half(f.deck, -1), f.half(f.deck, 1)]), dict(cam=(300, -520, 420), zoom=1.2)))
jobs.append(("po_back", plate_grid([f.back_L, f.back_R]), dict(cam=(300, -520, 420), zoom=1.2)))
arm_items = [(f.arm.translate((x, y, 0)), "active", 1) for x in (-40, 20) for y in (-30, 30)] + [(mr.plate(-128, 128, -128, 128), GREY, 1)]
jobs.append(("po_arms", arm_items, dict(cam=(120, -200, 220), zoom=1.6, focal=(-10, 0, 0))))

# ---------------------------------------------------------------- machining the trim
tb = f.trim.translate((0, 0, -f.Z_F))
stock = box(-f.TRIM_X / 2 - 8, f.TRIM_X / 2 + 8, -f.TRIM_Y / 2 - 8, f.TRIM_Y / 2 + 8, -12, 0)
jobs.append(("mach_op1", [(stock, (0.86, 0.86, 0.84), 1), (f.flip(tb).translate((0, 0, f.TRIM_T)), "alu", 1)],
             dict(cam=(300, -380, 520), zoom=1.25)))
jobs.append(("mach_op2", [(stock, (0.86, 0.86, 0.84), 1), (tb, "alu", 1)], dict(cam=(300, -380, 520), zoom=1.25)))

# ---------------------------------------------------------------- bench assembly
ins = [(f.arm.translate((x, 0, 0)), "print", 1) for x in (-54, -18, 18, 54)]
ins += [(zcyl(x, 0, 2.8, -0.5, f.ARM_T + 0.8), "hw", 1) for x in (-54, -18, 18, 54)]
jobs.append(("a1_arm_inserts", ins, dict(cam=(40, -170, 170), zoom=1.15)))
sl_back_up = f.sleeve        # back edge faces -Z; view from behind
bos = [(zcyl(x, y, 2.1, -f.SLEEVE_D - 0.8, -f.SLEEVE_D + 6), "hw", 1) for (x, y) in f.BACK_BOSSES]
jobs.append(("a1_sleeve_inserts", [(f.sleeve, "print", 1)] + bos, dict(cam=(-300, -360, -520), zoom=1.3)))
sl_face = f.flip(f.sleeve)
jobs.append(("a2_glue_sleeve", [(f.flip(f.half(f.sleeve, -1)).translate((-18, 0, 0)), "print", 1),
                                (f.flip(f.half(f.sleeve, 1)).translate((18, 0, 0)), "print2", 1),
                                (box(-0.4, 0.4, -f.BOX_Y / 2 - 6, f.BOX_Y / 2 + 6, f.Z_F - 0.1, f.Z_F + f.SLEEVE_D), "active", 1)],
             dict(cam=(320, -420, 520), zoom=1.25)))
jobs.append(("a3_glue_deck", [(f.half(f.deck, -1).translate((-18, 0, 0)), "print", 1),
                              (f.half(f.deck, 1).translate((18, 0, 0)), "print2", 1),
                              (box(-0.4, 0.4, -f.BOX_Y / 2, f.BOX_Y / 2, f.DECK_Z0, f.IPAD_Z0 + 0.1), "active", 1)],
             dict(cam=(320, -420, 520), zoom=1.25)))
mags_deck = [(zcyl(x, y, f.MAG_D / 2, f.Z_F - f.MAG_H + 10, f.Z_F + 10), "hw", 1) for (x, y) in f.MAG_PTS]
jobs.append(("a4_magnets_deck", [(f.deck, "print", 1)] + mags_deck, dict(cam=(300, -380, 520), zoom=1.25)))
tb_up = f.flip(f.trim)       # back face up
mags_trim = [(zcyl(x, -y, f.MAG_D / 2, -f.Z_F + 10, -f.Z_F + f.MAG_H + 10), "hw", 1) for (x, y) in f.MAG_PTS]
pins = [(zcyl(x, -y, 1.5, -f.Z_F - 2 + 14, -f.Z_F + 4 + 14), "active", 1) for (x, y) in f.PIN_PTS]
jobs.append(("a4_magnets_trim", [(tb_up, "alu", 1)] + mags_trim + pins, dict(cam=(300, -380, 520), zoom=1.25)))
back_items = [(f.back_L, "print", 1), (f.back_R, "print2", 1), (poe, "active", 1), (cat6, "hw", 1)]
jobs.append(("a5_poe", back_items, dict(cam=(260, -360, 420), zoom=1.3)))
bscr = [cap(x, y, -f.SLEEVE_D - f.BACK_T - 14, 6.6, 1.6, 3.0, 8.0, up=True) for (x, y) in f.BACK_BOSSES]
jobs.append(("a6_back_plate", [(f.sleeve, "print", 1), (f.back.translate((0, 0, -30)), "active", 1), (poe.translate((0, 0, -30)), "print2", 1)] +
             [(s.translate((0, 0, -30)), "hw", 1) for s in bscr], dict(cam=(-300, -360, -520), zoom=1.25)))
jobs.append(("a7_deck", [(f.sleeve, "print", 1), (f.back, "print2", 1), (f.deck.translate((0, 0, 45)), "active", 1),
                         (arms_in, "hw", 1)] + [(s.translate((0, 0, 45)), "hw", 1) for s in clamp_scr],
             dict(cam=(560, -460, 520), zoom=1.2)))

# ---------------------------------------------------------------- wall
corner_drills = [(zcyl(sx * (f.HOLE_X / 2 - 7), sy * (f.HOLE_Y / 2 - 7), 7, -11, 1), "active", 1) for sx in (-1, 1) for sy in (-1, 1)]
jobs.append(("w2_cut", [(plaster, "wall", 1), (studs, "stud", 1)] + corner_drills +
             [(zcyl(-70, 0, 3.0, -40, 40).rotate((-70, 0, 0), (-70, 1, 0), 0), "hw", 1)],
             dict(cam=(300, -330, 560), zoom=1.3)))
jobs.append(("w4_insert", [(plaster, "wall", 1), (studs, "stud", 1), (unit.translate((0, 0, 70)), "active", 1),
                           (arms_in.translate((0, 0, 70)), "hw", 1)], dict(cam=(560, -460, 520), zoom=1.15)))
order_lbl = []
jobs.append(("w5_clamp", [(plaster, "wall", 0.45), (studs, "stud", 1), (unit, "print", 1), (arms, "active", 1)] +
             [(s, "hw", 1) for s in clamp_scr], dict(cam=(-330, -260, -560), zoom=1.3)))
jobs.append(("w6_ipad", [(plaster, "wall", 1), (unit, "print", 1), (f.ipad.translate((0, 0, 50)), "active", 1),
                         (f.plug.translate((0, 0, 50)), "plug", 1)], dict(cam=(560, -420, 560), zoom=1.15)))
jobs.append(("w7_trim", [(plaster, "wall", 1), (unit, "print", 1), (f.ipad, "ipad", 1), (f.trim.translate((0, 0, 50)), "active", 1),
                         (tape.translate((0, 0, 50)), "tape", 1)], dict(cam=(560, -420, 560), zoom=1.15)))
jobs.append(("final", [(plaster_full.cut(rrect(f.HOLE_X, f.HOLE_Y, 7, -11, 1)), "wall", 1), (unit, "print", 1), (f.ipad, "ipad", 1),
                       (f.trim, "alu", 1)], dict(cam=(0, -60, 900), zoom=1.2)))
jobs.append(("service", [(plaster_full.cut(rrect(f.HOLE_X, f.HOLE_Y, 7, -11, 1)), "wall", 1), (unit, "print", 1),
                         (f.ipad.translate((0, 0, 35)), "ipad", 1), (f.trim.translate((0, 0, 110)), "alu", 1)],
             dict(cam=(620, -380, 520), zoom=1.15)))

only = set(sys.argv[1:])
for name, items, kw in jobs:
    if only and name not in only:
        continue
    render(f"{OUT}/{name}.png", items, **kw)
    print("rendered", name, flush=True)

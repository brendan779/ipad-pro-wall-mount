"""
Manual images for v6 (Float and Flush), rendered from the v6 CAD and the modelled hardware.

    cd tools/manual
    V6_TABLET=ipad_pro_12_9_gen3 python render_v6.py float out_dir [job ...]
    V6_TABLET=ipad_pro_12_9_gen3 python render_v6.py flush out_dir [job ...]

Blue in every image is real hardware from hardware6.py, in the place the STEP assembly puts it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "..", "src"), HERE]
import cadquery as cq  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle  # noqa: E402

import mr  # noqa: E402
from mr import render, BG, C  # noqa: E402

INK, BLUE, ORANGE, GREY = "#1c1d20", "#2f6db5", "#e8752a", "#8a8d93"
LIGHTPLUG = (0.72, 0.72, 0.72)
PLATE = (0.80, 0.80, 0.78)
style, OUT = sys.argv[1], sys.argv[2]
ONLY = set(sys.argv[3:])
os.makedirs(OUT, exist_ok=True)


def U(parts):
    u = parts[0]
    for p in parts[1:]:
        u = u.union(p)
    return u


def hw_items(shapes, dz=0.0, dx=0.0, dy=0.0, tf=None):
    out = []
    for s in shapes:
        s = s.translate((dx, dy, dz))
        out.append((tf(s) if tf else s, "hw", 1))
    return out


def plate_grid(parts, gap=24.0, cols=2):
    items = []
    for i, p in enumerate(parts):
        pp, _ = mr.on_plate(p)
        ox, oy = (i % cols) * (256 + gap), -(i // cols) * (256 + gap)
        items += [(pp.translate((ox, oy, 0)), "active", 1), (mr.plate(ox - 128, ox + 128, oy - 128, oy + 128), PLATE, 1)]
    return items


def rbox(ax, cx, cy, w, h, r, **kw):
    ax.add_patch(FancyBboxPatch((cx - w / 2 + r, cy - h / 2 + r), w - 2 * r, h - 2 * r, boxstyle=f"round,pad={r}", **kw))


def dim(ax, a, b, off, text, horiz=True, col=BLUE, fs=10):
    (x1, y1), (x2, y2) = a, b
    if horiz:
        ax.annotate("", xy=(x1, off), xytext=(x2, off), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.9, mutation_scale=8))
        for x, y in ((x1, y1), (x2, y2)):
            ax.plot([x, x], [y, off + (3 if off > y else -3)], color=col, lw=0.5)
        ax.text((x1 + x2) / 2, off + 3, text, ha="center", va="bottom", fontsize=fs, color=col)
    else:
        ax.annotate("", xy=(off, y1), xytext=(off, y2), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.9, mutation_scale=8))
        for x, y in ((x1, y1), (x2, y2)):
            ax.plot([x, off + (3 if off > x else -3)], [y, y], color=col, lw=0.5)
        ax.text(off + 4, (y1 + y2) / 2, text, ha="left", va="center", fontsize=fs, color=col, rotation=90)


def fig(w=11, h=7.2):
    f = plt.figure(figsize=(w, h), dpi=150); f.patch.set_facecolor(BG)
    ax = f.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
    return f, ax


def save(f, name):
    if ONLY and name not in ONLY:
        plt.close(f)
        return
    f.savefig(f"{OUT}/{name}.png", facecolor=BG); plt.close(f); print("saved", name, flush=True)


def want(name):
    return not ONLY or name in ONLY


def wiring(name, flush, tab_name):
    f = plt.figure(figsize=(14, 3.4), dpi=150); f.patch.set_facecolor(BG)
    ax = f.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    steps = [("PoE+ SWITCH PORT", "802.3at (PoE+)\n25.5 W per port"),
             ("Cat6 CABLE", "run inside\nthe wall cavity"),
             ("PoE+ to USB-C ADAPTER", "PoE Texas / Heckler T515\n" + ("zip-tied in the back box" if flush else "in the wall cavity,\nbehind the bracket")),
             ("USB-C CABLE", "standard straight plug,\nhidden in the frame"),
             ("iPad", "Pro 12.9″ · Pro 13″ · Pro 11″ · mini\npower + Ethernet")]
    W, H, gap, x = 236, 118, 50, 20
    for i, (t, sub) in enumerate(steps):
        col = ORANGE if i == 2 else (INK if i in (0, 4) else GREY)
        ax.add_patch(FancyBboxPatch((x + 10, -H / 2 + 10), W - 20, H - 20, boxstyle="round,pad=10",
                                    facecolor="white", edgecolor=col, lw=2.2))
        ax.text(x + W / 2, 24, t, ha="center", va="center", fontsize=15, weight="bold", color=INK)
        ax.text(x + W / 2, -16, sub, ha="center", va="center", fontsize=12.5, color="#4a4d53", linespacing=1.4)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + W + 4, 0), (x + W + gap - 4, 0), arrowstyle="-|>", mutation_scale=20, color=BLUE, lw=2.4))
        x += W + gap
    ax.set_xlim(0, x - gap + 20); ax.set_ylim(-66, 66)
    if want(name):
        f.savefig(f"{OUT}/{name}.png", facecolor=BG); print("saved", name, flush=True)
    plt.close(f)


def run(jobs):
    for name, items, kw in jobs:
        if ONLY and name not in ONLY:
            continue
        render(f"{OUT}/{name}.png", items, **kw)
        print("rendered", name, flush=True)


# ============================================================================ FLOAT
def do_float():
    import float6 as h
    import printed6 as p6
    S = h.STANDOFF
    TOP = S + h.SHELL_H
    box, zcyl, rrect = h.box, h.zcyl, h.rrect
    kit = h.float_kit()
    tname = h.TAB["name"]

    def bench(p):
        return p.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, TOP))

    wall = box(-245, 245, -175, 175, -10, 0)
    ipad, plug = h.ipad, h.plug
    cx = h.IPAD_L / 2 + h.PLUG_L + h.BEND_R / 2
    cable = (zcyl(cx, 0, h.CABLE_D / 2, 8.0, S + h.EDGE_Z)
             .union(cq.Workplane("YZ").circle(h.CABLE_D / 2).extrude(cx - 12).translate((12, 0, 8.0))))
    tape = (rrect(h.IPAD_L, h.IPAD_W, h.IPAD_R, 0.3, z0=0)
            .cut(rrect(h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP, 2, z0=-1))
            .translate((0, 0, S + h.PLATE_Z0 - 0.3)))
    car = h.car_a
    qTL, qTR = h.up(h.quad(h.car, -1, 1)), h.up(h.quad(h.car, 1, 1))
    qBL, qBR = h.up(h.quad(h.car, -1, -1)), h.up(h.quad(h.car, 1, -1))
    jobs = []
    jobs.append(("hero", [(wall, "wall", 1), (h.br, "print2", 1), (car, "print", 1), (h.hanger_a, "print", 1),
                          (h.lock_a, "print", 1), (ipad, "ipad", 1), (h.shell_a, "alu", 1)], dict(cam=(420, -300, 900), zoom=1.15)))
    if ONLY == {"hero"}:
        run(jobs)
        return
    jobs.append(("exploded", [(wall, "wall", 1), (h.br, "print2", 1),
                              (car.translate((0, 0, 70)), "print", 1), (h.hanger_a.translate((0, 0, 70)), "print2", 1),
                              (h.lock_a.translate((0, 0, 70)), "print2", 1), (ipad.translate((0, 0, 120)), "ipad", 1),
                              (plug.translate((0, 0, 120)), "plug", 1), (h.shell_a.translate((0, 0, 175)), "alu", 1)],
                 dict(cam=(760, -560, 640), zoom=1.05)))
    jobs.append(("rear_view", [(car, "print", 1), (h.hanger_a, "active", 1), (h.lock_a, "active", 1), (h.shell_a, "alu", 1),
                               (cable, "plug", 1)] + hw_items(kit.select(where="shell")) + hw_items(kit.select(where="lock boss hex")),
                 dict(cam=(-320, -300, -700), zoom=1.3)))
    # hardware overview: everything but the shell ghosted
    jobs.append(("hw_all", [(car, "print", 0.25), (h.hanger_a, "print2", 0.35), (h.lock_a, "print2", 0.35),
                            (h.br, "print2", 0.35), (h.shell_a, "alu", 0.2)] + hw_items(kit.shapes()),
                 dict(cam=(-420, -380, -620), zoom=1.25, edges=False)))
    # print orientation
    jobs.append(("po_carrier", plate_grid([h.quad(h.car, -1, 1), h.quad(h.car, 1, 1), h.quad(h.car, -1, -1), h.quad(h.car, 1, -1)]),
                 dict(cam=(420, -700, 760), zoom=1.15)))
    items, y = [], -80.0
    for p in (h.hanger, h.flip(h.lock_boss), h.flip(h.catch_rail)):
        pp, _ = mr.on_plate(p)
        items.append((pp.translate((0, y, 0)), "active", 1))
        y += 70
    items.append((mr.plate(-128, 128, -128, 128), PLATE, 1))
    jobs.append(("po_small", items, dict(cam=(160, -330, 300), zoom=1.15)))
    bp, plt_ = mr.on_plate(h.br_plate)
    jobs.append(("po_bracket", [(bp, "active", 1), (plt_, PLATE, 1)], dict(cam=(180, -320, 330), zoom=1.1)))
    jobs.append(("po_shell", plate_grid([p6.PARTS["float"]["shell_print_L"], p6.PARTS["float"]["shell_print_R"]]),
                 dict(cam=(300, -520, 420), zoom=1.2)))
    # machining
    sh_back = h.shell.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, h.SHELL_H))
    stock = box(-h.OUT_L / 2 - 8, h.OUT_L / 2 + 8, -h.OUT_W / 2 - 8, h.OUT_W / 2 + 8, -12, 0)
    jobs.append(("mach_op1", [(stock, (0.86, 0.86, 0.84), 1), (sh_back, "alu", 1)], dict(cam=(300, -380, 520), zoom=1.25)))
    jobs.append(("mach_op2", [(stock, (0.86, 0.86, 0.84), 1), (h.shell, "alu", 1)], dict(cam=(300, -380, 520), zoom=1.25)))

    # A1 heat-set inserts: hanger, lock boss, rail laid out on the bench with their real inserts
    def centred(p, y_target):
        bb = p.val().BoundingBox()
        return (-(bb.xmin + bb.xmax) / 2, y_target - (bb.ymin + bb.ymax) / 2, -bb.zmin)
    ins = []
    dx, dy, dz = centred(h.hanger, 55)
    ins += [(h.hanger.translate((dx, dy, dz)), "print", 1)]
    ins += hw_items(kit.select(where="hanger"), dx=dx, dy=dy, dz=dz - S + 0.8)
    dx, dy, dz = centred(h.lock_boss, 0)
    ins += [(h.lock_boss.translate((dx, dy, dz)), "print", 1)]
    ins += hw_items(kit.select(where="lock boss (end-on)"), dx=dx, dy=dy - 0.8, dz=dz - S)
    rl = h.flip(h.catch_rail)
    dx, dy, dz = centred(rl, -55)
    ins += [(rl.translate((dx, dy, dz)), "print", 1)]
    ins += hw_items(kit.select(where="catch rail"), tf=lambda s: h.flip(s).translate((dx, dy, dz + 0.8)))
    jobs.append(("a1_inserts", ins, dict(cam=(150, -230, 260), zoom=1.0)))
    # A2 rail to bracket (from the wall side)
    jobs.append(("a2_rail", [(h.br_plate, "print2", 1), (h.catch_rail.translate((0, 0, 25)), "active", 1)] +
                 hw_items(kit.select(where="catch rail"), dz=25) + hw_items(kit.select(where="bracket to catch rail"), dz=-12),
                 dict(cam=(300, -260, -420), zoom=1.3)))
    jobs.append(("a3_hanger", [(qTL, "print", 1), (qTR, "print2", 1), (h.hanger_a.translate((0, 0, -35)), "active", 1)] +
                 hw_items(kit.select(where="hanger"), dz=-35) + hw_items(kit.select(where="carrier to hanger"), dz=18),
                 dict(cam=(260, -120, 520), zoom=1.45, focal=(0, 60, 10))))
    jobs.append(("a4_lock", [(qBL, "print", 1), (qBR, "print2", 1), (h.lock_a.translate((0, 0, -35)), "active", 1)] +
                 hw_items(kit.select(where="lock boss"), dz=-35) + hw_items(kit.select(where="carrier to lock boss"), dz=18),
                 dict(cam=(260, -420, 420), zoom=1.45, focal=(0, -70, 10))))
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
    jobs.append(("a8_screws", [(B(h.shell_a), "alu", 1), (B(ipad), "ipad", 1), (B(car), "print", 1),
                               (B(h.hanger_a), "print2", 1), (B(h.lock_a), "print2", 1)] +
                 hw_items(kit.select(where="carrier to shell"), dz=-14, tf=B),
                 dict(cam=(300, -380, 520), zoom=1.25)))
    jobs.append(("a9_cable", [(B(h.shell_a), "alu", 1), (B(car), "print", 1), (B(h.hanger_a), "print2", 1),
                              (B(h.lock_a), "print2", 1), (B(cable), "active", 1), (B(plug), "plug", 1)],
                 dict(cam=(330, 120, 300), zoom=1.9, focal=(h.IPAD_L / 2 - 30, 0, 10))))
    # wall
    cut = box(-h.CUTOUT[0] / 2, h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2, h.CUTOUT[1] / 2, -11, 1)
    wall_cut = wall.cut(cut)
    poe = box(-24, 24, -30, 30, -45, -15)
    jobs.append(("w2_bracket", [(wall_cut, "wall", 1), (h.br.translate((0, 0, 25)), "active", 1)] +
                 hw_items(kit.select(where="bracket slots"), dz=25), dict(cam=(300, -330, 560), zoom=1.15)))
    jobs.append(("w3_poe", [(wall_cut, "wall", 0.35), (h.br, "print2", 1), (poe, "active", 1),
                            (zcyl(0, 0, 3, -60, -45), "hw", 1), (zcyl(0, 0, 2.25, -15, 6), "plug", 1)],
                 dict(cam=(260, -240, -420), zoom=2.2, focal=(0, 0, -20))))
    offered = [(p.translate((0, 10, 30)), c, 1) for p, c in ((car, "active"), (h.hanger_a, "active"), (h.lock_a, "active"),
                                                             (ipad, "ipad"), (h.shell_a, "alu"))]
    jobs.append(("w4_hang", [(wall, "wall", 1), (h.br, "print2", 1)] + offered, dict(cam=(620, -380, 520), zoom=1.1)))
    jobs.append(("final", [(wall, "wall", 1), (h.br, "print2", 1), (car, "print", 1), (ipad, "ipad", 1),
                           (h.shell_a, "alu", 1)], dict(cam=(0, -60, 900), zoom=1.2)))
    run(jobs)

    # ---- schematics
    zb = h.EDGE_Z + S
    cxp = cx
    cable2 = (h.zcyl(cxp, 0, h.CABLE_D / 2, 8.0, S + h.EDGE_Z)
              .union(cq.Workplane("YZ").circle(h.CABLE_D / 2).extrude(cxp - 40).translate((40, 0, 8.0))))
    x_end = h.IPAD_L / 2
    if want("sch_section_usb"):
        items = [(wall, "wall"), (h.br, "print2"), (car, "print"), (ipad, "ipad"), (h.shell_a, "alu"),
                 (cable2, "plug"), (plug, LIGHTPLUG)]
        labels = [("6061 SHELL", (x_end + 20, S + h.SHELL_H - 1), (x_end + 26, 33)),
                  ("iPad", (x_end - 28, S + h.CB + 3), (x_end - 22, 33)),
                  ("USB-C plug (straight)", (x_end + 9, zb), (x_end + 44, 20)),
                  ("PRINTED CARRIER", (x_end - 15, S + 1.5), (x_end + 24, 10)),
                  ("cable runs in the 14 mm shadow gap", (x_end - 40, 8), (x_end - 36, 4.5)),
                  ("WALL BRACKET", (x_end - 66, 1.5), (x_end - 60, -13)),
                  ("PLASTERBOARD", (x_end - 12, -5), (x_end - 6, -13))]
        mr.section(f"{OUT}/sch_section_usb.png", items, origin=(0, 1.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0),
                   v_axis=(0, 0, 1), labels=labels, xlim=(x_end - 78, x_end + 96), ylim=(-17, 40), w_in=14,
                   title="SECTION THROUGH THE USB-C END   (1:1)")
        print("saved sch_section_usb", flush=True)
    for tag, dyy in (("offered", 10.0), ("hung", 0.0)):
        nm = f"sch_hook_{tag}"
        if not want(nm):
            continue
        mv = lambda p: p.translate((0, dyy, 0))
        items = [(wall, "wall"), (h.br, "print2"), (mv(car), "print"), (mv(h.hanger_a), "active"),
                 (mv(ipad), "ipad"), (mv(h.shell_a), "alu")]
        if tag == "hung":
            labels = [("CATCH RAIL", (8.0, h.HOOK_Y + 4), (-13, h.HOOK_Y + 22)),
                      ("HANGER FOOT", (4.8, h.HOOK_Y + 3), (-13, h.HOOK_Y + 10)),
                      ("WALL BRACKET", (1.5, h.HOOK_Y - 15), (-13, h.HOOK_Y - 15))]
            title = "2  SLIDE DOWN ONTO THE RAIL"
        else:
            labels = [("foot clears the rail", (4.8, h.HOOK_Y + 3 + dyy), (-13, h.HOOK_Y + 24)),
                      ("CATCH RAIL", (8.0, h.HOOK_Y + 4), (-13, h.HOOK_Y + 2))]
            title = "1  HOLD 10 mm HIGH, PUSH FLAT"
        mr.section(f"{OUT}/{nm}.png", items, origin=(8, 0, 0), normal=(1, 0, 0), u_axis=(0, 0, 1), v_axis=(0, 1, 0),
                   labels=labels, xlim=(-52, 30), ylim=(h.HOOK_Y - 24, h.HOOK_Y + 40), w_in=7, title=title)
        print("saved", nm, flush=True)
    if want("sch_lock"):
        lock_hw = U(kit.select(where="lock screw") + kit.select(where="lock boss (end-on)"))
        items = [(wall, "wall"), (h.br, "print2"), (car, "print"), (h.lock_a, "print2"), (ipad, "ipad"),
                 (h.shell_a, "alu"), (lock_hw, "hw")]
        labels = [("M3 x 12 LOCK SCREW, driven up from below", (h.LOCK_Z + S, h.LOCK_Y - 1), (-13, h.LOCK_Y - 12)),
                  ("heat-set insert in the LOCK BOSS", (h.LOCK_Z + S, h.LOCK_Y + 12), (-13, h.LOCK_Y + 30)),
                  ("LOCK BLOCK on the bracket", (6, h.LOCK_Y + 4), (-13, h.LOCK_Y + 9))]
        mr.section(f"{OUT}/sch_lock.png", items, origin=(0.0, 0, 0), normal=(1, 0, 0), u_axis=(0, 0, 1), v_axis=(0, 1, 0),
                   labels=labels, xlim=(-88, 34), ylim=(h.LOCK_Y - 22, h.LOCK_Y + 42), w_in=10, title="LOCK SCREW (section)")
        print("saved sch_lock", flush=True)
    if want("sch_buttons"):
        b0 = [b for b in h.TAB["buttons"] if b[0] in ("top", "bottom")][0]
        xb = (b0[1] + b0[2]) / 2
        yt = h.IPAD_W / 2
        btn = [b for b in h.buttons if b.val().BoundingBox().ymin > 0][0]
        items = [(wall, "wall"), (car, "print"), (h.shell_a, "alu"), (ipad, "ipad"), (btn, "active")]
        labels = [("VOLUME BUTTON (0.6 mm proud)", (yt + 0.3, S + h.EDGE_Z), (yt + 14, S + h.EDGE_Z + 1)),
                  (f"{h.BUTTON_RELIEF:.1f} mm relief in the carrier wall", (yt + h.CLR + h.BUTTON_RELIEF - 0.3, S + h.CB + 1.5),
                   (yt + 14, S - 1)),
                  ("SHELL", (yt + 6, S + h.SHELL_H - 1), (yt + 14, S + h.SHELL_H + 3.5)),
                  ("iPad", (yt - 10, S + h.EDGE_Z), (yt - 14, S + h.SHELL_H + 3))]
        mr.section(f"{OUT}/sch_buttons.png", items, origin=(xb, 0, 0), normal=(1, 0, 0), u_axis=(0, 1, 0), v_axis=(0, 0, 1),
                   labels=labels, xlim=(yt - 30, yt + 52), ylim=(S - 3, S + h.SHELL_H + 7), w_in=12,
                   title="BUTTON RELIEF  (section through the volume buttons, 1:1)")
        print("saved sch_buttons", flush=True)
    if want("sch_loop"):
        zc = S + h.EDGE_Z
        xe = h.IPAD_L / 2
        clip = box(xe - 40, h.OUT_L / 2 + 50, -40, 16, -100, 100)
        items = [(car.intersect(clip), "print"), (h.shell_a.intersect(clip), "alu"), (ipad.intersect(clip), "ipad"),
                 (plug, LIGHTPLUG), (h.bend, "active")]
        labels = [("USB-C plug", (xe + 8, 3), (xe + 2, 22)),
                  (f"cable loop: {h.CAVITY_X:.1f} mm cavity (+{h.LOOP_EXTRA:.0f} mm in v6)", (xe + h.PLUG_L + 6, -1), (h.OUT_L / 2 + 6, -12)),
                  ("SHELL skirt", (h.OUT_L / 2 - 1, 10), (h.OUT_L / 2 + 6, 22)),
                  ("iPad", (xe - 8, 10), (xe - 14, 22))]
        mr.section(f"{OUT}/sch_loop.png", items, origin=(0, 0, zc), normal=(0, 0, 1), u_axis=(1, 0, 0), v_axis=(0, 1, 0),
                   labels=labels, xlim=(xe - 30, h.OUT_L / 2 + 75), ylim=(-30, 30), w_in=12,
                   title="USB-C END  (cut through the plug, seen from the front, 1:1)")
        print("saved sch_loop", flush=True)
    if want("sch_stops"):
        zc = h.BR_T + h.GAP / 2 + 0.5
        items = [(h.br, "print2"), (h.hanger_a, "active")]
        labels = [("END STOP (both ends)", (h.RAIL_HALF - 2.5, h.HOOK_Y + 14), (h.RAIL_HALF + 12, h.HOOK_Y + 24)),
                  (f"{h.STOP_CLR:.1f} mm each side", (h.HANGER_HALF + h.STOP_CLR / 2, h.HOOK_Y + 2), (h.RAIL_HALF + 12, h.HOOK_Y + 2)),
                  ("HANGER FOOT", (h.HANGER_HALF - 15, h.HOOK_Y + 4), (h.HANGER_HALF - 40, h.HOOK_Y + 30)),
                  ("CATCH RAIL", (20, h.HOOK_Y - 4), (10, h.HOOK_Y - 16))]
        mr.section(f"{OUT}/sch_stops.png", items, origin=(0, 0, zc), normal=(0, 0, 1), u_axis=(1, 0, 0), v_axis=(0, 1, 0),
                   labels=labels, xlim=(-5, h.RAIL_HALF + 70), ylim=(h.HOOK_Y - 24, h.HOOK_Y + 36), w_in=12,
                   title="LATERAL STOPS  (cut through the hook, seen from the front)")
        print("saved sch_stops", flush=True)
    wiring("sch_wiring", False, tname)
    # wall layout
    f, ax = fig(11, 7.2)
    rbox(ax, 0, 0, h.OUT_L, h.OUT_W, h.OUT_R, facecolor="none", edgecolor=GREY, lw=1.0, ls=(0, (4, 3)))
    rbox(ax, 0, 0, h.BR_L, h.BR_W, 14, facecolor="#d9d9d6", edgecolor=INK, lw=1.0)
    ax.add_patch(Rectangle((-h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), *h.CUTOUT, facecolor="white", edgecolor=ORANGE, lw=1.6))
    if h.AU_HOLES:
        for sy in (1, -1):
            ax.add_patch(Circle((0, sy * h.AU_PLATE_CTRS / 2), 2.0, facecolor=BLUE))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(FancyBboxPatch((sx * (h.BR_L / 2 - 18) - 8 + 2.6, sy * (h.BR_W / 2 - 18)), 16 - 5.2, 0.01,
                                        boxstyle="round,pad=2.6", facecolor=BLUE, edgecolor=BLUE))
    dim(ax, (-h.BR_L / 2, h.BR_W / 2), (h.BR_L / 2, h.BR_W / 2), h.OUT_W / 2 + 14, f"bracket {h.BR_L:.0f}")
    dim(ax, (h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), (h.CUTOUT[0] / 2, h.CUTOUT[1] / 2), 40, f"cut-out {h.CUTOUT[1]:.0f}", horiz=False)
    dim(ax, (-h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), (h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), -h.CUTOUT[1] / 2 - 14, f"{h.CUTOUT[0]:.0f}")
    if h.AU_HOLES:
        dim(ax, (0, -h.AU_PLATE_CTRS / 2), (0, h.AU_PLATE_CTRS / 2), -40, f"{h.AU_PLATE_CTRS:.0f} c/c", horiz=False)
    ax.text(-h.OUT_L / 2, -h.OUT_W / 2 - 22, "Dashed = finished panel outline.  Orange = plasterboard cut-out for the PoE adapter and cable.\n"
            + ("Blue = fixings: 2 screws at 84 mm (AU wall-plate mounting bracket) and/or 4 wall anchors in the slots.\n"
               if h.AU_HOLES else "Blue = fixings: 4 wall anchors or wood screws in the slots.\n")
            + "The bracket is centred on the panel: mark the panel centre on the wall and centre the bracket on it.",
            fontsize=9.3, color="#4a4d53", va="top", linespacing=1.4)
    ax.set_xlim(-h.OUT_L / 2 - 20, h.OUT_L / 2 + 20); ax.set_ylim(-h.OUT_W / 2 - 70, h.OUT_W / 2 + 40)
    save(f, "sch_wall")


def front_float(h, name):
    """dimensioned front elevation of the Float panel for one tablet"""
    f, ax = fig(11, 7.6)
    L, Wd = h.OUT_L, h.OUT_W
    rbox(ax, 0, 0, L, Wd, h.OUT_R, facecolor=C["alu"], edgecolor="#6b6e74", lw=1.2)
    WL, WW, WR = h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP
    rbox(ax, 0, 0, WL, WW, WR, facecolor="#15161a", edgecolor="#000", lw=0.8)
    rbox(ax, 0, 0, h.IPAD_L, h.IPAD_W, h.IPAD_R, facecolor="none", edgecolor=GREY, lw=0.6, ls=(0, (3, 2)))
    if h.CAM_SIDE == "end":
        ax.add_patch(FancyBboxPatch((-WL / 2 - 4.2, -h.CAM_LEN / 2), 8.4, h.CAM_LEN, boxstyle="round,pad=0,rounding_size=4.2",
                                    facecolor="#15161a", edgecolor="#000", lw=0.6))
        cam_xy = (-WL / 2, 0)
    else:
        ax.add_patch(FancyBboxPatch((-h.CAM_LEN / 2, WW / 2 - 4.2), h.CAM_LEN, 8.4, boxstyle="round,pad=0,rounding_size=4.2",
                                    facecolor="#15161a", edgecolor="#000", lw=0.6))
        cam_xy = (0, WW / 2 + 2)
    dim(ax, (-L / 2, Wd / 2), (L / 2, Wd / 2), Wd / 2 + 18, f"{L:.1f}")
    dim(ax, (L / 2, -Wd / 2), (L / 2, Wd / 2), L / 2 + 14, f"{Wd:.1f}", horiz=False)
    dim(ax, (L / 2 - h.FRAME_X, -Wd / 2), (L / 2, -Wd / 2), -Wd / 2 - 22, f"{h.FRAME_X:.1f}")
    dim(ax, (-L / 2, -Wd / 2), (-L / 2 + h.FRAME_X, -Wd / 2), -Wd / 2 - 22, f"{h.FRAME_X:.1f}")
    dim(ax, (-60, Wd / 2 - h.FRAME_Y), (-60, Wd / 2), -45, f"{h.FRAME_Y:.1f}", horiz=False)
    ax.text(0, 0, h.TAB["name"], ha="center", va="center", color="#9ea1a8", fontsize=12)
    ax.text(-L / 2 + 6, -Wd / 2 - 52, f"Shell, front view.  Dashed = iPad outline under the {h.LIP} mm lip.  "
            f"Depth off the wall {h.STANDOFF + h.SHELL_H:.1f} mm.", fontsize=9.5, color="#4a4d53")
    ax.annotate("front camera", xy=cam_xy, xytext=(-L / 2 - 30, 60) if h.CAM_SIDE == "end" else (-L / 2 + 10, Wd / 2 + 30),
                fontsize=9.5, ha="right" if h.CAM_SIDE == "end" else "left", arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    ax.annotate("USB-C end", xy=(L / 2 - 10, 0), xytext=(L / 2 + 40, 60), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    ax.set_xlim(-L / 2 - 95, L / 2 + 95); ax.set_ylim(-Wd / 2 - 62, Wd / 2 + 48)
    save(f, name)


# ============================================================================ FLUSH
def do_flush():
    import flush6 as f
    import printed6 as p6
    box, zcyl, rrect = f.box, f.zcyl, f.rrect
    kit = f.flush_kit()
    plaster = box(-300, 300, -200, 200, -f.PLASTER, 0).cut(rrect(f.HOLE_X, f.HOLE_Y, f.BOX_R + f.HOLE_CLR, -f.PLASTER - 1, 1))
    plaster_full = box(-300, 300, -200, 200, -f.PLASTER, 0)
    studs = (box(-f.STUD_CC / 2 - f.STUD_W / 2, -f.STUD_CC / 2 + f.STUD_W / 2, -200, 200, -f.PLASTER - f.STUD_D, -f.PLASTER)
             .union(box(f.STUD_CC / 2 - f.STUD_W / 2, f.STUD_CC / 2 + f.STUD_W / 2, -200, 200, -f.PLASTER - f.STUD_D, -f.PLASTER)))
    arms, arms_in = U(f.arms), U(f.arms_in)
    unit = f.sleeve.union(f.deck).union(f.back)
    poe = box(f.CAT6_X - 26 + 10, f.CAT6_X + 26 + 10, -32, 32, -f.SLEEVE_D, -f.SLEEVE_D + 24)
    cat6 = zcyl(f.CAT6_X, 0, 3.0, -f.SLEEVE_D - 40, -f.SLEEVE_D + 4)
    tape = (rrect(f.IPAD_L, f.IPAD_W, f.IPAD_R, f.Z_F - 0.3, f.Z_F)
            .cut(rrect(f.IPAD_L - 2 * f.LIP, f.IPAD_W - 2 * f.LIP, f.IPAD_R - f.LIP, f.Z_F - 1, f.Z_F + 1)))
    wall_hole = plaster_full.cut(rrect(f.HOLE_X, f.HOLE_Y, 7, -11, 1))
    clamp_hw = kit.select(label="M4x30")
    jobs = [("hero", [(wall_hole, "wall", 1), (unit, "print", 1), (f.ipad, "ipad", 1), (f.trim, "alu", 1)],
             dict(cam=(420, -300, 900), zoom=1.15))]
    if ONLY == {"hero"}:
        run(jobs)
        return
    jobs.append(("exploded", [(studs, "stud", 1), (plaster, "wall", 0.35), (f.back.translate((0, 0, -50)), "print2", 1),
                              (f.sleeve, "print", 1), (arms, "active", 1), (f.deck.translate((0, 0, 60)), "print2", 1),
                              (f.ipad.translate((0, 0, 110)), "ipad", 1), (f.plug.translate((0, 0, 110)), "plug", 1),
                              (f.trim.translate((0, 0, 165)), "alu", 1)], dict(cam=(700, -560, 480), zoom=1.15)))
    jobs.append(("behind_wall", [(plaster, "wall", 1), (studs, "stud", 1), (unit, "print", 1), (arms, "active", 1),
                                 (cat6, "hw", 1)] + hw_items(kit.select(label="M3x8")), dict(cam=(-320, -300, -700), zoom=1.3)))
    jobs.append(("hw_all", [(f.sleeve, "print", 0.22), (f.deck, "print2", 0.3), (f.back, "print2", 0.3), (arms, "active", 0.5),
                            (f.trim, "alu", 0.2)] + hw_items(kit.shapes()),
                 dict(cam=(520, -460, 560), zoom=1.2, edges=False)))
    jobs.append(("po_sleeve", plate_grid([f.flip(f.half(f.sleeve, -1)), f.flip(f.half(f.sleeve, 1))]),
                 dict(cam=(300, -520, 420), zoom=1.2)))
    jobs.append(("po_deck", plate_grid([f.half(f.deck, -1), f.half(f.deck, 1)]), dict(cam=(300, -520, 420), zoom=1.2)))
    jobs.append(("po_back", plate_grid([f.back_L, f.back_R]), dict(cam=(300, -520, 420), zoom=1.2)))
    arm_items = [(f.arm.translate((x, y, 0)), "active", 1) for x in (-40, 20) for y in (-30, 30)] + [(mr.plate(-128, 128, -128, 128), PLATE, 1)]
    jobs.append(("po_arms", arm_items, dict(cam=(120, -200, 220), zoom=1.6, focal=(-10, 0, 0))))
    jobs.append(("po_trim", plate_grid([p6.PARTS["flush"]["trim_print_L"], p6.PARTS["flush"]["trim_print_R"]]),
                 dict(cam=(300, -520, 420), zoom=1.2)))
    tb = f.trim.translate((0, 0, -f.Z_F))
    stock = box(-f.TRIM_X / 2 - 8, f.TRIM_X / 2 + 8, -f.TRIM_Y / 2 - 8, f.TRIM_Y / 2 + 8, -12, 0)
    jobs.append(("mach_op1", [(stock, (0.86, 0.86, 0.84), 1), (f.flip(tb).translate((0, 0, f.TRIM_T)), "alu", 1)],
                 dict(cam=(300, -380, 520), zoom=1.25)))
    jobs.append(("mach_op2", [(stock, (0.86, 0.86, 0.84), 1), (tb, "alu", 1)], dict(cam=(300, -380, 520), zoom=1.25)))
    # arm inserts: four arms in a row with real M4 inserts
    ins_shape = f.hw.insert("M4")
    ins = []
    for x in (-54, -18, 18, 54):
        ins.append((f.arm.translate((x, 0, 0)), "print", 1))
        ins.append((f.hw.placed(ins_shape, f.hw.loc(x, 0, f.ARM_T + 0.8, "-z")), "hw", 1))
    jobs.append(("a1_arm_inserts", ins, dict(cam=(40, -170, 170), zoom=1.15)))
    jobs.append(("a1_sleeve_inserts", [(f.sleeve, "print", 1)] + hw_items(kit.select(label="M3_heat"), dz=-8),
                 dict(cam=(-300, -360, -520), zoom=1.3)))
    jobs.append(("a2_glue_sleeve", [(f.flip(f.half(f.sleeve, -1)).translate((-18, 0, 0)), "print", 1),
                                    (f.flip(f.half(f.sleeve, 1)).translate((18, 0, 0)), "print2", 1),
                                    (box(-0.4, 0.4, -f.BOX_Y / 2 - 6, f.BOX_Y / 2 + 6, f.Z_F - 0.1, f.Z_F + f.SLEEVE_D), "active", 1)],
                 dict(cam=(320, -420, 520), zoom=1.25)))
    jobs.append(("a3_glue_deck", [(f.half(f.deck, -1).translate((-18, 0, 0)), "print", 1),
                                  (f.half(f.deck, 1).translate((18, 0, 0)), "print2", 1),
                                  (box(-0.4, 0.4, -f.BOX_Y / 2, f.BOX_Y / 2, f.DECK_Z0, f.IPAD_Z0 + 0.1), "active", 1)],
                 dict(cam=(320, -420, 520), zoom=1.25)))
    jobs.append(("a4_magnets_deck", [(f.deck, "print", 1)] + hw_items(kit.select(where="deck posts"), dz=10),
                 dict(cam=(300, -380, 520), zoom=1.25)))
    flipT = lambda s: f.flip(s)
    jobs.append(("a4_magnets_trim", [(f.flip(f.trim), "alu", 1)] + hw_items(kit.select(where="trim pockets"), dz=-12, tf=flipT) +
                 [(f.flip(s).translate((0, 0, 14)), "active", 1) for s in kit.select(label="dowel")],
                 dict(cam=(300, -380, 520), zoom=1.25)))
    jobs.append(("a5_poe", [(f.back_L, "print", 1), (f.back_R, "print2", 1), (poe, "active", 1), (cat6, "hw", 1)],
                 dict(cam=(260, -360, 420), zoom=1.3)))
    jobs.append(("a6_back_plate", [(f.sleeve, "print", 1), (f.back.translate((0, 0, -30)), "active", 1),
                                   (poe.translate((0, 0, -30)), "print2", 1)] + hw_items(kit.select(label="M3x8"), dz=-44),
                 dict(cam=(-300, -360, -520), zoom=1.25)))
    jobs.append(("a7_deck", [(f.sleeve, "print", 1), (f.back, "print2", 1), (f.deck.translate((0, 0, 45)), "active", 1),
                             (arms_in, "hw", 1)] + hw_items(clamp_hw, dz=45), dict(cam=(560, -460, 520), zoom=1.2)))
    corner_drills = [(zcyl(sx * (f.HOLE_X / 2 - 7), sy * (f.HOLE_Y / 2 - 7), 7, -11, 1), "active", 1) for sx in (-1, 1) for sy in (-1, 1)]
    jobs.append(("w2_cut", [(plaster, "wall", 1), (studs, "stud", 1)] + corner_drills +
                 [(zcyl(f.CAT6_X, 0, 3.0, -40, 40), "hw", 1)], dict(cam=(300, -330, 560), zoom=1.3)))
    jobs.append(("w4_insert", [(plaster, "wall", 1), (studs, "stud", 1), (unit.translate((0, 0, 70)), "active", 1),
                               (arms_in.translate((0, 0, 70)), "hw", 1)], dict(cam=(560, -460, 520), zoom=1.15)))
    jobs.append(("w5_clamp", [(plaster, "wall", 0.45), (studs, "stud", 1), (unit, "print", 1), (arms, "active", 1)] +
                 hw_items(clamp_hw) + hw_items(kit.select(label="M4_heat")), dict(cam=(-330, -260, -560), zoom=1.3)))
    jobs.append(("w6_ipad", [(plaster, "wall", 1), (unit, "print", 1), (f.ipad.translate((0, 0, 50)), "active", 1),
                             (f.plug.translate((0, 0, 50)), "plug", 1)], dict(cam=(560, -420, 560), zoom=1.15)))
    jobs.append(("w7_trim", [(plaster, "wall", 1), (unit, "print", 1), (f.ipad, "ipad", 1), (f.trim.translate((0, 0, 50)), "active", 1),
                             (tape.translate((0, 0, 50)), "tape", 1)], dict(cam=(560, -420, 560), zoom=1.15)))
    jobs.append(("final", [(wall_hole, "wall", 1), (unit, "print", 1), (f.ipad, "ipad", 1), (f.trim, "alu", 1)],
                 dict(cam=(0, -60, 900), zoom=1.2)))
    jobs.append(("service", [(wall_hole, "wall", 1), (unit, "print", 1), (f.ipad.translate((0, 0, 35)), "ipad", 1),
                             (f.trim.translate((0, 0, 110)), "alu", 1)], dict(cam=(620, -380, 520), zoom=1.15)))
    run(jobs)

    # ---- schematics
    cx = f.IPAD_L / 2 + f.PLUG_L + f.BEND_R / 2
    cable = (f.zcyl(cx, 0, f.CABLE_D / 2, -40.0, f.EDGE_Z)
             .union(cq.Workplane("YZ").circle(f.CABLE_D / 2).extrude(cx - 60).translate((60, 0, -40.0))))
    xe = f.IPAD_L / 2
    if want("sch_section_usb"):
        items = [(f.plaster, "wall"), (f.studs, "stud"), (f.sleeve, "print"), (f.deck, "print2"), (f.back, "print"),
                 (f.ipad, "ipad"), (f.trim, "alu"), (cable, "plug"), (f.plug, LIGHTPLUG)]
        labels = [("TRIM on magnets", (xe + 26, f.Z_F + 2.5), (xe + 44, 9)),
                  ("iPad glass, level with the wall face", (xe - 22, f.GLASS_Z - 0.6), (xe - 16, 9)),
                  ("USB-C plug", (xe + 9, f.EDGE_Z), (xe + 44, 2.5)),
                  ("DECK on 45° ledges", (xe - 14, f.DECK_Z0 + 1.5), (xe - 10, -20)),
                  ("cable dives back into the box", (cx, -30), (xe - 12, -31)),
                  ("SLEEVE wall", (f.BOX_X / 2 - 1, -46), (xe + 44, -46)),
                  ("BACK PLATE", (xe - 30, -f.SLEEVE_D - 1.2), (xe - 26, -48)),
                  ("PLASTERBOARD", (xe + 62, -5), (xe + 70, -17)),
                  ("STUD", (225 if xe < 200 else xe + 82, -40), ((225 if xe < 200 else xe + 82) + 28, -40))]
        mr.section(f"{OUT}/sch_section_usb.png", items, origin=(0, 1.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0),
                   v_axis=(0, 0, 1), labels=labels, xlim=(xe - 52, xe + 132), ylim=(-64, 16), w_in=14,
                   title="SECTION THROUGH THE USB-C END   (1:1)")
        print("saved sch_section_usb", flush=True)
    if want("sch_buttons"):
        tb_ = [b for b in f.TAB["buttons"] if b[0] in ("top", "bottom")]
        b0 = tb_[0] if tb_ else None
        if b0:
            xb = (b0[1] + b0[2]) / 2
            yt = f.IPAD_W / 2
            btn = [b for b in f.buttons if b.val().BoundingBox().ymin > 0][0]
            items = [(f.plaster, "wall"), (f.sleeve, "print"), (f.deck, "print2"), (f.trim, "alu"), (f.ipad, "ipad"), (btn, "active")]
            labels = [("VOLUME BUTTON (0.6 mm proud)", (yt + 0.3, f.EDGE_Z), (yt + 16, f.EDGE_Z - 6)),
                      (f"{f.BUTTON_RELIEF:.1f} mm relief in the sleeve wall, 45° roof", (yt + f.CLR + f.BUTTON_RELIEF - 0.3, f.IPAD_Z0 - 0.5),
                       (yt + 16, f.IPAD_Z0 - 12)),
                      ("TRIM", (yt + 5, f.Z_F + 2), (yt + 16, f.Z_F + 6)),
                      ("iPad", (yt - 10, f.EDGE_Z), (yt - 18, -14))]
            mr.section(f"{OUT}/sch_buttons.png", items, origin=(xb, 0, 0), normal=(1, 0, 0), u_axis=(0, 1, 0), v_axis=(0, 0, 1),
                       labels=labels, xlim=(yt - 30, yt + 60), ylim=(-22, 10), w_in=12,
                       title="BUTTON RELIEF  (section through the volume buttons, 1:1)")
            print("saved sch_buttons", flush=True)
    if want("sch_loop"):
        clip = box(xe - 40, f.BOX_X / 2 + 50, -40, 16, -100, 100)
        items = [(f.sleeve.intersect(clip), "print"), (f.deck.intersect(clip), "print2"), (f.ipad.intersect(clip), "ipad"),
                 (f.plug, LIGHTPLUG), (f.bend, "active")]
        labels = [("USB-C plug", (xe + 8, 3), (xe + 2, 22)),
                  (f"cable loop: {f.END_X:.1f} mm box end (+{f.LOOP_EXTRA:.0f} mm in v6)", (xe + f.PLUG_L + 6, -1), (f.BOX_X / 2 + 6, -12)),
                  ("SLEEVE wall", (f.BOX_X / 2 - 1, 10), (f.BOX_X / 2 + 6, 22)),
                  ("iPad", (xe - 8, 10), (xe - 14, 22))]
        mr.section(f"{OUT}/sch_loop.png", items, origin=(0, 0, f.EDGE_Z), normal=(0, 0, 1), u_axis=(1, 0, 0), v_axis=(0, 1, 0),
                   labels=labels, xlim=(xe - 30, f.BOX_X / 2 + 75), ylim=(-30, 30), w_in=12,
                   title="USB-C END  (cut through the plug, seen from the front, 1:1)")
        print("saved sch_loop", flush=True)
    if want("sch_clamp"):
        cp = [(x, y) for (x, y) in f.CLAMP_PTS if x > 0 and y > 0][0]
        x0, y0 = cp
        arm_ = [a for a, p in zip(f.arms, f.CLAMP_PTS) if p == cp][0]
        scr = [s for s in clamp_hw if abs(s.val().BoundingBox().center.x - x0) < 1 and abs(s.val().BoundingBox().center.y - y0) < 1]
        insr = [s for s in kit.select(label="M4_heat") if abs(s.val().BoundingBox().center.x - x0) < 1 and abs(s.val().BoundingBox().center.y - y0) < 1]
        items = [(f.plaster, "wall"), (f.studs, "stud"), (f.sleeve, "print"), (f.deck, "print2"), (f.back, "print"),
                 (f.trim, "alu"), (arm_, "active"), (U(scr + insr), "hw")]
        XL = f.STUD_CC / 2 + f.STUD_W / 2 + 8
        labels = [("M4 x 30 pan head, driven from the front", (x0, f.Z_F - 1.5), (XL, 11)),
                  ("SLEEVE FLANGE on the wall face", (f.BOX_X / 2 + 3, 0.7), (XL, 4)),
                  ("plasterboard clamped here", (f.HOLE_X / 2 + 4, -5), (XL, -5)),
                  ("deck post", (x0 - 4.5, -3), (x0 - 22, -22)),
                  ("DOG-EAR ARM + M4 insert pulls forward", (x0 + 14, f.ARM_Z0 + 3), (XL, -22)),
                  ("arm slot in the sleeve end wall", (f.BOX_X / 2 - 1, -30), (XL, -36))]
        mr.section(f"{OUT}/sch_clamp.png", items, origin=(0, y0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
                   labels=labels, xlim=(x0 - 45, XL + 75), ylim=(-62, 17), w_in=14,
                   title="DOG-EAR CLAMP   (section through one arm, 1:1)")
        print("saved sch_clamp", flush=True)
    wiring("sch_wiring", True, f.TAB["name"])
    # stud layout
    fg, ax = fig(11, 7.4)
    for sx in (-1, 1):
        ax.add_patch(Rectangle((sx * f.STUD_CC / 2 - f.STUD_W / 2, -190), f.STUD_W, 380, facecolor=C["stud"], edgecolor="#8a6b45", lw=0.8))
        ax.plot([sx * f.STUD_CC / 2] * 2, [-200, 200], color="#8a6b45", lw=0.6, ls="-.")
    rbox(ax, 0, 0, f.HOLE_X, f.HOLE_Y, f.BOX_R + f.HOLE_CLR, facecolor="white", edgecolor=ORANGE, lw=1.8)
    reach = f.CLAMP_X + f.ARM_REACH
    for (x, y) in f.CLAMP_PTS:
        sx = 1 if x > 0 else -1
        ax.add_patch(Rectangle((min(x - 6 * sx, sx * reach), y - 6), abs(sx * reach - (x - 6 * sx)), 12,
                               facecolor=ORANGE, edgecolor="#a54f17", lw=0.6, alpha=0.9))
    dim(ax, (-f.STUD_CC / 2, 190), (f.STUD_CC / 2, 190), 205, f"studs {f.STUD_CC:.0f} c/c")
    sf = f.STUD_CC / 2 - f.STUD_W / 2
    dim(ax, (-sf, -150), (sf, -150), -168, f"clear between studs {2 * sf:.0f}")
    dim(ax, (-f.HOLE_X / 2, f.HOLE_Y / 2), (f.HOLE_X / 2, f.HOLE_Y / 2), f.HOLE_Y / 2 + 16, f"cut-out {f.HOLE_X:.1f}")
    dim(ax, (f.HOLE_X / 2, -f.HOLE_Y / 2), (f.HOLE_X / 2, f.HOLE_Y / 2), f.HOLE_X / 2 + 8, f"{f.HOLE_Y:.1f}", horiz=False)
    dim(ax, (reach, -45), (sf, -45), -64, f"{sf - reach:.0f} spare", fs=9)
    ax.text(0, 0, "CENTRE BETWEEN THE STUDS\n(within ±%.0f mm)" % (f.STUD_CC / 2 - 45 / 2 - reach), ha="center", va="center",
            fontsize=12, weight="bold", color=INK)
    ax.text(-f.STUD_CC / 2 - 20, -222, f"{f.TAB['name']}.  Orange bars = dog-ear arms swung out (reach ±{reach:.1f} mm).  "
            f"Drawn with {f.STUD_W:.0f} mm studs; allow {f.STUD_CC/2 - 45/2 - reach:.0f} mm for 45 mm studs.",
            fontsize=9.5, color="#4a4d53")
    ax.set_xlim(-f.STUD_CC / 2 - 40, f.STUD_CC / 2 + 70); ax.set_ylim(-235, 225)
    save(fg, "sch_studs")
    # magnet polarity
    fg, ax = fig(10, 4.4)

    def mag(ax, x, y, top, col):
        ax.add_patch(Rectangle((x - 12, y), 24, 6, facecolor=col, edgecolor=INK, lw=0.8))
        ax.text(x, y + 3, top, ha="center", va="center", fontsize=10, weight="bold", color="white")
    ax.add_patch(Rectangle((-40, 20), 80, 8, facecolor=C["alu"], edgecolor="#6b6e74"))
    ax.text(-46, 24, "TRIM", ha="right", va="center", fontsize=10, weight="bold")
    mag(ax, 0, 14, "S", BLUE)
    ax.add_patch(Rectangle((-12, -22), 24, 28, facecolor=C["print"], edgecolor=INK))
    ax.text(-46, -8, "DECK POST", ha="right", va="center", fontsize=10, weight="bold")
    mag(ax, 0, 0, "N", ORANGE)
    ax.annotate("", xy=(0, 12.5), xytext=(0, 7.5), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
    ax.text(30, 10, "faces ATTRACT", fontsize=10, va="center")
    ax.text(70, 28, "1  Stack all the magnets into one column.\n2  Slide each off and dot its TOP face with a marker.\n"
            "3  TRIM: dot face UP, into the pocket (toward the room).\n4  DECK: dot face UP, exposed (toward the room).\n"
            "    All face the same way, so each pair attracts.\n"
            "5  Test each pair before the glue sets: the trim must snap on.", fontsize=10, va="top", linespacing=1.6)
    ax.set_xlim(-110, 250); ax.set_ylim(-30, 40)
    save(fg, "sch_polarity")


def front_flush(f, name):
    fg, ax = fig(11, 7.6)
    L, Wd = f.TRIM_X, f.TRIM_Y
    rbox(ax, 0, 0, L, Wd, f.TRIM_R, facecolor=C["alu"], edgecolor="#6b6e74", lw=1.2)
    WL, WW = f.IPAD_L - 2 * f.LIP, f.IPAD_W - 2 * f.LIP
    rbox(ax, 0, 0, WL, WW, f.IPAD_R - f.LIP, facecolor="#15161a", edgecolor="#000", lw=0.8)
    rbox(ax, 0, 0, f.HOLE_X, f.HOLE_Y, f.BOX_R + f.HOLE_CLR, facecolor="none", edgecolor=ORANGE, lw=1.0, ls=(0, (4, 3)))
    if f.CAM_SIDE == "end":
        ax.add_patch(FancyBboxPatch((-WL / 2 - 4.2, -f.CAM_LEN / 2), 8.4, f.CAM_LEN, boxstyle="round,pad=0,rounding_size=4.2",
                                    facecolor="#15161a", edgecolor="#000", lw=0.6))
    else:
        ax.add_patch(FancyBboxPatch((-f.CAM_LEN / 2, WW / 2 - 4.2), f.CAM_LEN, 8.4, boxstyle="round,pad=0,rounding_size=4.2",
                                    facecolor="#15161a", edgecolor="#000", lw=0.6))
    for sx, e in ((-1, "-x"), (1, "+x")):
        for gx in f.GRILLE_X:
            for (y0, y1) in f.WIN[e]:
                ln = max(6.0, (y1 - y0) - 6.0)
                ax.add_patch(FancyBboxPatch((sx * gx, (y0 + y1) / 2 - ln / 2 + 1), 0.01, ln - 2, boxstyle="round,pad=1",
                                            facecolor="#4a4d53", edgecolor="none"))
    dim(ax, (-L / 2, Wd / 2), (L / 2, Wd / 2), Wd / 2 + 18, f"{L:.1f}")
    dim(ax, (L / 2, -Wd / 2), (L / 2, Wd / 2), L / 2 + 14, f"{Wd:.1f}", horiz=False)
    ax.text(0, 0, f.TAB["name"], ha="center", va="center", color="#9ea1a8", fontsize=12)
    ax.text(-L / 2 + 6, -Wd / 2 - 40, f"Trim, front view.  Orange dashed = plasterboard cut-out {f.HOLE_X:.1f} x {f.HOLE_Y:.1f} mm (hidden).  "
            f"Proud of the wall {f.Z_F + f.TRIM_T:.1f} mm.", fontsize=9.5, color="#4a4d53")
    ax.set_xlim(-L / 2 - 60, L / 2 + 60); ax.set_ylim(-Wd / 2 - 50, Wd / 2 + 40)
    save(fg, name)


if __name__ == "__main__":
    if style == "float":
        do_float()
    elif style == "flush":
        do_flush()
    elif style == "fronts":            # front elevations only (for the model pages)
        import float6 as h
        import flush6 as fl
        tag = h.TAB_KEY
        front_float(h, f"front_float_{tag}")
        front_flush(fl, f"front_flush_{tag}")

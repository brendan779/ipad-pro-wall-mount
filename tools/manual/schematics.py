import sys
sys.path[:0] = ["../../float-v4.1", "../../flush-v5.1"]
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
import cadquery as cq
import mr
from mr import BG, C

INK, BLUE, ORANGE, GREY = "#1c1d20", "#2f6db5", "#e8752a", "#8a8d93"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})


def fig(w=11, h=7.2):
    f = plt.figure(figsize=(w, h), dpi=150); f.patch.set_facecolor(BG)
    ax = f.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_facecolor(BG); ax.set_aspect("equal"); ax.axis("off")
    return f, ax


def rbox(ax, cx, cy, w, h, r, **kw):
    ax.add_patch(FancyBboxPatch((cx - w / 2 + r, cy - h / 2 + r), w - 2 * r, h - 2 * r,
                                boxstyle=f"round,pad={r}", **kw))


def dim(ax, a, b, off, text, horiz=True, col=BLUE, fs=10):
    (x1, y1), (x2, y2) = a, b
    if horiz:
        y = off
        ax.annotate("", xy=(x1, y), xytext=(x2, y), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.9, mutation_scale=8))
        ax.plot([x1, x1], [y1, y], color=col, lw=0.4); ax.plot([x2, x2], [y2, y], color=col, lw=0.4)
        ax.text((x1 + x2) / 2, y + 2.5, text, ha="center", va="bottom", fontsize=fs, color=col)
    else:
        x = off
        ax.annotate("", xy=(x, y1), xytext=(x, y2), arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.9, mutation_scale=8))
        ax.plot([x1, x], [y1, y1], color=col, lw=0.4); ax.plot([x2, x], [y2, y2], color=col, lw=0.4)
        ax.text(x + 3, (y1 + y2) / 2, text, ha="left", va="center", fontsize=fs, color=col)


def save(f, path):
    f.savefig(path, facecolor=BG); plt.close(f); print("saved", path, flush=True)


# =============================================================== wiring (both)
def wiring(path, flush):
    f, ax = fig(12, 4.6)
    steps = [("PoE+ SWITCH PORT", "802.3at (PoE+)\n25.5 W per port"),
             ("Cat6 CABLE", "in the wall cavity"),
             ("PoE+ → USB-C ADAPTER", "PoE Texas / Heckler T515\n" + ("zip-tied in the back box" if flush else "in the wall cavity\nbehind the bracket")),
             ("USB-C CABLE", "standard, straight plug\nhidden in the frame"),
             ("iPad Pro 12.9\"", "3rd gen (A1876/A1895/A2014)\npower + 100 Mbps Ethernet")]
    W, H, gap = 190, 105, 52
    x = 0
    for i, (t, sub) in enumerate(steps):
        col = ORANGE if i == 2 else (INK if i in (0, 4) else GREY)
        rbox(ax, x + W / 2, 0, W, H, 10, facecolor="white", edgecolor=col, lw=2.0)
        ax.text(x + W / 2, 22, t, ha="center", va="center", fontsize=11.5, weight="bold", color=INK)
        ax.text(x + W / 2, -16, sub, ha="center", va="center", fontsize=9.5, color="#4a4d53", linespacing=1.35)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + W + 6, 0), (x + W + gap - 6, 0), arrowstyle="-|>", mutation_scale=16, color=BLUE, lw=2))
        x += W + gap
    ax.text(0, 90, "POWER + DATA PATH", fontsize=12, weight="bold", color=INK)
    ax.text(0, -92, "Use a PoE+ (802.3at) port. Plain 802.3af PoE can't supply the 25 W adapter. "
            "Ethernet is USB 2.0 speed (about 100 Mbps), which is plenty for HomeKit / Home Assistant dashboards.",
            fontsize=9.5, color="#4a4d53")
    ax.set_xlim(-10, x - gap + 10); ax.set_ylim(-110, 110)
    save(f, path)


# =============================================================== v4.1
def v41():
    import hybrid as h
    S = h.STANDOFF
    # ---- front elevation
    f, ax = fig(11, 7.6)
    L, Wd = h.OUT_L, h.OUT_W
    rbox(ax, 0, 0, L, Wd, h.OUT_R, facecolor=C["alu"], edgecolor="#6b6e74", lw=1.2)
    rbox(ax, 0, 0, h.IPAD_L - 2 * h.LIP, h.IPAD_W - 2 * h.LIP, h.IPAD_R - h.LIP, facecolor="#15161a", edgecolor="#000", lw=0.8)
    rbox(ax, 0, 0, h.IPAD_L, h.IPAD_W, h.IPAD_R, facecolor="none", edgecolor=GREY, lw=0.6, ls=(0, (3, 2)))
    ax.add_patch(FancyBboxPatch((-(h.IPAD_L / 2 - h.LIP) - 4.2, -16), 8.4, 32, boxstyle="round,pad=0,rounding_size=4.2",
                                facecolor="#15161a", edgecolor="#000", lw=0.6))
    dim(ax, (-L / 2, Wd / 2), (L / 2, Wd / 2), Wd / 2 + 18, f"{L:.1f}")
    dim(ax, (L / 2, -Wd / 2), (L / 2, Wd / 2), L / 2 + 14, f"{Wd:.1f}", horiz=False)
    dim(ax, (L / 2 - h.FRAME_X, -Wd / 2), (L / 2, -Wd / 2), -Wd / 2 - 22, f"{h.FRAME_X:.1f}")
    dim(ax, (-L / 2, -Wd / 2), (-L / 2 + h.FRAME_X, -Wd / 2), -Wd / 2 - 22, f"{h.FRAME_X:.1f}")
    dim(ax, (-60, Wd / 2 - h.FRAME_Y), (-60, Wd / 2), -45, f"{h.FRAME_Y:.1f}", horiz=False)
    ax.text(0, 0, "iPad Pro 12.9\"\nscreen", ha="center", va="center", color="#9ea1a8", fontsize=12)
    ax.text(-L / 2 + 6, -Wd / 2 - 52, "6061 aluminium shell, front view.  Dashed = iPad outline under the 2.8 mm lip.  "
            f"Depth off the wall {S + h.SHELL_H:.1f} mm.", fontsize=9.5, color="#4a4d53")
    ax.annotate("Face ID notch", xy=(-(h.IPAD_L / 2 - h.LIP), 0), xytext=(-L / 2 - 30, 60), fontsize=9.5, ha="right",
                arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    ax.annotate("USB-C end", xy=(L / 2 - 10, 0), xytext=(L / 2 + 40, 60), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    ax.set_xlim(-L / 2 - 95, L / 2 + 95); ax.set_ylim(-Wd / 2 - 62, Wd / 2 + 40)
    save(f, "v41/sch_front.png")

    # ---- side section through the USB-C end (y = 1)
    wall = h.box(-400, 400, -300, 300, -10, 0)
    items = [(wall, "wall", ""), (h.br, "print2", ""), (h.car_a, "print", ""), (h.ipad, "ipad", ""),
             (h.shell_a, "alu", ""), (h.plug, "plug", "")]
    zb = h.EDGE_Z + S
    labels = [("6061 SHELL (2.5 mm plate, 2.0 mm skirt)", (152, S + h.SHELL_H - 1), (128, 38)),
              ("iPad Pro (glass up to the lip)", (128, S + h.CB + 3), (106, 30)),
              ("USB-C plug, straight", (h.IPAD_L / 2 + 8, zb), (150, 33)),
              ("PRINTED CARRIER", (110, S + 1.5), (100, 6)),
              ("cable drops into the 14 mm shadow gap", (h.IPAD_L / 2 + h.PLUG_L + 4, 9), (172, -2)),
              ("WALL BRACKET", (60, 1.5), (40, -6)),
              ("PLASTERBOARD", (60, -5), (40, -14))]
    mr.section("v41/sch_section_usb.png", items, origin=(0, 1.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
               labels=labels, xlim=(30, 200), ylim=(-18, 44), w_in=12,
               title="SECTION THROUGH THE USB-C END")

    # ---- hook: offered vs hung (section at x = 8)
    for tag, dy in (("offered", 10.0), ("hung", 0.0)):
        mv = lambda p: p.translate((0, dy, 0))
        items = [(wall, "wall", ""), (h.br, "print2", ""), (mv(h.car_a), "print", ""), (mv(h.hanger_a), "active", ""),
                 (mv(h.ipad), "ipad", ""), (mv(h.shell_a), "alu", "")]
        lab = [("CATCH RAIL (on bracket)", (8, h.HOOK_Y + 4), (-14, h.HOOK_Y - 4)),
               ("HANGER FOOT", (h.BR_T + 2, h.HOOK_Y + 3 + dy), (24, h.HOOK_Y - 12))] if tag == "hung" else \
              [("foot sits 10 mm above the rail", (h.BR_T + 2, h.HOOK_Y + 3 + dy), (24, h.HOOK_Y - 6))]
        mr.section(f"v41/sch_hook_{tag}.png", items, origin=(8, 0, 0), normal=(1, 0, 0), u_axis=(0, 0, 1), v_axis=(0, 1, 0),
                   labels=lab, xlim=(-16, 40), ylim=(h.HOOK_Y - 22, h.HOOK_Y + 36), w_in=6,
                   title="1  OFFER UP 10 mm HIGH, PUSH FLAT" if tag == "offered" else "2  SLIDE DOWN ONTO THE RAIL")

    # ---- lock screw (section at x = 0.6)
    scr = (cq.Workplane("XZ").circle(1.5).extrude(-14).translate((0, h.LOCK_Y - 1, h.LOCK_Z + S))
           .union(cq.Workplane("XZ").circle(2.75).extrude(-3).translate((0, h.LOCK_Y - 4, h.LOCK_Z + S))))
    items = [(wall, "wall", ""), (h.br, "print2", ""), (h.car_a, "print", ""), (h.lock_a, "print2", ""),
             (h.ipad, "ipad", ""), (h.shell_a, "alu", ""), (scr, "hw", "")]
    lab = [("M3 x 12 LOCK SCREW (driven up from below)", (h.LOCK_Z + S, h.LOCK_Y - 2), (30, h.LOCK_Y - 10)),
           ("M3 heat-set insert in the LOCK BOSS", (h.LOCK_Z + S, h.LOCK_Y + 12), (30, h.LOCK_Y + 22)),
           ("lock block (bracket)", (6, h.LOCK_Y + 3), (-14, h.LOCK_Y + 30))]
    mr.section("v41/sch_lock.png", items, origin=(0.6, 0, 0), normal=(1, 0, 0), u_axis=(0, 0, 1), v_axis=(0, 1, 0),
               labels=lab, xlim=(-30, 75), ylim=(h.LOCK_Y - 22, h.LOCK_Y + 40), w_in=8.5,
               title="LOCK SCREW")
    wiring("v41/sch_wiring.png", flush=False)

    # ---- wall layout (surface mount)
    f, ax = fig(11, 7.2)
    rbox(ax, 0, 0, h.OUT_L, h.OUT_W, h.OUT_R, facecolor="none", edgecolor=GREY, lw=1.0, ls=(0, (4, 3)))
    rbox(ax, 0, 0, h.BR_L, h.BR_W, 14, facecolor="#d9d9d6", edgecolor=INK, lw=1.0)
    ax.add_patch(Rectangle((-h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), *h.CUTOUT, facecolor="white", edgecolor=ORANGE, lw=1.6))
    for sy in (1, -1):
        ax.add_patch(Circle((0, sy * h.AU_PLATE_CTRS / 2), 2.0, facecolor=BLUE))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(FancyBboxPatch((sx * (h.BR_L / 2 - 18) - 8 + 2.6, sy * (h.BR_W / 2 - 18) - 2.6 + 2.6), 16 - 5.2, 0.01,
                                        boxstyle="round,pad=2.6", facecolor=BLUE, edgecolor=BLUE))
    dim(ax, (-h.BR_L / 2, h.BR_W / 2), (h.BR_L / 2, h.BR_W / 2), h.OUT_W / 2 + 14, f"bracket {h.BR_L:.0f}")
    dim(ax, (h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), (h.CUTOUT[0] / 2, h.CUTOUT[1] / 2), 40, f"cut-out {h.CUTOUT[1]:.0f}", horiz=False)
    dim(ax, (-h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), (h.CUTOUT[0] / 2, -h.CUTOUT[1] / 2), -h.CUTOUT[1] / 2 - 14, f"{h.CUTOUT[0]:.0f}")
    dim(ax, (0, -h.AU_PLATE_CTRS / 2), (0, h.AU_PLATE_CTRS / 2), -40, f"{h.AU_PLATE_CTRS:.0f} c/c", horiz=False)
    ax.text(-h.OUT_L / 2, -h.OUT_W / 2 - 22, "Dashed = finished panel outline.  Orange = plasterboard cut-out for the PoE adapter and cable.\n"
            "Blue = fixings: 2 screws at 84 mm (AU wall-plate mounting bracket) and/or 4 wall anchors in the slots.\n"
            "The bracket is centred on the panel: mark the panel centre on the wall and centre the bracket on it.",
            fontsize=9.3, color="#4a4d53", va="top", linespacing=1.4)
    ax.set_xlim(-h.OUT_L / 2 - 20, h.OUT_L / 2 + 20); ax.set_ylim(-h.OUT_W / 2 - 70, h.OUT_W / 2 + 40)
    save(f, "v41/sch_wall.png")


# =============================================================== v5.1
def v51():
    import flush51 as f5
    # ---- front elevation
    f, ax = fig(11, 7.6)
    L, Wd = f5.TRIM_X, f5.TRIM_Y
    rbox(ax, 0, 0, L, Wd, f5.TRIM_R, facecolor=C["alu"], edgecolor="#6b6e74", lw=1.2)
    rbox(ax, 0, 0, f5.IPAD_L - 2 * f5.LIP, f5.IPAD_W - 2 * f5.LIP, f5.IPAD_R - f5.LIP, facecolor="#15161a", edgecolor="#000", lw=0.8)
    rbox(ax, 0, 0, f5.HOLE_X, f5.HOLE_Y, f5.BOX_R + f5.HOLE_CLR, facecolor="none", edgecolor=ORANGE, lw=1.0, ls=(0, (4, 3)))
    ax.add_patch(FancyBboxPatch((-(f5.IPAD_L / 2 - f5.LIP) - 4.2, -16), 8.4, 32, boxstyle="round,pad=0,rounding_size=4.2",
                                facecolor="#15161a", edgecolor="#000", lw=0.6))
    for sx in (-1, 1):
        for gx in f5.GRILLE_X:
            for yc, ln in ((f5.SPK_Y, f5.SPK_LEN - 6), (-f5.SPK_Y, f5.SPK_LEN - 6), (0.0, 16.0)):
                ax.add_patch(FancyBboxPatch((sx * gx - 1 + 1, yc - ln / 2 + 1), 0.01, ln - 2, boxstyle="round,pad=1",
                                            facecolor="#4a4d53", edgecolor="none"))
    dim(ax, (-L / 2, Wd / 2), (L / 2, Wd / 2), Wd / 2 + 18, f"{L:.1f}")
    dim(ax, (L / 2, -Wd / 2), (L / 2, Wd / 2), L / 2 + 14, f"{Wd:.1f}", horiz=False)
    dim(ax, (L / 2 - (L - f5.IPAD_L) / 2, -Wd / 2), (L / 2, -Wd / 2), -Wd / 2 - 22, f"{(L - f5.IPAD_L) / 2:.1f}")
    dim(ax, (-L / 2, -Wd / 2), (-L / 2 + (L - f5.IPAD_L) / 2, -Wd / 2), -Wd / 2 - 22, f"{(L - f5.IPAD_L) / 2:.1f}")
    dim(ax, (-60, Wd / 2 - (Wd - f5.IPAD_W) / 2), (-60, Wd / 2), -45, f"{(Wd - f5.IPAD_W) / 2:.1f}", horiz=False)
    ax.text(0, 0, "iPad Pro 12.9\"\nscreen", ha="center", va="center", color="#9ea1a8", fontsize=12)
    ax.text(-L / 2 + 6, -Wd / 2 - 52, f"6061 trim, front view.  Orange dashed = plasterboard cut-out {f5.HOLE_X:.1f} x {f5.HOLE_Y:.1f} mm (hidden).  "
            f"Proud of the wall {f5.Z_F + f5.TRIM_T:.1f} mm.", fontsize=9.5, color="#4a4d53")
    ax.annotate("speaker grilles", xy=(f5.GRILLE_X[2], f5.SPK_Y), xytext=(L / 2 + 30, 85), fontsize=9.5,
                arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    ax.annotate("mic grille", xy=(-f5.GRILLE_X[2], 0), xytext=(-L / 2 - 30, 40), fontsize=9.5, ha="right",
                arrowprops=dict(arrowstyle="-", lw=0.7, color=INK))
    ax.set_xlim(-L / 2 - 95, L / 2 + 95); ax.set_ylim(-Wd / 2 - 62, Wd / 2 + 40)
    save(f, "v51/sch_front.png")

    # ---- side section through the USB-C end
    items = [(f5.plaster, "wall", ""), (f5.studs, "stud", ""), (f5.sleeve, "print", ""), (f5.deck, "print2", ""),
             (f5.back, "print", ""), (f5.ipad, "ipad", ""), (f5.trim, "alu", ""), (f5.plug, "plug", "")]
    labels = [("6061 TRIM (3 mm) on magnets", (160, f5.Z_F + 2.5), (128, 14)),
              ("iPad glass, flush with the wall face", (125, f5.GLASS_Z - 1), (95, 10.5)),
              ("USB-C plug", (f5.IPAD_L / 2 + 8, f5.EDGE_Z), (175, 7)),
              ("DECK (on 45° ledges)", (125, f5.DECK_Z0 + 1.5), (95, -16)),
              ("SLEEVE wall", (f5.BOX_X / 2 - 1, -30), (205, -30)),
              ("BACK PLATE", (120, -f5.SLEEVE_D - 1.2), (95, -64)),
              ("PLASTERBOARD 10 mm", (f5.HOLE_X / 2 + 8, -5), (205, -5)),
              ("cable dives back into the box", (f5.IPAD_L / 2 + f5.PLUG_L + 4, -20), (140, -40))]
    mr.section("v51/sch_section_usb.png", items, origin=(0, 1.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
               labels=labels, xlim=(85, 245), ylim=(-70, 18), w_in=12, title="SECTION THROUGH THE USB-C END")

    # ---- clamp section (y = 45 plane)
    x0 = f5.CLAMP_PTS[1][0] if f5.CLAMP_PTS[1][0] > 0 else f5.CLAMP_PTS[3][0]
    scr = f5.zcyl(x0, 45, 2.0, f5.ARM_Z0 - 2, f5.Z_F - 3).union(f5.zcyl(x0, 45, 3.75, f5.Z_F - 3, f5.Z_F - 0.2))
    arm_ = [a for a, (x, y) in zip(f5.arms, f5.CLAMP_PTS) if x > 0 and y > 0][0]
    items = [(f5.plaster, "wall", ""), (f5.studs, "stud", ""), (f5.sleeve, "print", ""), (f5.deck, "print2", ""),
             (f5.back, "print", ""), (f5.trim, "alu", ""), (arm_, "active", ""), (scr, "hw", "")]
    labels = [("M4 x 30 screw, driven from the front", (x0, f5.Z_F - 1.5), (120, 12)),
              ("deck post (screw head seat)", (x0 - 5, -2), (120, 2)),
              ("DOG-EAR ARM pulls forward", (x0 + 12, f5.ARM_Z0 + 3), (205, -24)),
              ("plasterboard is clamped here", (f5.HOLE_X / 2 + 5, -5), (205, -5)),
              ("SLEEVE FLANGE on the wall face", (f5.BOX_X / 2 + 3, 0.7), (205, 9)),
              ("slot in the sleeve end wall", (f5.BOX_X / 2 - 1, -28), (205, -40))]
    mr.section("v51/sch_clamp.png", items, origin=(0, 45.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
               labels=labels, xlim=(110, 260), ylim=(-62, 18), w_in=12, title="DOG-EAR CLAMP (section through one arm)")

    wiring("v51/sch_wiring.png", flush=True)

    # ---- stud layout
    f, ax = fig(11, 7.4)
    for sx in (-1, 1):
        ax.add_patch(Rectangle((sx * f5.STUD_CC / 2 - f5.STUD_W / 2, -190), f5.STUD_W, 380, facecolor=C["stud"], edgecolor="#8a6b45", lw=0.8))
        ax.plot([sx * f5.STUD_CC / 2] * 2, [-200, 200], color="#8a6b45", lw=0.6, ls="-.")
    rbox(ax, 0, 0, f5.HOLE_X, f5.HOLE_Y, f5.BOX_R + f5.HOLE_CLR, facecolor="white", edgecolor=ORANGE, lw=1.8)
    reach = f5.BOX_X / 2 - f5.WALL - 6.0 + f5.ARM_REACH
    for (x, y) in f5.CLAMP_PTS:
        sx = 1 if x > 0 else -1
        ax.add_patch(Rectangle((min(x - 6 * sx, sx * reach), y - 6), abs(sx * reach - (x - 6 * sx)), 12,
                               facecolor=ORANGE, edgecolor="#a54f17", lw=0.6, alpha=0.9))
    dim(ax, (-f5.STUD_CC / 2, 190), (f5.STUD_CC / 2, 190), 205, f"studs {f5.STUD_CC:.0f} c/c")
    sf = f5.STUD_CC / 2 - f5.STUD_W / 2
    dim(ax, (-sf, -150), (sf, -150), -168, f"clear between studs {2 * sf:.0f}")
    dim(ax, (-f5.HOLE_X / 2, f5.HOLE_Y / 2), (f5.HOLE_X / 2, f5.HOLE_Y / 2), f5.HOLE_Y / 2 + 16, f"cut-out {f5.HOLE_X:.1f}")
    dim(ax, (f5.HOLE_X / 2, -f5.HOLE_Y / 2), (f5.HOLE_X / 2, f5.HOLE_Y / 2), f5.HOLE_X / 2 + 8, f"{f5.HOLE_Y:.1f}", horiz=False)
    dim(ax, (reach, -45), (sf, -45), -64, f"{sf - reach:.0f} spare", fs=9)
    ax.text(0, 0, "CENTRE BETWEEN THE STUDS\n(within ±%.0f mm)" % (sf - reach), ha="center", va="center", fontsize=12, weight="bold", color=INK)
    ax.text(-f5.STUD_CC / 2 - 20, -222, f"Orange bars = dog-ear arms swung out (reach ±{reach:.1f} mm).  "
            f"Stud width assumed {f5.STUD_W:.0f} mm (use {f5.STUD_CC/2 - 45/2 - reach:.0f} mm spare for 45 mm studs).",
            fontsize=9.5, color="#4a4d53")
    ax.set_xlim(-f5.STUD_CC / 2 - 40, f5.STUD_CC / 2 + 70); ax.set_ylim(-235, 225)
    save(f, "v51/sch_studs.png")

    # ---- magnet polarity
    f, ax = fig(10, 4.4)
    for i, (lab, x) in enumerate((("TRIM (back face)", 0), ("DECK POST", 70))):
        pass
    def mag(ax, x, y, top, col):
        ax.add_patch(Rectangle((x - 12, y), 24, 6, facecolor=col, edgecolor=INK, lw=0.8))
        ax.text(x, y + 3, top, ha="center", va="center", fontsize=10, weight="bold", color="white")
    ax.add_patch(Rectangle((-40, 20), 80, 8, facecolor=C["alu"], edgecolor="#6b6e74")); ax.text(-46, 24, "TRIM", ha="right", va="center", fontsize=10, weight="bold")
    mag(ax, 0, 14, "S", BLUE)
    ax.add_patch(Rectangle((-12, -22), 24, 28, facecolor=C["print"], edgecolor=INK)); ax.text(-46, -8, "DECK POST", ha="right", va="center", fontsize=10, weight="bold")
    mag(ax, 0, 0, "N", ORANGE)
    ax.annotate("", xy=(0, 12.5), xytext=(0, 7.5), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
    ax.text(30, 10, "faces ATTRACT", fontsize=10, va="center")
    ax.text(70, 28, "1  Stack all 16 magnets into one column.\n2  Slide each off and dot its TOP face with a marker.\n"
            "3  TRIM: dot face UP, into the pocket (toward the room).\n4  DECK: dot face UP, exposed (toward the room).\n"
            "    All 16 face the same way, so each pair attracts.\n"
            "5  Test each pair before the glue sets: the trim must snap on.", fontsize=10, va="top", linespacing=1.6)
    ax.set_xlim(-110, 250); ax.set_ylim(-30, 40)
    save(f, "v51/sch_polarity.png")


if __name__ == "__main__":
    which = sys.argv[1:] or ["v41", "v51"]
    if "v41" in which:
        v41()
    if "v51" in which:
        v51()

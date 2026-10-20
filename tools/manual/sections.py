"""Cross-section schematics (1:1 cuts through the CAD) and the wiring diagram."""
import sys
sys.path[:0] = ["../../previous-releases/float-v4.1", "../../previous-releases/flush-v5.1"]
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import mr
from mr import BG

INK, BLUE, ORANGE, GREY = "#1c1d20", "#2f6db5", "#e8752a", "#8a8d93"
LIGHTPLUG = (0.72, 0.72, 0.72)


def wiring(path, flush):
    f = plt.figure(figsize=(14, 3.4), dpi=150); f.patch.set_facecolor(BG)
    ax = f.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    steps = [("PoE+ SWITCH PORT", "802.3at (PoE+)\n25.5 W per port"),
             ("Cat6 CABLE", "run inside\nthe wall cavity"),
             ("PoE+ to USB-C ADAPTER", "PoE Texas / Heckler T515\n" + ("zip-tied in the back box" if flush else "in the wall cavity,\nbehind the bracket")),
             ("USB-C CABLE", "standard straight plug,\nhidden in the frame"),
             ("iPad Pro 12.9\"", "3rd gen\npower + 100 Mbps Ethernet")]
    W, H, gap, x = 236, 118, 50, 20
    for i, (t, sub) in enumerate(steps):
        col = ORANGE if i == 2 else (INK if i in (0, 4) else GREY)
        ax.add_patch(FancyBboxPatch((x + 10, -H / 2 + 10), W - 20, H - 20, boxstyle="round,pad=10",
                                    facecolor="white", edgecolor=col, lw=2.2))
        ax.text(x + W / 2, 24, t, ha="center", va="center", fontsize=15, weight="bold", color=INK)
        ax.text(x + W / 2, -16, sub, ha="center", va="center", fontsize=13, color="#4a4d53", linespacing=1.4)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + W + 4, 0), (x + W + gap - 4, 0), arrowstyle="-|>", mutation_scale=20, color=BLUE, lw=2.4))
        x += W + gap
    ax.set_xlim(0, x - gap + 20); ax.set_ylim(-66, 66)
    f.savefig(path, facecolor=BG); plt.close(f); print("saved", path, flush=True)


def v41():
    import hybrid as h
    S = h.STANDOFF
    wall = h.box(-400, 400, -300, 300, -10, 0)
    cxp = h.IPAD_L / 2 + h.PLUG_L + h.BEND_R / 2
    cable = (h.zcyl(cxp, 0, h.CABLE_D / 2, 8.0, S + h.EDGE_Z)
             .union(cq.Workplane("YZ").circle(h.CABLE_D / 2).extrude(cxp - 40).translate((40, 0, 8.0))))
    zb = h.EDGE_Z + S
    items = [(wall, "wall"), (h.br, "print2"), (h.car_a, "print"), (h.ipad, "ipad"), (h.shell_a, "alu"),
             (cable, "plug"), (h.plug, LIGHTPLUG)]
    labels = [("6061 SHELL", (160, S + h.SHELL_H - 1), (166, 33)),
              ("iPad Pro", (112, S + h.CB + 3), (118, 33)),
              ("USB-C plug (straight)", (h.IPAD_L / 2 + 9, zb), (184, 20)),
              ("PRINTED CARRIER", (125, S + 1.5), (164, 10)),
              ("cable runs in the 14 mm shadow gap", (100, 8), (104, 4.5)),
              ("WALL BRACKET", (74, 1.5), (80, -13)),
              ("PLASTERBOARD", (128, -5), (134, -13))]
    mr.section("v41/sch_section_usb.png", items, origin=(0, 1.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
               labels=labels, xlim=(62, 232), ylim=(-17, 40), w_in=14, title="SECTION THROUGH THE USB-C END   (1:1)")

    for tag, dy in (("offered", 10.0), ("hung", 0.0)):
        mv = lambda p: p.translate((0, dy, 0))
        items = [(wall, "wall"), (h.br, "print2"), (mv(h.car_a), "print"), (mv(h.hanger_a), "active"),
                 (mv(h.ipad), "ipad"), (mv(h.shell_a), "alu")]
        if tag == "hung":
            labels = [("CATCH RAIL", (8.0, h.HOOK_Y + 4), (-13, h.HOOK_Y + 22)),
                      ("HANGER FOOT", (4.8, h.HOOK_Y + 3), (-13, h.HOOK_Y + 10)),
                      ("WALL BRACKET", (1.5, h.HOOK_Y - 15), (-13, h.HOOK_Y - 15))]
            title = "2  SLIDE DOWN ONTO THE RAIL"
        else:
            labels = [("foot clears the rail", (4.8, h.HOOK_Y + 3 + dy), (-13, h.HOOK_Y + 24)),
                      ("CATCH RAIL", (8.0, h.HOOK_Y + 4), (-13, h.HOOK_Y + 2))]
            title = "1  HOLD 10 mm HIGH, PUSH FLAT"
        mr.section(f"v41/sch_hook_{tag}.png", items, origin=(8, 0, 0), normal=(1, 0, 0), u_axis=(0, 0, 1), v_axis=(0, 1, 0),
                   labels=labels, xlim=(-52, 30), ylim=(h.HOOK_Y - 24, h.HOOK_Y + 40), w_in=7, title=title)

    scr = (cq.Workplane("XZ").circle(1.5).extrude(-14).translate((0, h.LOCK_Y - 1, h.LOCK_Z + S))
           .union(cq.Workplane("XZ").circle(2.75).extrude(-3).translate((0, h.LOCK_Y - 4, h.LOCK_Z + S))))
    items = [(wall, "wall"), (h.br, "print2"), (h.car_a, "print"), (h.lock_a, "print2"), (h.ipad, "ipad"),
             (h.shell_a, "alu"), (scr, "hw")]
    labels = [("M3 x 12 LOCK SCREW, driven up from below", (h.LOCK_Z + S, h.LOCK_Y - 3), (-13, h.LOCK_Y - 12)),
              ("heat-set insert in the LOCK BOSS", (h.LOCK_Z + S, h.LOCK_Y + 12), (-13, h.LOCK_Y + 30)),
              ("LOCK BLOCK on the bracket", (6, h.LOCK_Y + 4), (-13, h.LOCK_Y + 9))]
    mr.section("v41/sch_lock.png", items, origin=(0.6, 0, 0), normal=(1, 0, 0), u_axis=(0, 0, 1), v_axis=(0, 1, 0),
               labels=labels, xlim=(-88, 34), ylim=(h.LOCK_Y - 22, h.LOCK_Y + 42), w_in=10, title="LOCK SCREW (section)")
    wiring("v41/sch_wiring.png", flush=False)


def v51():
    import flush51 as f
    cx = f.IPAD_L / 2 + f.PLUG_L + f.BEND_R / 2
    cable = (f.zcyl(cx, 0, f.CABLE_D / 2, -40.0, f.EDGE_Z)
             .union(cq.Workplane("YZ").circle(f.CABLE_D / 2).extrude(cx - 60).translate((60, 0, -40.0))))
    items = [(f.plaster, "wall"), (f.studs, "stud"), (f.sleeve, "print"), (f.deck, "print2"), (f.back, "print"),
             (f.ipad, "ipad"), (f.trim, "alu"), (cable, "plug"), (f.plug, LIGHTPLUG)]
    labels = [("6061 TRIM on magnets", (166, f.Z_F + 2.5), (184, 9)),
              ("iPad glass, level with the wall face", (118, f.GLASS_Z - 0.6), (124, 9)),
              ("USB-C plug", (f.IPAD_L / 2 + 9, f.EDGE_Z), (184, 2.5)),
              ("DECK on 45° ledges", (126, f.DECK_Z0 + 1.5), (130, -20)),
              ("cable dives back into the box", (cx, -30), (128, -31)),
              ("SLEEVE wall", (f.BOX_X / 2 - 1, -46), (180, -46)),
              ("BACK PLATE", (110, -f.SLEEVE_D - 1.2), (114, -48)),
              ("PLASTERBOARD", (186, -5), (182, -15)),
              ("STUD", (222, -40), (250, -40))]
    mr.section("v51/sch_section_usb.png", items, origin=(0, 1.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
               labels=labels, xlim=(88, 272), ylim=(-64, 16), w_in=14, title="SECTION THROUGH THE USB-C END   (1:1)")

    x0 = [x for (x, y) in f.CLAMP_PTS if x > 0 and y > 0][0]
    scr = f.zcyl(x0, 45, 2.0, f.ARM_Z0 - 2, f.Z_F - 3).union(f.zcyl(x0, 45, 3.75, f.Z_F - 3, f.Z_F - 0.2))
    arm_ = [a for a, (x, y) in zip(f.arms, f.CLAMP_PTS) if x > 0 and y > 0][0]
    items = [(f.plaster, "wall"), (f.studs, "stud"), (f.sleeve, "print"), (f.deck, "print2"), (f.back, "print"),
             (f.trim, "alu"), (arm_, "active"), (scr, "hw")]
    labels = [("M4 x 30 screw, driven from the front", (x0, f.Z_F - 1.5), (186, 11)),
              ("SLEEVE FLANGE on the wall face", (f.BOX_X / 2 + 3, 0.7), (250, 5)),
              ("plasterboard clamped here", (f.HOLE_X / 2 + 4, -5), (250, -5)),
              ("deck post", (x0 - 4.5, -3), (133, -22)),
              ("DOG-EAR ARM pulls forward", (x0 + 14, f.ARM_Z0 + 3), (250, -22)),
              ("arm slot in the sleeve end wall", (f.BOX_X / 2 - 1, -30), (250, -36))]
    mr.section("v51/sch_clamp.png", items, origin=(0, 45.0, 0), normal=(0, 1, 0), u_axis=(1, 0, 0), v_axis=(0, 0, 1),
               labels=labels, xlim=(116, 330), ylim=(-62, 17), w_in=14, title="DOG-EAR CLAMP   (section through one arm, 1:1)")
    wiring("v51/sch_wiring.png", flush=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["v41", "v51"]
    if "v41" in which:
        v41()
    if "v51" in which:
        v51()

"""
Bambu Studio 3MFs for the fully printed v6 builds of one tablet (Float + Flush).

    python make3mf6.py <tablet_key> <float_out> <flush_out> <printed_out> <dest_dir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make3mf import build, load, FACE, LIGHT, MID, BRACKET, STRONG, SOLID  # noqa: E402
import tablets  # noqa: E402

key, fo, fl, po, dest = sys.argv[1:6]
name = tablets.TABLETS[key]["name"].replace("″", "in")
FP, LP = f"{fo}/print", f"{fl}/print"
PF, PL = f"{po}/float/print", f"{po}/flush/print"

flt = [
    ("Face · shell left (face down)", [("shell_print_L", load(f"{PF}/shell_print_L.stl"), 2, FACE)]),
    ("Face · shell right (face down)", [("shell_print_R", load(f"{PF}/shell_print_R.stl"), 2, FACE)]),
    ("Carrier · top quarters", [("carrier_TL", load(f"{FP}/carrier_TL.stl"), 1, LIGHT),
                                ("carrier_TR", load(f"{FP}/carrier_TR.stl"), 1, LIGHT)]),
    ("Carrier · bottom quarters", [("carrier_BL", load(f"{FP}/carrier_BL.stl"), 1, LIGHT),
                                   ("carrier_BR", load(f"{FP}/carrier_BR.stl"), 1, LIGHT)]),
    ("Bracket, hanger, lock boss, catch rail", [("wall_bracket", load(f"{FP}/wall_bracket.stl"), 1, BRACKET),
                                                 ("hanger", load(f"{FP}/hanger.stl"), 1, STRONG),
                                                 ("lock_boss", load(f"{FP}/lock_boss.stl"), 1, STRONG),
                                                 ("catch_rail", load(f"{FP}/catch_rail.stl"), 1, STRONG)]),
]
fls = [
    ("Face · trim left (face down)", [("trim_print_L", load(f"{PL}/trim_print_L.stl"), 2, FACE)]),
    ("Face · trim right (face down)", [("trim_print_R", load(f"{PL}/trim_print_R.stl"), 2, FACE)]),
    ("Sleeve left (flange down)", [("sleeve_L", load(f"{LP}/sleeve_L.stl"), 1, LIGHT)]),
    ("Sleeve right (flange down)", [("sleeve_R", load(f"{LP}/sleeve_R.stl"), 1, LIGHT)]),
    ("Deck left", [("deck_L", load(f"{LP}/deck_L.stl"), 1, MID)]),
    ("Deck right", [("deck_R", load(f"{LP}/deck_R.stl"), 1, MID)]),
    ("Back plate left", [("back_plate_L", load(f"{LP}/back_plate_L.stl"), 1, MID)]),
    ("Back plate right + 4 dog-ear arms", [("back_plate_R", load(f"{LP}/back_plate_R.stl"), 1, MID)] +
     [(f"dog_ear_arm_{i}", load(f"{LP}/dog_ear_arm_x4.stl"), 1, SOLID) for i in (1, 2, 3, 4)]),
]
os.makedirs(dest, exist_ok=True)
tag = key.replace("ipad_", "").replace("_", "-")
a = build(f"{dest}/Float_Mount_v6_{tag}_Float_Printed.3mf", f"Float Mount v6 Float · {name} (fully printed)",
          f"Surface PoE wall mount for {name}. Filament 1: hidden parts. Filament 2: the visible face, "
          "printed face-down on a textured plate. PETG or ASA.", flt, f"{dest}/_thumbs_f_{tag}")
b = build(f"{dest}/Float_Mount_v6_{tag}_Flush_Printed.3mf", f"Float Mount v6 Flush · {name} (fully printed)",
          f"Flush in-wall PoE mount for {name}. Filament 1: hidden parts. Filament 2: the visible trim, "
          "printed face-down on a textured plate. PETG or ASA.", fls, f"{dest}/_thumbs_l_{tag}")
print(key, len(a), len(b))

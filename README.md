# iPad PoE Wall Mount · v6

Turn an iPad into a permanently powered HomeKit / Home Assistant wall panel, running on a single Cat6 cable (PoE+) with the cable completely hidden. There are two mounts, and each comes with a machined 6061 aluminium face or fully 3D-printed:

| **Float**: surface mount | **Flush**: in-wall |
|---|---|
| ![Float Mount on a wall](manuals/float/images/hero.png) | ![Flush Mount in a plasterboard wall](manuals/flush/images/hero.png) |
| Floats 14 mm off the wall on a shadow gap. Needs only a small cut-out behind the panel for the cable. | The glass sits 1.2 mm off the wall and the trim stands 4.5 mm proud. Fits a cut-out between studs in existing plasterboard. |
| Hangs on a wall bracket between two end stops, locked by one hidden M3 screw | Four dog-ear arms clamp the plasterboard; the trim is held on by magnets |
| 📘 [**Build manual (PDF)**](manuals/float/Float_Mount_v6_Build_Manual.pdf) · [web version](manuals/float/BUILD_MANUAL.md) | 📘 [**Build manual (PDF)**](manuals/flush/Float_Mount_v6_Flush_Build_Manual.pdf) · [web version](manuals/flush/BUILD_MANUAL.md) |

Supported iPads:

- **iPad Pro 12.9″** (3rd gen: A1876, A1895, A2014, A1983)
- **iPad Pro 13″** (M5, 2025)
- **iPad Pro 11″** (M5, 2025)
- **iPad mini** (A17 Pro, 2024)

## Start here

1. **Pick a mount:** Float (on the wall) or Flush (in the wall).
2. **Pick your iPad:** each one has its own folder below.
3. **Pick machined or printed:** the `machined/` build has an aluminium face you order from a CNC service or cut yourself. The `printed/` build prints everything, including the face, from a ready-made Bambu Studio project.
4. **Follow the manual for your mount.** One manual covers all four iPads. The steps are drawn on the 12.9″, and anything that differs between models is called out in a **BY MODEL** box.

| iPad | Float, machined | Float, printed | Flush, machined | Flush, printed | Flush wall template |
|---|---|---|---|---|---|
| **Pro 12.9″** (3rd gen) | [files](ipad_pro_12_9_gen3/float/machined/) · [CNC drawing](ipad_pro_12_9_gen3/float/machined/machine/shell_6061_drawing.pdf) | [3MF](ipad_pro_12_9_gen3/float/printed/Float_Mount_v6_pro-12-9-gen3_Float_Printed.3mf) · [files](ipad_pro_12_9_gen3/float/printed/) | [files](ipad_pro_12_9_gen3/flush/machined/) | [3MF](ipad_pro_12_9_gen3/flush/printed/Float_Mount_v6_pro-12-9-gen3_Flush_Printed.3mf) · [files](ipad_pro_12_9_gen3/flush/printed/) | [A3 PDF](ipad_pro_12_9_gen3/flush/machined/CUTOUT_TEMPLATE_A3.pdf) |
| **Pro 13″** (M5) | [files](ipad_pro_13_m5/float/machined/) · [CNC drawing](ipad_pro_13_m5/float/machined/machine/shell_6061_drawing.pdf) | [3MF](ipad_pro_13_m5/float/printed/Float_Mount_v6_pro-13-m5_Float_Printed.3mf) · [files](ipad_pro_13_m5/float/printed/) | [files](ipad_pro_13_m5/flush/machined/) | [3MF](ipad_pro_13_m5/flush/printed/Float_Mount_v6_pro-13-m5_Flush_Printed.3mf) · [files](ipad_pro_13_m5/flush/printed/) | [A3 PDF](ipad_pro_13_m5/flush/machined/CUTOUT_TEMPLATE_A3.pdf) |
| **Pro 11″** (M5) | [files](ipad_pro_11_m5/float/machined/) · [CNC drawing](ipad_pro_11_m5/float/machined/machine/shell_6061_drawing.pdf) | [3MF](ipad_pro_11_m5/float/printed/Float_Mount_v6_pro-11-m5_Float_Printed.3mf) · [files](ipad_pro_11_m5/float/printed/) | [files](ipad_pro_11_m5/flush/machined/) | [3MF](ipad_pro_11_m5/flush/printed/Float_Mount_v6_pro-11-m5_Flush_Printed.3mf) · [files](ipad_pro_11_m5/flush/printed/) | [A3 PDF](ipad_pro_11_m5/flush/machined/CUTOUT_TEMPLATE_A3.pdf) |
| **mini** (A17 Pro) | [files](ipad_mini_a17_pro/float/machined/) · [CNC drawing](ipad_mini_a17_pro/float/machined/machine/shell_6061_drawing.pdf) | [3MF](ipad_mini_a17_pro/float/printed/Float_Mount_v6_mini-a17-pro_Float_Printed.3mf) · [files](ipad_mini_a17_pro/float/printed/) | [files](ipad_mini_a17_pro/flush/machined/) | [3MF](ipad_mini_a17_pro/flush/printed/Float_Mount_v6_mini-a17-pro_Flush_Printed.3mf) · [files](ipad_mini_a17_pro/flush/printed/) | [A3 PDF](ipad_mini_a17_pro/flush/machined/CUTOUT_TEMPLATE_A3.pdf) |

> [!IMPORTANT]
> **Building for the 12.9″?** Apple publishes no drawing for that model, so its button positions are estimates. Before you print, measure yours (see [Check the 12.9″ buttons](#check-the-129-buttons)).

## What you need

- A **PoE+ (802.3at)** switch port and a Cat6 run to the wall
- A **PoE+ to USB-C adapter**, e.g. PoE Texas / Heckler T515 (25 W)
- A **standard straight USB-C cable**. The frame is sized for a 17 × 12.5 × 7 mm plug overmold.
- **PETG or ASA** filament (not PLA) and a 256 mm bed. Nothing needs supports.
- For a machined face: 6061 plate (Float 12 mm, or 15 mm for the mini; Flush 3 mm), or a CNC service such as JLCCNC
- Hardware: M3 / M2.5 screws, M3 and M4 heat-set inserts and, for the Flush, N52 10 × 1.5 mm magnets. Each assembly folder's `hardware.txt` lists exactly what that build needs, and the manuals list it step by step.

## What's new in v6

- **The buttons are left alone.** Every button has a 1.2 mm relief pocket. v4.2 pressed the 12.9″'s volume buttons.
- **There's room for the cable loop.** Each end is 2 mm longer, so the USB-C cable can bend back round the plug. Panels are 4 mm longer overall.
- **The Float can't slide sideways.** The wall rail has end stops with 0.4 mm clearance each side of the hanger.
- **Four iPads.** One set of parametric sources builds every model, from Apple's dimensional drawings for the M5 iPads and the mini.
- **The tapped holes are drill-safe on every model.** The shell bosses follow each iPad's thickness, so there is always 1.45 mm of metal under each drill point.
- **All the hardware is in the STEP files.** Every screw, insert, nut, magnet and pin is modelled in place and named by size and standard, e.g. `hw_M3x5_cap_ISO4762_3`. A clash check confirms that every part fits its hole and touches nothing it shouldn't.

## Per-model summary

| (mm) | 12.9″ (3rd gen) | 13″ M5 | 11″ M5 | mini A17 Pro |
|---|---|---|---|---|
| **Float** panel | 348.1 × 238.9 × 11.7 | 349.1 × 239.5 × 10.9 | 317.2 × 201.5 × 11.1 | 262.9 × 158.8 × 12.1 |
| Shell mass (6061) | 231 g | 227 g | 196 g | 161 g |
| Depth off the wall | 25.7 | 24.9 | 25.1 | 26.1 |
| Shell screws (8 × M3 × 5 + 8 × M2.5 × 5) | socket cap (ISO 4762) | **button head (ISO 7380)** | **button head (ISO 7380)** | socket cap (ISO 4762) |
| Wall bracket | 200 × 200, AU wall-plate holes | 200 × 200.6, AU holes | 200 × 162.6, AU holes | 200 × 119.8, anchors only |
| **Flush** trim (3 mm) | 359.1 × 233.6 | 360.1 × 234.2 | 328.2 × 196.2 | 273.9 × 153.4 |
| Plasterboard cut-out | 347.1 × 221.6 | 348.1 × 222.2 | 316.2 × 184.2 | 261.9 × 141.4 |
| Max off-centre between studs (450 c/c) | 19 | 19 | 35 | 62 |
| Magnet pairs | 8 | 8 | 4 | 4 |

The Flush box goes 57.5 mm deep from the wall face on every model. The M5 iPads are thinner, which leaves only 2.2–2.4 mm under each shell screw head. That is why they use button heads: a 3 mm cap head would stand proud and rock the panel on its bracket.

## Check the 12.9″ buttons

Hold the iPad in landscape with USB-C on the right, and measure from the top-left corner:

- the start and end of the volume buttons along the top edge (v6 leaves them clear from **8 to 48 mm**), and
- the start and end of the top button down the left end (clear from **8 to 36 mm**).

If either one falls outside its range, change `buttons` in `_g3()` in [`src/tablets.py`](src/tablets.py) and regenerate (see [Customising and regenerating](#customising-and-regenerating)).

## Ordering the Float shell (JLCCNC)

Upload your iPad's `float/machined/machine/shell_6061.step` together with `shell_6061_drawing.pdf`. The drawing has the hole table (A1–A8 M3, B1–B8 M2.5) and a section through a boss, so the shop knows what to tap. Choose 6061-T6, bead blast + anodise, threads per drawing.

## Fully printed builds

Each `printed/` 3MF opens in Bambu Studio with every part on its own plate. Filament 2 is the visible face, so you can choose its colour. Per-part walls and infill are already set, and nothing needs supports. The face prints face-down in two dovetailed halves: on the 12.9″ and mini the seam is on the centreline, and on the M5s it sits just right of the camera notch. Printer, process and filament presets aren't embedded, so pick your own printer, PETG or ASA, and a Textured PEI plate. Each `print/one_piece/` folder has the split parts uncut, for large-bed printers.

## Repository layout

```
manuals/float/, manuals/flush/   build manuals: PDF, web version (BUILD_MANUAL.md), images
ipad_pro_12_9_gen3/              one folder per iPad, each with four builds:
ipad_pro_13_m5/                    float/machined/   aluminium shell (STEP + CNC drawing) + printed parts
ipad_pro_11_m5/                    float/printed/    everything printed: Bambu Studio 3MF + STL/STEP
ipad_mini_a17_pro/                 flush/machined/   aluminium trim (STEP) + printed parts + A3 template
                                   flush/printed/    everything printed: 3MF + STL/STEP + A3 template
                                 each with assembly_*.step (all hardware), hardware.txt and checks.txt
src/                             the parametric CadQuery sources that generate every file
tools/manual/                    scripts that render the manual images
overhang_audit.txt               overhang check of every printed part, for every iPad
previous-releases/               Float v4.1 / v4.2, Flush v5.1 (12.9″ only, superseded)
```

## Customising and regenerating

Every size comes from the sources in [`src/`](src/): `tablets.py` describes each iPad, and `float6.py` / `flush6.py` hold the mount parameters (plug size, clearances, wall thickness). Change a number and regenerate:

```bash
pip install cadquery trimesh vtk shapely matplotlib
cd src
export V6_TABLET=ipad_pro_11_m5          # or ipad_pro_12_9_gen3, ipad_pro_13_m5, ipad_mini_a17_pro
python float6.py out/float               # Float parts + assembly + checks.txt
python drawing6.py out/float/machine/shell_6061_drawing.pdf
python flush6.py out/flush               # Flush parts + assembly + checks.txt
python template6.py out/flush/CUTOUT_TEMPLATE_A3.pdf
python printed6.py out/printed           # printed faces (halves + one piece) + printed assemblies
python make3mf6.py $V6_TABLET out/float out/flush out/printed out/3mf
python audit_all.py out                  # overhang audit
```

Each `checks.txt` ends in `RESULT: ALL CHECKS PASS` or lists what clashes. To add another iPad, add it to `tablets.py` with its size, corner radius, cameras, speakers, mics and buttons. The generators then place the bosses, magnets, pins and clamps clear of its openings.

## Previous releases

[`previous-releases/`](previous-releases/) keeps Float v4.1 and v4.2, Flush v5.1 and their fully printed versions, with their manuals. They are for the iPad Pro 12.9″ only and are superseded by v6. Use v6 for any new build.

## Notes

- The M5 and mini features come from Apple's Accessory Design Guidelines; the 12.9″'s are close estimates. Print a test fit before you machine metal or cut a wall.
- The physical buttons end up covered, so use AssistiveTouch, Siri or Settings › Shut Down. On the mini the Touch ID button is covered too, so unlock with the passcode.
- The build manuals follow the style of the free [Flightory](https://flightory.com) RC plane manuals.

## Licence

[GPL-3.0](LICENSE)

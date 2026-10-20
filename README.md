# iPad PoE Wall Mount (v6)

Turns an iPad into a permanently powered HomeKit / Home Assistant panel over a single Cat6 cable (PoE+), with the cable fully hidden. There are two mounts, each machined (6061 aluminium face) or fully 3D-printed, for four iPads:

- **iPad Pro 12.9″** (3rd gen: A1876, A1895, A2014, A1983)
- **iPad Pro 13″** (M5, 2025)
- **iPad Pro 11″** (M5, 2025)
- **iPad mini** (A17 Pro, 2024)

| | **Float** (surface mount) | **Flush** (in-wall) |
|---|---|---|
| | ![Float Mount](manuals/float/images/hero.png) | ![Flush Mount](manuals/flush/images/hero.png) |
| Look | Floats 14 mm off the wall on a shadow gap | Glass 1.2 mm off the wall, trim 4.5 mm proud |
| Wall work | One small cut-out behind the panel for the cable | A cut-out between studs (10 mm plasterboard, studs at 450 c/c) |
| Fixing | Bracket + hook between end stops + one hidden M3 lock screw | 4 dog-ear arms clamp the plasterboard; magnetic trim |
| Build manual (PDF) | [Float_Mount_v6_Build_Manual.pdf](manuals/float/Float_Mount_v6_Build_Manual.pdf) | [Float_Mount_v6_Flush_Build_Manual.pdf](manuals/flush/Float_Mount_v6_Flush_Build_Manual.pdf) |
| Build manual (web) | [BUILD_MANUAL.md](manuals/float/BUILD_MANUAL.md) | [BUILD_MANUAL.md](manuals/flush/BUILD_MANUAL.md) |

One manual per mount covers all four iPads. The steps are drawn on the 12.9″, and every difference between models is called out in a **BY MODEL** box. Both mounts use a **standard straight USB-C cable**, a PoE+ to USB-C adapter (e.g. PoE Texas / Heckler T515), and print with **no supports** on a 256 mm bed in PETG or ASA.

## Repository layout

```
README.md                  this page
manuals/float/             Float build manual: PDF, BUILD_MANUAL.md, images/
manuals/flush/             Flush build manual: PDF, BUILD_MANUAL.md, images/
ipad_pro_12_9_gen3/        one folder per iPad, each with four builds (below)
ipad_pro_13_m5/
ipad_pro_11_m5/
ipad_mini_a17_pro/
src/                       parametric CadQuery sources that generate every file
  tablets.py               the four iPads: size, cameras, speakers, mics, buttons
  float6.py · flush6.py    the two mounts (+ checks.txt clash tests)
  printed6.py              printed faces (halves + one-piece)
  drawing6.py              JLCCNC drawing for the Float shell
  template6.py             A3 cut-out template for the Flush
  hardware6.py             screws, inserts, nuts, magnets, pins for the STEP assemblies
  make3mf6.py · make3mf.py Bambu Studio projects
  overhang_audit.py · audit_all.py · render6.py
tools/manual/              scripts that render the manual images (VTK + matplotlib)
overhang_audit.txt         overhang audit of every printed part, every iPad
previous-releases/         Float v4.1 / v4.2, Flush v5.1 and their fully printed versions (12.9″ only)
```

## The iPads

| Folder | iPad | Size (mm) | Source of the dimensions |
|---|---|---|---|
| [`ipad_pro_12_9_gen3/`](ipad_pro_12_9_gen3/) | iPad Pro 12.9″ (3rd gen: A1876, A1895, A2014, A1983) | 280.6 × 214.9 × 5.9 | v4.2 / v5.1 values. **Button positions are estimates** (see below) |
| [`ipad_pro_13_m5/`](ipad_pro_13_m5/) | iPad Pro 13″ (M5, 2025) | 281.58 × 215.53 × 5.125 | Apple Accessory Design Guidelines |
| [`ipad_pro_11_m5/`](ipad_pro_11_m5/) | iPad Pro 11″ (M5, 2025) | 249.70 × 177.51 × 5.288 | Apple Accessory Design Guidelines |
| [`ipad_mini_a17_pro/`](ipad_mini_a17_pro/) | iPad mini (A17 Pro, 2024) | 195.43 × 134.75 × 6.32 | Apple Accessory Design Guidelines |

Each iPad folder holds four builds, with machined and printed kept apart:

```
<ipad>/
  float/machined/   aluminium shell (STEP + JLCCNC drawing) + printed carrier, hanger, lock, bracket, rail
                    assembly_float6.step (with all hardware) · hardware.txt · checks.txt
  float/printed/    the same mount with a printed face: Bambu Studio 3MF + STLs
                    assembly_float6_printed.step · hardware.txt
  flush/machined/   aluminium trim (STEP) + printed sleeve, deck, back plate, arms + A3 cut-out template
                    assembly_flush6.step (with all hardware) · hardware.txt · checks.txt
  flush/printed/    the same mount with a printed trim: Bambu Studio 3MF + STLs + A3 cut-out template
                    assembly_flush6_printed.step · hardware.txt
  printed_checks.txt
```

Every `print/` folder also has a `one_piece/` subfolder with the split parts uncut (carrier, sleeve, deck, back plate and printed faces), for large-bed printers.

## What changed from v4.2 / v5.1 ([previous releases](previous-releases/))

1. **Volume buttons no longer pressed.** The carrier (Float) and the sleeve wall (Flush) now have a relief pocket at every button: 1.2 mm deep into the wall, running the button's length plus a margin at each end. On the 12.9″ the volume relief runs 8 to 48 mm from the top-left corner along the top edge, and the top-button relief 8 to 36 mm down the left end. These are generous because v4.2 pressed the buttons and Apple publishes no drawing for that model.
2. **2 mm more room for the USB-C loop at each end.** The plug cavity is 2 mm longer, so the cable can bend back around the plug. The frame ends are 2 mm wider to match, so each mount is **4 mm longer overall** than v4.2 / v5.1. Both ends grow so the face stays symmetric.
3. **Lateral stops on the Float hook.** The catch rail on the wall bracket now has an end cheek at each side, rising 12 mm above the lip. The hanger drops between them with 0.4 mm clearance each side, so the carrier can no longer slide left or right on the wall. In the model, shifting the hanger 0.5 mm either way runs it into a cheek.
4. **Thinner iPads, same safe holes.** The shell's boss height now tracks the iPad's thickness, so every tapped hole keeps a **1.45 mm (M3) / 1.58 mm (M2.5) skin** under the drill point on all four models.
5. **Every screw, insert, nut, magnet and pin is in the STEP assemblies** (`hardware6.py`): 42 parts in the Float, 42 in the Flush (34 on the 11″ and mini, which have 4 magnet pairs). Each is named by size and standard, e.g. `hw_M3x5_cap_ISO4762_3`, and `hardware.txt` beside each assembly is its bill of materials. The build checks that no head, nut, magnet or pin touches a part it shouldn't, and that every thread and insert bites into its own part. That check found a real fault in the Flush for the 11″ and mini (a locating pin hole under a clamp post), now fixed.
6. **iPad Pro M5 front camera on the long edge.** The camera slot moves to the top bar. The printed face's seam moves 3 mm past it, and the inner top/bottom bosses move out to clear the seam keys.

Each model's speaker, mic and button openings come from Apple's drawings (the 12.9″ from v4.2), and they set where the bosses, magnets, pins and clamp arms go. `checks.txt` lists the positions chosen and every clash test.

## Per-model summary

| | 12.9″ (3rd gen) | 13″ M5 | 11″ M5 | mini A17 Pro |
|---|---|---|---|---|
| **Float** shell | 348.1 × 238.9 × 11.7 | 349.1 × 239.5 × 10.9 | 317.2 × 201.5 × 11.1 | 262.9 × 158.8 × 12.1 |
| Shell mass (6061) | 231 g | 227 g | 196 g | 161 g |
| Plate stock | 12 mm | 12 mm | 12 mm | 15 mm (or 12.7) |
| Off the wall | 25.7 | 24.9 | 25.1 | 26.1 |
| Shell screws | 8× M3 × 5 + 8× M2.5 × 5 socket cap (ISO 4762) | M3 × 5 / M2.5 × 5 **button head (ISO 7380)** | M3 × 5 / M2.5 × 5 **button head (ISO 7380)** | 8× M3 × 5 + 8× M2.5 × 5 socket cap (ISO 4762) |
| Wall bracket | 200 × 200, AU plate holes | 200 × 200.6, AU plate holes | 200 × 162.6, AU plate holes | 200 × 119.8, no AU holes (no room) |
| **Flush** trim | 359.1 × 233.6 × 3 | 360.1 × 234.2 × 3 | 328.2 × 196.2 × 3 | 273.9 × 153.4 × 3 |
| Trim mass (6061) | 196 g | 199 g | 169 g | 135 g |
| Plasterboard cut-out | 347.1 × 221.6 | 348.1 × 222.2 | 316.2 × 184.2 | 261.9 × 141.4 |
| Max off-centre between studs (450 c/c, 45 mm studs) | 19 mm | 19 mm | 35 mm | 62 mm |
| Magnets | 8 pairs | 8 pairs | 4 pairs | 4 pairs |

All sizes are in mm. Box depth is 57.5 mm from the wall face on every model.

**Why button heads on the M5s:** these iPads are about 0.6 mm thinner than the 12.9″, so the carrier is thinner too. The counterbore under each screw head is then only 2.2–2.4 mm deep, so a standard cap head (3 mm) would sit 0.6–0.8 mm proud of the carrier back and could rock the carrier on the bracket. ISO 7380 button heads (1.65 mm on M3, 1.3 mm on M2.5) sit below the surface. DIN 7984 low-head screws are hard to find in M2.5, so button heads are used for both sizes.

## Ordering the shell from JLCCNC (Float, machined)

Upload `float/machined/machine/shell_6061.step` together with `shell_6061_drawing.pdf`. The drawing is generated from the same parameters, with its own hole table (A1–A8 M3, B1–B8 M2.5) and section B–B. Choose 6061-T6, bead blast + anodise, and threads per drawing. JLCCNC quotes from the STEP and taps from the drawing.

## Fully printed builds

In each `printed/` folder, `Float_Mount_v6_<ipad>_Float_Printed.3mf` or `…_Flush_Printed.3mf` opens in Bambu Studio with every part on its plate: filament 2 for the face, per-part walls and infill set, no supports, 256 mm beds. The face halves are dovetailed. On the 12.9″ and the mini the seam is at the centre; on the M5s it is just right of the camera notch. The Float shell's pilot holes take the same screws without tapping.

Printer, process and filament presets are not embedded, so choose your own printer, PETG or ASA, and a Textured PEI plate.

## Before you print: check the 12.9″ buttons

Apple has not published a drawing for the 3rd-gen 12.9″. Hold your iPad in landscape with USB-C on the right and measure from the top-left corner:

- along the top edge, the start and end of the volume buttons, and
- down the left end, the start and end of the top button.

If either one falls outside the relief zones above, change `buttons` in `_g3()` in `src/tablets.py` and regenerate.

## Regenerating

```bash
pip install cadquery trimesh vtk shapely matplotlib
cd src
export V6_TABLET=ipad_pro_11_m5          # or ipad_pro_12_9_gen3, ipad_pro_13_m5, ipad_mini_a17_pro
python float6.py out/float               # shell, carrier, bracket… + checks.txt
python drawing6.py out/float/machine/shell_6061_drawing.pdf
python flush6.py out/flush               # trim, sleeve, deck, back plate, arms + checks.txt
python template6.py out/flush/CUTOUT_TEMPLATE_A3.pdf
python printed6.py out/printed           # printed shell + trim, halves and one-piece
python make3mf6.py $V6_TABLET out/float out/flush out/printed out/3mf
python audit_all.py out                  # overhang audit of every printed part → out/overhang_audit.txt
```

The manual images come from `tools/manual/render_v6.py` (`float`, `flush` or `fronts`), and the hardware in them is the same hardware the STEP assemblies carry.

[`overhang_audit.txt`](overhang_audit.txt) lists every printed part for every iPad. The only unsupported areas left are the Ø6 screw-counterbore ceilings in the Float carrier (small bridges) and first-layer countersink and chamfer edges.

To add another iPad, add an entry to `src/tablets.py`. Give its size, corner radius, camera, speakers, mics, buttons and rear camera keep-out, then run the commands above. The generators place the bosses, magnets, pins and clamps clear of the openings, and `checks.txt` ends in `RESULT: ALL CHECKS PASS` or lists what clashes.

## Previous releases

[`previous-releases/`](previous-releases/) keeps Float v4.1 and v4.2, Flush v5.1 and their fully printed versions, all for the iPad Pro 12.9″ only, with their manuals. v6 replaces them: it fixes the 12.9″'s pressed volume buttons and adds the room for the cable loop, so use v6 for any new build.

## Notes

- The M5 and mini features come from Apple's Accessory Design Guidelines drawings; the 12.9″'s are close estimates. Print a test fit before you machine metal or cut a wall.
- The physical buttons end up covered. Use AssistiveTouch, Siri or Settings › Shut Down.
- The build manuals follow the style of the free [Flightory](https://flightory.com) RC plane manuals.

## Licence

[GPL-3.0](LICENSE)

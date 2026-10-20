# v6: four iPads, Float + Flush, machined or fully printed

v6 builds both mounts for four iPads from one set of parametric sources:

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
  float/printed/    the same mount with a printed face: Bambu Studio 3MF + STLs
  flush/machined/   aluminium trim (STEP) + printed sleeve, deck, back plate, arms + A3 cut-out template
  flush/printed/    the same mount with a printed trim: Bambu Studio 3MF + STLs + A3 cut-out template
  printed_checks.txt
```

Every `print/` folder also has a `one_piece/` subfolder with the split parts uncut (carrier, sleeve, deck, back plate and printed faces), for large-bed printers.

## What changed from v4.2 / v5.1

1. **Volume buttons no longer pressed.** The carrier (Float) and the sleeve wall (Flush) now have a relief pocket at every button: 1.2 mm deep into the wall, running the button's length plus a margin at each end. On the 12.9″ the volume relief runs 8 to 48 mm from the top-left corner along the top edge, and the top-button relief 8 to 36 mm down the left end. These are generous because v4.2 pressed the buttons and Apple publishes no drawing for that model.
2. **2 mm more room for the USB-C loop at each end.** The plug cavity is 2 mm longer, so the cable can bend back around the plug. The frame ends are 2 mm wider to match, so each mount is **4 mm longer overall** than v4.2 / v5.1. Both ends grow so the face stays symmetric.
3. **Lateral stops on the Float hook.** The catch rail on the wall bracket now has an end cheek at each side, rising 12 mm above the lip. The hanger drops between them with 0.4 mm clearance each side, so the carrier can no longer slide left or right on the wall. In the model, shifting the hanger 0.5 mm either way runs it into a cheek.
4. **Thinner iPads, same safe holes.** The shell's boss height now tracks the iPad's thickness, so every tapped hole keeps a **1.45 mm (M3) / 1.58 mm (M2.5) skin** under the drill point on all four models.
5. **iPad Pro M5 front camera on the long edge.** The camera slot moves to the top bar. The printed face's seam moves 3 mm past it, and the inner top/bottom bosses move out to clear the seam keys.

Each model's speaker, mic and button openings come from Apple's drawings (the 12.9″ from v4.2), and they set where the bosses, magnets, pins and clamp arms go. `checks.txt` lists the positions chosen and every clash test.

## Per-model summary

| | 12.9″ (3rd gen) | 13″ M5 | 11″ M5 | mini A17 Pro |
|---|---|---|---|---|
| **Float** shell | 348.1 × 238.9 × 11.7 | 349.1 × 239.5 × 10.9 | 317.2 × 201.5 × 11.1 | 262.9 × 158.8 × 12.1 |
| Shell mass (6061) | 231 g | 227 g | 196 g | 161 g |
| Plate stock | 12 mm | 12 mm | 12 mm | 15 mm (or 12.7) |
| Off the wall | 25.7 | 24.9 | 25.1 | 26.1 |
| Shell screws | 8× M3 × 5 + 8× M2.5 × 5 cap | M3 × 5 / M2.5 × 5 **low-head (DIN 7984)** | M3 × 5 / M2.5 × 5 **low-head (DIN 7984)** | 8× M3 × 5 + 8× M2.5 × 5 cap |
| Wall bracket | 200 × 200, AU plate holes | 200 × 200.6, AU plate holes | 200 × 162.6, AU plate holes | 200 × 119.8, no AU holes (no room) |
| **Flush** trim | 359.1 × 233.6 × 3 | 360.1 × 234.2 × 3 | 328.2 × 196.2 × 3 | 273.9 × 153.4 × 3 |
| Trim mass (6061) | 196 g | 199 g | 169 g | 135 g |
| Plasterboard cut-out | 347.1 × 221.6 | 348.1 × 222.2 | 316.2 × 184.2 | 261.9 × 141.4 |
| Max off-centre between studs (450 c/c, 45 mm studs) | 19 mm | 19 mm | 35 mm | 62 mm |
| Magnets | 8 pairs | 8 pairs | 4 pairs | 4 pairs |

All sizes are in mm. Box depth is 57.5 mm from the wall face on every model.

**Why low-head screws on the M5s:** these iPads are about 0.6 mm thinner than the 12.9″, so the carrier is thinner too. The counterbore under each screw head is then only 2.2–2.4 mm deep, so a standard cap head (3 mm) would sit 0.6–0.8 mm proud of the carrier back and could rock the carrier on the bracket. DIN 7984 low-head cap screws (2 mm head) sit flush.

## Ordering the shell from JLCCNC (Float, machined)

Upload `float/machined/machine/shell_6061.step` together with `shell_6061_drawing.pdf`. The drawing is generated from the same parameters, with its own hole table (A1–A8 M3, B1–B8 M2.5) and section B–B. Choose 6061-T6, bead blast + anodise, and threads per drawing. JLCCNC quotes from the STEP and taps from the drawing.

## Fully printed builds

In each `printed/` folder, `Float_Mount_v6_<ipad>_Float_Printed.3mf` or `…_Flush_Printed.3mf` opens in Bambu Studio with every part on its plate: filament 2 for the face, per-part walls and infill set, no supports, 256 mm beds. The face halves are dovetailed. On the 12.9″ and the mini the seam is at the centre; on the M5s it is just right of the camera notch. The Float shell's pilot holes take the same screws without tapping.

Printer, process and filament presets are not embedded, so choose your own printer, PETG or ASA, and a Textured PEI plate.

## Before you print: check the 12.9″ buttons

Apple has not published a drawing for the 3rd-gen 12.9″. Hold your iPad in landscape with USB-C on the right and measure from the top-left corner:

- along the top edge, the start and end of the volume buttons, and
- down the left end, the start and end of the top button.

If either one falls outside the relief zones above, change `buttons` in `_g3()` in `tablets.py` and regenerate.

## Regenerating

```bash
pip install cadquery trimesh vtk shapely matplotlib
export V6_TABLET=ipad_pro_11_m5          # or ipad_pro_12_9_gen3, ipad_pro_13_m5, ipad_mini_a17_pro
python float6.py out/float               # shell, carrier, bracket… + checks.txt
python drawing6.py out/float/machine/shell_6061_drawing.pdf
python flush6.py out/flush               # trim, sleeve, deck, back plate, arms + checks.txt
python template6.py out/flush/CUTOUT_TEMPLATE_A3.pdf
python printed6.py out/printed           # printed shell + trim, halves and one-piece
python make3mf6.py $V6_TABLET out/float out/flush out/printed out/3mf
```

To add another iPad, add an entry to `tablets.py`. Give its size, corner radius, camera, speakers, mics, buttons and rear camera keep-out, then run the commands above. The generators place the bosses, magnets, pins and clamps clear of the openings, and `checks.txt` ends in `RESULT: ALL CHECKS PASS` or lists what clashes.

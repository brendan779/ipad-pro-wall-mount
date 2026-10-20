> **Build manual:** [PDF](Float_Mount_v4.1_Build_Manual.pdf) (print-ready, one step per page) · [read on GitHub](BUILD_MANUAL.md)

# Float Mount v4.1: Hybrid (aluminium shell + printed carrier)

iPad Pro 12.9" 3rd gen · standard straight USB-C cable · deep ends, slim top/bottom

**Overall:** 344.1 × 238.9 mm · ends 31.8 mm (both match) · top/bottom 12.0 mm · 25.7 mm off the wall
**Aluminium shell:** about 223 g of 6061 · the only visible part · no visible screws

---

## Parts

### Machine (6061 aluminium)
| File | Notes |
|---|---|
| `machine/shell_6061.step` | From 12 mm plate (shell height is 11.7 mm). Front frame 2.5 mm, skirt 2.0 mm, 8 blind M3 bosses on the ends + 8 M2.5 bosses on the top/bottom (tied into the skirt). |

### Print (PETG or ASA, P1S bed)
| File | Qty | Orientation / supports |
|---|---|---|
| `print/carrier_TL/TR/BL/BR.stl` | 4 | Back face down, no supports. 4 walls, 15% gyroid |
| `print/hanger.stl` | 1 | As exported (foot down), **no supports**. 4 × M3 heat-set inserts from the top |
| `print/lock_boss.stl` | 1 | Pad down (already flipped), no supports |
| `print/wall_bracket.stl` | 1 | Plate down, no supports |
| `print/catch_rail.stl` | 1 | Flange down (already flipped), no supports. 4 × M3 heat-set inserts |
| `print/optional_shell_prototype/shell_print_*.stl` | 4 | **Optional.** A printed copy of the alu shell (face down) so you can test everything before cutting metal |

---

## Machining the shell (StrongHold)

**Op 1: back side up**
1. Face the stock to 11.7 mm.
2. Pocket the interior to 9.2 mm deep, leaving the bosses standing 4.2 mm proud of the floor: 8 × Ø8 on the ends, and 8 × Ø6 on the top/bottom, which merge into the skirt so there is no narrow tool gap. Use a 6 mm flat end mill; the smallest internal radius is 21.7 mm.
3. Cut the plug relief: a 0.55 mm deep pocket on the plate underside at the USB-C end (only needed because the plug is taller than the iPad).
4. Spot drill each boss tip and drill **5.5 mm deep from the tip** (it leaves a **1.2 mm skin** on the front face, so don't go deeper): Ø2.5 on the ends, then tap M3; Ø2.05 on the top/bottom, then tap M2.5. A forming tap is best.

**Op 2: front side up** (locate off the pocket walls, or use a sacrificial plate with soft locating pins in two boss holes)
1. Cut the window profile through. The inner corner radius is 7.5 mm, and the Face ID notch is a stadium with R4.2 ends, so a 6 mm end mill fits both.
2. Profile the outside with tabs.
3. Put a 0.8 mm radius on the front outer edge, plus a light deburr on the window edge.

**Finish:** bead blast (fine glass) then clear or black anodise.

---

## Hardware
- 8 × M3 × 6 mm cap screws (ends) + 8 × M2.5 × 6 mm cap screws (top/bottom): carrier into the shell bosses, from the back
- 4 × M3 × 8 mm countersunk screws + 4 × M3 heat-set inserts: hanger (heads flush under the iPad)
- 2 × M3 × 8 mm countersunk screws + 2 × M3 nuts: lock boss
- 4 × M3 × 8 mm countersunk screws + 4 × M3 heat-set inserts: catch rail to the bracket plate (heads flush on the wall side)
- 1 × M3 heat-set insert (4.2 mm) in the lock boss + 1 × M3 × 12 mm lock screw (from underneath)
- 0.3 mm PORON or felt tape on the shell lip, where it touches the glass
- PoE+ to USB-C adapter (PoE Texas / Heckler T515) in the wall cavity, plus a **standard straight USB-C cable**

## Cable fit (measure your cable)
The frame is sized for a plug 17 × 12.5 × 7 mm, a 4.5 mm cable and an 8 mm bend radius. If your cable is different, change `PLUG_L`, `PLUG_W`, `PLUG_H`, `CABLE_D` and `BEND_R` at the top of `hybrid.py` and rerun it. **The end frames resize automatically.** Every 1 mm shorter plug makes both ends 1 mm thinner. The top/bottom width is `FRAME_Y` (12 mm); set `LONG_BOSSES = False` to take it down to about 8 mm, with the shell then held only by the end bosses.

## Sound
Speakers and mics fire into galleries in the carrier that vent out the back into the shadow gap, so the aluminium needs no side machining. For visible grille slots in the skirt instead, set `GRILLE = "skirt"`; that adds an on-edge setup for the shell.

## Buttons
The power and volume buttons sit under the frame and **can't be reached**. On a wall panel that's normal: use Settings > Accessibility > AssistiveTouch, or Siri, or Shut Down in Settings. Physical plungers can be added later if you want them.

## Assembly
1. Lay the shell face-down on a towel. Put the PORON tape on the lip.
2. Plug the USB-C cable into the iPad, lay the iPad face-down into the shell and route the cable into the cavity.
3. Drop in the four carrier quarters. The shell aligns them. Fit the 16 cap screws.
4. Bolt on the hanger and lock boss. They also tie the quarters together.
5. Hang it on the bracket: offer it up 10 mm high, push it flat, slide it down, then fit the lock screw from below.

---

## v4.1 printability changes
- **Carrier:** the sound galleries are now **open-top chambers**, and the aluminium plate forms their ceiling. A 2 mm end rib with windows still locates the iPad in X. There are no unsupported overhangs left. The only remaining unsupported surfaces are the 1.4 mm ring steps inside the screw-head recesses, which bridge fine.
- **Hanger:** solid down to the foot, so it prints foot-down with **no supports**. Heat-set inserts replace the nut traps.
- **Wall bracket:** the catch rail is now a separate bolt-on part printed flange-down. The plate itself is flat.
- **Unchanged:** fit, function and every clash check. The shell is the same.

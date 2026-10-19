> **Build manual:** [PDF](Float_Mount_v5.1_Flush_Build_Manual.pdf) (print-ready, one step per page) · [read on GitHub](BUILD_MANUAL.md)

# Float Mount v5.1: FLUSH in-wall (printable)

iPad Pro 12.9" 3rd gen · standard straight USB-C · existing 10 mm plasterboard on 70 mm studs at 450 c/c

**On the wall:** a 355.1 × 233.6 mm aluminium trim, only **4.5 mm proud** of the wall. Ends are 37.2 mm, top/bottom 9.3 mm. The glass sits 3.3 mm below the trim face.
**Cut-out:** 343.1 × 221.6 mm, R7 corners. Use `CUTOUT_TEMPLATE_A3.pdf`.
**In the wall:** 57.5 mm deep from the wall face including the back plate, so 47.5 mm into a 70 mm stud cavity (22.5 mm clear of the far side).

---

## Parts

### Machine (6061)
| File | Notes |
|---|---|
| `machine/trim_6061.step` | 3 mm flat plate, about 188 g. Unchanged from v5 |

### Print (PETG or ASA, P1S): every part prints flat with no supports
| File | Qty | Orientation | Size |
|---|---|---|---|
| `print/sleeve_L`, `sleeve_R` | 2 | **Face down** (already flipped), so the wall-contact face is dead flat | 176.6 × 231.6 × 56.5 |
| `print/deck_L`, `deck_R` | 2 | Bottom down, as exported | 168.3 × 215 × 9.2 |
| `print/back_plate_L`, `back_plate_R` | 2 | Flat | 230.6 and 110.6 × 219.6 × 2.5 |
| `print/dog_ear_arm_x4` | 4 | Flat | 24 × 12 × 6 |

Overhang audit in print orientation: sleeves **0 mm²**, deck 3 mm², back plate 21 mm² (countersinks on the first layer), arms 0 mm².

---

## How it works (v5.1)
1. **Sleeve:** just walls and the 6 mm flange, open at the back. It's in two halves glued at the centre seam. Inside, continuous **45° ledges** run around the walls.
2. **Deck:** a separate flat insert (two halves) with 45° bevelled back edges that **seat on the ledges and self-centre**. It carries the iPad, the end ribs, the magnet posts, the locating-pin posts and the 4 dog-ear screw posts.
3. **Dog-ear screws** pass through the deck posts into the arms behind the plasterboard. Tightening them clamps the plasterboard between the arms and the sleeve flange, **and locks the deck in place**, so pulling the trim off never pulls the deck out.
4. **Back plate** (two pieces, split off-centre so it bridges the sleeve seam) screws to 8 bosses on the sleeve's back edge. It carries the PoE adapter (zip-tie slots) and the Cat6 entry.
5. **Trim, magnets, pins, grilles, iPad removal:** all unchanged from v5.

## Machining the trim (StrongHold)
- **Stock:** 3 mm 6061 plate (or 4 mm faced down), about 360 × 240 mm.
- **Op 1, back side up:** 8 × Ø10.2 magnet pockets 1.6 mm deep (leaves a **1.4 mm skin**, don't go deeper), 2 × Ø3 pin holes 2 mm deep, and the 0.55 mm plug relief at the USB-C end.
- **Op 2, front side up:** window profile through (inner R7.5), Face ID stadium (R4.2 ends), grille slots (2 mm, so a 2 mm end mill; climb, light passes), outer profile with tabs, and a 0.8 mm radius on the front outer edge.
- **Finish:** bead blast, then anodise (clear or black).
- **Watch for:** the magnet-pocket skin and the grille webs between slots (2 mm) are the delicate bits. Hold the plate down with a vacuum table or double-sided tape on a spoilboard.

## Hardware
- 16 × N52 magnets, 10 × 1.5 mm (8 in the trim, 8 in the deck posts). **Check the polarity:** they must attract. Stack all 16, dot the top face of each, and fit every one dot face toward the room (into the pocket on the trim, exposed on the deck).
- 2 × Ø3 × 6 mm dowel pins (pressed into the trim)
- 4 × M4 × 30 mm pan-head screws + 4 × M4 heat-set inserts (in the arms)
- 8 × M3 × 8 mm countersunk screws + 8 × M3 heat-set inserts: back plate to the sleeve
- 2-part epoxy for the sleeve centre seam (and the deck seam)
- 0.3 mm PORON tape on the underside of the trim lip
- PoE+ to USB-C adapter (PoE Texas / Heckler T515), zip ties, and a standard straight USB-C cable

## Install
1. **Bench assembly first:** glue the sleeve halves on a flat surface, and glue the deck halves. Fit the heat-set inserts. Zip-tie the PoE adapter to the back plate and screw the back plate on. Drop the deck onto its ledges, fit the arms on their screws, and back the screws out about 5 mm so the arms sit low.
2. **Find the studs** and centre the template between them. Look inside the wall through a small test hole first for cables, pipes or noggings.
3. Tape up the template, drill the 4 corners at Ø14, and cut the straight edges.
4. Lift the deck out (undo the 4 M4s and catch the arms), push the Cat6 in through the back plate and plug it into the PoE adapter, then refit the deck, screws and arms.
5. Fold the arms in, push the whole unit into the hole until the flange is on the wall, then swing each arm out and tighten until snug. **Don't overtighten**, or you'll crush the plasterboard.
6. Plug the USB-C into the iPad, lay it on the deck, and fit the trim. The magnets will pull it home.

## Notes
- **Buttons are inaccessible.** Use AssistiveTouch or Siri.
- **Heat:** the iPad back vents into a closed in-wall box. It's fine at wall-panel duty (a few watts), but avoid hours of video or gaming on it.
- **Plug size:** all dimensions are driven by `PLUG_L`, `PLUG_W` and `PLUG_H` in `flush.py`. A shorter plug makes the ends thinner and the cut-out smaller.

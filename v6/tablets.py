"""
Tablet definitions for Float Mount v6 (float + flush, machined + printed).

Landscape, FRONT view: origin at the iPad centre, +X toward the USB-C end, +Y up.
Every model is mounted with USB-C on the right (+X) end.

Sources
  * iPad Pro 11-inch (M5), iPad Pro 13-inch (M5), iPad mini (A17 Pro):
    Apple Accessory Design Guidelines dimensional drawings (2025-12-08 / 2024-10-21).
    Corner radius measured from the drawings' vector outlines (straight edge starts).
  * iPad Pro 12.9-inch (3rd gen): the v4.2 values. Its button positions are NOT from
    an Apple drawing; the reliefs are deliberately generous (see BUTTONS) because the
    v4.2 carrier pressed the volume buttons.

Feature lists
  cam      ("end", length) : front camera centred on the -X short end (stadium slot)
           ("top", length) : front camera centred on the top long edge
  spk      {"-x": [(y0, y1)...], "+x": [...]}   speaker openings on each short end
  mic_end  {"-x": [(y0, y1)], "+x": [...]}      mic openings on the short ends
  mic_top  [(x0, x1)]                            mic openings on the top long edge
  buttons  [("top", x0, x1), ("-x", y0, y1), ...] relief zones (button span + margin)
  rear     [("circle", x, y, r) | ("rect", x0, x1, y0, y1)] camera bump keep-outs on the back
"""


def _m5(L, W, T, sensor_span):
    xl, yt = -L / 2, W / 2
    return dict(
        L=L, W=W, T=T, R=14.5,
        cam=("top", sensor_span + 13.0),                  # sensors + 121° FOV cone margin
        spk={"-x": [(yt - 65.49, yt - 35.07), (-yt + 35.07, -yt + 65.49)],
             "+x": [(yt - 65.49, yt - 35.07), (-yt + 35.07, -yt + 65.49)]},
        mic_end={"-x": [(-3.0, 3.0)], "+x": []},           # top mic (portrait top centre)
        mic_top=[(L / 2 - 28.0, L / 2 - 21.0)],           # side mic, 24.36 from the USB end
        buttons=[("top", xl + 12.0, xl + 39.0),           # volume: centres 19.33 / 31.39, 10.06 long
                 ("-x", yt - 28.0, yt - 12.0)],           # top button: 13.98..26.04 from the corner
        rear=[("rect", xl - 1.0, xl + 38.5, yt - 38.5, yt + 1.0)],   # camera module to 35.76
    )


def _mini():
    L, W = 195.43, 134.75
    xl, yt = -L / 2, W / 2
    return dict(
        L=L, W=W, T=6.32, R=14.5,
        cam=("end", 16.0),
        spk={"-x": [(-yt + 32.74, -yt + 50.70), (yt - 50.69, yt - 37.87)],
             "+x": [(yt - 50.69, yt - 27.61), (-yt + 27.61, -yt + 50.69)]},
        mic_end={"-x": [], "+x": []},
        mic_top=[],
        buttons=[("-x", -yt + 11.0, -yt + 31.5),          # sleep/wake (Touch ID): 12.69..29.81
                 ("-x", yt - 37.0, yt - 11.0)],           # volume: 12.82..22.88 and 24.88..34.94
        rear=[("circle", xl + 27.7, yt - 26.4, 10.5)],    # Ø11.89 turret + strobe
    )


def _g3():
    L, W = 280.6, 214.9
    xl, yt = -L / 2, W / 2
    return dict(
        L=L, W=W, T=5.9, R=10.3,
        cam=("end", 32.0),
        spk={"-x": [(yt - 56.0, yt - 20.0), (-yt + 20.0, -yt + 56.0)],
             "+x": [(yt - 56.0, yt - 20.0), (-yt + 20.0, -yt + 56.0)]},
        mic_end={"-x": [(-11.0, 11.0)], "+x": []},
        mic_top=[],
        buttons=[("top", xl + 8.0, xl + 48.0),            # volume (generous: the v4.2 fault)
                 ("-x", yt - 36.0, yt - 8.0)],            # top button
        rear=[("circle", xl + 16.0, yt - 16.0, 11.0)],
    )


TABLETS = {
    "ipad_pro_12_9_gen3": dict(name="iPad Pro 12.9″ (3rd gen)", models="A1876 · A1895 · A2014 · A1983", **_g3()),
    "ipad_pro_13_m5": dict(name="iPad Pro 13″ (M5)", models="M5, 2025", **_m5(281.58, 215.53, 5.125, 39.45)),
    "ipad_pro_11_m5": dict(name="iPad Pro 11″ (M5)", models="M5, 2025", **_m5(249.70, 177.51, 5.288, 36.45)),
    "ipad_mini_a17_pro": dict(name="iPad mini (A17 Pro)", models="A17 Pro, 2024", **_mini()),
}

DEFAULT = "ipad_pro_12_9_gen3"


def get(key=None):
    import os
    key = key or os.environ.get("V6_TABLET", DEFAULT)
    if key not in TABLETS:
        raise SystemExit(f"unknown tablet {key!r}; choose from {', '.join(TABLETS)}")
    return key, TABLETS[key]

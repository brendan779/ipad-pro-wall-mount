"""
Hardware models for the v6 STEP assemblies: screws, heat-set inserts, nuts, magnets, dowel pins.

Simplified but dimensionally true envelopes (threads not modelled; shanks at the nominal
major diameter so the STEP shows exactly where each screw ends up). Every part is built
with its axis on Z, the bearing face of the head on Z0 and the shank running down -Z.
place() turns and moves it onto a hole.

ISO 4762 socket cap, ISO 7380-1 button head, ISO 10642 countersunk, ISO 7045 pan head,
ISO 4032 nut; inserts are the common "short" brass heat-set type (M3 x 5.7, Ø4.6 knurl
for a Ø4.0-4.2 hole; M4 x 6, Ø5.9 knurl for a Ø5.6 hole).
"""
import math

import cadquery as cq

CAP = {"M2.5": (4.5, 2.5, 2.0), "M3": (5.5, 3.0, 2.5), "M4": (7.0, 4.0, 3.0)}          # dk, k, socket
BUTTON = {"M2.5": (4.7, 1.3, 1.5), "M3": (5.7, 1.65, 2.0), "M4": (7.6, 2.2, 2.5)}
CSK = {"M3": (6.0, 1.65, 2.0), "M4": (8.0, 2.2, 2.5)}                                   # dk, head height, socket
PAN = {"M4": (8.0, 2.6)}
DIA = {"M2.5": 2.5, "M3": 3.0, "M4": 4.0}

_cache = {}


def _hexagon(af, depth):
    return cq.Workplane("XY").polygon(6, af / math.cos(math.pi / 6)).extrude(depth)


def _shank(d, length):
    s = cq.Workplane("XY").circle(d / 2).extrude(-length)
    return s.faces("<Z").chamfer(min(0.3, d * 0.1))


def screw(kind, size, length):
    """kind: cap | button | csk | pan. length = nominal (under head; overall for csk)."""
    key = ("s", kind, size, length)
    if key in _cache:
        return _cache[key]
    d = DIA[size]
    if kind == "cap":
        dk, k, s = CAP[size]
        head = cq.Workplane("XY").circle(dk / 2).extrude(k).faces(">Z").edges().chamfer(0.2)
        head = head.cut(_hexagon(s, k * 0.6).translate((0, 0, k * 0.4 + 0.01)))
        body = head.union(_shank(d, length))
    elif kind == "button":
        dk, k, s = BUTTON[size]
        head = (cq.Workplane("XZ").moveTo(0, 0).lineTo(dk / 2, 0).lineTo(dk / 2, k * 0.25)
                .threePointArc((dk * 0.33, k * 0.85), (dk * 0.18, k)).lineTo(0, k).close()
                .revolve(360, (0, 0, 0), (0, 1, 0)))
        head = head.cut(_hexagon(s, k * 0.65).translate((0, 0, k * 0.35 + 0.01)))
        body = head.union(_shank(d, length))
    elif kind == "csk":
        dk, kh, s = CSK[size]
        # bearing face = the TOP of the head (flush with the surface); cone runs down into the part
        head = cq.Workplane("XY").circle(d / 2).workplane(offset=kh).circle(dk / 2).loft().translate((0, 0, -kh))
        head = head.cut(_hexagon(s, kh * 0.8).translate((0, 0, -kh * 0.8 + 0.01)))
        body = head.union(_shank(d, length - kh).translate((0, 0, -kh)))
    elif kind == "pan":
        dk, k = PAN[size]
        head = cq.Workplane("XY").circle(dk / 2).extrude(k).faces(">Z").edges().fillet(k * 0.45)
        slot = cq.Workplane("XY").rect(dk * 0.75, 0.9).extrude(k).union(cq.Workplane("XY").rect(0.9, dk * 0.75).extrude(k))
        head = head.cut(slot.translate((0, 0, k * 0.55)))
        body = head.union(_shank(d, length))
    else:
        raise ValueError(kind)
    _cache[key] = body
    return body


def insert(size):
    """Heat-set insert, flush end on Z0, body down -Z."""
    key = ("i", size)
    if key in _cache:
        return _cache[key]
    od, length, bore = {"M3": (4.6, 5.7, 3.0), "M4": (5.9, 6.0, 4.0)}[size]
    b = cq.Workplane("XY").circle(od / 2).extrude(-length)
    for zc in (-length * 0.3, -length * 0.72):                     # two knurl grooves
        b = b.cut(cq.Workplane("XY").circle(od / 2 + 1).circle(od / 2 - 0.25).extrude(0.6).translate((0, 0, zc - 0.3)))
    b = b.cut(cq.Workplane("XY").circle(bore / 2).extrude(-length - 1).translate((0, 0, 0.5)))
    _cache[key] = b
    return b


def nut(size="M3"):
    af, m = {"M3": (5.5, 2.4), "M4": (7.0, 3.2)}[size]
    return _hexagon(af, m).cut(cq.Workplane("XY").circle(DIA[size] / 2).extrude(m + 1).translate((0, 0, -0.5)))


def disc(d, t):
    return cq.Workplane("XY").circle(d / 2).extrude(-t)


def pin(d, length):
    return cq.Workplane("XY").circle(d / 2).extrude(-length).edges().chamfer(0.3)


# shank direction -> rotation that takes -Z onto it
_ROT = {"-z": None, "+z": ((1, 0, 0), 180), "+y": ((1, 0, 0), 90), "-y": ((1, 0, 0), -90),
        "+x": ((0, 1, 0), -90), "-x": ((0, 1, 0), 90)}


def loc(x, y, z, shank="-z"):
    r = _ROT[shank]
    if r is None:
        return cq.Location(cq.Vector(x, y, z))
    return cq.Location(cq.Vector(x, y, z), cq.Vector(*r[0]), r[1])


def placed(shape, l):
    """the shape moved to a Location (for clash checks / renders)"""
    return cq.Workplane("XY").add(shape.val().moved(l))


STEEL = (0.55, 0.57, 0.60)
BLACK = (0.10, 0.10, 0.11)
BRASS = (0.80, 0.62, 0.25)
MAGNET = (0.70, 0.72, 0.76)


class Kit:
    """collects placed hardware: (name, shape, Location, rgb) + a bill of materials"""

    def __init__(self):
        self.items, self.bom, self.where = [], {}, []

    def add(self, label, shape, l, rgb, where, bites=None):
        """bites: name of the part this item is meant to cut into (thread in a tapped or
        self-tapped hole, knurl of a heat-set insert); every other overlap is a clash."""
        n = sum(1 for it in self.items if it[0].startswith(label + "_")) + 1
        self.items.append((f"{label}_{n}", shape, l, rgb, bites))
        self.where.append(where)
        q, w = self.bom.get(label, (0, {}))
        w[where] = w.get(where, 0) + 1
        self.bom[label] = (q + 1, w)

    def to_assembly(self, assy, prefix="hw"):
        for name, shape, l, rgb, _ in self.items:
            assy.add(shape, name=f"{prefix}_{name}", loc=l, color=cq.Color(*rgb))

    def shapes(self):
        return [placed(s, l) for _, s, l, _, _ in self.items]

    def select(self, label=None, where=None):
        """placed shapes whose label starts with `label` and/or whose `where` contains `where`"""
        out = []
        for (name, s, l, _, _), w in zip(self.items, self.where):
            if (label is None or name.startswith(label)) and (where is None or where in w):
                out.append(placed(s, l))
        return out

    def clashes(self, parts):
        """[(item, part, volume)] for every overlap that is not the item's intended bite"""
        out = []
        for (name, s, l, _, bites), ps in zip(self.items, self.shapes()):
            bb = ps.val().BoundingBox()
            if bites in parts:                       # the intended bite must really be there
                try:
                    vb = ps.intersect(parts[bites]).val().Volume()
                except Exception:
                    vb = 0.0
                if vb <= 0.01:
                    out.append((name, f"{bites} (NO ENGAGEMENT)", 0.0))
            for pname, p in parts.items():
                if pname == bites:
                    continue
                pb = p.val().BoundingBox()
                if bb.xmax < pb.xmin or bb.xmin > pb.xmax or bb.ymax < pb.ymin or bb.ymin > pb.ymax or \
                        bb.zmax < pb.zmin or bb.zmin > pb.zmax:
                    continue
                try:
                    v = ps.intersect(p).val().Volume()
                except Exception:
                    v = 0.0
                if v > 0.01:
                    out.append((name, pname, round(v, 3)))
        return out

    def union(self):
        sh = self.shapes()
        u = sh[0]
        for s in sh[1:]:
            u = u.union(s)
        return u

    def bom_lines(self):
        out = []
        for label, (q, w) in self.bom.items():
            where = " · ".join(f"{k} {v}" for k, v in w.items())
            out.append(f"{q:3d} × {label.replace('_', ' ')}   ({where})")
        return out

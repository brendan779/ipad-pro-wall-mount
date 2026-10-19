"""Manual render toolkit: CAD-style renders (shaded + feature edges) with a fixed
palette, plus cross-section schematics drawn with matplotlib."""
import os, tempfile, hashlib
import cadquery as cq
import vtk

BG = (0xF2 / 255, 0xF1 / 255, 0xEE / 255)        # slide background, so renders sit seamlessly
C = {
    "active": (0.91, 0.46, 0.16),   # the part(s) this step is about
    "print": (0.24, 0.25, 0.28),    # printed parts already fitted
    "print2": (0.36, 0.37, 0.41),
    "alu": (0.80, 0.81, 0.84),
    "ipad": (0.07, 0.07, 0.09),
    "wall": (0.90, 0.88, 0.84),
    "stud": (0.79, 0.65, 0.48),
    "hw": (0.18, 0.43, 0.71),       # hardware markers (screws, inserts, magnets)
    "plug": (0.93, 0.93, 0.93),
    "ghost": (0.70, 0.71, 0.74),
    "tape": (0.95, 0.75, 0.20),
}
_cache = os.path.join(tempfile.gettempdir(), "mr_stl")
os.makedirs(_cache, exist_ok=True)


def _stl(shape):
    s = shape.val() if hasattr(shape, "val") else shape
    key = hashlib.md5(str(s.BoundingBox().__dict__).encode() + str(s.Volume()).encode()
                      + str(s.Area()).encode()).hexdigest()
    p = os.path.join(_cache, key + ".stl")
    if not os.path.exists(p):
        cq.exporters.export(cq.Workplane().add(s), p, tolerance=0.04, angularTolerance=0.15)
    return p


def screw(x, y, z, axis="z", d=3.0, length=8.0, head=5.5, head_t=2.0, toward=+1):
    """Hardware marker: shank + head. toward = which way the head faces along the axis."""
    sh = cq.Workplane("XY").circle(d / 2).extrude(length)
    hd = cq.Workplane("XY").circle(head / 2).extrude(head_t).translate((0, 0, length))
    s = sh.union(hd)
    if toward < 0:
        s = s.rotate((0, 0, 0), (1, 0, 0), 180)
    if axis == "y":
        s = s.rotate((0, 0, 0), (1, 0, 0), -90)
    elif axis == "x":
        s = s.rotate((0, 0, 0), (0, 1, 0), 90)
    return s.translate((x, y, z))


def disc(x, y, z, d, t, axis="z"):
    s = cq.Workplane("XY").circle(d / 2).extrude(t)
    if axis == "y":
        s = s.rotate((0, 0, 0), (1, 0, 0), -90)
    return s.translate((x, y, z))


def render(path, items, cam, w=1650, h=1080, edges=True, zoom=1.0, focal=None, up=(0, 1, 0),
           parallel=False):
    """items: list of (shape, colour key or rgb, opacity). cam: camera position (x,y,z)."""
    ren = vtk.vtkRenderer()
    ren.SetBackground(*BG)
    pass
    for shape, col, op in items:
        rgb = C[col] if isinstance(col, str) else col
        r = vtk.vtkSTLReader(); r.SetFileName(_stl(shape))
        n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort())
        n.SetFeatureAngle(32); n.SplittingOn()
        m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort())
        m.SetResolveCoincidentTopologyToPolygonOffset()
        a = vtk.vtkActor(); a.SetMapper(m)
        p = a.GetProperty(); p.SetColor(*rgb); p.SetOpacity(op)
        p.SetAmbient(0.25); p.SetDiffuse(0.75); p.SetSpecular(0.25 if col != "alu" else 0.45)
        p.SetSpecularPower(30)
        ren.AddActor(a)
        if edges and op > 0.6:
            fe = vtk.vtkFeatureEdges(); fe.SetInputConnection(r.GetOutputPort())
            fe.BoundaryEdgesOn(); fe.FeatureEdgesOn(); fe.SetFeatureAngle(32)
            fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff()
            em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort())
            em.ScalarVisibilityOff()
            ea = vtk.vtkActor(); ea.SetMapper(em)
            dark = tuple(max(0.0, c * 0.45) for c in rgb) if col not in ("ipad", "print") else (0.02, 0.02, 0.03)
            if col in ("ipad", "print"):
                dark = (0.55, 0.56, 0.6) if col == "print" else (0.35, 0.35, 0.38)
            ea.GetProperty().SetColor(*dark); ea.GetProperty().SetLineWidth(1.6)
            ea.GetProperty().SetOpacity(op)
            ren.AddActor(ea)
    lk = vtk.vtkLightKit(); lk.SetKeyLightIntensity(0.85); lk.AddLightsToRenderer(ren)
    camr = ren.GetActiveCamera()
    if parallel:
        camr.ParallelProjectionOn()
    ren.ResetCamera()
    bb = ren.ComputeVisiblePropBounds()
    fp = focal or ((bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2, (bb[4] + bb[5]) / 2)
    camr.SetFocalPoint(*fp); camr.SetPosition(*cam); camr.SetViewUp(*up)
    ren.ResetCamera(); camr.Zoom(zoom)
    rw = vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.AddRenderer(ren)
    rw.SetSize(w, h); rw.SetMultiSamples(8); rw.Render()
    wf = vtk.vtkWindowToImageFilter(); wf.SetInput(rw); wf.Update()
    pw = vtk.vtkPNGWriter(); pw.SetFileName(path); pw.SetInputConnection(wf.GetOutputPort()); pw.Write()
    return path


def plate(x0, x1, y0, y1, z=0.0):
    """A thin build plate under a part in print orientation."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, 1.0).translate(((x0 + x1) / 2, (y0 + y1) / 2, z - 0.5))


def on_plate(part, size=256.0):
    """Drop a part onto Z0 and centre it on a 256 mm plate. Returns (part, plate)."""
    bb = part.val().BoundingBox()
    p = part.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))
    return p, plate(-size / 2, size / 2, -size / 2, size / 2)


# ---------------------------------------------------------------- sections
def section(path, items, origin, normal, u_axis, v_axis, labels=(), xlim=None, ylim=None,
            w_in=12.0, title=None, fs=12):
    """2D cut through the parts, drawn 1:1 (figure shape follows xlim/ylim).
    items: (shape, colour key or rgb). labels: (text, (u,v) target, (u,v) text pos);
    text is left-aligned when it sits right of its target, else right-aligned."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    h_in = w_in * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    fig = plt.figure(figsize=(w_in, h_in), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(BG); ax.axis("off")
    u = np.array(u_axis, float); v = np.array(v_axis, float); o = np.array(origin, float)
    for it in items:
        shape, col = it[0], it[1]
        r = vtk.vtkSTLReader(); r.SetFileName(_stl(shape)); r.Update()
        pl = vtk.vtkPlane(); pl.SetOrigin(*origin); pl.SetNormal(*normal)
        cut = vtk.vtkCutter(); cut.SetInputConnection(r.GetOutputPort()); cut.SetCutFunction(pl)
        st = vtk.vtkStripper(); st.SetInputConnection(cut.GetOutputPort()); st.JoinContiguousSegmentsOn(); st.Update()
        pd = st.GetOutput(); pts = pd.GetPoints()
        if pts is None:
            continue
        verts, codes = [], []
        lines = pd.GetLines(); lines.InitTraversal(); idl = vtk.vtkIdList()
        while lines.GetNextCell(idl):
            loop = []
            for i in range(idl.GetNumberOfIds()):
                p = np.array(pts.GetPoint(idl.GetId(i))) - o
                loop.append((p @ u, p @ v))
            if len(loop) < 3:
                continue
            verts += loop + [loop[0]]
            codes += [Path.MOVETO] + [Path.LINETO] * (len(loop) - 1) + [Path.CLOSEPOLY]
        if not verts:
            continue
        rgb = C[col] if isinstance(col, str) else col
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=rgb, edgecolor=tuple(c * 0.45 for c in rgb), lw=0.9))
    for text, (tu, tv), (lu, lv) in labels:
        ax.annotate(text, xy=(tu, tv), xytext=(lu, lv), fontsize=fs, color="#1c1d20",
                    ha="left" if lu >= tu else "right", va="center",
                    arrowprops=dict(arrowstyle="-", color="#1c1d20", lw=0.8, shrinkA=2, shrinkB=0))
        ax.plot([tu], [tv], "o", ms=3.4, color="#1c1d20")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    if title:
        ax.text(0.012, 0.975, title, transform=ax.transAxes, fontsize=fs + 2, weight="bold", va="top", color="#1c1d20")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)
    return path

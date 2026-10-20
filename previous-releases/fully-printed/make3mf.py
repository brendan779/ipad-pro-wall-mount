"""
Write Bambu Studio project 3MFs (geometry, plates, plate thumbnails, per-object
settings, filament slot per object) for the fully printed Float Mount builds.

Printer, process and filament presets are deliberately NOT embedded: Bambu Studio
applies the ones you pick when the project opens (P1S / X1 / A1 / H2 ...), so
nothing in here can override your machine's start G-code or limits.

    python make3mf.py <out_printed_dir> <repo_milled_v41_print_dir> <repo_milled_v51_print_dir>
"""
import math
import os
import sys
import uuid
import zipfile
from xml.sax.saxutils import escape

import numpy as np
import trimesh

BED = 256.0           # P1S / X1 / P1P plate; every part here also fits A1 and H2 beds
GAP = 8.0             # spacing between parts on a plate
STRIDE = BED * 1.2    # Bambu Studio lays plates out on a grid with a 1/5 plate gap
APP = "BambuStudio-02.03.00.70"

FACE = {"wall_loops": "4", "sparse_infill_density": "20%", "sparse_infill_pattern": "gyroid",
        "bottom_shell_layers": "4", "bottom_surface_pattern": "monotonic"}
LIGHT = {"wall_loops": "4", "sparse_infill_density": "15%", "sparse_infill_pattern": "gyroid"}
MID = {"wall_loops": "4", "sparse_infill_density": "20%", "sparse_infill_pattern": "gyroid"}
BRACKET = {"wall_loops": "4", "sparse_infill_density": "25%", "sparse_infill_pattern": "gyroid"}
STRONG = {"wall_loops": "5", "sparse_infill_density": "40%", "sparse_infill_pattern": "gyroid"}
SOLID = {"wall_loops": "6", "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag"}


def load(path, rot_x180=False):
    m = trimesh.load_mesh(path, process=True)
    m.merge_vertices()
    if rot_x180:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    b = m.bounds
    m.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    return m


def pack(items):
    """Shelf-pack [(name, mesh, ...)] onto one BED x BED plate; may rotate 90°. Returns [(item, x, y, rotated)]."""
    order = sorted(items, key=lambda it: -max(it[1].extents[:2]))
    rows, placed = [], []
    for it in order:
        ex, ey = it[1].extents[:2]
        done = False
        for row in rows:                           # 1) any existing shelf, either orientation
            for rot in (False, True):
                w, d = (ey, ex) if rot else (ex, ey)
                if row["x"] + w <= BED - 2 and d <= row["h"] + 1e-6:
                    placed.append((it, row["x"] + w / 2, row["y"] + d / 2, rot))
                    row["x"] += w + GAP
                    done = True
                    break
            if done:
                break
        if not done:                               # 2) new shelf, flattest orientation first
            y0 = (rows[-1]["y"] + rows[-1]["h"] + GAP) if rows else 2.0
            for rot in sorted((False, True), key=lambda r: (ex if r else ey)):
                w, d = (ey, ex) if rot else (ex, ey)
                if w <= BED - 4 and y0 + d <= BED - 2:
                    rows.append({"y": y0, "h": d, "x": 2.0 + w + GAP})
                    placed.append((it, 2.0 + w / 2, y0 + d / 2, rot))
                    done = True
                    break
        if not done:
            raise SystemExit(f"{it[0]} does not fit on a {BED:.0f} mm plate")
    # centre the whole layout on the plate
    xs = [x for _, x, _, _ in placed]
    allx0 = min(x - (it[1].extents[1] if r else it[1].extents[0]) / 2 for it, x, _, r in placed)
    allx1 = max(x + (it[1].extents[1] if r else it[1].extents[0]) / 2 for it, x, _, r in placed)
    ally0 = min(y - (it[1].extents[0] if r else it[1].extents[1]) / 2 for it, _, y, r in placed)
    ally1 = max(y + (it[1].extents[0] if r else it[1].extents[1]) / 2 for it, _, y, r in placed)
    dx, dy = BED / 2 - (allx0 + allx1) / 2, BED / 2 - (ally0 + ally1) / 2
    return [(it, x + dx, y + dy, r) for it, x, y, r in placed]


def cols_for(n):
    v = math.sqrt(n)
    r = round(v)
    return r + 1 if v > r else r


def mesh_xml(m):
    v = "\n".join(f'     <vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in m.vertices)
    t = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return f"    <mesh>\n     <vertices>\n{v}\n     </vertices>\n     <triangles>\n{t}\n     </triangles>\n    </mesh>"


def thumbnail(path, placed_meshes, size):
    """Iso render of one plate. placed_meshes: [(trimesh in plate coords, rgb)]."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.95, 0.95, 0.94)

    def add(m, rgb, edges=False):
        pts = vtk.vtkPoints()
        pts.SetData(numpy_to_vtk(np.ascontiguousarray(m.vertices, dtype=np.float64), deep=True))
        f = np.hstack([np.full((len(m.faces), 1), 3), m.faces]).astype(np.int64).ravel()
        cells = vtk.vtkCellArray()
        cells.ImportLegacyFormat(numpy_to_vtkIdTypeArray(f, deep=True))
        pd = vtk.vtkPolyData()
        pd.SetPoints(pts)
        pd.SetPolys(cells)
        nrm = vtk.vtkPolyDataNormals()
        nrm.SetInputData(pd)
        nrm.SetFeatureAngle(35)
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nrm.GetOutputPort())
        a = vtk.vtkActor()
        a.SetMapper(mp)
        a.GetProperty().SetColor(*rgb)
        a.GetProperty().SetSpecular(0.15)
        ren.AddActor(a)
        if edges:
            fe = vtk.vtkFeatureEdges()
            fe.SetInputData(pd)
            fe.BoundaryEdgesOn(); fe.FeatureEdgesOn(); fe.SetFeatureAngle(35)
            fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff()
            em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort()); em.ScalarVisibilityOff()
            ea = vtk.vtkActor(); ea.SetMapper(em); ea.GetProperty().SetColor(0.15, 0.15, 0.17)
            ea.GetProperty().SetLineWidth(1.0)
            ren.AddActor(ea)

    bed = trimesh.creation.box(extents=[BED, BED, 1.0])
    bed.apply_translation([BED / 2, BED / 2, -0.5])
    add(bed, (0.36, 0.37, 0.39))
    for m, rgb in placed_meshes:
        add(m, rgb, edges=True)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(BED / 2, BED / 2, 0)
    cam.SetPosition(BED / 2, -BED * 0.95, BED * 1.35)
    cam.SetViewUp(0, 0, 1)
    ren.ResetCamera()
    cam.Zoom(1.25)
    kit = vtk.vtkLightKit()
    kit.AddLightsToRenderer(ren)
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.AddRenderer(ren)
    rw.SetSize(size, size)
    rw.SetMultiSamples(8)
    rw.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(path)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()


def build(out_path, title, description, plates, tmpdir):
    """plates: [(plate_name, [(object_name, mesh, extruder, settings)])]"""
    os.makedirs(tmpdir, exist_ok=True)
    cols = cols_for(len(plates))
    colours = {1: (0.24, 0.25, 0.27), 2: (0.83, 0.84, 0.86)}
    objects, plate_xml, thumbs = [], [], []
    mesh_id = 1
    ident = 100
    for pi, (pname, items) in enumerate(plates):
        ox = (pi % cols) * STRIDE
        oy = -(pi // cols) * STRIDE
        placed = pack(items)
        inst = []
        thumb_meshes = []
        for (name, m, ext, settings), x, y, rot in placed:
            mm = m.copy()
            if rot:
                mm.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
                b = mm.bounds
                mm.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
            obj_id = mesh_id + 1
            objects.append(dict(name=name, mesh=mm, mesh_id=mesh_id, obj_id=obj_id, ext=ext,
                                settings=settings, x=ox + x, y=oy + y, ident=ident))
            inst.append((obj_id, ident))
            ident += 1
            mesh_id += 2
            tm = mm.copy()
            tm.apply_translation([x, y, 0])
            thumb_meshes.append((tm, colours[ext]))
        n = pi + 1
        thumbnail(f"{tmpdir}/plate_{n}.png", thumb_meshes, 512)
        thumbnail(f"{tmpdir}/plate_{n}_small.png", thumb_meshes, 128)
        thumbs.append(n)
        mi = "\n".join(f'    <model_instance>\n      <metadata key="object_id" value="{oid}"/>\n'
                       f'      <metadata key="instance_id" value="0"/>\n'
                       f'      <metadata key="identify_id" value="{iid}"/>\n    </model_instance>'
                       for oid, iid in inst)
        plate_xml.append(f'  <plate>\n    <metadata key="plater_id" value="{n}"/>\n'
                         f'    <metadata key="plater_name" value="{escape(pname)}"/>\n'
                         f'    <metadata key="locked" value="false"/>\n'
                         f'    <metadata key="thumbnail_file" value="Metadata/plate_{n}.png"/>\n'
                         f'{mi}\n  </plate>')

    U = lambda: str(uuid.uuid4())
    ns = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
          'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
          'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
    files = {}
    res, items_xml, rels = [], [], []
    for k, o in enumerate(objects, 1):
        path = f"/3D/Objects/object_{k}.model"
        files[path[1:]] = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {ns}>\n'
                           f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
                           f'  <object id="{o["mesh_id"]}" p:UUID="{U()}" type="model">\n{mesh_xml(o["mesh"])}\n  </object>\n'
                           f' </resources>\n <build/>\n</model>\n')
        res.append(f'  <object id="{o["obj_id"]}" p:UUID="{U()}" type="model">\n   <components>\n'
                   f'    <component p:path="{path}" objectid="{o["mesh_id"]}" p:UUID="{U()}" '
                   f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>')
        items_xml.append(f'  <item objectid="{o["obj_id"]}" p:UUID="{U()}" '
                         f'transform="1 0 0 0 1 0 0 0 1 {o["x"]:.4f} {o["y"]:.4f} 0" printable="1"/>')
        rels.append(f' <Relationship Target="{path}" Id="rel-{k}" '
                    f'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>')
    meta = {"Application": APP, "BambuStudio:3mfVersion": "1", "Title": title, "Designer": "brendan779",
            "Description": description, "License": "GPL-3.0", "Origin": "",
            "CreationDate": "2026-10-19", "ModificationDate": "2026-10-19"}
    md = "\n".join(f' <metadata name="{k}">{escape(v)}</metadata>' for k, v in meta.items())
    files["3D/3dmodel.model"] = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {ns}>\n'
                                 f'{md}\n <resources>\n' + "\n".join(res) + f'\n </resources>\n <build p:UUID="{U()}">\n'
                                 + "\n".join(items_xml) + "\n </build>\n</model>\n")
    files["3D/_rels/3dmodel.model.rels"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                                            + "\n".join(rels) + "\n</Relationships>\n")
    objs = []
    for o in objects:
        sets = "\n".join(f'    <metadata key="{k}" value="{escape(v)}"/>' for k, v in o["settings"].items())
        objs.append(f'  <object id="{o["obj_id"]}">\n    <metadata key="name" value="{escape(o["name"])}"/>\n'
                    f'    <metadata key="extruder" value="{o["ext"]}"/>\n{sets}\n'
                    f'    <part id="{o["mesh_id"]}" subtype="normal_part">\n'
                    f'      <metadata key="name" value="{escape(o["name"])}"/>\n'
                    f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                    f'      <metadata key="extruder" value="{o["ext"]}"/>\n'
                    f'      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
                    f'    </part>\n  </object>')
    files["Metadata/model_settings.config"] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "\n".join(objs)
                                               + "\n" + "\n".join(plate_xml) + "\n</config>\n")
    files["[Content_Types].xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                                    ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                                    ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                                    ' <Default Extension="png" ContentType="image/png"/>\n'
                                    ' <Default Extension="config" ContentType="text/xml"/>\n</Types>\n')
    files["_rels/.rels"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
                            ' <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>\n'
                            ' <Relationship Target="/Metadata/plate_1_small.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>\n'
                            '</Relationships>\n')
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        z.writestr("_rels/.rels", files.pop("_rels/.rels"))
        for k in sorted(files):
            z.writestr(k, files[k])
        for n in thumbs:
            z.write(f"{tmpdir}/plate_{n}.png", f"Metadata/plate_{n}.png")
            z.write(f"{tmpdir}/plate_{n}_small.png", f"Metadata/plate_{n}_small.png")
    return objects


if __name__ == "__main__":
    pdir, m41, m51 = sys.argv[1:4]
    P41 = f"{pdir}/float-v4.1-printed/print"
    P51 = f"{pdir}/flush-v5.1-printed/print"

    v41 = [
        ("Face · shell left (face down)", [("shell_print_L", load(f"{P41}/shell_print_L.stl"), 2, FACE)]),
        ("Face · shell right (face down)", [("shell_print_R", load(f"{P41}/shell_print_R.stl"), 2, FACE)]),
        ("Carrier · top quarters", [("carrier_TL", load(f"{m41}/carrier_TL.stl"), 1, LIGHT),
                                    ("carrier_TR", load(f"{m41}/carrier_TR.stl"), 1, LIGHT)]),
        ("Carrier · bottom quarters", [("carrier_BL", load(f"{m41}/carrier_BL.stl"), 1, LIGHT),
                                       ("carrier_BR", load(f"{m41}/carrier_BR.stl"), 1, LIGHT)]),
        ("Bracket, hanger, lock boss, catch rail", [("wall_bracket", load(f"{m41}/wall_bracket.stl"), 1, BRACKET),
                                                     ("hanger", load(f"{m41}/hanger.stl"), 1, STRONG),
                                                     ("lock_boss", load(f"{m41}/lock_boss.stl"), 1, STRONG),
                                                     ("catch_rail", load(f"{m41}/catch_rail.stl"), 1, STRONG)]),
    ]
    v51 = [
        ("Face · trim left (face down)", [("trim_print_L", load(f"{P51}/trim_print_L.stl"), 2, FACE)]),
        ("Face · trim right (face down)", [("trim_print_R", load(f"{P51}/trim_print_R.stl"), 2, FACE)]),
        ("Sleeve left (flange down)", [("sleeve_L", load(f"{m51}/sleeve_L.stl"), 1, LIGHT)]),
        ("Sleeve right (flange down)", [("sleeve_R", load(f"{m51}/sleeve_R.stl"), 1, LIGHT)]),
        ("Deck left", [("deck_L", load(f"{m51}/deck_L.stl"), 1, MID)]),
        ("Deck right", [("deck_R", load(f"{m51}/deck_R.stl"), 1, MID)]),
        ("Back plate left", [("back_plate_L", load(f"{m51}/back_plate_L.stl"), 1, MID)]),
        ("Back plate right + 4 dog-ear arms", [("back_plate_R", load(f"{m51}/back_plate_R.stl"), 1, MID)] +
                                               [(f"dog_ear_arm_{i}", load(f"{m51}/dog_ear_arm_x4.stl"), 1, SOLID) for i in (1, 2, 3, 4)]),
    ]
    out = f"{pdir}"
    o41 = build(f"{out}/float-v4.1-printed/Float_Mount_v4.1_Printed.3mf", "Float Mount v4.1 (fully printed)",
                "Surface PoE wall mount for iPad Pro 12.9in (3rd gen). Filament 1: hidden parts. "
                "Filament 2: the visible face, printed face-down on a textured plate. PETG or ASA.",
                v41, f"{pdir}/_thumbs41")
    o51 = build(f"{out}/flush-v5.1-printed/Float_Mount_v5.1_Flush_Printed.3mf", "Float Mount v5.1 Flush (fully printed)",
                "Flush in-wall PoE mount for iPad Pro 12.9in (3rd gen). Filament 1: hidden parts. "
                "Filament 2: the visible trim, printed face-down on a textured plate. PETG or ASA.",
                v51, f"{pdir}/_thumbs51")
    for nm, objs in (("v4.1", o41), ("v5.1", o51)):
        print(nm, len(objs), "objects:", ", ".join(o["name"] for o in objs))

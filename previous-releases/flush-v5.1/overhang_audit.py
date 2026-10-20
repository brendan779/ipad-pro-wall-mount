import numpy as np
def audit(name, part, quiet_below=1.0):
    shape = part.val(); zmin = shape.BoundingBox().zmin
    verts, tris = shape.tessellate(0.2, 0.3)
    V = np.array([(v.x, v.y, v.z) for v in verts]); T = np.array(tris)
    a, b, c = V[T[:,0]], V[T[:,1]], V[T[:,2]]
    n = np.cross(b-a, c-a); area = np.linalg.norm(n, axis=1)/2
    nz = n[:,2]/np.maximum(np.linalg.norm(n, axis=1), 1e-12)
    cz = (a[:,2]+b[:,2]+c[:,2])/3
    bad = (nz < -0.7072) & (cz > zmin + 0.05)
    tot = area[bad].sum()
    hz = sorted(set(np.round(cz[bad]-zmin, 0))) if bad.any() else []
    print(f"{name:26s} unsupported: {tot:8.1f} mm2" + (f"   heights: {hz[:8]}" if tot > quiet_below else ""))
    return tot

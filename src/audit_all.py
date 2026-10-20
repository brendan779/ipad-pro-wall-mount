"""Overhang audit of every printed part (print orientation, as exported) for every tablet."""
import glob, os, sys
import cadquery as cq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overhang_audit import audit
out = sys.argv[1]
rows = []
for f in sorted(glob.glob(f"{out}/float_*/print/**/*.step", recursive=True) + glob.glob(f"{out}/flush_*/print/**/*.step", recursive=True)
                + glob.glob(f"{out}/printed_*/*/print/**/*.step", recursive=True)):
    p = cq.importers.importStep(f)
    a = audit(os.path.relpath(f, out)[:60], p)
    rows.append((os.path.relpath(f, out), a))
with open(f"{out}/overhang_audit.txt", "w") as fh:
    for r, a in rows:
        fh.write(f"{a:8.1f} mm2  {r}\n")
print("max", max(a for _, a in rows))

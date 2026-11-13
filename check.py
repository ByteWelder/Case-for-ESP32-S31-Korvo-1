"""Sanity checks + SVG previews for case.py.  Run: .venv-cad/bin/python check.py"""
import subprocess
from pathlib import Path
from build123d import *
import case

p = case.build()
OUT = Path(__file__).parent / "preview"
OUT.mkdir(parents=True, exist_ok=True)


def vol(a, b):
    try:
        return (a & b).volume
    except Exception:
        return 0.0


for k in ("shell", "bezel", "button_long", "button_short"):
    s = p[k]
    bb = s.bounding_box()
    print(f"{k:13s} valid={s.is_valid} solids={len(s.solids())} vol={s.volume/1000:.1f}cm3 "
          f"bbox={bb.size.X:.1f}x{bb.size.Y:.1f}x{bb.size.Z:.1f}")

btns = case.placed_buttons(p)
pairs = [("shell", "bezel"), ("shell", "main"), ("shell", "comps"), ("shell", "sub"), ("shell", "lcd"),
         ("bezel", "main"), ("bezel", "comps"), ("bezel", "sub"), ("bezel", "lcd")]
print("interference volumes (mm3), want 0:")
for a, b in pairs:
    print(f"  {a:6s} x {b:6s} {vol(p[a], p[b]):8.3f}")
for i, b in enumerate(btns):
    print(f"  button{i} x bezel {vol(b, p['bezel']):.3f}  x comps {vol(b, p['comps']):.3f}  "
          f"x sub {vol(b, p['sub']):.3f} x lcd {vol(b, p['lcd']):.3f}")


def svg(name, shapes, origin, up=(0, 0, 1)):
    look = (53, 40, 13)
    vis, hid = [], []
    for s in shapes:
        v, h = s.project_to_viewport(origin, viewport_up=up, look_at=look)
        vis += v
    ex = ExportSVG(scale=4, line_weight=0.5)
    ex.add_layer("v", line_color=(0, 0, 0))
    ex.add_shape(vis, layer="v")
    ex.write(str(OUT / f"{name}.svg"))
    subprocess.run(["magick", "-background", "white", "-density", "110", str(OUT / f"{name}.svg"),
                    "-flatten", "-resize", "1600x1600>", str(OUT / f"{name}.png")], check=True)


board = [p["main"], p["comps"], p["sub"], p["lcd"]]
svg("shell_iso", [p["shell"]], (300, -260, 330))
svg("shell_top", [p["shell"]], (53, 40, 500), up=(0, 1, 0))
svg("bezel_front", [p["bezel"]], (53, 40, 500), up=(0, 1, 0))
svg("bezel_inside", [p["bezel"]], (300, -260, -300))
svg("asm_iso", [p["shell"], p["bezel"], *btns, p["lcd"]], (300, -260, 330))
svg("asm_right", [p["shell"], p["bezel"], *board], (600, 40, 13))
svg("asm_top_edge", [p["shell"], p["bezel"], *board], (53, 600, 13))
svg("shell_board_iso", [p["shell"], *board], (300, -260, 330))
svg("shell_back", [p["shell"]], (53, 40, -500), up=(0, 1, 0))
svg("asm_back_iso", [p["shell"], p["bezel"]], (300, -260, -300))

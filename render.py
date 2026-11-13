"""Shaded isometric render of the assembled case (software z-buffer, no GPU needed).

Run: .venv-cad/bin/python render.py   ->  preview/render_iso.png
"""
from pathlib import Path
import numpy as np
from PIL import Image
import case

OUT = Path(__file__).parent / "preview"
W, SS = 1600, 2                      # final width in px, supersampling factor
BG = np.array([244, 245, 247], float)


def camera(origin, look, up=(0, 0, 1)):
    f = np.array(look, float) - np.array(origin, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    return r, np.cross(r, f), f


def render(items, origin, look, name, light=(-0.35, -0.55, 0.75)):
    r, u, f = camera(origin, look)
    light = np.array(light, float)
    light /= np.linalg.norm(light)
    tris, cols = [], []
    for shape, color in items:
        v, t = shape.tessellate(0.08, 0.25)
        v = np.array([(p.X, p.Y, p.Z) for p in v])
        t = np.array(t)
        tris.append(v[t])
        cols.append(np.tile(np.array(color, float), (len(t), 1)))
    tris, cols = np.concatenate(tris), np.concatenate(cols)

    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(n, axis=1)
    keep = ln > 1e-9
    tris, cols, n = tris[keep], cols[keep], n[keep] / ln[keep, None]
    n[(n @ f) > 0] *= -1                                 # face the camera
    shade = 0.42 + 0.58 * np.clip(n @ light, 0, 1)
    shade += 0.25 * np.clip(n @ (-f), 0, 1) ** 8         # soft highlight

    sx, sy, sz = tris @ r, tris @ u, tris @ f
    wpx = W * SS
    pad = 0.05
    scale = wpx * (1 - 2 * pad) / (sx.max() - sx.min())
    hpx = int((sy.max() - sy.min()) * scale + 2 * pad * wpx)
    px = (sx - sx.min()) * scale + pad * wpx
    py = hpx - ((sy - sy.min()) * scale + pad * wpx)

    zbuf = np.full((hpx, wpx), np.inf)
    img = np.tile(BG, (hpx, wpx, 1))
    nid = np.full((hpx, wpx), -1)
    for i in range(len(tris)):
        x, y, z = px[i], py[i], sz[i]
        x0, x1 = max(int(x.min()), 0), min(int(x.max()) + 1, wpx - 1)
        y0, y1 = max(int(y.min()), 0), min(int(y.max()) + 1, hpx - 1)
        if x1 < x0 or y1 < y0:
            continue
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        a = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        b = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        c = 1 - a - b
        zz = a * z[0] + b * z[1] + c * z[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        m = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6) & (zz < sub)
        if m.any():
            sub[m] = zz[m]
            img[y0:y1 + 1, x0:x1 + 1][m] = cols[i] * shade[i]
            nid[y0:y1 + 1, x0:x1 + 1][m] = i

    # outline: depth steps and creases between differently oriented faces
    nb = np.where(nid[..., None] >= 0, n[nid], 0.0)
    zf = np.where(np.isfinite(zbuf), zbuf, zbuf[np.isfinite(zbuf)].max() + 50)
    edge = np.zeros((hpx, wpx), bool)
    for ax in (0, 1):
        dz = np.abs(np.diff(zf, axis=ax))
        dn = 1 - np.sum(nb * np.roll(nb, -1, axis=ax), axis=2)
        e = (dz > 0.6) if ax == 0 else (dz > 0.6)
        pad_shape = [(0, 1), (0, 0)] if ax == 0 else [(0, 0), (0, 1)]
        e = np.pad(e, pad_shape)
        edge |= e | ((dn > 0.35) & (nid >= 0))
    img[edge] *= 0.45

    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    out = out.resize((W, hpx // SS), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    out.save(OUT / f"{name}.png")
    print("wrote", OUT / f"{name}.png", out.size)


if __name__ == "__main__":
    p = case.build()
    SHELL, BEZEL = (62, 68, 78), (232, 120, 44)
    items = [
        (p["shell"], SHELL), (p["bezel"], BEZEL),
        (p["lcd"], (22, 24, 28)), (p["comps"], (186, 190, 196)),
        (p["main"], (28, 30, 32)), (p["sub"], (28, 30, 32)),
        *[(b, (240, 240, 236)) for b in case.placed_buttons(p)],
    ]
    render(items, (300, -260, 330), (53, 40, 13), "render_iso")

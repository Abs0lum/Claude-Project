#!/usr/bin/env python3
"""mob_mers_census.py — his 17:38 report ("some mobs are too shiny — animals aren't shiny … certainly not a buffalo").
For every entity texture set in his installed stack (textures/entity/**.texture_set.json, top pack per path): the MERS layer's
values over the colour's opaque pixels — metalness mean / share > 0, roughness mean / share below 0.5 (128), subsurface mean,
emissive share — plus where the set came from (tier-1 Patrix LabPBR vs derived: _docs/mers/MERS-INVENTORY.json when present).
Writes _docs/mers/MOB-MERS-CENSUS.json; prints the shiniest."""
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as SN  # noqa: E402

EXT = (".tga", ".png", ".jpg")


def layer(p, base_dir, name):
    for e in EXT:
        if p.has(f"{base_dir}/{name}{e}"):
            return f"{base_dir}/{name}{e}"
    return None


def main():
    P = SN.packs()
    done, rows = set(), []
    for p in P:
        for f in sorted(p.files):
            if not (f.startswith("textures/entity/") and f.endswith(".texture_set.json")):
                continue
            path = f[: -len(".texture_set.json")]
            if path in done:
                continue
            done.add(path)
            top = next(q for q in P if any(q.has(path + e) for e in EXT + (".texture_set.json",)))
            r = {"path": path, "set_pack": p.name, "top_pack": top.name}
            if top is not p:
                r["note"] = "SHADOWED: a higher pack holds a plain image at this path"
            try:
                ts = p.json(f)["minecraft:texture_set"]
            except Exception as e:  # noqa: BLE001
                r["note"] = f"unreadable {e}"
                rows.append(r)
                continue
            bd = path.rsplit("/", 1)[0]
            col = layer(p, bd, ts.get("color", "")) if isinstance(ts.get("color"), str) else None
            mk = next((k for k in ts if k.startswith("metalness")), None)
            mv = ts.get(mk)
            if not col or not isinstance(mv, str):
                r["mers"] = mv
                rows.append(r)
                continue
            ml = layer(p, bd, mv)
            if not ml:
                r["note"] = "MERS layer missing"
                rows.append(r)
                continue
            c = np.asarray(Image.open(io.BytesIO(p.read(col))).convert("RGBA"))
            m = Image.open(io.BytesIO(p.read(ml))).convert("RGBA")
            if m.size != (c.shape[1], c.shape[0]):
                m = m.resize((c.shape[1], c.shape[0]), Image.NEAREST)
                r["resized"] = True
            m = np.asarray(m).astype(float)
            op = c[..., 3] > 0
            if not op.any():
                rows.append(r)
                continue
            M, E, R, S = (m[..., i][op] for i in range(4))
            if mk == "metalness_emissive_roughness":
                S = np.zeros_like(M)
            r.update({"layer": mk, "metal_mean": round(M.mean() / 255, 3), "metal_share": round(float((M > 25).mean()), 3),
                      "rough_mean": round(R.mean() / 255, 3), "smooth_share": round(float((R < 128).mean()), 3),
                      "very_smooth_share": round(float((R < 64).mean()), 3), "sss_mean": round(S.mean() / 255, 3),
                      "emissive_share": round(float((E > 25).mean()), 3), "normal": bool(ts.get("normal"))})
            rows.append(r)
    out = ROOT / "_docs/mers/MOB-MERS-CENSUS.json"
    out.write_text(json.dumps(rows, indent=1))
    measured = [r for r in rows if "rough_mean" in r]
    print(f"entity texture sets {len(rows)} · measured {len(measured)}")
    shiny = sorted(measured, key=lambda r: (r["smooth_share"] + r["metal_share"]), reverse=True)
    for r in shiny[:40]:
        print(f"  {r['path'][16:]:70s} {r['set_pack']:14s} rough {r['rough_mean']:.2f} smooth<0.5 {r['smooth_share']:.2f} "
              f"metal {r['metal_share']:.2f} sss {r['sss_mean']:.2f} {r.get('note', '')}")
    return rows


if __name__ == "__main__":
    main()

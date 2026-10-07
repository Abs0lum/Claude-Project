#!/usr/bin/env python3
"""verify_rp06_149.py — gate for RP-06 v1.4.9 (D-C267). Static checks only rule OUT (P1); the witness rules IN.
  A  the diff vs v1.4.8 is exactly the intended files
  B  every JSON parses; bones unique, parents exist, no cycles (the 5 touched geometries)
  C  creeper armor RC gated on query.is_powered
  D  husk: every limb cube has per-face uv inside 64x64, and those texture regions are opaque (the mechanism, in numbers:
     alpha coverage before = what the missing uv sampled, after = what the new uv samples)
  E  pillager rightItem/leftItem under the forearms; vindicator `arms` holds the 3 crossed cubes, body keeps 2, rightItem present
  F  witch arms/arms2 (3 cubes, rest -43 X) inside 64x128, arm faces mostly opaque
  G  manifest 1.4.9, header uuid unchanged
Writes _logs/rp06_149_gate.json; exit 1 on any FAIL."""
import filecmp, json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp06-148", ROOT / "_build/rp06-149"
EXPECTED = {"entity/creeper.entity.json", "models/entity/pw_husk.geo.json", "models/entity/pw_pillager.geo.json",
            "models/entity/pw_vindicator.geo.json", "models/entity/pw_witch.geo.json", "manifest.json"}
results = []


def check(tag, ok, msg):
    results.append({"tag": tag, "ok": bool(ok), "msg": msg}); print(f"{'PASS' if ok else 'FAIL'} {tag}: {msg}")


def jl(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def files(root):
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def g_of(root, name):
    return jl(root / f"models/entity/{name}.geo.json")["minecraft:geometry"][0]


def bone(g, n):
    return next((b for b in g["bones"] if b["name"] == n), None)


def rect_alpha(img, rect, tw, th):
    """alpha-coverage (fraction of texels with alpha >= 128) of a uv rect given in geometry texture units."""
    H, W = img.shape[:2]; sx, sy = W / tw, H / th
    u0, v0, u1, v1 = rect
    x0, x1 = sorted((int(round(u0 * sx)), int(round(u1 * sx)))); y0, y1 = sorted((int(round(v0 * sy)), int(round(v1 * sy))))
    reg = img[max(0, y0):min(H, y1), max(0, x0):min(W, x1), 3]
    return float((reg >= 128).mean()) if reg.size else 0.0


def box_rects(u, v, s):
    w, h, d = s
    return {"up": (u + d, v, u + d + w, v + d), "down": (u + d + w, v, u + d + 2 * w, v + d), "west": (u, v + d, u + d, v + d + h),
            "north": (u + d, v + d, u + d + w, v + d + h), "east": (u + d + w, v + d, u + 2 * d + w, v + d + h), "south": (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h)}


def face_rects(c):
    uv = c.get("uv", [0, 0])
    if isinstance(uv, dict):
        return {f: (r["uv"][0], r["uv"][1], r["uv"][0] + r["uv_size"][0], r["uv"][1] + r["uv_size"][1]) for f, r in uv.items()}
    return box_rects(uv[0], uv[1], c["size"])


def main():
    # A — diff
    fo, fn = files(OLD), files(NEW)
    changed = {f for f in fo & fn if not filecmp.cmp(OLD / f, NEW / f, shallow=False)}
    check("A1", fo == fn, f"same file set ({len(fn)} files)" if fo == fn else f"added {sorted(fn - fo)} removed {sorted(fo - fn)}")
    check("A2", changed == EXPECTED, f"changed = {sorted(changed)}")
    # B — parse + bone sanity
    for name in ("pw_husk", "pw_pillager", "pw_vindicator", "pw_witch"):
        g = g_of(NEW, name); names = [b["name"] for b in g["bones"]]
        by = {b["name"]: b for b in g["bones"]}
        cyc = False
        for b in g["bones"]:
            seen, n = set(), b["name"]
            while n:
                if n in seen: cyc = True; break
                seen.add(n); n = by[n].get("parent") if n in by else None
        check(f"B-{name}", len(names) == len(set(names)) and all((b.get("parent") in by) for b in g["bones"] if b.get("parent")) and not cyc,
              f"{len(names)} bones, unique, parents exist, acyclic")
    jl(NEW / "entity/creeper.entity.json"); jl(NEW / "manifest.json")
    # C — creeper
    rc = jl(NEW / "entity/creeper.entity.json")["minecraft:client_entity"]["description"]["render_controllers"]
    check("C", rc == ["controller.render.creeper", {"controller.render.creeper_armor": "query.is_powered"}], f"render_controllers = {rc}")
    # D — husk
    img = np.asarray(Image.open(NEW / "textures/entity/zombie/husk.png").convert("RGBA"))
    gn, go = g_of(NEW, "pw_husk"), g_of(OLD, "pw_husk")
    tw, th = gn["description"]["texture_width"], gn["description"]["texture_height"]
    limbs = ["rightArm", "rightForearm", "leftArm", "leftForearm", "rightLeg", "rightShin", "leftLeg", "leftShin"]
    worst_new, rows = 1.0, []
    for bn in limbs:
        cn, co = bone(gn, bn)["cubes"][0], bone(go, bn)["cubes"][0]
        rn = face_rects(cn); ro = face_rects(co)
        inside = all(0 <= min(r[0], r[2]) and max(r[0], r[2]) <= tw and 0 <= min(r[1], r[3]) and max(r[1], r[3]) <= th for r in rn.values())
        sides = ("north", "east", "south", "west")
        an = min(rect_alpha(img, rn[f], tw, th) for f in sides); ao = min(rect_alpha(img, ro[f], tw, th) for f in sides)
        worst_new = min(worst_new, an); rows.append(f"{bn}: before {ao:.2f} -> after {an:.2f}{'' if inside else ' OUT-OF-RANGE'}")
        check(f"D-{bn}", isinstance(cn.get("uv"), dict) and inside and an >= 0.9, f"per-face uv in range; side-face alpha coverage before {ao:.2f} after {an:.2f}")
    # E — pillager / vindicator
    gp = g_of(NEW, "pw_pillager")
    ri, li = bone(gp, "rightItem"), bone(gp, "leftItem")
    check("E1", ri and ri["parent"] == "rightForearm" and ri["pivot"] == [-6, 15, 1] and li and li["parent"] == "leftForearm", f"pillager rightItem {ri} leftItem {li}")
    gv = g_of(NEW, "pw_vindicator")
    arms, body, rv = bone(gv, "arms"), bone(gv, "body"), bone(gv, "rightItem")
    check("E2", arms and len(arms.get("cubes", [])) == 3 and "rotation" not in arms and len(body["cubes"]) == 2, f"vindicator arms cubes {len(arms.get('cubes', [])) if arms else None}, body cubes {len(body['cubes'])}, arms pivot {arms and arms['pivot']}")
    check("E3", rv and rv["parent"] == "rightForearm", f"vindicator rightItem {rv}")
    # F — witch
    gw = g_of(NEW, "pw_witch"); wimg = np.asarray(Image.open(NEW / "textures/entity/witch.png").convert("RGBA"))
    a, a2 = bone(gw, "arms"), bone(gw, "arms2")
    twf, thf = gw["description"]["texture_width"], gw["description"]["texture_height"]
    ok = a and a2 and a2.get("parent") == "arms" and len(a2.get("cubes", [])) == 3 and a2.get("rotation") == [-43, 0, 0]
    cov = []
    if ok:
        for c in a2["cubes"]:
            rr = face_rects(c)
            cov.append(round(float(np.mean([rect_alpha(wimg, r, twf, thf) for r in rr.values()])), 2))
            ok = ok and all(0 <= min(r[0], r[2]) and max(r[0], r[2]) <= twf and 0 <= min(r[1], r[3]) and max(r[1], r[3]) <= thf for r in rr.values())
    check("F", ok and cov and min(cov) >= 0.5, f"witch arms pivot {a and a['pivot']} arms2 rot {a2 and a2.get('rotation')} cubes 3, mean face alpha coverage per cube {cov}")
    # G — manifest
    mo, mn = jl(OLD / "manifest.json"), jl(NEW / "manifest.json")
    check("G", mn["header"]["version"] == [1, 4, 9] and mn["header"]["uuid"] == mo["header"]["uuid"] and all(m["version"] == [1, 4, 9] for m in mn["modules"]),
          f"version {mn['header']['version']} uuid kept")
    fails = [r for r in results if not r["ok"]]
    json.dump({"results": results, "husk_rows": rows, "pass": len(results) - len(fails), "total": len(results)}, open(ROOT / "_logs/rp06_149_gate.json", "w"), indent=1)
    print(f"GATE {'OPEN' if not fails else 'CLOSED'} {len(results) - len(fails)}/{len(results)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

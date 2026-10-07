#!/usr/bin/env python3
"""mob_pbr_reach.py — his 17:47 report: the buffalo "actually LACKS its MERS and normal maps. Make sure they're applied to
each mob correctly across all mobs." (AMBIGUOUS 'I think' -> rigorous census of EVERY creature.)

Engine rule used (same as the block census D-C421, witnessed on grass/dirt): per texture PATH the top pack holding ANY image
at that path draws it, and a texture set only works inside the pack that holds it (its layers resolve in its own pack).
So for every client entity (top pack per identifier) and every texture it names:
  OK          the drawing pack holds <path>.texture_set.json, and its MERS + normal/heightmap layer files exist there
  SHADOWED    the drawing pack has a plain image; a LOWER pack has the set (the set never reaches the screen)
  NO_SET      no pack has a set for this path
  BROKEN      the set names a layer file that does not exist in its pack
  NO_NORMAL   set present, MERS present, no normal / heightmap layer
  NO_MERS     set present, no MERS layer (only colour / normal)
  NO_IMAGE    no pack (vanilla included) has the picture at all
Usage: PW_STACK=<name> python3 tools/mob_pbr_reach.py [label]  -> _docs/mers/MOB-PBR-REACH-<label>.json"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as SN  # noqa: E402

EXT = (".png", ".tga", ".jpg")


def layer_file(p, base_dir, name):
    if not isinstance(name, str):
        return "inline"                       # a colour value instead of a file
    for e in EXT:
        if p.has(f"{base_dir}/{name}{e}"):
            return f"{base_dir}/{name}{e}"
    return None


def set_status(p, path):
    ts_file = path + ".texture_set.json"
    try:
        ts = p.json(ts_file)["minecraft:texture_set"]
    except Exception as e:  # noqa: BLE001
        return "BROKEN", {"error": f"unreadable set {e}"}
    bd = path.rsplit("/", 1)[0]
    mers_key = next((k for k in ("metalness_emissive_roughness_subsurface", "metalness_emissive_roughness") if k in ts), None)
    nrm_key = next((k for k in ("normal", "heightmap") if k in ts), None)
    info = {"set_pack": p.name, "mers": None, "normal": None}
    missing = []
    for key, slot in ((mers_key, "mers"), (nrm_key, "normal")):
        if key is None:
            continue
        f = layer_file(p, bd, ts[key])
        info[slot] = f"{key}={ts[key]}" if f else None
        if f is None:
            missing.append(f"{key}:{ts[key]}")
    if missing:
        info["missing"] = missing
        return "BROKEN", info
    if mers_key is None:
        return "NO_MERS", info
    if nrm_key is None:
        return "NO_NORMAL", info
    return "OK", info


def client_entities(P):
    out = {}
    for i, p in enumerate(P):
        for f in sorted(p.files):
            if not (f.startswith("entity/") and f.endswith(".json")):
                continue
            try:
                d = p.json(f)
            except Exception:  # noqa: BLE001
                continue
            ce = (d or {}).get("minecraft:client_entity")
            if not ce:
                continue
            desc = ce.get("description", {})
            ident = desc.get("identifier")
            if ident and ident not in out:
                out[ident] = (p.name, f, desc.get("textures") or {})
    return out


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "installed"
    P = SN.packs()
    rows, counts = [], Counter()
    for ident, (pack, f, textures) in sorted(client_entities(P).items()):
        for tkey, path in textures.items():
            if not isinstance(path, str):
                continue
            draw_p, draw_f = SN.find_image(P, path)
            r = {"entity": ident, "client_pack": pack, "texture_key": tkey, "path": path}
            if draw_p is None:
                st, info = "NO_IMAGE", {}
            else:
                r["draw_pack"] = draw_p.name
                if draw_p.has(path + ".texture_set.json"):
                    st, info = set_status(draw_p, path)
                else:
                    lower = next((q for q in P[P.index(draw_p) + 1:] if q.has(path + ".texture_set.json")), None)
                    st, info = ("SHADOWED", {"set_in": lower.name}) if lower else ("NO_SET", {})
            r["status"] = st
            r.update(info)
            rows.append(r)
            counts[st] += 1
    vanilla_only = sum(1 for r in rows if r.get("draw_pack", "").startswith("vanilla"))
    out = ROOT / f"_docs/mers/MOB-PBR-REACH-{label}.json"
    out.write_text(json.dumps({"stack": [p.name for p in P], "counts": counts, "vanilla_drawn": vanilla_only, "rows": rows}, indent=1))
    print(label, dict(counts), "textures", len(rows), "drawn by vanilla", vanilla_only)
    by_pack = Counter((r["status"], r.get("draw_pack", "-")) for r in rows if r["status"] != "OK")
    for k, v in sorted(by_pack.items(), key=lambda kv: -kv[1])[:20]:
        print("  ", k, v)


if __name__ == "__main__":
    main()

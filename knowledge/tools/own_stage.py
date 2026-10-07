#!/usr/bin/env python3
"""own_stage.py — OWNERSHIP FIX planner + bark stager (his 00:07 / 00:53 rulings).

Problem (D-C437): a terrain key defined in pack Kp points at a path whose top image + texture set live in another pack
Ip. His TV shows those blocks without depth/shine (dodecagon bark). Rule adopted: key, image and set live in ONE pack.

Operations (planned here, applied by build_round_1002a.py):
  BARK  keys defined in RP-01 (dodecagon trunk keys): the top image + its set layers are COPIED into RP-01 under
        textures/blocks/bark/<stem>.* (a new path, so no two packs share a path) and the RP-01 key is re-pointed there.
  LIB   every tree species' bark (sides of *_log / *_wood, all 9 tree species) is also copied into RP-01 bark/ with
        its maps — his 00:53 ask (Tectonic holds all bark), even where no RP-01 key uses it yet.
  MOVE  any other key whose paths all resolve to ONE image pack Ip != Kp: the key definition moves to Ip (added to Ip's
        terrain_texture.json, removed from Kp's), so key + image + set are together. No image is duplicated.
  VAN   a key defined only by vanilla: LISTED ONLY, not applied (the standard override; dirt/grass/stone depth seen).
  COPY  a key whose paths resolve to several packs: images + sets copied into Kp under textures/blocks/own/<stem>.
Scope: every key used by BP block material_instances (BP-02 1.3.200, BP-03 1.3.134) and every key used by any
blocks.json in the stack (vanilla blocks included).
Output: _staging/own/<pack key>/... (files) + _docs/blocks/OWN-PLAN.json."""
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import os  # noqa: E402

os.environ["PW_STACK"] = "tier"
import stack_now as S  # noqa: E402

STAGE = ROOT / "_staging/own"
PKEY = {"RP-01": "rp01", "RP-03": "rp03", "RP-04": "rp04", "RP-05": "rp05", "RP-10": "rp10"}
SPECIES = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak")
EXT = (".png", ".tga", ".jpg")


def img_of(p, path):
    return next((path + e for e in EXT if p.has(path + e)), None)


def set_files(p, path):
    """the set json + every layer file it names (same folder, same pack)."""
    ts = p.json(path + ".texture_set.json")
    out = [path + ".texture_set.json"]
    d = path.rsplit("/", 1)[0]
    for k, v in ts["minecraft:texture_set"].items():
        if k == "color" or not isinstance(v, str) or v.startswith("#"):
            continue
        f = img_of(p, f"{d}/{v}")
        if f:
            out.append(f)
    return ts, out


def main():
    P = S.packs()
    T = S.terrain(P)
    by = {p.name: p for p in P}
    used = set()
    for f in glob.glob(str(ROOT / "_build/bp02-200/blocks/*.json")) + glob.glob(str(ROOT / "_build/bp03-134/blocks/*.json")):
        used |= set(re.findall(r'"texture"\s*:\s*"([^"]+)"', open(f).read()))
    blocks = {}
    for p in reversed(P):
        for k, v in (p.json("blocks.json") or {}).items():
            if isinstance(v, dict):
                blocks[k] = v
    for v in blocks.values():
        t = v.get("textures")
        used |= {t} if isinstance(t, str) else set(t.values()) if isinstance(t, dict) else set()
    trunk_keys = {k for k in used if re.match(r"pw_(%s)_(young|mature|old|elder)_log_v\d+$" % "|".join(SPECIES), k)}
    plan = {"BARK": [], "LIB": [], "MOVE": [], "VAN": [], "COPY": [], "SKIP": []}
    staged = Counter()

    def stage(pack_name, src_pack, src_rel, dst_rel):
        dst = STAGE / PKEY[pack_name[:5]] / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src_pack.read(src_rel))
        staged[pack_name[:5]] += 1

    def copy_set(dst_pack, src_pack, path, new_dir):
        """copy image + set + layers of `path` from src_pack into dst_pack under new_dir; returns the new path."""
        stem = path.rsplit("/", 1)[1]
        new_path = f"{new_dir}/{stem}"
        img = img_of(src_pack, path)
        stage(dst_pack, src_pack, img, new_path + img[len(path):])
        if src_pack.has(path + ".texture_set.json"):
            ts, files = set_files(src_pack, path)
            for f in files[1:]:
                stage(dst_pack, src_pack, f, f"{new_dir}/{f.rsplit('/', 1)[1]}")
            dst = STAGE / PKEY[dst_pack[:5]] / (new_path + ".texture_set.json")
            dst.write_text(json.dumps(ts, indent=1))
            staged[dst_pack[:5]] += 1
        return new_path

    for key in sorted(used):
        if key not in T:
            continue
        kp, d, _ = T[key]
        paths = S.paths_of(d)
        res = []
        for path in paths:
            ip = next((p for p in P if img_of(p, path)), None)
            res.append((path, ip.name if ip else None, bool(ip and ip.has(path + ".texture_set.json"))))
        bad = [r for r in res if r[1] and r[1] != kp and r[2]]
        if not bad:
            continue
        if key in trunk_keys and kp.startswith("RP-01"):
            new = {}
            for path, ipn, _ in res:
                if ipn and ipn != kp:
                    new[path] = copy_set(kp, by[ipn], path, "textures/blocks/bark")
            plan["BARK"].append({"key": key, "pack": kp, "repoint": new})
            continue
        ips = {r[1] for r in res if r[1]}
        if len(ips) == 1:
            ip = ips.pop()
            if kp.startswith("vanilla"):
                plan["VAN"].append({"key": key, "to": ip, "applied": False,
                                    "why": "vanilla key + our image/set = normal texture-pack override (witnessed working)"})
            elif ip.startswith("vanilla"):
                plan["SKIP"].append({"key": key, "why": "image only in vanilla"})
            else:
                between = [p.name for p in P[P.index(by[kp]) + 1:P.index(by[ip])] + P[P.index(by[ip]) + 1:P.index(by[kp])]
                           if (p.json("textures/terrain_texture.json") or {}).get("texture_data", {}).get(key) is not None]
                plan["MOVE"].append({"key": key, "from": kp, "to": ip, "def": d, "also_defined_between": between})
        else:
            if kp.startswith("vanilla"):
                plan["SKIP"].append({"key": key, "why": f"vanilla key, paths in {sorted(ips)}"})
                continue
            new = {}
            for path, ipn, _ in res:
                if ipn and ipn != kp and not ipn.startswith("vanilla"):
                    new[path] = copy_set(kp, by[ipn], path, "textures/blocks/own")
            plan["COPY"].append({"key": key, "pack": kp, "repoint": new})
    # LIB: all species bark (log / wood sides) into RP-01
    done = {v for b in plan["BARK"] for v in b["repoint"].values()}
    rp01 = next(p.name for p in P if p.name.startswith("RP-01"))
    for blk, v in sorted(blocks.items()):
        m = re.match(r"(minecraft:)?(%s)_(log|wood)$" % "|".join(SPECIES), blk)
        if not m:
            continue
        t = v.get("textures")
        side = t if isinstance(t, str) else (t.get("side") if isinstance(t, dict) else None)
        if not side or side not in T:
            continue
        for path in S.paths_of(T[side][1]):
            ip = next((p for p in P if img_of(p, path)), None)
            if ip is None or ip.name.startswith("vanilla"):
                continue
            stem = path.rsplit("/", 1)[1]
            if f"textures/blocks/bark/{stem}" in done:
                continue
            if ip.name.startswith("RP-01") and ip.has(path + ".texture_set.json"):
                plan["LIB"].append({"block": blk, "path": path, "note": "already in RP-01 with its set"})
                continue
            if not ip.has(path + ".texture_set.json"):
                plan["LIB"].append({"block": blk, "path": path, "note": f"NO SET in {ip.name} — later"})
                continue
            new = copy_set(rp01, ip, path, "textures/blocks/bark")
            done.add(new)
            plan["LIB"].append({"block": blk, "path": path, "copied_to": new, "from": ip.name})
    (ROOT / "_docs/blocks/OWN-PLAN.json").write_text(json.dumps(plan, indent=1))
    print({k: len(v) for k, v in plan.items()}, "staged files", dict(staged))
    print("MOVE by (from,to):", Counter((m["from"][:5], m["to"][:5]) for m in plan["MOVE"]))
    print("MOVE with a key defined in between:", [m["key"] for m in plan["MOVE"] if m["also_defined_between"]])
    print("VAN to:", Counter(v["to"][:5] for v in plan["VAN"]), "SKIP:", plan["SKIP"][:6])


if __name__ == "__main__":
    main()

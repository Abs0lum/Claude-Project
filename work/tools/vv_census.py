#!/usr/bin/env python3
"""vv_census.py — Vibrant Visuals (VV) load census of Bedrock resource packs, for the PS5 VV join crash (CE-108255-1).

Why: the PS5 cannot join the phone-hosted world with Vibrant Visuals ON (his witness 2026-10-07); with VV off it can.
Everything VV adds on top of the classic renderer is RP data: texture_set.json PBR maps (normal / heightmap / MER(S)),
`*_vv.png` variants, the atmospherics / lighting / fog / water / color_grading / cubemap / local_lighting JSON. This tool
measures that layer per pack so a pack (or a file class) that is out of line can be named with numbers, and lists every
file the engine may reject or choke on.

Reads packs as folders or as .mcpack/.zip archives (never extracts to disk). Image sizes come from headers (PIL lazy open).

Usage:
    python3 vv_census.py PACK [PACK ...] [--json out.json] [--md out.md]
Each PACK = a resource-pack folder (with manifest.json) or a .mcpack/.zip.

Output per pack:
  * manifest: name, version, capabilities (pbr / raytraced), min_engine_version, has subpacks
  * texture sets: count, by format_version; field usage; INVALID list:
      - normal AND heightmap both set (mutually exclusive)
      - MER/MERS given as an array of the wrong length (1.16.100 = 3, 1.21.30 MERS = 4; CLAUDE-AR §7: 3-value MERS forbidden)
      - a referenced map / colour file missing in the same pack (H-18: same-pack resolution)
      - JSON that does not parse
  * images: count + megapixels by class (colour, normal, heightmap, MER(S), *_vv, cubemap, other) and by area
    (blocks, entity, items, environment, particle, ui, other)
  * risk lists: non-power-of-two sides (except vertical flipbook strips n*w x w), any side > 4096, any side > 8192,
    palette / 16-bit / unusual modes, unreadable images
  * VV JSON inventory: atmospherics, lighting, fogs, water, color_grading, cubemaps, local_lighting, point_lights,
    client_biome counts, each parsed (parse failures listed)
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
IMG_EXT = (".png", ".tga", ".jpg", ".jpeg")
VV_DIRS = ("atmospherics", "lighting", "fogs", "water", "color_grading", "cubemaps", "local_lighting",
           "point_lights", "biomes_client", "client_biome", "pbr")
MAP_FIELDS = ("color", "normal", "heightmap", "metalness_emissive_roughness",
              "metalness_emissive_roughness_subsurface")


class Pack:
    """Uniform read access to a pack folder or archive; paths are '/'-separated and relative to the pack root."""

    def __init__(self, src: str):
        self.src = src
        self.zip = None
        if os.path.isdir(src):
            self.files = []
            for d, _, fs in os.walk(src):
                for f in fs:
                    self.files.append(os.path.relpath(os.path.join(d, f), src).replace(os.sep, "/"))
            self.root = ""
        else:
            self.zip = zipfile.ZipFile(src)
            names = [n for n in self.zip.namelist() if not n.endswith("/")]
            mans = sorted((n for n in names if n.endswith("manifest.json")), key=lambda n: n.count("/"))
            self.root = mans[0][: -len("manifest.json")] if mans else ""
            self.files = [n[len(self.root):] for n in names if n.startswith(self.root)]
        self.lower = {f.lower(): f for f in self.files}

    def read(self, rel: str) -> bytes:
        if self.zip:
            return self.zip.read(self.root + rel)
        with open(os.path.join(self.src, rel), "rb") as fh:
            return fh.read()

    def size(self, rel: str) -> int:
        if self.zip:
            return self.zip.getinfo(self.root + rel).file_size
        return os.path.getsize(os.path.join(self.src, rel))

    def open_image(self, rel: str):
        if self.zip:
            return Image.open(io.BytesIO(self.read(rel)))
        return Image.open(os.path.join(self.src, rel))


def load_json(raw: bytes):
    """Bedrock JSON allows // and /* */ comments; strip them (outside strings) before parsing."""
    txt = raw.decode("utf-8-sig", errors="replace")
    out, i, n, in_str = [], 0, len(txt), False
    while i < n:
        c = txt[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(txt[i + 1]); i += 2; continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True; out.append(c)
        elif txt.startswith("//", i):
            j = txt.find("\n", i); i = n if j < 0 else j; continue
        elif txt.startswith("/*", i):
            j = txt.find("*/", i + 2); i = n if j < 0 else j + 2; continue
        else:
            out.append(c)
        i += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))


def is_pow2(v: int) -> bool:
    return v > 0 and (v & (v - 1)) == 0


def area_of(rel: str) -> str:
    p = rel.lower()
    for key, name in (("textures/blocks/", "blocks"), ("textures/entity/", "entity"), ("textures/items/", "items"),
                      ("textures/environment/", "environment"), ("textures/particle", "particle"),
                      ("textures/ui/", "ui"), ("textures/gui/", "ui"), ("textures/models/", "models"),
                      ("textures/painting", "painting")):
        if key in p:
            return name
    return "other"


def resolve(pack: Pack, base_dir: str, ref: str):
    """A texture_set field names a file in the same folder, without extension."""
    for ext in IMG_EXT:
        cand = f"{base_dir}/{ref}{ext}" if base_dir else f"{ref}{ext}"
        hit = pack.lower.get(cand.lower())
        if hit:
            return hit
    return None


def census(src: str) -> dict:
    pack = Pack(src)
    rep: dict = {"source": os.path.basename(src.rstrip("/")), "files": len(pack.files)}
    # manifest
    try:
        man = load_json(pack.read("manifest.json"))
        h = man.get("header", {})
        rep["manifest"] = {"name": h.get("name"), "version": h.get("version"),
                           "min_engine_version": h.get("min_engine_version"),
                           "capabilities": man.get("capabilities", []),
                           "subpacks": len(man.get("subpacks", []) or [])}
    except Exception as e:  # noqa: BLE001 - report, never stop the census
        rep["manifest"] = {"error": repr(e)}

    # texture sets
    role_of: dict[str, str] = {}
    ts_fmt, ts_fields, invalid = Counter(), Counter(), []
    sets = [f for f in pack.files if f.lower().endswith(".texture_set.json")]
    for f in sets:
        base_dir = f.rsplit("/", 1)[0] if "/" in f else ""
        try:
            js = load_json(pack.read(f))
        except Exception as e:  # noqa: BLE001
            invalid.append({"file": f, "why": f"json: {e}"}); continue
        fmt = str(js.get("format_version"))
        ts_fmt[fmt] += 1
        body = js.get("minecraft:texture_set", {}) or {}
        for k in body:
            ts_fields[k] += 1
        if "normal" in body and "heightmap" in body:
            invalid.append({"file": f, "why": "normal and heightmap both set"})
        for k in MAP_FIELDS:
            v = body.get(k)
            if v is None:
                continue
            if isinstance(v, list):
                # MER = 3 values; MERS (…_subsurface) = 4 values (CLAUDE-AR §7: a 3-value MERS is forbidden);
                # colour = RGB or RGBA; normal / heightmap must be files, never uniform arrays.
                allowed = {"metalness_emissive_roughness": (3,),
                           "metalness_emissive_roughness_subsurface": (4,),
                           "color": (3, 4)}.get(k, ())
                if len(v) not in allowed:
                    invalid.append({"file": f, "why": f"{k} array of {len(v)} values (allowed {allowed or 'none'})"})
                continue
            if isinstance(v, str) and v.startswith("#"):
                continue  # hex colour
            hit = resolve(pack, base_dir, str(v))
            if not hit:
                invalid.append({"file": f, "why": f"{k} -> '{v}' not found in this pack"})
            else:
                role_of[hit] = {"color": "colour", "normal": "normal", "heightmap": "heightmap"}.get(k, "mers")
    rep["texture_sets"] = {"count": len(sets), "format_version": dict(ts_fmt), "fields": dict(ts_fields),
                           "invalid_count": len(invalid), "invalid": invalid[:400]}

    # images
    by_class, by_area = defaultdict(lambda: [0, 0.0]), defaultdict(lambda: [0, 0.0])
    npot, big4k, big8k, odd_mode, unreadable = [], [], [], [], []
    largest = []
    for f in pack.files:
        if not f.lower().endswith(IMG_EXT):
            continue
        low = f.lower()
        try:
            im = pack.open_image(f)
            w, h = im.size
            mode = im.mode
        except Exception as e:  # noqa: BLE001
            unreadable.append({"file": f, "why": repr(e)[:120]}); continue
        mpx = w * h / 1e6
        if f in role_of:
            cls = role_of[f]
        elif "overworld_cubemap" in low or "/cubemap" in low:
            cls = "cubemap"
        elif re.search(r"_vv\.(png|tga|jpe?g)$", low):
            cls = "vv_variant"
        elif re.search(r"_n\.(png|tga)$", low) or low.endswith("_normal.png"):
            cls = "normal"
        elif re.search(r"_(mer|mers)\.(png|tga)$", low):
            cls = "mers"
        elif re.search(r"_(h|height|heightmap)\.(png|tga)$", low):
            cls = "heightmap"
        else:
            cls = "colour"
        by_class[cls][0] += 1; by_class[cls][1] += mpx
        a = area_of(f); by_area[a][0] += 1; by_area[a][1] += mpx
        strip = w > 0 and h % w == 0 and is_pow2(w)
        if not (is_pow2(w) and (is_pow2(h) or strip)):
            npot.append({"file": f, "size": [w, h], "class": cls})
        if max(w, h) > 4096:
            big4k.append({"file": f, "size": [w, h], "class": cls})
        if max(w, h) > 8192:
            big8k.append({"file": f, "size": [w, h], "class": cls})
        if mode not in ("RGBA", "RGB", "L", "LA"):
            odd_mode.append({"file": f, "mode": mode, "class": cls})
        largest.append((mpx, f, w, h, cls))
    largest.sort(reverse=True)
    rep["images"] = {
        "by_class": {k: {"count": v[0], "Mpx": round(v[1], 2)} for k, v in sorted(by_class.items())},
        "by_area": {k: {"count": v[0], "Mpx": round(v[1], 2)} for k, v in sorted(by_area.items())},
        "total_Mpx": round(sum(v[1] for v in by_class.values()), 2),
        "pbr_Mpx": round(sum(by_class[k][1] for k in ("normal", "heightmap", "mers")), 2),
        "non_power_of_two": {"count": len(npot), "list": npot[:200]},
        "side_over_4096": big4k[:200], "side_over_8192": big8k[:200],
        "unusual_mode": {"count": len(odd_mode), "list": odd_mode[:200]},
        "unreadable": unreadable[:100],
        "largest_20": [{"file": f, "size": [w, h], "Mpx": round(m, 2), "class": c} for m, f, w, h, c in largest[:20]],
    }

    # VV JSON inventory
    inv, bad = Counter(), []
    for f in pack.files:
        top = f.split("/", 1)[0].lower()
        if top in VV_DIRS and f.lower().endswith(".json"):
            inv[top] += 1
            try:
                load_json(pack.read(f))
            except Exception as e:  # noqa: BLE001
                bad.append({"file": f, "why": repr(e)[:160]})
    rep["vv_json"] = {"counts": dict(inv), "parse_failures": bad}
    return rep


def to_md(reports: list[dict]) -> str:
    rows = ["| pack | version | pbr cap | texture sets | invalid sets | images Mpx | PBR maps Mpx | *_vv | cubemap | NPOT | >4096 | odd mode | VV json |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in reports:
        m, i, t = r.get("manifest", {}), r["images"], r["texture_sets"]
        caps = ",".join(m.get("capabilities", []) or []) if isinstance(m.get("capabilities"), list) else m.get("capabilities")
        vv = i["by_class"].get("vv_variant", {}).get("count", 0)
        cube = i["by_class"].get("cubemap", {}).get("count", 0)
        rows.append(f"| {m.get('name') or r['source']} | {m.get('version')} | {caps} | {t['count']} | {t['invalid_count']} | "
                    f"{i['total_Mpx']} | {i['pbr_Mpx']} | {vv} | {cube} | {i['non_power_of_two']['count']} | "
                    f"{len(i['side_over_4096'])} | {i['unusual_mode']['count']} | {sum(r['vv_json']['counts'].values())} |")
    tot = sum(r["images"]["total_Mpx"] for r in reports)
    pbr = sum(r["images"]["pbr_Mpx"] for r in reports)
    rows.append(f"\nAll packs: images {tot:.1f} Mpx, of which PBR maps {pbr:.1f} Mpx.")
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("packs", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    reports = []
    for p in a.packs:
        print(f"[vv_census] {p}", file=sys.stderr)
        reports.append(census(p))
    md = to_md(reports)
    print(md)
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(reports, fh, indent=1)
    if a.md:
        with open(a.md, "w") as fh:
            fh.write(md + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

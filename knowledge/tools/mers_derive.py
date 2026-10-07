#!/usr/bin/env python3
"""mers_derive.py — MERS program step 2 (D-C367, his M1 = (c) for every mob).

Writes, for every texture in _docs/mers/MERS-INVENTORY.json that needs one, a MERS map (+ a normal map for
tier 1) and a texture_set.json into a STAGING tree that mirrors the pack holding the colour:
    _staging/mers/<pack>/<rel>_mers.png
    _staging/mers/<pack>/<rel>_n.png                (tier 1 only: Patrix's own LabPBR normal)
    _staging/mers/<pack>/<rel>.texture_set.json     (format 1.21.30; colour + MERS [+ normal])

Tier 1   Patrix's own LabPBR _s -> MERS by Lesson #156 (resampled to our colour's size when needed).
Derive   per-pixel material from the body part the pixel is painted on (cube face -> bone -> part token) and
         the creature's material class (body plan + id keywords). Emissive is always 0 here (glow stays with
         Patrix's own maps and the glow-layer materials). Roughness is nudged by local shading (crevices rougher).
Vanilla  kept as Mojang's map, except the flat placeholders listed in MR2-vanilla-flatness.json (derived).

Channel values are 0-255: R = metalness, G = emissive, B = roughness, A = subsurface.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
INV = ROOT / "_docs/mers/MERS-INVENTORY.json"
CENSUS = ROOT / "_docs/standard/SKELETON-CENSUS.json"
FLAT = ROOT / "_docs/mers/MR2-vanilla-flatness.json"
STAGE = ROOT / "_staging/mers"
VANILLA = ROOT / "_intake/bedrock-samples/resource_pack"
GEO_STACK = [ROOT / "_build" / d for d in ("rp07-1438", "rp06-1424", "rp08-148", "rp04-142", "rp01-107")] + [VANILLA]

# ---------------------------------------------------------------- material model
# (metalness, emissive, roughness, subsurface) per material class
MATERIALS = {
    "fur":      (0, 0, 225, 30),
    "feather":  (0, 0, 210, 20),
    "skin":     (0, 0, 190, 70),
    "scale":    (0, 0, 150, 15),
    "chitin":   (0, 0, 120, 10),
    "wet":      (0, 0, 85, 90),
    "jelly":    (0, 0, 60, 200),
    "cloth":    (0, 0, 205, 40),
    "wood":     (0, 0, 210, 12),
    "metal":    (255, 0, 110, 0),
    "stone":    (0, 0, 200, 5),
    "eggshell": (0, 0, 120, 10),
    "default":  (0, 0, 200, 20),
}
PLAN_MATERIAL = {
    "quadruped": "fur", "biped_ape": "fur", "macropod": "fur", "bat": "fur",
    "bird": "feather",
    "snake": "scale", "lizard_croc": "scale", "fish": "scale", "turtle": "scale",
    "insect_flying": "chitin", "insect_walking": "chitin", "arachnid": "chitin", "crustacean": "chitin",
    "amphibian": "wet", "cetacean": "wet", "pinniped": "wet", "cephalopod": "wet", "jellyfish": "jelly",
    "humanoid": "skin", "fantasy": "skin", "object": "default",
}
# id keywords that override the body plan's material (token-exact on the id's name part)
ID_MATERIAL = [
    ({"elephant", "rhinoceros", "rhino", "hippo", "hippopotamus", "pig", "piglet", "walrus", "babirusa", "warthog",
      "naked", "hairless", "sphynx", "tapir", "manatee", "dugong"}, "skin"),
    ({"axolotl", "frog", "toad", "salamander", "newt", "slime", "magma", "magmacube", "dolphin", "orca", "whale",
      "seal", "sealion", "octopus", "squid", "cuttlefish", "eel", "tadpole", "spit"}, "wet"),
    ({"jellyfish"}, "jelly"),
    ({"egg", "eggs"}, "eggshell"),
    ({"book", "pages", "blank", "plushies", "cushion", "balloon"}, "cloth"),
    ({"boat", "raft", "chest", "armor", "stand", "cage", "bed", "wheel"}, "wood"),
    ({"minecart", "iron", "trident", "hook", "fishhook"}, "metal"),
]
# a body-plan keyword like 'elephant' or 'rhinoceros' also names beetles: the id override only applies to these plans
ID_OVERRIDE_PLANS = {"quadruped", "biped_ape", "macropod", "pinniped", "cetacean", "amphibian", "lizard_croc",
                     "cephalopod", "jellyfish", "humanoid", "fantasy", "object", "fish"}
# bone-name tokens -> (roughness, subsurface) overrides; None keeps the class value
PART_RULES = [
    ({"eye", "eyes", "pupil", "iris", "eyeball"}, (30, 0)),
    ({"beak", "bill"}, (120, 10)),
    ({"horn", "horns", "antler", "antlers", "tusk", "tusks", "claw", "claws", "hoof", "hooves", "teeth", "tooth",
      "fang", "fangs", "nail", "nails", "talon", "talons", "stinger", "pincer", "pincers", "mandible", "mandibles"},
     (110, 5)),
    ({"shell", "carapace", "plastron"}, (125, 5)),
    ({"nose", "snout", "tongue", "mouth", "lip", "lips", "nostril"}, (120, 60)),
    ({"ear", "ears"}, (None, 120)),
    ({"fin", "fins", "tailfin", "flipper", "flippers", "dorsal", "pectoral"}, (None, 90)),
]
MEMBRANE_WINGS = {"bat", "fantasy"}            # plans whose wings are skin membranes (bat, phantom)
INSECT_WINGS = {"insect_flying"}               # thin, glossy, light passes through
CREVICE_GAIN, CREVICE_LIMIT = 0.3, 25


def tokens(name):
    """Bone / id name -> lowercase word tokens ('leftEar2' -> {'left', 'ear'}; 'pw_wing_l' -> {'pw','wing','l'})."""
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return {t for t in re.split(r"[^a-zA-Z]+", s.lower()) if t}


def material_class(plan, entity_id):
    words = tokens(entity_id.split(":", 1)[-1])
    if plan in ID_OVERRIDE_PLANS:
        for keys, mat in ID_MATERIAL:
            if words & keys:
                return mat
    return PLAN_MATERIAL.get(plan, "default")


def part_values(bone_name, plan, base):
    """(roughness, subsurface) for a pixel painted on `bone_name`, starting from the class base values."""
    r, s = base[2], base[3]
    words = tokens(bone_name)
    if words & {"wing", "wings"}:
        if plan in MEMBRANE_WINGS:
            return r, max(s, 130)
        if plan in INSECT_WINGS:
            return 60, 60
    for keys, (pr, ps) in PART_RULES:
        if words & keys:
            return (r if pr is None else pr), (max(s, ps) if keys & {"ear", "ears", "fin", "fins"} else ps)
    return r, s


def crevice(colour):
    """Roughness nudge per pixel: darker than its 5x5 neighbourhood -> rougher (clamped)."""
    rgb = colour[..., :3].astype(np.float32)
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    pad = np.pad(lum, 2, mode="edge")
    h, w = lum.shape
    local = sum(pad[dy:dy + h, dx:dx + w] for dy in range(5) for dx in range(5)) / 25.0
    return np.clip((local - lum) * CREVICE_GAIN, -CREVICE_LIMIT, CREVICE_LIMIT)


# ---------------------------------------------------------------- geometry -> per-pixel bone labels
_GEO = None


def geo_index():
    """geometry id -> geometry dict (new or legacy format), first pack in GEO_STACK wins."""
    global _GEO
    if _GEO is not None:
        return _GEO
    _GEO = {}
    for pack in GEO_STACK:
        for p in sorted((pack / "models").rglob("*.json")) if (pack / "models").exists() else []:
            try:
                d = json.loads(p.read_text(encoding="utf-8-sig"))
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            for g in d.get("minecraft:geometry", []) or []:
                gid = (g.get("description") or {}).get("identifier")
                if gid and gid not in _GEO:
                    _GEO[gid] = g
            for k, g in d.items():
                if k.startswith("geometry.") and isinstance(g, dict):
                    gid, _, parent = k.partition(":")
                    if gid not in _GEO:
                        _GEO[gid] = {"description": {"identifier": gid,
                                                     "texture_width": g.get("texturewidth", 64),
                                                     "texture_height": g.get("textureheight", 64)},
                                     "bones": g.get("bones") or [], "_parent": parent or None}
    for gid, g in _GEO.items():  # legacy inheritance: a child without bones takes its parent's bones
        if not g.get("bones") and g.get("_parent") in _GEO:
            g["bones"] = _GEO[g["_parent"]].get("bones") or []
    return _GEO


def face_rects(cube):
    """[(u0, v0, u1, v1)] texel rects of every face of a cube (box UV or per-face UV)."""
    from bb_truth import face_uvs
    s = [abs(x) for x in cube.get("size", [0, 0, 0])]
    out = []
    for uv in face_uvs(cube.get("uv"), s, cube.get("mirror", False)).values():
        u0, v0, u1, v1 = uv
        out.append((min(u0, u1), min(v0, v1), max(u0, u1), max(v0, v1)))
    return out


def bone_label_map(geo, size):
    """(labels HxW int array, names list): index of the bone whose cube face covers each texture pixel, -1 none."""
    w, h = size
    desc = geo.get("description") or {}
    tw, th = desc.get("texture_width", 64) or 64, desc.get("texture_height", 64) or 64
    sx, sy = w / tw, h / th
    labels = -np.ones((h, w), dtype=np.int32)
    names = []
    for b in geo.get("bones") or []:
        cubes = b.get("cubes") or []
        if not cubes:
            continue
        names.append(b.get("name", ""))
        k = len(names) - 1
        for c in cubes:
            for u0, v0, u1, v1 in face_rects(c):
                x0, x1 = int(np.floor(u0 * sx)), int(np.ceil(u1 * sx))
                y0, y1 = int(np.floor(v0 * sy)), int(np.ceil(v1 * sy))
                x0, y0 = max(0, x0), max(0, y0)
                x1, y1 = min(w, x1), min(h, y1)
                if x1 > x0 and y1 > y0:
                    labels[y0:y1, x0:x1] = k
    return labels, names


def entity_geometries(client_file):
    try:
        d = json.loads(Path(client_file).read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    geos = (d.get("minecraft:client_entity", {}).get("description", {}) or {}).get("geometry") or {}
    return [g for g in geos.values() if isinstance(g, str)]


def pick_geometry(texture_size, client_files):
    """First geometry (entity order, then its geometry order) whose texture aspect matches ours and has bones."""
    w, h = texture_size
    idx = geo_index()
    for cf in client_files:
        for gid in entity_geometries(cf):
            g = idx.get(gid)
            if not g or not g.get("bones"):
                continue
            d = g.get("description") or {}
            tw, th = d.get("texture_width", 64) or 64, d.get("texture_height", 64) or 64
            if tw * h == th * w:
                return gid, g
    return None, None


# ---------------------------------------------------------------- MERS builders
def mers_156(spec):
    """Lesson #156 LabPBR _s -> Bedrock MERS (identical to tools/build_leaf_pilot_rp.py, witnessed)."""
    R, G, B, A = (spec[..., i].astype(int) for i in range(4))
    out = np.zeros(spec.shape, dtype=np.uint8)
    out[..., 0] = np.where(G >= 230, 255, 0)
    out[..., 1] = np.where(A < 255, A, 0)
    out[..., 2] = 255 - R
    out[..., 3] = np.where(B >= 65, np.round((B - 64) * 255 / 191), 0)
    return out


def normal_156(n):
    """LabPBR _n (RG = normal XY, B = AO, A = height) -> RGB normal with Z rebuilt, A = 255 (as the leaf builds)."""
    x = n[..., 0].astype(float) / 255 * 2 - 1
    y = n[..., 1].astype(float) / 255 * 2 - 1
    z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    out = np.zeros(n.shape, dtype=np.uint8)
    # 19:1x 10-01: z is encoded like x and y, (z + 1) / 2 * 255 — it was z * 255 (tilted pixels decoded too short)
    out[..., 0], out[..., 1], out[..., 2], out[..., 3] = n[..., 0], n[..., 1], np.round((z + 1) / 2 * 255), 255
    return out


def rgba(p, size=None, resample=Image.BOX):
    im = Image.open(p).convert("RGBA")
    if size and im.size != size:
        im = im.resize(size, resample)
    return np.asarray(im)


def tier1(t):
    colour = Image.open(t["file"])
    mers = mers_156(rgba(t["patrix_s"]))
    if mers.shape[1::-1] != colour.size:   # convert at Patrix size, then resample; metal snaps back to 0 / 255
        mers = np.asarray(Image.fromarray(mers, "RGBA").resize(colour.size, Image.BOX)).copy()
        mers[..., 0] = np.where(mers[..., 0] >= 128, 255, 0)
    normal = normal_156(rgba(t["patrix_n"], colour.size)) if t.get("patrix_n") else None
    return mers, normal, {"kind": "tier1", "from": t["patrix_s"]}


def derive(t, census_by_id, client_by_id):
    colour = rgba(t["file"])
    h, w = colour.shape[:2]
    ents = [e for e in t["entities"] if e in census_by_id]
    plan = census_by_id[ents[0]]["body_plan"] if ents else "object"
    mat = material_class(plan, ents[0] if ents else t["rel"])
    base = MATERIALS[mat]
    gid, geo = pick_geometry((w, h), [client_by_id[e] for e in ents if e in client_by_id])
    rough = np.full((h, w), float(base[2]))
    sss = np.full((h, w), float(base[3]))
    parts = {}
    if geo is not None:
        labels, names = bone_label_map(geo, (w, h))
        for k, name in enumerate(names):
            r, s = part_values(name, plan, base)
            if (r, s) != (base[2], base[3]):
                m = labels == k
                if m.any():
                    rough[m], sss[m] = r, s
                    parts[name] = [int(r), int(s)]
    rough = np.clip(rough + crevice(colour), 0, 255)
    mers = np.zeros((h, w, 4), dtype=np.uint8)
    mers[..., 0] = base[0]
    mers[..., 1] = 0
    mers[..., 2] = np.round(rough).astype(np.uint8)
    mers[..., 3] = np.round(sss).astype(np.uint8)
    return mers, None, {"kind": "derive", "plan": plan, "material": mat, "geometry": gid, "parts": parts}


def write(t, mers, normal, pack_dir):
    rel = t["rel"]
    stem = Path(rel).name
    out = pack_dir / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mers, "RGBA").save(out.with_name(stem + "_mers.png"))
    ts = {"color": stem, "metalness_emissive_roughness_subsurface": stem + "_mers"}
    if normal is not None:
        Image.fromarray(normal, "RGBA").save(out.with_name(stem + "_n.png"))
        ts["normal"] = stem + "_n"
    out.with_name(stem + ".texture_set.json").write_text(
        json.dumps({"format_version": "1.21.30", "minecraft:texture_set": ts}, indent=1))


def main():
    inv = json.loads(INV.read_text())
    census = json.loads(CENSUS.read_text())
    census_by_id = {c["id"]: c for c in census}
    client_by_id = {c["id"]: c["file"] for c in census}
    flat = {r[0] for r in json.loads(FLAT.read_text()) if r[1] == "flat"}
    report = []
    for t in inv:
        cls = t["class"]
        if cls == "vanilla" and t["rel"] in flat:
            cls = "derive_vanilla"
        if cls not in ("tier1", "derive", "derive_vanilla") or t.get("existing_set"):
            continue
        # derived vanilla flats live in RP-07 beside a copy of Mojang's colour (H-18: set + colour in one pack)
        pack = "rp07-1438" if cls == "derive_vanilla" else t["pack"]
        try:
            mers, normal, info = tier1(t) if cls == "tier1" else derive(t, census_by_id, client_by_id)
        except Exception as e:  # noqa: BLE001 — recorded per texture, never silent
            report.append({"rel": t["rel"], "error": repr(e)})
            continue
        write(t, mers, normal, STAGE / pack)
        if cls == "derive_vanilla":
            dst = STAGE / pack / (t["rel"] + Path(t["file"]).suffix)
            dst.write_bytes(Path(t["file"]).read_bytes())
        report.append({"rel": t["rel"], "pack": pack, "class": cls, **info,
                       "mean": [round(float(mers[..., i].mean()), 1) for i in range(4)]})
    (ROOT / "_docs/mers/MERS-DERIVE-REPORT.json").write_text(json.dumps(report, indent=1))
    errs = [r for r in report if "error" in r]
    from collections import Counter
    print("written:", len(report) - len(errs), "errors:", len(errs))
    print(Counter(r.get("class") for r in report if "error" not in r))
    print(Counter(r.get("material") for r in report if r.get("kind") == "derive"))
    print("derived with a geometry part map:", sum(1 for r in report if r.get("kind") == "derive" and r.get("geometry")))
    for e in errs[:10]:
        print("ERR", e)


if __name__ == "__main__":
    sys.exit(main())

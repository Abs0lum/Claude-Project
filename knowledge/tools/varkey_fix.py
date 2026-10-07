#!/usr/bin/env python3
"""varkey_fix.py — L-VAR-1: custom-block material_instances must reference SINGLE-PATH terrain keys.

Witness (Abs0lum 2026-09-22 09:29, content log): every HOMESTEAD block referencing a weighted-`variations`
key ("oak_planks", "mud_bricks", ... and RP-10's "fire_0") warns
   'Material "<face>" texture "<key>" is an array of un-weighted textures. First texture in array will always be used'
=> the custom-block resolver flattens `variations` to a plain array and uses entry 0.  Vanilla blocks vary; custom
blocks do not, and the log floods (161 blocks x up to 64 permutations x faces).

Fix (two packs, no geometry, no scripts):
  RP-04 v1.3.128 -> v1.3.129 : single-path keys pw_mat_<material>[_top] (= the material's FIRST variation path, the
                               texture the engine was already using), pw_mat_stripped_<wood>[_top] for the rafters,
                               pw_hearth_flame (= RP-04's own fire_0 flipbook, with its own flipbook entry).
  BP-02 v1.3.179 -> v1.3.180 : the 161 HOMESTEAD blocks' material_instances repointed to those keys; ledger rows
                               updated.  Every other byte identical.
"""
import json, os, re, shutil, sys, hashlib, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from homestead_materials import OUTER, INNER16, RAFTER_WOODS  # noqa: E402

ROOT = Path("/home/claude")
BP_SRC, BP_DST = ROOT / "_build/bp02-179", ROOT / "_build/bp02-180"
RP_SRC, RP_DST = ROOT / "_build/rp04-128", ROOT / "_build/rp04-129"
BP_VER, RP_VER = "1.3.180", "1.3.129"
DATE = "2026-09-22"

def first_path(entry):
    t = entry.get("textures")
    if isinstance(t, str): return t
    if isinstance(t, list): return t[0] if isinstance(t[0], str) else t[0].get("path")
    if isinstance(t, dict) and "variations" in t:
        v = t["variations"][0]; return v.get("path") if isinstance(v, dict) else v
    if isinstance(t, dict): return t.get("path")
    raise ValueError(entry)

def is_multi(entry):
    t = entry.get("textures")
    return isinstance(t, list) or (isinstance(t, dict) and "variations" in t)

def main():
    for d in (BP_DST, RP_DST):
        if d.exists(): shutil.rmtree(d)
    shutil.copytree(BP_SRC, BP_DST); shutil.copytree(RP_SRC, RP_DST)

    # ---------------- RP-04: keys ----------------
    ttp = RP_DST / "textures/terrain_texture.json"
    tt = json.loads(ttp.read_text(encoding="utf-8-sig"))
    td = tt["texture_data"]
    keymap = {}                      # old key -> new key
    new_entries = {}
    def single_key(old_key, new_key):
        if old_key in keymap: return keymap[old_key]
        entry = td[old_key]
        path = first_path(entry)
        if not is_multi(entry):      # already single: keep referencing it, nothing to add
            keymap[old_key] = old_key; return old_key
        assert (RP_DST / (path + ".png")).exists(), f"{old_key}: {path}.png missing"
        new_entries[new_key] = {"textures": path}
        keymap[old_key] = new_key
        return new_key
    for mid, (name, item, side, top) in OUTER.items():
        single_key(side, f"pw_mat_{mid}")
        if top != side: single_key(top, f"pw_mat_{mid}_top")
    for wid, (wname, planks, side, end) in RAFTER_WOODS.items():
        single_key(side, f"pw_mat_stripped_{wid}"); single_key(end, f"pw_mat_stripped_{wid}_top")
    # the flame: RP-10 overrides fire_0 with 4 variations, so a dedicated tile on RP-04's own flipbook
    new_entries["pw_hearth_flame"] = {"textures": "textures/blocks/fire_0"}
    keymap["fire_0"] = "pw_hearth_flame"
    for k in new_entries: assert k not in td, f"key collision {k}"
    td.update(new_entries)
    ttp.write_text(json.dumps(tt, indent=1) + "\n", encoding="utf-8")
    fbp = RP_DST / "textures/flipbook_textures.json"
    fb = json.loads(fbp.read_text(encoding="utf-8-sig"))
    src = [e for e in fb if e.get("atlas_tile") == "fire_0"][0]
    flame = dict(src); flame["atlas_tile"] = "pw_hearth_flame"
    assert not any(e.get("atlas_tile") == "pw_hearth_flame" for e in fb)
    fb.append(flame)
    fbp.write_text(json.dumps(fb, indent=1) + "\n", encoding="utf-8")
    man = json.loads((RP_DST / "manifest.json").read_text(encoding="utf-8-sig"))
    man["header"]["name"] = f"AbsolutRealism Basic RP v{RP_VER}"
    man["header"]["description"] = (f"v{RP_VER} ({DATE}) L-VAR-1 — {len(new_entries)} single-path terrain keys for the HOMESTEAD blocks "
        f"(pw_mat_<material>[_top] = each material's first variation, pw_mat_stripped_<wood>[_top], pw_hearth_flame on RP-04's own "
        f"fire_0 flipbook with its own flipbook entry). Witness 09-22: custom-block material_instances flatten weighted `variations` keys "
        f"into an un-weighted array (first entry used, one warning per face per permutation) — custom blocks must reference single-path keys. "
        f"Every existing entry and file byte-identical to v1.3.128. Pair with BP-02 v1.3.180.")
    man["header"]["version"] = [1, 3, 129]
    for m in man["modules"]: m["version"] = [1, 3, 129]
    (RP_DST / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    led = RP_DST / "PW-DEPENDENCIES.md"; led.write_text(led.read_text(encoding="utf-8").replace("v1.3.128 ·", f"v{RP_VER} ·", 1), encoding="utf-8")

    # ---------------- BP-02: repoint ----------------
    changed = 0; touched = set()
    def repoint(c):
        nonlocal changed
        mi = c.get("minecraft:material_instances", {})
        for name, v in mi.items():
            if isinstance(v, dict) and v.get("texture") in keymap and keymap[v["texture"]] != v["texture"]:
                v["texture"] = keymap[v["texture"]]; changed += 1
    for p in sorted((BP_DST / "blocks").glob("pw_*.json")):
        d = json.loads(p.read_text(encoding="utf-8-sig")); b = d["minecraft:block"]
        ident = b["description"]["identifier"]
        if not any(ident.startswith(x) for x in ("pw:hearth_", "pw:flue_", "pw:wall_", "pw:rafter45_")): continue
        before = changed
        repoint(b["components"])
        for pm in b.get("permutations", []): repoint(pm.get("components", {}))
        if changed > before:
            touched.add(ident); p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    # ledger: recompute needs from the homestead blocks (drop the old key rows added in .178, add the new ones)
    ledp = BP_DST / "PW-DEPENDENCIES.md"; text = ledp.read_text(encoding="utf-8")
    rows = set(re.findall(r'^\|(\w+)\|`([^`]+)`\|$', text, re.M))
    old_keys = {k for k, v in keymap.items() if v != k}
    rows = {r for r in rows if not (r[0] == "terrain_key" and r[1] in old_keys)}
    rows |= {("terrain_key", v) for v in keymap.values()}
    h = hashlib.sha256(json.dumps(sorted([list(r) for r in rows])).encode()).hexdigest()[:16]
    body = "\n".join(f"|{t}|`{i}`|" for t, i in sorted(rows))
    ledp.write_text(f"# PW-DEPENDENCIES — BP-02 Tectonic BP\n\nv{BP_VER} · needs-hash `{h}`\n\n|type|identifier|\n|---|---|\n{body}\n", encoding="utf-8")
    man = json.loads((BP_DST / "manifest.json").read_text(encoding="utf-8-sig"))
    man["header"]["name"] = f"AbsolutRealism Tectonic BP v{BP_VER}"
    man["header"]["description"] = (f"v{BP_VER} ({DATE}) L-VAR-1 — the {len(touched)} HOMESTEAD blocks' material_instances repointed from weighted-"
        f"variations keys to RP-04 v1.3.129's single-path pw_mat_* keys (+ pw_hearth_flame): {changed} texture references. Witness 09-22: "
        f"custom blocks flatten `variations` keys to an un-weighted array (first entry used) and warn once per face per permutation. "
        f"No geometry, box, state, recipe or script change; every other byte identical to v1.3.179. Pair with RP-04 v1.3.129 + RP-02 v2.0.2.")
    man["header"]["version"] = [1, 3, 180]
    for m in man["modules"]: m["version"] = [1, 3, 180]
    (BP_DST / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print(f"RP-04: {len(new_entries)} keys added; BP-02: {changed} references repointed in {len(touched)} blocks; ledger rows {len(rows)} hash {h}")
    print("keymap:", json.dumps(keymap, indent=0)[:600])

if __name__ == "__main__":
    main()

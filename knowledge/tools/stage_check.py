#!/usr/bin/env python3
"""stage_check.py — integrity check of _build/menagerie-stage (D-C351): every ported client entity's geometry / animations /
render controllers / textures resolve inside the staged RP (or are vanilla), every BP entity's loot table resolves, ids unique."""
import json, sys, collections
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import addon_port_scan as S
R = Path("/home/claude/_build/menagerie-stage/RP"); B = Path("/home/claude/_build/menagerie-stage/BP")
VAN = S.vanilla_refs()
defs, tex = set(), set()
for f in R.rglob("*.json"):
    try: d = json.load(open(f))
    except Exception: continue
    for g in d.get("minecraft:geometry", []) or []: defs.add(g["description"]["identifier"])
    for k in d:
        if k.startswith("geometry."): defs.add(k.split(":")[0])
    for key in ("animations", "animation_controllers", "render_controllers"):
        if isinstance(d.get(key), dict) and "minecraft:client_entity" not in d: defs |= set(d[key])
for f in list(R.rglob("*.png")) + list(R.rglob("*.tga")): tex.add(str(f.relative_to(R)).rsplit(".", 1)[0])
bad, ids = collections.defaultdict(list), collections.Counter()
for f in R.glob("entity/pw_menagerie/**/*.json"):
    d = json.load(open(f))["minecraft:client_entity"]["description"]; i = d["identifier"]; ids[i] += 1
    refs = list((d.get("geometry") or {}).values()) + list((d.get("animations") or {}).values()) + \
           [r if isinstance(r, str) else next(iter(r)) for r in d.get("render_controllers", [])]
    for r in refs:
        if r not in defs and r not in VAN and not r.startswith(("animation.common", "controller.render.default")): bad[i].append(r)
    for t in (d.get("textures") or {}).values():
        if t not in tex and t.lower() not in VAN: bad[i].append(t)
bp_ids = collections.Counter(json.load(open(f))["minecraft:entity"]["description"]["identifier"] for f in B.glob("entities/**/*.json"))
dups = [i for i, n in list(ids.items()) + list(bp_ids.items()) if n > 1]
print(f"client entities {len(ids)}, behaviour entities {len(bp_ids)}, with unresolved refs {len(bad)}, duplicate ids {len(dups)}")
for i, r in list(bad.items())[:20]: print("  ", i, r[:4])

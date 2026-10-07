#!/usr/bin/env python3
"""build_rp06_1411.py — RP-06 Hostile Mobs RP v1.4.11: CREEPER RENDER-CONTROLLER SCHEMA FIX (his content log 19:51 09-28, D-C270).

Mechanism: round 3 (1.4.9, D-C267) gated the charged-creeper shell with the conditional form
  "render_controllers": ["controller.render.creeper", {"controller.render.creeper_armor": "query.is_powered"}]
but our creeper.entity.json is format_version 1.8.0, whose schema allows STRINGS only in that list (the object form arrives with
1.10.0 — vanilla's creeper file is 1.10.0). The engine logged: `entity/creeper.entity.json | ... | render_controllers | [1] |
unknown child schema option type. Allowed types: 'string'` — so the gate never worked (1.4.10 carried the same file).
Fix (keeps the file at 1.8.0 so its legacy animation_controllers keep running exactly as before):
  - render_controllers = ["controller.render.creeper", "controller.render.pw_creeper_armor"]  (strings only)
  - render_controllers/pw_creeper_armor.render.json (format 1.8.0) = vanilla controller.render.creeper_armor, verbatim, plus
    "part_visibility": [{"*": "query.is_powered"}] — every bone of the shell hidden unless the creeper is charged
    (the pattern vanilla's own 1.8.0 controller.render.villager_v2_level uses to switch a whole layer with Molang).
Everything else byte-identical to v1.4.10 (verify_rp06_1411.py asserts the diff)."""
import json, re, shutil, time
from pathlib import Path

ROOT = Path("/home/claude"); SRC, DST, VER = ROOT / "_build/rp06-1410", ROOT / "_build/rp06-1411", "1.4.11"
VANILLA_RC = ROOT / "_intake/bedrock-samples/resource_pack/render_controllers/creeper_armor.render_controllers.json"


def jl(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    rc = jl(VANILLA_RC)["render_controllers"]["controller.render.creeper_armor"]
    rc = dict(rc); rc["part_visibility"] = [{"*": "query.is_powered"}]
    (DST / "render_controllers/pw_creeper_armor.render.json").write_text(
        json.dumps({"format_version": "1.8.0", "render_controllers": {"controller.render.pw_creeper_armor": rc}}, indent=1), encoding="utf-8")
    ep = DST / "entity/creeper.entity.json"; d = jl(ep)
    desc = d["minecraft:client_entity"]["description"]
    assert d["format_version"] == "1.8.0" and desc["render_controllers"] == ["controller.render.creeper", {"controller.render.creeper_armor": "query.is_powered"}], desc["render_controllers"]
    desc["render_controllers"] = ["controller.render.creeper", "controller.render.pw_creeper_armor"]
    ep.write_text(json.dumps(d, indent=1), encoding="utf-8")
    mp = DST / "manifest.json"; man = jl(mp); v = [int(x) for x in VER.split(".")]
    man["header"]["version"] = v
    for m in man["modules"]: m["version"] = v
    man["header"]["name"] = f"AbsolutRealism Hostile Mobs RP v{VER}"
    man["header"]["description"] = (f"v{VER} (2026-09-28) CREEPER FIX (D-C270): the charged-creeper shell now shows only when the creeper is charged "
                                    "(1.4.9/1.4.10 used a render-controller form this file's format does not accept - content-log error). "
                                    "Includes everything in v1.4.10 (zombie horse + skeleton horse rebuilt). Else byte-identical to v1.4.10.")
    mp.write_text(json.dumps(man, indent=1), encoding="utf-8")
    line = f"RP-06 v{VER}: creeper RC list strings only + controller.render.pw_creeper_armor (part_visibility * = query.is_powered) -> {DST}"
    print(line)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-28] BUILD {line}\n")


if __name__ == "__main__":
    main()

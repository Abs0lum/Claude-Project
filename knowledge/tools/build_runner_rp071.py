#!/usr/bin/env python3
"""build_runner_rp071.py — PW-TestRunner RP 0.7.1 = RP 0.7.0 + pw:nbump on its OWN copies of the four models (his content log 2,
15:42 CT 10-01): the bump-test mob shows warden / dolphin / turtle / parrot in one entity; four `head` bones at four places made
the engine's armor_offset.default_neck clash. nbump has no animations, so its copies carry no `head` bone at all (renamed
head_<animal>); the real warden / dolphin / turtle / parrot keep their models untouched."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

SRC, DST = ROOT / "_build/testrunner-rp-0.7.0", ROOT / "_build/testrunner-rp-0.7.1"


def main():
    assert not DST.exists(), "never rebuild a build dir"
    shutil.copytree(SRC, DST)
    lib = {}
    for p in ("rp06-1426", "rp07-1440"):
        lib.update(S.Pack(ROOT / "_build" / p).geos)
    ef = DST / "entity/pw_nbump.entity.json"
    ent = S.jload(ef)
    geo = ent["minecraft:client_entity"]["description"]["geometry"]
    out = []
    for slot, gid in list(geo.items()):
        g = json.loads(json.dumps(lib[gid]))
        animal = slot.replace("g_", "")
        new_id = f"geometry.pw_nbump_{animal}"
        g["description"]["identifier"] = new_id
        for b in g["bones"]:
            if b["name"] == "head":
                b["name"] = f"head_{animal}"
            if b.get("parent") == "head":
                b["parent"] = f"head_{animal}"
            if b.get("locators"):
                b["locators"].pop("armor_offset.default_neck", None)
        (DST / "models/entity").mkdir(parents=True, exist_ok=True)
        (DST / f"models/entity/pw_nbump_{animal}.geo.json").write_text(json.dumps({"format_version": "1.12.0",
                                                                                 "minecraft:geometry": [g]}, indent=1))
        geo[slot] = new_id
        out.append(new_id)
    ef.write_text(json.dumps(ent, indent=1))
    m = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 7, 1]
    for mod in m["modules"]:
        mod["version"] = [0, 7, 1]
    m["header"]["name"] = "PW Test Runner RP v0.7.1"
    m["header"]["description"] = ("v0.7.1 (2026-10-01) the bump-test mob pw:nbump on its own model copies (his content log 2: "
                                  "armor_offset.default_neck clash). Includes all of v0.7.0.")
    (DST / "manifest.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("built", DST.name, out)


if __name__ == "__main__":
    main()

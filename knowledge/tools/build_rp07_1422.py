#!/usr/bin/env python3
"""build_rp07_1422.py — D-C284 (found after the 1.4.21 upload, before his test): RP-07 Neutral Mobs RP v1.4.22 from v1.4.21.

THE ENDERMAN WOULD NOT HAVE SHOWN. PW-StripMine RP 3.0.1 sits ABOVE RP-07 in his list and defines `minecraft:enderman` (the April
entity, geometry.enderman.v1.8, min_engine_version 1.8.0). 1.4.21's own enderman entity carried the same 1.8.0, so on the tie the
higher pack wins (the new standing PREC check: tools/entity_precedence.py) — the game would have drawn StripMine's April entity
on the 64x32-layout geometry with the 512x256 Patrix skin now that the old .tga is gone: a silverfish-style mismatch, and no jaw.
Fix (L-ENT-PREC, the 1.4.12 chicken rule): our enderman entity declares min_engine_version 1.21.0, above StripMine's and
vanilla's 1.8.0. Nothing else changes (gate: the diff is manifest + entity/enderman.entity.json, and only that key in it).
Backlog (ownership law): drop the duplicate enderman from StripMine RP at its next build.
verify: python3 tools/build_rp07_1422.py --verify"""
import hashlib, json, shutil, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/rp07-1421", ROOT / "_build/rp07-1422", [1, 4, 22]
NAME = "AbsolutRealism Neutral Mobs RP v1.4.22"
DESC = ("v1.4.22 (2026-09-29) = 1.4.21 + THE ENDERMAN WINS (D-C284): our enderman declares min_engine_version 1.21.0 so it beats the "
        "April enderman in PW-StripMine RP above it (the Patrix skin + model + jaw draw). 1.4.21: warm + cold chickens built like the white "
        "one; the enderman on its Patrix model and skin with the Patrix jaw; dolphin fins, squid tilt, rabbit head fixed; spider texture "
        "holes fixed; mooshroom name-tag probe A-D; small mobs + fox and sheep drawn at real-size proportions to a 5'10\" player.")
STACK_ABOVE = [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148")]


def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()


def build():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    pe = DST / "entity/enderman.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert desc["identifier"] == "minecraft:enderman" and desc["min_engine_version"] == "1.8.0", desc.get("min_engine_version")
    desc["min_engine_version"] = "1.21.0"
    R.wj(pe, d)
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = VER; m["header"]["name"] = NAME; m["header"]["description"] = DESC
    for mod in m.get("modules", []): mod["version"] = VER
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    print("built", DST)


def verify():
    fails = []
    def check(tag, ok, msg=""):
        print(("PASS " if ok else "FAIL ") + tag + (" — " + msg if msg else ""))
        if not ok: fails.append(tag)
    fo = {str(p.relative_to(SRC)): md5(p) for p in SRC.rglob("*") if p.is_file()}
    fn = {str(p.relative_to(DST)): md5(p) for p in DST.rglob("*") if p.is_file()}
    changed = sorted(k for k in fo if k in fn and fo[k] != fn[k]); added = sorted(set(fn) - set(fo)); removed = sorted(set(fo) - set(fn))
    check("A1 only manifest + entity/enderman.entity.json changed, nothing added or removed",
          changed == ["entity/enderman.entity.json", "manifest.json"] and not added and not removed, f"changed {changed} added {added} removed {removed}")
    a = R.jl(SRC / "entity/enderman.entity.json"); b = R.jl(DST / "entity/enderman.entity.json")
    a["minecraft:client_entity"]["description"]["min_engine_version"] = "1.21.0"
    check("A2 the enderman entity differs ONLY in min_engine_version 1.8.0 -> 1.21.0", a == b)
    m = json.loads((DST / "manifest.json").read_text()); mo = json.loads((SRC / "manifest.json").read_text())
    check("K manifest 1.4.22, uuids kept", m["header"]["version"] == VER and m["header"]["uuid"] == mo["header"]["uuid"]
          and [x["uuid"] for x in m["modules"]] == [x["uuid"] for x in mo["modules"]], str(m["header"]["version"]))
    import entity_precedence
    rows = entity_precedence.census(STACK_ABOVE + [("RP-07", DST), ("RP-06", ROOT / "_build/rp06-1415")])
    lose = [r["id"] for r in rows if r["ours_lose"]]
    en = [r for r in rows if r["id"] == "minecraft:enderman"]
    check("PREC every client entity of ours wins in his order (StripMine RP above RP-08 above RP-07 above RP-06)", not lose and en and en[0]["winner"].startswith("RP-07"),
          f"shared {[r['id'] for r in rows]}; enderman winner {en[0]['winner'] if en else '-'}")
    n, e = ML.lint_pack(DST)
    check("MLS every Molang string parses (standing gate)", not e, f"{n} strings, {len(e)} errors")
    import anim_resolve_lint as A
    na, ea = A.lint_pack(DST, stack=(ROOT / "_build/rp06-1415",))
    base = set(json.load(open(ROOT / "_docs/convb/ars_baseline.json"))["RP-07"]); found = {f"{x[0]} | {x[2]}" for x in ea}
    check("ARS every animation an entity plays exists (standing gate; RP-07 baseline)", not (found - base), f"{na} entities, {len(found)} findings, new {sorted(found - base)[:3]}")
    print(f"\n{'GATE OPEN' if not fails else 'GATE CLOSED'} {6 - len(fails)}/6")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else build())

#!/usr/bin/env python3
"""build_std_round.py — Phase 4: the STANDARD round into the packs (new versions only; a delivered build dir is never rebuilt).
  RP-07 1.4.39 -> 1.4.40 · RP-06 1.4.25 -> 1.4.26 · RP-08 stays 1.4.9 (nothing of it staged: its 29 entries are objects)  (+ the staged vanilla creatures go into RP-07)
  BP-02 1.3.199 -> 1.3.200 (+ scripts/pw_flutter.js — his J3 = d)
For each staged creature (_staging/std/<pack>/): its standard client entity REPLACES the pack's own entity file (same path, same
identifier — no duplicate ids), and its std geometry / animations / render controllers are added under */std/. The original
geometries and animations stay (other entities may use them; nothing is deleted).
Gate: every JSON parses; one client entity per identifier per pack; every geometry / animation / render controller a std entity
names resolves (this pack, a lower pack of the stack, or vanilla); manifests carry the new versions. Report _docs/standard/
BUILD-STD-ROUND.json."""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

DATE = "2026-10-01"
RP = {  # staged dir -> (source build, new build, new version)
    "rp07-1439": ("rp07-1439", "rp07-1440", [1, 4, 40]),
    "rp06-1425": ("rp06-1425", "rp06-1426", [1, 4, 26]),
}
VANILLA_INTO = "rp07-1439"
NOTE = None   # a driver may set the manifest note of a later round
EXTRA_ENTITY_PACKS = [ROOT / "_build/testrunner-rp-0.7.0"]   # their entities use our models too (pw:nbump)
BP02 = ("bp02-199", "bp02-200", [1, 3, 200])


def jl(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def bump_manifest(d, ver, note):
    m = jl(d / "manifest.json")
    old = ".".join(map(str, m["header"]["version"]))
    m["header"]["version"] = ver
    for mod in m["modules"]:
        mod["version"] = ver
    v = ".".join(map(str, ver))
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", f"v{v}", m["header"]["name"])
    m["header"]["description"] = f"v{v} ({DATE}) {note} Includes all of v{old}."
    (d / "manifest.json").write_text(json.dumps(m, indent=1))


def build_rps():
    report = {}
    for staged, (src, dst, ver) in RP.items():
        D = ROOT / "_build" / dst
        assert not D.exists(), f"{dst} exists — never rebuild a build dir"
        shutil.copytree(ROOT / "_build" / src, D)
        P = S.Pack(D)
        stage_dirs = [S.STAGE / staged] + ([S.STAGE / "resource_pack"] if staged == VANILLA_INTO else [])
        n_ent = n_new = 0
        for sd in stage_dirs:
            if not sd.exists():
                continue
            for sub in ("models/entity/std", "animations/std", "render_controllers/std", "animation_controllers/std"):
                if (sd / sub).exists():
                    (D / sub).mkdir(parents=True, exist_ok=True)
                    for f in (sd / sub).glob("*.json"):
                        shutil.copy2(f, D / sub / f.name)
            for f in sorted((sd / "entity/std").glob("*.entity.json")):
                ent = jl(f)
                ident = ent["minecraft:client_entity"]["description"]["identifier"]
                if ident in P.entities and sd.name != "resource_pack":
                    target = P.entities[ident][0]
                    n_ent += 1
                else:
                    (D / "entity/std").mkdir(parents=True, exist_ok=True)
                    target = D / "entity/std" / f.name
                    n_new += 1
                target.write_text(json.dumps(ent, indent=1))
        bump_manifest(D, ver, NOTE or "STANDARD ROUND (his T1 naming for ALL mobs, Q1 real leg joints, the standard bird flight / "
                              "flutter / fold, species-shared candidate clips): every creature's client entity now names a standard "
                              "COPY of its rig (geometry.std.*) + animations (animation.std.*), identical poses under every old clip.")
        report[dst] = {"entities_replaced": n_ent, "entities_added": n_new}
    return report


def build_bp02():
    src, dst, ver = BP02
    D = ROOT / "_build" / dst
    assert not D.exists(), f"{dst} exists"
    shutil.copytree(ROOT / "_build" / src, D)
    shutil.copy2(ROOT / "src/bp02/pw_flutter.js", D / "scripts/pw_flutter.js")
    main = (D / "scripts/main.js").read_text()
    line = 'import "./pw_flutter.js"; // v1.3.200: fowl FLUTTER physics - a hop, slow fall 1.2 s, then the drop (his J3 = d, 10-01)\n'
    anchor = 'import "./pw_mob_light.js";'
    assert anchor in main and "pw_flutter" not in main
    main = main.replace(anchor, line + anchor, 1)
    main = re.sub(r'const PW_BUILD = "[0-9.]+";', 'const PW_BUILD = "1.3.200";', main)
    (D / "scripts/main.js").write_text(main)
    bump_manifest(D, ver, "FLUTTER (his J3 = d): chicken, turkeys, peafowl, kakapos hop up as they start to fall, fall slowly "
                          "for 1.2 s while they flutter, then drop.")
    return {dst: "pw_flutter.js + import"}


STACK = ["rp06-1426", "rp07-1440", "rp08-149"]   # bottom -> top (RP-08: no std change -> 1.4.9 ships as built, 14:25 10-01)


def gate(report, stack=None):
    stack = stack or STACK
    checks = []
    vanilla = S.Pack(S.VANILLA)
    geos, anims, rcs = dict(vanilla.geos), dict(vanilla.anims), dict(vanilla.rcs)
    for name in stack:
        P = S.Pack(ROOT / "_build" / name)
        geos.update(P.geos)
        anims.update(P.anims)
        rcs.update(P.rcs)
    for name in stack:
        D = ROOT / "_build" / name
        bad_json = []
        strict_only = 0   # files with // comments: Bedrock reads them (Mojang's own vanilla files carry them) — info only
        for f in D.rglob("*.json"):
            try:
                jl(f)
            except Exception:  # noqa: BLE001
                try:
                    S.jload(f)   # the comment-tolerant reader (Bedrock's leniency)
                    strict_only += 1
                except Exception as e:  # noqa: BLE001
                    bad_json.append(f"{f.relative_to(D)}: {str(e)[:60]}")
        ids = {}
        dup = []
        for f in (D / "entity").rglob("*.json"):
            try:
                i = jl(f)["minecraft:client_entity"]["description"]["identifier"]
            except Exception:
                continue
            if i in ids:
                dup.append(i)
            ids[i] = f
        unresolved = []
        for i, f in ids.items():
            d = jl(f)["minecraft:client_entity"]["description"]
            for g in (d.get("geometry") or {}).values():
                if g.startswith("geometry.std.") and g not in geos:
                    unresolved.append(f"{i} geo {g}")
            for a in (d.get("animations") or {}).values():
                if a.startswith("animation.std.") and a not in anims:
                    unresolved.append(f"{i} anim {a}")
            for r in d.get("render_controllers") or []:
                rid = r if isinstance(r, str) else list(r)[0]
                if rid.startswith("controller.render.std.") and rid not in rcs:
                    unresolved.append(f"{i} rc {rid}")
        checks.append({"pack": name, "json_errors": bad_json[:10], "n_json_errors": len(bad_json), "comment_json_files": strict_only, "duplicate_ids": dup,
                       "unresolved_std_refs": unresolved[:20], "n_unresolved": len(unresolved), "entities": len(ids)})
    # every staged std file reached its pack byte-for-byte
    staged_vs_built = []
    for staged, (src, dst, ver) in RP.items():
        for sd in [S.STAGE / staged] + ([S.STAGE / "resource_pack"] if staged == VANILLA_INTO else []):
            for f in sd.rglob("*.json"):
                rel = f.relative_to(sd)
                if rel.parts[0] == "entity":
                    continue   # entities land on the pack's own entity path (checked by identifier above)
                b = ROOT / "_build" / dst / rel
                if not b.exists() or b.read_bytes() != f.read_bytes():
                    staged_vs_built.append(str(rel))
    checks.append({"staged_vs_built_mismatch": staged_vs_built[:20], "n": len(staged_vs_built)})
    # 15:2x 10-01 — the GAME-LOG gates (his content log 1: what the game rejected, now refused before shipping)
    import game_log_gates as GL
    gl = GL.run([ROOT / "_build" / n for n in stack], extra_entity_packs=EXTRA_ENTITY_PACKS)
    checks.append({"game_log_gates": gl})
    ok = not staged_vs_built and gl["ok"] and all(c["n_json_errors"] == 0 and not c["duplicate_ids"] and c["n_unresolved"] == 0
                                                  for c in checks if "pack" in c)
    return ok, checks


def run(gate_only=False, with_bp02=True):
    import std_groups as G   # his 14:35 prudence rule: no build on a working copy that differs from the frozen groups
    if not G.check():
        sys.exit("GUARD FAIL — the staged creatures differ from the frozen groups (see the list); nothing built")
    if gate_only:
        rep = {"gate_only": True}
    else:
        rep = build_rps()
        if with_bp02:
            rep.update(build_bp02())
    return rep, gate(rep)


if __name__ == "__main__":
    rep, (ok, checks) = run("--gate-only" in sys.argv)
    out = {"report": rep, "gate_ok": ok, "checks": checks}
    (ROOT / "_docs/standard/BUILD-STD-ROUND.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:3000])

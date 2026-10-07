#!/usr/bin/env python3
"""game_log_gates.py — STANDING GATES from his content log 1 (15:04 CT 10-01): what the game rejected is refused before a ship.

FMT      no client entity uses a section its format_version does not allow (entity_schema_lint; existed since D-C285 but was not
         in the standard-round gate — the miss that let 8 birds ship without flight).
EMPTY    no animation has an empty `bones {}` block (game: "bones | Required child [a-zA-Z0-9_.-]+ not found").
LOCATOR  no explicit `armor_offset.default_neck`; no entity whose 2+ models carry `head` at different places (logs 1 + 2).
EMPTY_FILE / UNCONVERTED  log 2: no empty animation file; no converted creature playing an original clip on renamed-away bones.
NWR      per-entity never-written reads (nwr_entity_lint): none in shared_ / fam_ clips; in an entity's own clips no read beyond the
         pre-existing baseline (_docs/standard/NWR-BASELINE.json, written the first time from the source packs).
API: run(pack_dirs bottom->top, extra_entity_packs=()) -> {"ok": bool, ...}"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import entity_schema_lint as ESL  # noqa: E402
import nwr_entity_lint as NWR  # noqa: E402
import std_convert as S  # noqa: E402

LOC = "armor_offset.default_neck"
BASELINE = ROOT / "_docs/standard/NWR-BASELINE.json"


def empty_bones(pack):
    out = []
    for f in Path(pack).rglob("animations/**/*.json"):
        try:
            d = S.jload(f)
        except Exception:  # noqa: BLE001
            continue
        for aid, a in (d.get("animations") or {}).items():
            if isinstance(a, dict) and "bones" in a and not a["bones"]:
                out.append(aid)
    return out


LOCATOR_EXCEPT = {"minecraft:sniffer": "our adult model + Mojang's own baby model, paired the way the vanilla game pairs them"}


def locator_clashes(packs):
    """his logs 1 + 2: the engine GENERATES armor_offset.default_neck per model; explicit ones only add clashes (log 2). Refused:
    (a) any explicit armor_offset.default_neck in our models; (b) an entity whose 2+ models carry a bone named `head` at
    different places (the std naming did that; the SF originals had none)."""
    geos, ents = {}, {}
    V = S.Pack(S.VANILLA)
    geos.update(V.geos)
    for p in packs:
        P = S.Pack(p)
        geos.update(P.geos)
        for i, (f, desc) in P.entities.items():
            ents[i] = desc
    bad = []
    for gid, g in geos.items():
        if gid in V.geos and V.geos[gid] is g:
            continue
        if any(LOC in (b.get("locators") or {}) for b in g["bones"]):
            bad.append(f"explicit {LOC} in {gid}")
    for i, desc in ents.items():
        # log 3 (16:31): ANY locator named in 2+ models of one entity must sit on the SAME bone name with the SAME value
        # (the blobfish's `lead`: same offset, bones `head` vs `head_land` -> "doesn't exactly match")
        seen = {}
        for g in dict.fromkeys((desc.get("geometry") or {}).values()):
            for b in (geos.get(g) or {}).get("bones", []):
                for ln, lv in (b.get("locators") or {}).items():
                    seen.setdefault(ln, set()).add((b["name"], json.dumps(lv)))
        for ln, v in seen.items():
            if len(v) > 1:
                bad.append(f"{i}: locator {ln} differs across its models {sorted(v)}")
        if i in LOCATOR_EXCEPT:
            continue
        models = [geos[g] for g in dict.fromkeys((desc.get("geometry") or {}).values()) if g in geos]
        heads = [next(b for b in m["bones"] if b["name"].lower() == "head") for m in models
                 if any(b["name"].lower() == "head" for b in m["bones"])]
        if len(heads) >= 2 and len({json.dumps(h.get("pivot", [0, 0, 0])) for h in heads}) >= 2:
            bad.append(i)
    return bad


def empty_anim_files(pack):
    out = []
    for f in Path(pack).rglob("animations/**/*.json"):
        try:
            d = S.jload(f)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(d, dict) and "animations" in d and not d["animations"]:
            out.append(str(f.relative_to(pack)))
    return out


def unconverted(packs):
    """his log 2: a converted creature (geometry.std.*) must not play an ORIGINAL clip whose channels name bones its models
    no longer have (12 RP-06 SF creatures stood with frozen legs / fins / jaws)."""
    anims, geos, ents = {}, {}, {}
    V = S.Pack(S.VANILLA)
    anims.update(V.anims)
    for p in packs:
        P = S.Pack(p)
        anims.update(P.anims)
        geos.update(P.geos)
        ents.update({i: d for i, (f, d) in P.entities.items()})
    bad = []
    for i, d in ents.items():
        gids = list((d.get("geometry") or {}).values())
        if not any(g.startswith("geometry.std.") for g in gids):
            continue
        names = {b["name"] for g in gids if g in geos for b in geos[g]["bones"]}
        for s, a in (d.get("animations") or {}).items():
            if a.startswith(("controller.", "animation.std.")) or a not in anims:
                continue
            miss = [b for b in (anims[a].get("bones") or {}) if b not in names]
            if miss:
                bad.append(f"{i} {s} -> {a}: {len(miss)} channels on missing bones")
    return bad


def manifest_names(packs):
    """his 16:31 catch: the pack NAME shown in game must carry the pack's real version (RP-04 said v1.3.142 at 1.3.143)."""
    import re
    bad = []
    for p in packs:
        m = json.loads((Path(p) / "manifest.json").read_text(encoding="utf-8-sig"))
        v = ".".join(map(str, m["header"]["version"]))
        mv = re.search(r"v(\d+\.\d+\.\d+)", m["header"].get("name", ""))
        if mv and mv.group(1) != v:
            bad.append(f"{Path(p).name}: name says v{mv.group(1)}, version {v}")
    return bad


def run(packs, extra_entity_packs=()):
    packs = [Path(p) for p in packs]
    fmt = []
    for p in list(packs) + [Path(x) for x in extra_entity_packs]:
        n, errs, infos = ESL.lint_pack(p)
        fmt += [f"{p.name}: {e[0]} {e[1]}" for e in errs]
    empty = {p.name: empty_bones(p) for p in packs}
    empty_files = [f"{p.name}: {x}" for p in packs for x in empty_anim_files(p)]
    unconv = unconverted(packs)
    names = manifest_names(list(packs) + [Path(x) for x in extra_entity_packs])
    loc = locator_clashes(list(packs) + [Path(x) for x in extra_entity_packs])
    res = NWR.lint([S.VANILLA] + list(packs))
    shared_bad = [(i, s, v) for i, rows in res.items() for s, a, v in rows if s.startswith(("shared_", "fam_", "parade_"))]
    own = sorted({f"{i}|{v}" for i, rows in res.items() for s, a, v in rows if not s.startswith(("shared_", "fam_", "parade_"))})
    if not BASELINE.exists():
        raise SystemExit("NWR baseline missing — write it from the SOURCE packs first (game_log_gates.write_baseline)")
    base = set(json.loads(BASELINE.read_text()))
    own_new = [x for x in own if x not in base]
    ok = not fmt and not any(empty.values()) and not loc and not shared_bad and not own_new and not empty_files and not unconv and not names
    return {"ok": ok, "manifest_names": names, "n_manifest_names": len(names), "empty_anim_files": empty_files[:20], "n_empty_files": len(empty_files), "unconverted": unconv[:20],
            "n_unconverted": len(unconv), "fmt_errors": fmt[:20], "n_fmt": len(fmt), "empty_bones": {k: v[:10] for k, v in empty.items()},
            "n_empty": sum(len(v) for v in empty.values()), "locator_clashes": loc[:40], "n_locator": len(loc),
            "nwr_shared": shared_bad[:20], "n_nwr_shared": len(shared_bad), "nwr_own_new": own_new[:20], "n_nwr_own_new": len(own_new),
            "nwr_own_baseline": len(base)}


def write_baseline(source_packs):
    res = NWR.lint([S.VANILLA] + [Path(p) for p in source_packs])
    own = sorted({f"{i}|{v}" for i, rows in res.items() for s, a, v in rows if not s.startswith(("shared_", "fam_", "parade_"))})
    BASELINE.write_text(json.dumps(own, indent=0))
    return len(own)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--baseline"]:
        print("baseline", write_baseline(sys.argv[2:]))
    else:
        print(json.dumps(run(sys.argv[1:]), indent=1)[:4000])

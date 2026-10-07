#!/usr/bin/env python3
"""build_rp0608_147.py — RP-06 Hostile Mobs RP v1.4.7 + RP-08 Items RP v1.4.7 (D-C260, Abs0lum 21:56 'All go' item E).
The 176-shot P0 read found both 1.4.6 packs still shipping 64x VANILLA copies of NEUTRAL-mob files on RP-07's paths
(cat/chicken/wolf/polar_bear/llama/panda_fa geometries, the cow/mooshroom/pig/sheep ambient animations, cat + chicken +
bee + iron golem textures).  A pack above RP-07 replaces RP-07's file outright; a pack below is harmless for these but
still dead weight.  v1.4.7 removes exactly those files from both packs (RP-06 also drops its dead vanilla-copy
entity/zombie_pigman.entity.json, which RP-07 1.4.12 supersedes), prunes them from textures_list.json, bumps the
manifests.  Everything else byte-identical to 1.4.6 (the gate asserts the diff).
NOT touched (surfaced for the backlog): RP-06's hostile files that RP-07 ALSO ships as 64x vanilla copies (creeper, zombie,
skeleton, illager, drowned...) — those are RP-07 leftovers to purge in an RP-07 build, not RP-06's to lose.
Sources: _intake/rp0608/RP-06-1.4.6.mcpack (Drive 11GYZKiDhYht0nAfd0WXjK2gcKQcPgQ2x) and RP-08-1.4.6.mcpack (1D2Kb7eEjbPxmnJH3yOw58YroJj0vXI0S)."""
import json, os, shutil, time, zipfile
from pathlib import Path

ROOT = Path("/home/claude")
DATE = "2026-09-27"
NEUTRAL_PURGE = [
    "models/entity/wolf.geo.json", "models/entity/polar_bear.geo.json", "models/entity/cat.geo.json", "models/entity/llama.geo.json",
    "models/entity/panda_fa.geo.json", "models/entity/chicken.geo.json",
    "animations/sheep_pw_ambient.animation.json", "animations/mooshroom_pw_ambient.animation.json", "animations/pig_pw_ambient.animation.json",
    "animations/cow_pw_ambient.animation.json",
    "textures/entity/chicken/chicken_cold.png", "textures/entity/chicken/chicken.png", "textures/entity/chicken/chicken_warm.png",
    "textures/entity/bee/bee_angry_nectar.png", "textures/entity/bee/bee_nectar.png", "textures/entity/bee/bee.png", "textures/entity/bee/bee_angry.png",
    "textures/entity/iron_golem/iron_golem.png",
    "textures/entity/cat/britishshorthair.png", "textures/entity/cat/siamese.png", "textures/entity/cat/white.png", "textures/entity/cat/jellie.png",
    "textures/entity/cat/calico.png", "textures/entity/cat/ragdoll.png", "textures/entity/cat/tabby.png", "textures/entity/cat/tuxedo.png",
    "textures/entity/cat/persian.png", "textures/entity/cat/red.png",
]
PACKS = {
    "RP-06": {"src": ROOT / "_intake/rp0608/RP-06-1.4.6.mcpack", "dst": ROOT / "_build/rp06-147", "purge": NEUTRAL_PURGE + ["entity/zombie_pigman.entity.json"],
              "name": "AbsolutRealism Hostile Mobs RP v1.4.7",
              "desc": (f"v1.4.7 ({DATE}) NEUTRAL-MOB PURGE (D-C260, P0 witness round): 28 vanilla-copy NEUTRAL-mob files that sat on RP-07's paths "
                       "(cat/chicken/wolf/polar_bear/llama/panda_fa geometries, cow/mooshroom/pig/sheep ambient animations, 64x cat + chicken + bee + "
                       "iron golem textures) are removed, plus the dead vanilla-copy zombie_pigman client entity (RP-07 v1.4.12 carries the Patrix one). "
                       "Everything else byte-identical to v1.4.6.")},
    "RP-08": {"src": ROOT / "_intake/rp0608/RP-08-1.4.6.mcpack", "dst": ROOT / "_build/rp08-147", "purge": NEUTRAL_PURGE,
              "name": "AbsolutRealism Items RP v1.4.7",
              "desc": (f"v1.4.7 ({DATE}) NEUTRAL-MOB PURGE (D-C260, P0 witness round): 28 vanilla-copy NEUTRAL-mob files that sat on RP-07's paths "
                       "(cat/chicken/wolf/polar_bear/llama/panda_fa geometries, cow/mooshroom/pig/sheep ambient animations, 64x cat + chicken + bee + "
                       "iron golem textures) are removed — an Items pack above RP-07 was replacing RP-07's Patrix files with them. "
                       "Everything else byte-identical to v1.4.6.")},
}

def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD {m}\n")

report = {}
for pk, cfg in PACKS.items():
    dst = cfg["dst"]
    if dst.exists():
        shutil.rmtree(dst)
    with zipfile.ZipFile(cfg["src"]) as z:
        z.extractall(dst)
    removed, absent = [], []
    for rel in cfg["purge"]:
        p = dst / rel
        if p.exists():
            p.unlink(); removed.append(rel)
        else:
            absent.append(rel)
    # prune empty dirs left behind
    for d in sorted({str((dst / r).parent) for r in removed}, key=len, reverse=True):
        try:
            if not os.listdir(d): os.rmdir(d)
        except OSError:
            pass
    # textures_list.json: drop the purged texture paths (with or without extension)
    tl = dst / "textures/textures_list.json"
    pruned = 0
    if tl.exists():
        lst = json.loads(tl.read_text(encoding="utf-8-sig"))
        stems = {r[:-4] for r in removed if r.endswith(".png")} | {r for r in removed if r.endswith(".png")}
        new = [x for x in lst if x not in stems]
        pruned = len(lst) - len(new)
        tl.write_text(json.dumps(new, indent=1), encoding="utf-8")
    man = json.loads((dst / "manifest.json").read_text(encoding="utf-8-sig"))
    man["header"]["name"] = cfg["name"]; man["header"]["version"] = [1, 4, 7]
    for mod in man["modules"]:
        mod["version"] = [1, 4, 7]
    man["header"]["description"] = cfg["desc"]
    (dst / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    dep = dst / "PW-DEPENDENCIES.md"
    if dep.exists():
        dep.write_text(dep.read_text(encoding="utf-8") + f"\n\n_v1.4.7 ({DATE}): {len(removed)} neutral-mob vanilla-copy files removed (they shadowed RP-07's Patrix files); see D-C260._\n", encoding="utf-8")
    report[pk] = {"removed": removed, "absent": absent, "textures_list_pruned": pruned}
    log(f"{pk} v1.4.7: {len(removed)} files removed ({len(absent)} already absent), textures_list pruned {pruned}, manifest stamped -> {dst}")
json.dump(report, open(ROOT / "_logs/rp0608_147_build_report.json", "w"), indent=1)
print(json.dumps({k: {"removed": len(v["removed"]), "absent": v["absent"], "pruned": v["textures_list_pruned"]} for k, v in report.items()}, indent=1))

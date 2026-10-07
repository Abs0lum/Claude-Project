#!/usr/bin/env python3
"""build_rp07_1425.py — D-C288 (R10 witness p7 d02, his 17:52 CT 09-29 "he has no bow ... then the bog failed"; Round 13 GO 18:0x).
RP-07 Neutral Mobs RP v1.4.25 from v1.4.24.

L-ATTACH-3: an attachable item (bow, crossbow, trident, shield, spyglass, WOLF ARMOR ...) is bound and drawn only when the holder's
client entity sets "enable_attachables": true. Vanilla wolf.entity.json and zombie_pigman.entity.json set it; our Converter-B rebuilds
(format 1.26.0) dropped it -> wolf armor is never drawn on our wolf, and an attachable in a zombified piglin's hand never shows
(its golden sword is a plain item, which is why nothing looked wrong). Fix = the one flag, nothing else (gate: only these two entity
files + manifest change; every other key of both descriptions byte-equal). The new ATT standing gate keeps it from coming back.
WATCH (P1): the vanilla wolf_armor attachable was modelled on the vanilla wolf's bones; ours is the Patrix / Converter-B wolf, so the
armor may sit wrong once it is drawn - the p8 wolf-armor step decides.
verify: python3 tools/verify_rp07_1425.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
RP06 = ROOT / "_build/rp06-1418" if (ROOT / "_build/rp06-1418/manifest.json").exists() else ROOT / "_build/rp06-1417"
FILES = {"entity/wolf.entity.json": "minecraft:wolf", "entity/zombie_pigman.entity.json": "minecraft:zombie_pigman"}


def attachables_on(dst, files=FILES):
    import attachables_lint as ATT
    n, before = ATT.lint_pack(dst)
    assert sorted(before) == sorted(files.items()), before
    for rel, ident in files.items():
        p = dst / rel; d = R.jl(p); de = d["minecraft:client_entity"]["description"]
        assert de["identifier"] == ident and de.get("enable_attachables") is not True, (rel, de.get("enable_attachables"))
        de["enable_attachables"] = True
        R.wj(p, d); CHANGED.append(rel)
    n, after = ATT.lint_pack(dst)
    assert not after, after
    return f"enable_attachables: true on {sorted(files.values())} (ATT findings {len(before)} -> 0)"


def verify_extra(cfg, check, files=FILES):
    OLD, NEW = cfg["src"], cfg["dst"]
    for rel, ident in files.items():
        a = R.jl(OLD / rel); b = R.jl(NEW / rel)
        da = dict(a["minecraft:client_entity"]["description"]); db = dict(b["minecraft:client_entity"]["description"])
        flag = db.pop("enable_attachables", None); da.pop("enable_attachables", None)
        check(f"AT1 {ident}: enable_attachables true and every other description key identical; file format_version unchanged",
              flag is True and da == db and a.get("format_version") == b.get("format_version"), f"flag {flag}")


CFG = {
    "src": ROOT / "_build/rp07-1424", "dst": ROOT / "_build/rp07-1425", "version": "1.4.25",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.25",
    "desc": ("v1.4.25 (2026-09-29) R10 FIX (D-C288): wolf and zombified piglin can show attachable items again (wolf armor, bows, "
             "crossbows) - the switch that lets the game draw them was missing. Includes all of 1.4.24: enderman jaw, tadpole, pufferfish, "
             "squid tilt, wolf / sheep sizes."),
    "pre": [], "jobs": [], "look": {}, "unbound_ok": {}, "placement": {},
    "post": [attachables_on],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-07", "ars_stack": [RP06],
    "prec_order": [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                   ("RP-07", ROOT / "_build/rp07-1425"), ("RP-06", RP06)],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp07_1425_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp07_1425_files.json", "w"), indent=1)

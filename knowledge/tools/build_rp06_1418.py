#!/usr/bin/env python3
"""build_rp06_1418.py — D-C288 (R10 witness p7 d02, his 17:52 CT 09-29 "he has no bow ... then the bog failed"; Round 13 GO 18:0x).
RP-06 Hostile Mobs RP v1.4.18 from v1.4.17.

THE BOGGED'S BOW (L-ATTACH-3): the bow is an ATTACHABLE; the game binds and draws an attachable only when the holder's client entity
sets "enable_attachables": true. Vanilla bogged.entity.json sets it (bedrock-samples, line 97); our Converter-B bogged (format 1.26.0)
does not -> the bow was never bound or drawn, before and after the 1.4.17 hand point, and the log stayed silent. (The one R9 binding
error was the STRAY - attachables on, no hand bone - which 1.4.17 fixed; D-C286's attribution to the bogged is corrected in D-C288.)
Same missing flag, same fix: piglin (its CROSSBOW), piglin brute, wither skeleton (a bow or any attachable). Their swords / axes are
plain items and showed already. Fix = the one flag, nothing else (the 1.4.17 bogged hand points stay: vanilla-frame, now actually used).
verify: python3 tools/verify_rp06_1418.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import build_rp07_1425 as B7

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
FILES = {"entity/bogged.entity.json": "minecraft:bogged", "entity/piglin.entity.json": "minecraft:piglin",
         "entity/piglin_brute.entity.json": "minecraft:piglin_brute", "entity/wither_skeleton.entity.json": "minecraft:wither_skeleton"}


def attachables_on(dst):
    out = B7.attachables_on(dst, FILES)
    CHANGED.extend(FILES)
    return out


def verify_extra(cfg, check):
    B7.verify_extra(cfg, check, FILES)
    _, g = R.geo_file(cfg["dst"], "geometry.bogged.patrix")
    hp = {b["name"]: b.get("pivot") for b in g["bones"] if b["name"] in ("rightItem", "leftItem")}
    check("AT2 bogged keeps the 1.4.17 hand points (now used by the bow)", hp == {"rightItem": [-6.0, 14.4956, 0.0008], "leftItem": [6.0, 14.4956, 2.4992]}, f"{hp}")


CFG = {
    "src": ROOT / "_build/rp06-1417", "dst": ROOT / "_build/rp06-1418", "version": "1.4.18",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.18",
    "desc": ("v1.4.18 (2026-09-29) R10 FIX (D-C288): the bogged holds its bow for real (the switch that lets the game draw a bow was "
             "missing); piglin crossbows, piglin brute and wither skeleton held attachables too. Includes all of 1.4.17: stray + bogged "
             "hand points, silverfish visible, skeleton + wither skeleton grip."),
    "pre": [], "jobs": [], "look": {}, "unbound_ok": {}, "placement": {},
    "post": [attachables_on],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1425"],
    "prec_order": [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                   ("RP-07", ROOT / "_build/rp07-1425"), ("RP-06", ROOT / "_build/rp06-1418")],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp06_1418_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp06_1418_files.json", "w"), indent=1)

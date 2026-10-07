#!/usr/bin/env python3
"""fetch_civmods.py — his 00:06 ask ("Can you fetch these to my drive FOR me?" / 00:08 "Any you can't fetch, I'll download
manually"): the civ-reference mods from the 10-05 list that Modrinth hosts are downloaded (one file per project: the
Minecraft 1.20.1 Forge build when there is one — the Casket of Reveries' version — else 1.20.1 any loader, else the
newest), each checked against Modrinth's sha1, into _intake/civmods/modrinth/. A ledger (LEDGER.json there) records slug,
title, licence, version, file, bytes, sha1, source URL. Personal use (§9): licences are recorded, not judged.
Usage: fetch_civmods.py"""
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

OUT = Path("/home/claude/_intake/civmods/modrinth")
UA = {"User-Agent": "AbsolutRealism-personal-research/1.0"}
SLUGS = ["bountiful-villager", "bountiful", "p1neros-dialog-lib", "minecolonies", "minecraft-comes-alive-reborn", "libertyvillagers",
         "villager-workers", "villager-recruits", "guard-villagers", "numismatic-overhaul", "countereds-settlement-roads", "easy-npc",
         "townstead", "townsteadfactions", "villagertimetable", "villager-schedules", "tale-of-kingdoms-a-new-conquest", "civilians",
         "observant-villagers", "reputated-villagers", "village-business", "dynamic-villager-trades", "villagerquests", "roadweaver",
         "roadarchitect", "routes", "easy-villagers", "village-bounties", "villager-retaliation", "better-wandering-trader",
         "villages-and-pillages", "medieval-buildings", "mebahels-rpg-villager-quests-and-companions", "villager-names",
         "towns-and-towers", "structurize", "domum-ornamentum"]


def get(url):
    err = None
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 — retried, then reported
            err = e
            if getattr(e, "code", None) == 404:
                break
            time.sleep(2 ** k)
    raise err


def pick(versions):
    def has(v, loader, mc):
        return (loader is None or loader in v["loaders"]) and (mc is None or mc in v["game_versions"])
    for loader, mc in (("forge", "1.20.1"), (None, "1.20.1"), (None, None)):
        for v in versions:                                   # Modrinth lists the newest first
            if has(v, loader, mc):
                return v
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ledger_p = OUT / "LEDGER.json"
    ledger = json.loads(ledger_p.read_text()) if ledger_p.exists() else {}
    misses = []
    for slug in SLUGS:
        if slug in ledger and (OUT / ledger[slug]["file"]).exists():
            print(f"have {slug}")
            continue
        try:
            proj = json.loads(get(f"https://api.modrinth.com/v2/project/{slug}"))
            vers = json.loads(get(f"https://api.modrinth.com/v2/project/{slug}/version"))
            v = pick(vers)
            if not v:
                raise RuntimeError("no versions")
            f = next((x for x in v["files"] if x.get("primary")), v["files"][0])
            data = get(f["url"])
        except Exception as e:  # noqa: BLE001
            print(f"MISS {slug}: {e}")
            misses.append(slug)
            continue
        sha1 = hashlib.sha1(data).hexdigest()
        if sha1 != f["hashes"]["sha1"]:
            print(f"MISS {slug}: sha1 mismatch")
            misses.append(slug)
            continue
        name = f"{slug}__{f['filename']}"
        (OUT / name).write_bytes(data)
        ledger[slug] = {"title": proj["title"], "license": (proj.get("license") or {}).get("id"), "version": v["version_number"],
                        "loaders": v["loaders"], "game_versions": v["game_versions"][-6:], "file": name, "bytes": len(data), "sha1": sha1,
                        "source": f"https://modrinth.com/mod/{slug}", "url": f["url"], "fetched": time.strftime("%Y-%m-%d")}
        ledger_p.write_text(json.dumps(ledger, indent=1))
        print(f"OK {slug} {v['version_number']} {len(data):,} B {ledger[slug]['license']}")
    print(f"DONE {len(ledger)} files in {OUT}; missed: {misses}")


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""fetch_cf.py — his 00:06 / 00:08 ask, the CurseForge half: project + file names come from the public widget API
(api.cfwidget.com — curseforge.com and its API refuse this workspace), the bytes from the CurseForge CDN
(edge.forgecdn.net/files/<id/1000>/<id%1000>/<name>). One file per project: the exact file the Casket of Reveries pack
pins (its manifest.json) when the project is in it, else the newest 1.20.1 Forge file, else the newest file. Each download
must match the widget's byte count. Ledger: _intake/civmods/curseforge/LEDGER.json. Personal use (§9).
Usage: fetch_cf.py"""
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("/home/claude/_intake/civmods/curseforge")
CASKET = Path("/home/claude/_intake/casket/x/manifest.json")
UA = {"User-Agent": "AbsolutRealism-personal-research/1.0"}
PROJECTS = [  # (widget path, label)
    ("minecraft/mc-mods/tudigong-wayfinder", "TuDiGong: Wayfinder (Casket)"),
    ("minecraft/mc-mods/bountiful-villager", "Bountiful Villager (Casket)"),
    ("minecraft/mc-mods/p1neros-dialogue-lib", "P1nero's Dialogue Lib (Casket)"),
    ("minecraft/mc-mods/bountiful", "Bountiful (Casket)"),
    ("minecraft/mc-mods/tektopia", "TekTopia"),
    ("minecraft/mc-mods/millenaire", "Millenaire"),
    ("minecraft/mc-mods/custom-npcs", "Custom NPCs"),
    ("minecraft/mc-mods/lightmans-currency", "Lightman's Currency"),
    ("minecraft/mc-mods/human-companions", "Human Companions"),
    ("minecraft/mc-mods/taterzens-forge", "Taterzens (Forge)"),
    ("minecraft/mc-mods/structurize", "Structurize"),
    ("minecraft/mc-mods/domum-ornamentum", "Domum Ornamentum"),
    ("minecraft/mc-mods/more-villagers-re-employed", "More Villagers Re-employed"),
    ("minecraft/mc-mods/villagersplus", "VillagersPlus"),
    ("minecraft/mc-mods/villager-reputation", "Villager Reputation"),
    ("minecraft/mc-mods/mindofthecolony", "MindOfTheColony"),
    ("minecraft/mc-mods/talking-colonists-minecolonies-addon", "Talking Colonists"),
    ("minecraft/mc-mods/speaking-villagers", "Speaking Villagers"),
    ("minecraft/mc-mods/minecolonies-war-n-taxes", "MineColonies War N Taxes"),
    ("minecraft/mc-mods/choicetheorems-overhauled-village", "ChoiceTheorem's Overhauled Village"),
    ("minecraft/mc-mods/better-village-forge", "Better Villages (Forge)"),
    ("minecraft/mc-mods/guard-villagers", "Guard Villagers"),
    ("minecraft/mc-mods/recruits", "Villager Recruits"),
    ("minecraft/mc-mods/workers", "Villager Workers"),
    ("minecraft-bedrock/addons/jerrys-colonies", "Jerry's Colonies (Bedrock)"),
    ("minecraft-bedrock/addons/empire-expansion", "Empire Expansion (Bedrock)"),
    ("minecraft-bedrock/addons/village-ruler", "Village Ruler (Bedrock)"),
    ("minecraft-bedrock/addons/hardworking-villagers", "Hardworking Villagers (Bedrock)"),
    ("minecraft-bedrock/addons/guard-villager-add-on", "Guard Villager (Bedrock)"),
    ("minecraft-bedrock/addons/village-guards-add-on", "Village Guards (Bedrock)"),
    ("minecraft-bedrock/addons/village-generator-function-pack", "Village Generator (Bedrock)"),
    ("minecraft-bedrock/addons/human-companions", "Human Companions (Bedrock)"),
    ("minecraft/mc-addons/kingdom-constructor", "Kingdom Constructor (Bedrock)"),
]


def get(url, tries=4):
    err = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            err = e
            if getattr(e, "code", None) in (403, 404):
                break
            time.sleep(2 ** k)
    raise err


def pick(files, pinned):
    if pinned:
        for f in files:
            if f["id"] in pinned:
                return f
    for f in files:
        if "1.20.1" in f.get("versions", []) and "Forge" in f.get("versions", []):
            return f
    return files[0] if files else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pinned = {f["fileID"] for f in json.loads(CASKET.read_text())["files"]} if CASKET.exists() else set()
    ledger_p = OUT / "LEDGER.json"
    ledger = json.loads(ledger_p.read_text()) if ledger_p.exists() else {}
    misses = []
    for path, label in PROJECTS:
        if path in ledger and (OUT / ledger[path]["file"]).exists():
            print(f"have {label}")
            continue
        try:
            d = json.loads(get(f"https://api.cfwidget.com/{path}"))
            if d.get("error") or not d.get("files"):
                raise RuntimeError(d.get("error") or "no files")
            files = sorted(d["files"], key=lambda f: f.get("uploaded_at", ""), reverse=True)
            f = pick(files, pinned)
            fid, name = f["id"], f["name"]
            url = f"https://edge.forgecdn.net/files/{fid // 1000}/{fid % 1000}/{urllib.parse.quote(name)}"
            data = get(url)
            if f.get("filesize") and len(data) != f["filesize"]:
                raise RuntimeError(f"size {len(data)} != {f['filesize']}")
        except Exception as e:  # noqa: BLE001
            print(f"MISS {label}: {e}")
            misses.append(label)
            continue
        slug = path.split("/")[-1]
        fname = f"{slug}__{name}"
        (OUT / fname).write_bytes(data)
        ledger[path] = {"label": label, "project": d.get("id"), "title": d.get("title"), "file_id": fid, "file": fname, "bytes": len(data),
                        "md5": hashlib.md5(data).hexdigest(), "versions": f.get("versions"), "pinned_by_casket": fid in pinned,
                        "source": f"https://www.curseforge.com/{path}", "url": url, "fetched": time.strftime("%Y-%m-%d")}
        ledger_p.write_text(json.dumps(ledger, indent=1))
        print(f"OK {label}: {name} {len(data):,} B{' (Casket pin)' if fid in pinned else ''}")
    print(f"DONE {len(ledger)} files in {OUT}; missed: {misses}")


if __name__ == "__main__":
    sys.exit(main())

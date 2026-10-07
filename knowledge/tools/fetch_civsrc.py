#!/usr/bin/env python3
"""fetch_civsrc.py — his 00:06 / 00:08 ask, the open-source half: each repository on the 10-05 civ list is cloned shallow
(git, the only route to GitHub from this workspace) into the scratchpad, packed WITHOUT .git as
_intake/civmods/source/<owner>__<repo>.tar.gz, and the working copy removed (a temporary copy; the archive is the keep).
Ledger: _intake/civmods/source/LEDGER.json (repo, commit, licence file name, bytes, md5).
Usage: fetch_civsrc.py"""
import hashlib
import json
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

OUT = Path("/home/claude/_intake/civmods/source")
TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/civsrc")
REPOS = ["watabou/TownGeneratorOS", "gitsh01/libertyvillagers", "ejektaflex/Bountiful", "Coun7ered/settlement-roads-new",
         "Luke100000/minecraft-comes-alive", "Leviaria/Millenaire", "ldtteam/minecolonies", "ldtteam/Structurize", "ldtteam/Domum-Ornamentum",
         "avdstaaij/gdpc", "SamB440/Tale-of-Kingdoms", "MarkusBordihn/BOs-Easy-NPC",
         "seymourimadeit/guardvillagers", "gliscowo/numismatic-overhaul", "Globox1997/VillagerQuests", "Serilum/Villager-Names",
         "shiroha-233/RoadWeaver", "0xCoDSnet/RoadArchitect", "CitizensDev/Citizens2", "mcmonkeyprojects/Sentinel",
         "Niels-NTG/gdmc_http_interface", "ScholliYT/MGAIA-Minecraft-GDMC",
         "LynixPlayz/villager-schedules", "henkelmax/easy-villagers", "microsoft/minecraft-scripting-samples"]
MAX_BYTES = 60 * 1024 * 1024


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    ledger_p = OUT / "LEDGER.json"
    ledger = json.loads(ledger_p.read_text()) if ledger_p.exists() else {}
    misses = []
    for repo in REPOS:
        name = repo.replace("/", "__")
        tgz = OUT / f"{name}.tar.gz"
        if repo in ledger and tgz.exists():
            print(f"have {repo}")
            continue
        work = TMP / name
        if work.exists():
            shutil.rmtree(work)
        r = subprocess.run(["git", "clone", "--depth", "1", "-q", f"https://github.com/{repo}", str(work)], capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            print(f"MISS {repo}: {r.stderr.strip()[:200]}")
            misses.append(repo)
            continue
        commit = subprocess.run(["git", "-C", str(work), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        lic = sorted(p.name for p in work.iterdir() if p.name.upper().startswith(("LICENSE", "LICENCE", "COPYING")))
        size = sum(p.stat().st_size for p in work.rglob("*") if p.is_file() and ".git" not in p.parts)
        if size > MAX_BYTES:
            print(f"MISS {repo}: {size:,} B is over the {MAX_BYTES:,} B cap")
            misses.append(repo)
            shutil.rmtree(work)
            continue
        with tarfile.open(tgz, "w:gz") as tf:
            tf.add(work, arcname=name, filter=lambda ti: None if "/.git" in ti.name or ti.name.endswith(".git") else ti)
        shutil.rmtree(work)
        data = tgz.read_bytes()
        ledger[repo] = {"commit": commit, "licence_files": lic, "tree_bytes": size, "file": tgz.name, "bytes": len(data),
                        "md5": hashlib.md5(data).hexdigest(), "source": f"https://github.com/{repo}", "fetched": time.strftime("%Y-%m-%d")}
        ledger_p.write_text(json.dumps(ledger, indent=1))
        print(f"OK {repo} {commit[:8]} tree {size:,} B -> {len(data):,} B {lic}")
    print(f"DONE {len(ledger)} archives in {OUT}; missed: {misses}")


if __name__ == "__main__":
    main()

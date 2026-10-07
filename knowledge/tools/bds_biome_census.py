#!/usr/bin/env python3
"""bds_biome_census.py — the MODERN-BIOME TREE CENSUS (tree program, grove ruling, D-C504): which biomes grow OUR trees
and which still grow vanilla's? Drives the workspace BDS through its console (stdin): `locate biome <id>` finds the
nearest sample of each biome from the world origin, then `scriptevent pw:census go <x> <z> <id>` has the census BP
(_build/biomecensus-0.0.2) count vanilla logs by species / vanilla leaves / our tree blocks / our roots in the 96 x 96
area around it. Fresh pristine world per run (bds_load.install) — the seed reproduces, so the coordinates are a
regression test. Nothing is shipped; this is a measurement.
Usage: bds_biome_census.py [--seconds N] [--biomes a,b,c] DIR [DIR ...]
Output: _bds/logs/biomecensus-<stamp>.txt (console) + .json (per-biome records) + a table on stdout."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import bds_load as B  # noqa: E402

# the console wants the namespaced BEDROCK id (console probe 01:40 CT 10-03: "locate biome forest" -> syntax error,
# "locate biome minecraft:forest" -> "The nearest minecraft:forest is at block -32, 95, -32 (45 blocks away)")
BEDROCK_ID = {"dark_forest": "roofed_forest", "old_growth_pine_taiga": "mega_taiga", "old_growth_spruce_taiga": "redwood_taiga_mutated",
              "windswept_forest": "extreme_hills_plus_trees", "windswept_hills": "extreme_hills", "swamp": "swampland",
              "old_growth_birch_forest": "birch_forest_mutated", "wooded_badlands": "mesa_plateau_stone", "sparse_jungle": "jungle_edge",
              "snowy_taiga": "cold_taiga", "snowy_plains": "ice_plains"}
MODERN = ["grove", "snowy_slopes", "jagged_peaks", "frozen_peaks", "stony_peaks", "meadow", "cherry_grove", "mangrove_swamp", "pale_garden"]
CLASSIC = ["forest", "birch_forest", "taiga", "old_growth_pine_taiga", "dark_forest", "savanna", "jungle", "flower_forest", "windswept_forest", "swamp", "plains", "snowy_taiga"]
LOCATED = re.compile(r"is at block (-?\d+), (?:\(y\?\)|-?\d+), (-?\d+)")


def wait_for(out, needle, t0, limit, p):
    """poll the console log for a substring (or a crash); returns the log text or None on timeout"""
    while time.time() - t0 < limit:
        time.sleep(1.5)
        txt = out.read_text(errors="ignore")
        if needle in txt:
            return txt
        if "Crash" in txt or p.poll() is not None:
            return None
    return None


def send(p, line):
    p.stdin.write(line + "\n")
    p.stdin.flush()


def run(dirs, biomes, seconds=1200):
    B.install(dirs, False)
    B.LOGS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = B.LOGS / f"biomecensus-{stamp}.txt"
    results = []
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=B.SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT,
                             env={"LD_LIBRARY_PATH": "."}, text=True)
        t0 = time.time()
        if wait_for(out, '"step":"ready"', t0, 180, p) is None:
            print("server never reported ready")
        for bio in biomes:
            if time.time() - t0 > seconds:
                results.append({"biome": bio, "status": "budget"})
                continue
            before = len(out.read_text(errors="ignore"))
            send(p, f"locate biome minecraft:{BEDROCK_ID.get(bio, bio)}")
            hit = None
            t1 = time.time()
            while time.time() - t1 < 60:
                time.sleep(1)
                tail = out.read_text(errors="ignore")[before:]
                m = LOCATED.search(tail)
                if m:
                    hit = (int(m.group(1)), int(m.group(2)))
                    break
                if re.search(r"(?i)could not find|unknown biome|no such|syntax error", tail):
                    break
            if hit is None:
                results.append({"biome": bio, "status": "not located", "tail": out.read_text(errors="ignore")[before:][-300:]})
                continue
            x, z = hit
            before = len(out.read_text(errors="ignore"))
            send(p, f"scriptevent pw:census go {x} {z} {bio}")
            txt = None
            t2 = time.time()
            while time.time() - t2 < 240:
                time.sleep(2)
                tail = out.read_text(errors="ignore")[before:]
                if f'"label":"{bio}"' in tail:
                    txt = tail
                    break
                if "Crash" in tail or p.poll() is not None:
                    break
            rec = {"biome": bio, "at": [x, z], "status": "no census record"}
            if txt:
                for line in txt.splitlines():
                    m = re.search(r"\[CIVTEST\] (\{.*\})\s*$", line)
                    if m and f'"label":"{bio}"' in m.group(1):
                        try:
                            rec = json.loads(m.group(1))
                            rec["biome"] = bio
                            rec["status"] = "ok"
                        except json.JSONDecodeError:
                            rec["status"] = "unparsed"
            results.append(rec)
        try:
            send(p, "scriptevent pw:census done")
            time.sleep(2)
            send(p, "stop")
        except Exception:
            pass
        try:
            p.wait(timeout=90)
        except subprocess.TimeoutExpired:
            p.kill()
    text = out.read_text(errors="ignore")
    errs = [l for l in text.splitlines() if re.search(r"\b(ERROR)\b|\[error\]", l)]
    (B.LOGS / f"biomecensus-{stamp}.json").write_text(json.dumps({"results": results, "errors": errs}, indent=1))
    return out, results, errs


def table(results):
    rows = ["biome                  | at              | loaded | vanilla logs                     | v.leaves | pw blocks | roots | on roots"]
    for r in results:
        if r.get("status") != "ok":
            rows.append(f"{r['biome']:<22} | {r.get('status')}" + (f" {r.get('at')}" if r.get("at") else ""))
            continue
        vl = ", ".join(f"{k} {v}" for k, v in sorted(r.get("vanillaLogs", {}).items())) or "-"
        rows.append(f"{r['biome']:<22} | {str(r.get('at')):<15} | {str(r.get('loaded')):<6} | {vl:<32} | {r.get('vanillaLeaves', 0):>8} | {r.get('pwBlocks', 0):>9} | {r.get('roots', 0):>5} | {r.get('treesOnRoots', '-')}")
    return "\n".join(rows)


if __name__ == "__main__":
    args = sys.argv[1:]
    secs = 1200
    biomes = MODERN + CLASSIC
    while args and args[0].startswith("--"):
        if args[0] == "--seconds":
            secs = int(args[1])
            args = args[2:]
        elif args[0] == "--biomes":
            biomes = args[1].split(",")
            args = args[2:]
        else:
            raise SystemExit(f"unknown flag {args[0]}")
    out, results, errs = run(args, biomes, secs)
    print(f"log {out} · {len(results)} biomes · {len(errs)} ERROR lines")
    print(table(results))
    for e in errs[:10]:
        print("ERR", e[-200:])

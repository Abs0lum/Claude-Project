#!/usr/bin/env python3
"""all_mob_size_census.py — D-C363 (his 01:51 'EVERY MOB through the hyper-real scaling'): how big every mob is DRAWN in game.
Drawn size = visible_size (texels past the alpha cut, everyday render state, client scripts.scale) x the adult minecraft:scale of
the behaviour entity that runs it. Covers: every client entity in RP-07 (ported pw_menagerie + sf_nba + vanilla re-skins), RP-06,
RP-08, + vanilla client entities for vanilla mobs we do not re-skin. Behaviour: PW-StripMine BP 1.3.11, BP-02 1.3.198, else Mojang.
Output: _docs/sizes/all_mob_census.json (one row per identifier). READ-ONLY."""
import glob, json, sys
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import roster_size_census as RC

ROOT = Path("/home/claude")
import os
RPS = [ROOT / "_build" / os.environ.get("CENSUS_RP07", "rp07-1437"), ROOT / "_build/rp06-1424", ROOT / "_build/rp08-148"]
BPS = [ROOT / "_build" / os.environ.get("CENSUS_SM", "stripmine-bp-1311"), ROOT / "_build" / os.environ.get("CENSUS_BP02", "bp02-198"),
       ROOT / "_intake/bedrock-samples/behavior_pack"]
OUT = os.environ.get("CENSUS_OUT", "all_mob_census.json")
VAN_RP = ROOT / "_intake/bedrock-samples/resource_pack"


def jl(p): return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))


def bp_index():
    """identifier -> (file, adult scale, groups that set a scale) — first pack in BPS order wins (StripMine, BP-02, Mojang)"""
    out = {}
    for bp in BPS:
        for f in glob.glob(str(bp / "entities/**/*.json"), recursive=True):
            try: e = jl(f)["minecraft:entity"]
            except Exception: continue
            i = e.get("description", {}).get("identifier")
            if not i or i in out: continue
            top = float(((e.get("components") or {}).get("minecraft:scale") or {}).get("value", 1.0) or 1.0)
            groups = {g: c["minecraft:scale"].get("value") for g, c in (e.get("component_groups") or {}).items()
                      if isinstance(c, dict) and isinstance(c.get("minecraft:scale"), dict)}
            adult = [v for g, v in groups.items() if "adult" in g.lower() and isinstance(v, (int, float))]
            out[i] = {"bp_file": str(f), "bp_pack": bp.name, "top_scale": top, "groups": groups,
                      "adult_scale": float(adult[0]) if adult else top}
    return out


def client_index():
    out = {}
    for rp in RPS:
        for f in glob.glob(str(rp / "entity/**/*.json"), recursive=True):
            d = RC.client_desc(f)
            if d and d.get("identifier") and d["identifier"] not in out: out[d["identifier"]] = (f, rp)
    van = RC.vanilla_entity_files()
    for i, f in van.items():
        if i not in out: out[i] = (f, VAN_RP)
    return out


class Slow(Exception): pass


def _alarm(*_): raise Slow()


def one(args):
    """one entity; 90 s cap (a bone-parent loop or a huge model must not stall the census — listed instead)"""
    import signal
    i, f, rp = args
    stack = [str(x) for x in RPS if x != Path(rp)] + [str(VAN_RP)]
    signal.signal(signal.SIGALRM, _alarm); signal.alarm(90)
    try: m = RC.measure_file(f, Path(rp), [Path(s) for s in stack])
    except Slow: return i, {"error": "timed out after 90 s"}
    except Exception as e: return i, {"error": str(e)[:120]}
    finally: signal.alarm(0)
    return i, m


if __name__ == "__main__":
    bps, cls = bp_index(), client_index()
    jobs = [(i, f, str(rp)) for i, (f, rp) in sorted(cls.items())]
    with Pool(8) as p: res = dict(p.imap_unordered(one, jobs, chunksize=1))
    rows = []
    for i, (f, rp) in sorted(cls.items()):
        m = res.get(i) or {}; b = bps.get(i, {})
        s = b.get("adult_scale", 1.0)
        row = {"id": i, "client_file": f, "rp": Path(rp).name, "bp_pack": b.get("bp_pack"), "bp_file": b.get("bp_file"),
               "adult_scale": s, "top_scale": b.get("top_scale"), "scale_groups": b.get("groups")}
        if m and "h" in m:
            row.update({"model_h": m["h"], "model_l": m["l"], "model_w": m["w"], "client_scale": m.get("client_scale"),
                        "h": round(m["h"] * s, 3), "l": round(m["l"] * s, 3), "w": round(m["w"] * s, 3), "rule": m.get("visibility_rule")})
        else: row["measure_error"] = (m or {}).get("error", "no visible geometry")
        rows.append(row)
    out = ROOT / "_docs/sizes" / OUT; out.write_text(json.dumps(rows, indent=1))
    ok = sum(1 for r in rows if "h" in r)
    print(f"{len(rows)} client entities, {ok} measured, {len(rows) - ok} not; -> {out}")

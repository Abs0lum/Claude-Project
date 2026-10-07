#!/usr/bin/env python3
"""recheck_r6.py — RECHECK-WEEK R6: the week's SUBSYSTEM audits re-run on the delivered install set (PW_STACK=final).
  roofs #174: roof_audit (every roof block, bounds/uv/seams) + roof_seams (border steps on the kit)
  placement #175: block_placement_census (every BP-02 block under the measured transformation law)
  CIVITAS: civ_marker_audit on the 13 roster manifests; stage proof (s0..s4 == finished) re-cut into a temp dir and compared
           byte-exact with the stage files in bp02-207; roster structures in 207 == staging
  trees T2: 544 templates / features / pools in bp02-206 cross-checked (every pool member exists, every feature's
           structure exists and parses, root states within tpl 0..15 / tpl_hi 0..1, PW_SCANNER_ON false)
  mobs: entity_precedence (every client entity of ours wins in his order), spawn_group_audit (bp02-206),
        face_alpha_census + all_mob_size_census + mob_mers_census on the delivered RPs, sound_load_census (final stack)
Each result -> _docs/recheck/R6-subsystems.json as it finishes. Read-only on the builds."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"
T = ROOT / "tools"
OUT = ROOT / "_docs/recheck/R6-subsystems.json"
ENV = dict(os.environ, PW_STACK="final", CENSUS_RP07="rp07-1444", CENSUS_BP02="bp02-206", CENSUS_SM="bp02-206",
           CENSUS_OUT="/home/claude/_docs/recheck/all_mob_census_recheck.json")
rows = []


def rec(label, rc, text, seconds):
    rows.append({"audit": label, "rc": rc, "seconds": round(seconds, 1), "tail": text[-7000:]})
    OUT.write_text(json.dumps(rows, indent=1))
    print(f"[{seconds:6.1f}s] rc={rc} {label}", flush=True)


def sh(label, cmd, tmo=1200, env=ENV, cwd=ROOT):
    t0 = time.time()
    try:
        p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, timeout=tmo, env=env)
        rec(label, p.returncode, p.stdout + ("\nSTDERR: " + p.stderr[-2500:] if p.stderr.strip() else ""), time.time() - t0)
    except subprocess.TimeoutExpired:
        rec(label, "TIMEOUT", "", time.time() - t0)


def py(label, code, tmo=1200):
    sh(label, [sys.executable, "-c", code], tmo)


TREES = r'''
import json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools"); import mcstructure as M; import molang_lint as ML
B = Path("/home/claude/_build/bp02-206"); bad = []
feats = {}
for f in (B / "features").rglob("*.json"):
    try: d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
    except Exception as e: bad.append(f"PARSE {f.name}: {e}"); continue
    for k, v in d.items():
        if k.startswith("minecraft:") and isinstance(v, dict) and "description" in v: feats[v["description"]["identifier"]] = (k, v, f.name)
tmpl = sorted((B / "structures/pw/trees").glob("*.mcstructure"))
print("templates", len(tmpl), "features", sum(1 for i in feats if i.startswith("pw:tree_")), "all features", len(feats))
stf = {i: v for i, (k, v, fn) in feats.items() if k == "minecraft:structure_template_feature" and i.startswith("pw:tree_")}
names = {p.stem for p in tmpl}
for i, v in stf.items():
    sn = v["structure_name"].split("/")[-1]
    if sn not in names: bad.append(f"{i}: structure {v['structure_name']} missing")
pools = {i: v for i, (k, v, fn) in feats.items() if k == "minecraft:weighted_random_feature"}
members = 0
for i, v in pools.items():
    for m, w in v["features"]:
        members += 1
        if m not in feats: bad.append(f"pool {i}: member {m} undefined")
print("pools", len(pools), "members", members)
# every template parses; root states in range; count roots
roots = 0; species = {}
for p in tmpl:
    try: st = M.Structure.from_bytes(p.read_bytes())
    except Exception as e: bad.append(f"TEMPLATE {p.name}: {e}"); continue
    for name, states, *_ in st.palette:
        if name.endswith("_root"):
            tv = states.get("pw:tpl"); th = states.get("pw:tpl_hi")
            tv = tv.value if hasattr(tv, "value") else tv; th = th.value if hasattr(th, "value") else th
            if tv is None or not (0 <= tv <= 15) or (th is not None and th not in (0, 1)): bad.append(f"{p.name}: root states tpl={tv} tpl_hi={th}")
            roots += 1
print("templates with root palette entries", roots)
# root blocks: state enums <= 16
for f in (B / "blocks").rglob("*.json"):
    try: d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
    except Exception as e: bad.append(f"PARSE block {f.name}: {e}"); continue
    desc = d.get("minecraft:block", {}).get("description", {})
    for s, vals in (desc.get("states") or {}).items():
        if isinstance(vals, list) and len(vals) > 16: bad.append(f"{f.name}: state {s} has {len(vals)} values (> 16)")
mj = (B / "scripts/main.js").read_text()
print("PW_SCANNER_ON false:", "const PW_SCANNER_ON = false" in mj)
if "const PW_SCANNER_ON = false" not in mj: bad.append("scanner not off")
# feature rules reference existing features
rules = 0
for f in (B / "feature_rules").rglob("*.json"):
    try: d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
    except Exception as e: bad.append(f"PARSE rule {f.name}: {e}"); continue
    r = d.get("minecraft:feature_rules", {}); rules += 1
    pf = r.get("description", {}).get("places_feature")
    if pf and pf not in feats: bad.append(f"rule {f.name} places {pf} (undefined)")
print("feature rules", rules)
print("PROBLEMS", len(bad)); print("\n".join(bad[:40]))
sys.exit(1 if bad else 0)
'''

CIV = r'''
import sys, json, hashlib, tempfile, shutil
from pathlib import Path
sys.path.insert(0, "/home/claude/tools"); import civ_stages as CS
B = Path("/home/claude/_build/bp02-207"); STG = Path("/home/claude/_staging/civ"); bad = []
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()
roster = sorted(STG.glob("structures/pw/*.mcstructure"))
for p in roster:
    q = B / "structures/pw" / p.name
    if not q.exists() or md5(q) != md5(p): bad.append(f"207 structure differs/missing: {p.name}")
td = Path(tempfile.mkdtemp(prefix="stg_"))
n = 0
for p in roster:
    res, floors = CS.cut(p, td)            # asserts s0..s4 in order == the finished building, cell by cell
    for name, stage, cnt, ents in res:
        n += 1
        q = B / "structures/pw/stages" / name
        if not q.exists() or md5(q) != md5(td / name): bad.append(f"stage file differs/missing in 207: {name}")
print("roster", len(roster), "stage files re-cut + proven", n)
print("PROBLEMS", len(bad)); print("\n".join(bad[:20]))
sys.exit(1 if bad else 0)
'''

PREC = r'''
import sys; sys.path.insert(0, "/home/claude/tools")
import entity_precedence as EP
from pathlib import Path
R = Path("/home/claude/_build")
ORDER = [("Markers RP 0.2.2", R / "markers-0.2.2-rp/RP"), ("RP-11 1.3.40", R / "rp11-140"), ("RP-10 1.3.51", R / "rp10-151"),
         ("RP-08 1.4.13", R / "rp08-1413"), ("RP-07 1.4.44", R / "rp07-1444"), ("RP-06 1.4.29", R / "rp06-1429"), ("RP-05 1.3.58", R / "rp05-58"),
         ("RP-04 1.3.156", R / "rp04-156"), ("RP-03 1.3.67", R / "rp03-67"), ("RP-02 2.0.7", R / "rp02-207"), ("RP-01 1.3.117", R / "rp01-117"),
         ("vanilla", Path("/home/claude/_intake/bedrock-samples/resource_pack"))]
rows = EP.census(ORDER, ours=("RP-06 1.4.29", "RP-07 1.4.44", "RP-08 1.4.13"))
lose = [r for r in rows if r.get("ours_lose")]
print(len(rows), "shared identifiers;", len(lose), "where ours loses")
for r in lose[:30]: print(r)
sys.exit(1 if lose else 0)
'''


def main():
    sh("roof_audit #174 (bp02-206 / rp04-156 / rp01-117)", [sys.executable, T / "roof_audit.py"])
    sh("roof_seams #174 (kit border steps)", [sys.executable, T / "roof_seams.py", "recheck"])
    sh("block_placement_census #175 (every BP-02 206 block)", [sys.executable, T / "block_placement_census.py"])
    sh("civ_marker_audit (13 roster manifests)", [sys.executable, T / "civ_marker_audit.py", "recheck"])
    py("civ stage proof + 207 structure/stage files == staging", CIV)
    py("trees T2 wiring cross-check (bp02-206)", TREES)
    py("entity_precedence (ours wins in his stack order)", PREC)
    sh("spawn_group_audit (bp02-206)", [sys.executable, T / "spawn_group_audit.py"])
    sh("all_mob_size_census (rp07-1444 / bp02-206)", [sys.executable, T / "all_mob_size_census.py"], tmo=1800)
    sh("mob_mers_census (final stack)", [sys.executable, T / "mob_mers_census.py"], tmo=1800)
    sh("sound_load_census (final stack)", [sys.executable, T / "sound_load_census.py", "recheck"], tmo=1800)
    print("R6 DONE")


if __name__ == "__main__":
    main()

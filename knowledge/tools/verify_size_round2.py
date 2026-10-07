#!/usr/bin/env python3
"""verify_size_round2.py — gate for SIZE ROUND 2 (BP-02 1.3.192 · PW-StripMine BP 1.3.5), FA-1 / D-C298.
VSC: every changed behaviour entity differs from its source (the previous build, or Mojang 1.26.50 for a new override) ONLY in
minecraft:scale values (x the planned factor, 3 dp) plus at most one inserted adult scale (= the factor) and, for the parrot, one
scale in the minecraft:parrot_silver group (= the grey factor); the text diff is exactly those edits. Plus: changed sets,
manifests / uuids / dependencies, identifiers unique across his BPs, sizes land on the targets, predators never shrink,
wolf + sharks untouched, every figure traceable to a sourced row."""
import difflib, hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import build_size_round as R1
import build_size_round2 as B
import size_law as SL

ROOT = Path("/home/claude")
fails = []; n = [0]
def check(tag, ok, msg):
    n[0] += 1; print(("PASS " if ok else "FAIL ") + tag + " — " + msg)
    if not ok: fails.append(tag)
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(d): return {str(p.relative_to(d)): p for p in Path(d).rglob("*") if p.is_file()}
def changed_set(old, new):
    fo, fn = files(old), files(new)
    return (sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])), sorted(set(fn) - set(fo)), sorted(set(fo) - set(fn)))


def scale_diff(a, b, factor, path="", group_extra=None):
    probs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            p = f"{path}/{k}"
            if k not in a:
                if k == "minecraft:scale" and path.endswith("/components") and set(b[k]) == {"value"} and abs(float(b[k]["value"]) - round(factor, 3)) < 1e-9: continue
                if k == "minecraft:scale" and group_extra and path.endswith("/" + group_extra[0]) and set(b[k]) == {"value"} \
                        and abs(float(b[k]["value"]) - round(group_extra[1], 3)) < 1e-9: continue
                probs.append(f"added {p}"); continue
            if k not in b: probs.append(f"removed {p}"); continue
            if k == "minecraft:scale" and isinstance(a[k], dict) and isinstance(b[k], dict) and set(a[k]) == set(b[k]) == {"value"}:
                want = round(float(a[k]["value"]) * factor, 3)
                if abs(float(b[k]["value"]) - want) > 1e-9: probs.append(f"{p} {b[k]['value']} != {want}")
                continue
            probs += scale_diff(a[k], b[k], factor, p, group_extra)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): probs.append(f"list length {path}")
        else:
            for i, (x, y) in enumerate(zip(a, b)): probs += scale_diff(x, y, factor, f"{path}[{i}]", group_extra)
    elif a != b: probs.append(f"value {path}: {str(a)[:30]} -> {str(b)[:30]}")
    return probs


def tdiff(a, b): return sum(1 for l in difflib.ndiff(a.splitlines(), b.splitlines()) if l.startswith(("+ ", "- ")))


rep = json.load(open(ROOT / "_docs/sizes/size_round2_report.json"))
# ---------------------------------------------------------------- BP-02 1.3.192
OLD, NEW = ROOT / "_build/bp02-191", ROOT / "_build/bp02-192"
ch, add, rem = changed_set(OLD, NEW)
exp_ch = sorted(["manifest.json"] + [d["file"] for d in rep["bp02"] if not d.get("new_file")])
exp_add = sorted(d["file"] for d in rep["bp02"] if d.get("new_file"))
check("B1 BP-02 changed set = manifest + round-1 files resized; added = the new overrides", ch == exp_ch and add == exp_add and not rem,
      f"changed {ch}; added {add}; removed {rem}")
m = json.loads((NEW / "manifest.json").read_text()); mo = json.loads((OLD / "manifest.json").read_text(encoding="utf-8-sig"))
check("B2 BP-02 manifest 1.3.192, uuids + dependencies kept", m["header"]["version"] == [1, 3, 192] and all(x["version"] == [1, 3, 192] for x in m["modules"])
      and m["header"]["uuid"] == mo["header"]["uuid"] and [x["uuid"] for x in m["modules"]] == [x["uuid"] for x in mo["modules"]] and m["dependencies"] == mo["dependencies"], "")
bad, lines = [], []
for d in rep["bp02"]:
    fn = Path(d["file"]).name
    a_raw = (R1.VAN_BP / fn).read_text(encoding="utf-8") if d.get("new_file") else (OLD / d["file"]).read_text(encoding="utf-8")
    b_raw = (NEW / d["file"]).read_text(encoding="utf-8")
    ge = ("minecraft:parrot_silver", d["grey_factor"]) if d["id"] == "minecraft:parrot" else None
    probs = scale_diff(ML._parse_json(a_raw), ML._parse_json(b_raw), d["factor"], group_extra=ge)
    if probs: bad.append((fn, probs[:3]))
    want = (d.get("scales_changed") or 0) * 2 + (1 if d.get("base_inserted", d["id"] == "minecraft:parrot") else 0) + (1 if ge else 0)
    if tdiff(a_raw, b_raw) != want: lines.append((fn, tdiff(a_raw, b_raw), want))
check("VSC1 BP-02: each file differs from its source ONLY in scale values (parrot: + the grey group scale)", not bad, f"{len(rep['bp02'])} files; {bad[:3]}")
check("VSC2 BP-02 text diff = exactly the scale edits", not lines, f"{lines[:4]}")
pa = ML._parse_json((NEW / "entities/parrot.json").read_text())["minecraft:entity"]
sil = pa["component_groups"]["minecraft:parrot_silver"]
check("P1 parrot: base scale = macaw factor, the silver (grey) group scale = African-grey factor, variant 4 kept",
      abs(pa["components"]["minecraft:scale"]["value"] - round(next(d for d in rep["bp02"] if d["id"] == "minecraft:parrot")["factor"], 3)) < 1e-9
      and sil.get("minecraft:variant") == {"value": 4} and "minecraft:scale" in sil, f"base {pa['components']['minecraft:scale']} silver {sil.get('minecraft:scale')}")
pr = next(d for d in rep["bp02"] if d["id"] == "minecraft:parrot"); bt = next(d for d in rep["bp02"] if d["id"] == "minecraft:bat")
check("P2 parrot / bat land on the curve (measured Patrix model x factor = target)",
      abs(pr["measured_max"] * pr["factor"] - pr["to_blocks"]) < 0.01 * pr["to_blocks"] and abs(pr["grey_measured_max"] * pr["grey_factor"] - pr["grey_to_blocks"]) < 0.01 * pr["grey_to_blocks"]
      and abs(bt["measured_max"] * bt["factor"] - bt["to_blocks"]) < 0.01 * bt["to_blocks"],
      f"macaw {pr['measured_max']} x{pr['factor']} -> {pr['to_blocks']:.3f}; grey {pr['grey_measured_max']} x{pr['grey_factor']} -> {pr['grey_to_blocks']:.3f}; bat {bt['measured_max']} x{bt['factor']} -> {bt['to_blocks']:.3f}")
check("P3 bat wingspan = 0.42 block (his ruling D-C303: between life-size 0.29 and the curve's 0.56)",
      abs(bt["to_blocks"] - 0.42) < 1e-9 and abs(bt["measured_max"] * bt["factor"] - 0.42) < 0.005, f"{bt['measured_max']} x {bt['factor']} = {bt['measured_max'] * bt['factor']:.4f}")
ids = {}
for bp in [NEW, ROOT / "_build/stripmine-bp-135", ROOT / "_build/bp03-134", ROOT / "_build/bp01-135"]:
    for p in (bp / "entities").rglob("*.json") if (bp / "entities").exists() else []:
        mm = re.search(r'"identifier"\s*:\s*"([a-z0-9_:]+)"', p.read_text(encoding="utf-8-sig", errors="replace"))
        if mm: ids.setdefault(mm.group(1), []).append(f"{bp.name}/{p.name}")
dups = {k: v for k, v in ids.items() if len(v) > 1}
check("B3 every identifier defined once across his behaviour packs", not dups, f"{dups}")
# ---------------------------------------------------------------- StripMine BP 1.3.5
OLD, NEW = ROOT / "_build/stripmine-bp-134", ROOT / "_build/stripmine-bp-135"
ch, add, rem = changed_set(OLD, NEW)
exp = sorted([r["file"] for r in rep["stripmine"]] + ["manifest.json"])
check("S1 StripMine changed set = the resized predators + manifest", sorted(ch) == exp and not add and not rem, f"changed {len(ch)} (expected {len(exp)}); added {add}; removed {rem}")
bad, lines = [], []
for r in rep["stripmine"]:
    a_raw = (OLD / r["file"]).read_text(encoding="utf-8-sig"); b_raw = (NEW / r["file"]).read_text(encoding="utf-8")
    probs = scale_diff(ML._parse_json(a_raw), ML._parse_json(b_raw), r["factor"])
    if probs: bad.append((r["id"], probs[:2]))
    if tdiff(a_raw, b_raw) != r["scales_changed"] * 2 + (1 if r["base_inserted"] else 0): lines.append(r["id"])
check("VSC3 StripMine entities differ from 1.3.4 ONLY in scale values", not bad, f"{len(rep['stripmine'])} files; {bad[:3]}")
check("VSC4 StripMine text diff = exactly the scale edits", not lines, f"{lines[:5]}")
mf = json.loads((NEW / "manifest.json").read_text()); mfo = json.loads((OLD / "manifest.json").read_text(encoding="utf-8-sig"))
check("S2 StripMine manifest 1.3.5, uuids kept", mf["header"]["version"] == [1, 3, 5] and all(x["version"] == [1, 3, 5] for x in mf["modules"])
      and mf["header"]["uuid"] == mfo["header"]["uuid"], "")
# ---------------------------------------------------------------- the rules
rows = rep["rows"]
touched = {r["id"] for r in rep["stripmine"]} | {d["id"] for d in rep["bp02"]}
check("R1 wolf (his calibration) and the sharks (his 'imposing') untouched", not ({"minecraft:wolf", "sf_nba:great_white_shark", "sf_nba:hammer_head_shark"} & touched), "")
shrunk = [r["id"] for r in rows if r["action"] != "keep" and r["factor"] < 1.0]
check("R2 no predator drawn smaller than today (his 'predators come out large')", not shrunk, f"{shrunk}")
off = [(r["id"], r["from_blocks"], r["factor"], r["to_blocks"]) for r in rows if r["action"] != "keep" and abs(r["from_blocks"] * r["factor"] - r["to_blocks"]) > 0.01 * r["to_blocks"]]
check("C1 every resized predator lands on its target (today x factor = target(top of the sourced male range), 1 %)", not off, f"{off[:3]}")
src = json.load(open(ROOT / "_docs/sizes/predator_male_sizes.json")); sk = {s["key"] for s in src}
ALIAS = {"ravenous_hyena": "hyena"}          # the Naturalist 'ravenous' hyena variant = the spotted hyena
check("R3 every predator row traces to a sourced research row (URL + quote)", all(ALIAS.get(r["key"], r["key"]) in sk for r in rows),
      f"{sorted({ALIAS.get(r['key'], r['key']) for r in rows} - sk)}")
print(f"\n{'GATE OPEN' if not fails else 'GATE CLOSED'} {n[0] - len(fails)}/{n[0]}" + (f"  FAILS: {fails}" if fails else ""))
sys.exit(1 if fails else 0)

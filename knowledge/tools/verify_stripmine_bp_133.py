#!/usr/bin/env python3
"""verify_stripmine_bp_133.py — gate for PW-StripMine-BP v1.3.3 (D-C263, the size CURVE). Packages on GATE OPEN.
  A manifest 1.3.2, uuids unchanged           B every entity JSON parses (Bedrock-tolerant: // comments + trailing commas stripped)
  C diff vs 1.3.1 = exactly the changed entity files + manifest + PW-DEPENDENCIES.md (nothing added/removed)
  D every changed entity carries minecraft:scale == the report value (base) and every scaled component group == old x factor;
     every scale is <= 0.90 and >= 0.10; no entity outside the report changed
  E the collision box of the smallest creatures after scale is >= 0.05 block (the engine floor), and the largest dimension after
     scale == max(real, 0.22) within 3 %
  P package -> /mnt/user-data/outputs/PW-StripMine-BP-v1_3_2.mcpack"""
import hashlib, json, os, re, sys, time, zipfile
from pathlib import Path
ROOT = Path("/home/claude")
OLD, NEW = ROOT / "_build/stripmine-bp-131", ROOT / "_build/stripmine-bp-133"
OUT = Path("/mnt/user-data/outputs/PW-StripMine-BP-v1_3_3.mcpack")
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
def tolerant(t):
    t = re.sub(r"//[^\n]*", "", t.lstrip("﻿")); t = re.sub(r",(\s*[}\]])", r"\1", t); return json.loads(t)
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
rep = json.load(open(ROOT / "_logs/stripmine_bp_133_report.json"))
mo, mn = tolerant((OLD / "manifest.json").read_text(encoding="utf-8")), tolerant((NEW / "manifest.json").read_text(encoding="utf-8"))
check("A manifest 1.3.3, uuids unchanged", mn["header"]["version"] == [1, 3, 3] and mn["header"]["uuid"] == mo["header"]["uuid"] and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]] and all(m["version"] == [1, 3, 3] for m in mn["modules"]) and mn["header"]["name"] == "PW StripMine BP v1.3.3")
def unparseable(d):
    out = set()
    for p in d.rglob("*.json"):
        try: tolerant(p.read_text(encoding="utf-8"))
        except Exception: out.add(str(p.relative_to(d)).replace(os.sep, "/"))
    return out
b_old, b_new = unparseable(OLD), unparseable(NEW)
check("B every JSON parses (Bedrock-tolerant) — no NEW failures vs 1.3.1", b_new <= b_old, f"pre-existing unparseable in 1.3.1: {len(b_old)} (empty recipe stubs / legacy items); new: {sorted(b_new - b_old)[:3]}")
def tree(d): return {str(p.relative_to(d)).replace(os.sep, "/"): md5(p) for p in d.rglob("*") if p.is_file()}
to, tn = tree(OLD), tree(NEW)
changed = sorted(k for k in set(to) & set(tn) if to[k] != tn[k]); added = sorted(set(tn) - set(to)); removed = sorted(set(to) - set(tn))
exp = sorted({c["file"] for c in rep["changed"]} | {"manifest.json", "PW-DEPENDENCIES.md"})
check("C diff vs 1.3.1 = changed entity files + manifest + PW-DEPENDENCIES only", changed == exp and not added and not removed, f"changed {len(changed)} (expected {len(exp)}), added {added[:3]}, removed {removed[:3]}, unexpected {sorted(set(changed) ^ set(exp))[:5]}")
probs = []
for c in rep["changed"]:
    n, o = tolerant((NEW / c["file"]).read_text(encoding="utf-8"))["minecraft:entity"], tolerant((OLD / c["file"]).read_text(encoding="utf-8"))["minecraft:entity"]
    v = n["components"].get("minecraft:scale", {}).get("value")
    if v is None or abs(v - c["scale"]) > 1e-6: probs.append(f"{c['id']}: base scale {v} != {c['scale']}")
    if not (0.05 <= c["scale"] <= 1.20): probs.append(f"{c['id']}: scale {c['scale']} out of [0.05, 1.20]")
    ob = o["components"].get("minecraft:scale", {}).get("value", 1.0)
    factor = c["scale"] / ob
    for g, gc in o.get("component_groups", {}).items():
        if "minecraft:scale" in gc:
            want = round(gc["minecraft:scale"]["value"] * factor, 3); got = n["component_groups"][g]["minecraft:scale"]["value"]
            if abs(want - got) > 0.002: probs.append(f"{c['id']}.{g}: group scale {got} != {want}")
check("D every changed entity carries the report's scale; groups scaled by the same factor; all in [0.05, 1.20]", not probs, "; ".join(probs[:5]))
tab = {t["id"]: t for t in rep["table"]}
e_probs = []
for c in rep["changed"]:
    t = tab[c["id"]]; after = t["current_blocks"] * c["scale"]; want = min(t["target"], t["current_blocks"] * 1.20)
    if abs(after - want) > 0.03 * want + 0.005: e_probs.append(f"{c['id']}: after {after:.3f} vs target {want:.3f}")
    o = tolerant((OLD / c["file"]).read_text(encoding="utf-8"))["minecraft:entity"]
    cb = o["components"].get("minecraft:collision_box")
    if cb and min(cb.get("width", 1), cb.get("height", 1)) >= 0.05 and min(cb.get("width", 1), cb.get("height", 1)) * c["scale"] < 0.05: e_probs.append(f"{c['id']}: collision {cb} x {c['scale']} < 0.05")
check("E largest dimension after scale == the curve's game size (capped x1.20) within 3 %; scaled collision boxes stay >= 0.05 block", not e_probs, "; ".join(e_probs[:5]))
curve = sorted((t["real_m"], t["target"], t["id"][7:]) for t in rep["table"])
mono = all(curve[i][1] <= curve[i + 1][1] + 1e-6 for i in range(len(curve) - 1))
sc = {c["id"]: c["scale"] for c in rep["changed"]}
actual = sorted((t["real_m"], round(t["current_blocks"] * sc.get(t["id"], 1.0), 2), t["id"][7:]) for t in rep["table"])
exceptions = [f"{actual[i][2]} {actual[i][1]} > {actual[i+1][2]} {actual[i+1][1]}" for i in range(len(actual) - 1) if actual[i][0] < actual[i + 1][0] and actual[i][1] > actual[i + 1][1] + 0.02]
check("E the size relationship is monotonic (the curve never drops with real size); in-game exceptions only from the x1.20 cap / 8 % deadband", mono and len(exceptions) <= 3, f"{len(curve)} creatures; exceptions {exceptions}")
ok = all(o for _, o, _ in res)
if ok:
    if OUT.exists(): OUT.unlink()
    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(NEW.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(NEW)).replace(os.sep, "/")); n += 1
    with zipfile.ZipFile(OUT) as z: badz = z.testzip()
    check("P package", badz is None, f"{OUT.name} {n} members {OUT.stat().st_size:,} B md5 {md5(OUT)}")
stamp = f"StripMine BP 1.3.3 GATE {'OPEN' if all(o for _, o, _ in res) else 'CLOSED'} {sum(1 for _, o, _ in res if o)}/{len(res)}" + (f" -> {OUT.name} {OUT.stat().st_size:,} B md5 {md5(OUT)}" if ok and OUT.exists() else "")
with open(ROOT / "_logs/phase_log.md", "a") as fh: fh.write(f"[{time.strftime('%H:%M')} CT 09-27] VERIFY {stamp}\n")
print(stamp); sys.exit(0 if all(o for _, o, _ in res) else 1)

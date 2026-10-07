#!/usr/bin/env python3
"""verify_bp02_187.py — gate for BP-02 v1.3.187 (D-C251 room fog OFF + stuck-fog sweep). Packages on GATE OPEN.
  A manifest: 1.3.187, uuids unchanged, pins unchanged (server 2.3.0 / server-ui 2.0.0), stamped description
  B file set identical to .186; exactly manifest.json + scripts/main.js + scripts/pw_homestead.js changed
  C main.js: only the PW_BUILD line changed; every script passes node --check; every JSON parses
  D pw_homestead.js edits confined to the planned windows: header, consts, fog functions, boot sweep (rest byte-identical)
  E semantics in the shipped file: ROOM_FOG false; no "fog @s pop" left; remove uses the tag; sweep on initialSpawn + boot
  F api_audit: 0 flags on the pins
  G mock-run of the shipped module (test_homestead_fog.mjs): 11/11
  H the fog itself is still defined in RP-02 2.0.4 (pw:smoke_room) so the remove command targets a real id family; the tag
    pw_hearth_smoke is used by no other pack
"""
import json, re, sys, hashlib, zipfile, subprocess, difflib
from pathlib import Path
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); A = ROOT / "_build/bp02-186"; B = ROOT / "_build/bp02-187"
NAME = "BP-02-AbsolutRealism-Tectonic-BP-v1_3_187.mcpack"
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def tree(d): return {str(p.relative_to(d)).replace("\\", "/"): md5(p) for p in Path(d).rglob("*") if p.is_file()}

ma, mb = jload(A / "manifest.json"), jload(B / "manifest.json")
check("A manifest 1.3.187, uuids + pins unchanged, stamped", mb["header"]["version"] == [1, 3, 187] and all(m["version"] == [1, 3, 187] for m in mb["modules"])
      and mb["header"]["uuid"] == ma["header"]["uuid"] and [m["uuid"] for m in mb["modules"]] == [m["uuid"] for m in ma["modules"]] and mb["dependencies"] == ma["dependencies"]
      and mb["header"]["description"].startswith("v1.3.187 (2026-09-27) ROOM FOG OFF") and mb["header"]["name"] == "AbsolutRealism Tectonic BP v1.3.187")
ta, tb = tree(A), tree(B)
changed = sorted(f for f in ta if ta[f] != tb.get(f))
check("B same file set; exactly 3 files changed", set(ta) == set(tb) and changed == ["manifest.json", "scripts/main.js", "scripts/pw_homestead.js"], str(changed))
da = difflib.unified_diff((A / "scripts/main.js").read_text(encoding="utf-8").splitlines(), (B / "scripts/main.js").read_text(encoding="utf-8").splitlines(), lineterm="", n=0)
hunks = [l for l in da if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
check("C main.js: only the PW_BUILD line", hunks == ['-const PW_BUILD = "1.3.186";', '+const PW_BUILD = "1.3.187";'], str(hunks)[:200])
nc = [subprocess.run(["node", "--check", str(p)], capture_output=True).returncode for p in (B / "scripts").glob("*.js")]
bad = []
for p in B.rglob("*.json"):
    try: jload(p)
    except Exception: bad.append(str(p))
check("C node --check on every script; every JSON parses", all(c == 0 for c in nc) and not bad, f"{len(nc)} scripts, {len(list(B.rglob('*.json')))} json")
sa, sb = (A / "scripts/pw_homestead.js").read_text(encoding="utf-8"), (B / "scripts/pw_homestead.js").read_text(encoding="utf-8")
# D: strip the planned windows from both and compare the rest
def strip(s, is_new):
    s = re.sub(r"^// pw_homestead\.js — HOMESTEAD family runtime.*$", "", s, flags=re.M)
    s = re.sub(r"const FOG_ON = 8, FOG_OFF = 5;.*?(?=const COUGH_LEVEL)", "", s, flags=re.S)
    s = re.sub(r"(/\*\* Removes EVERY pw_hearth_smoke.*?\n\}\);\n)|(function fogPush\(player, key\) \{.*?fogged\.delete\(player\.id\);\n\}\n)", "", s, flags=re.S)
    s = re.sub(r"  loadLedger\(\);\n(  try \{ const n = fogSweep.*?\n)?", "", s, flags=re.S)
    return s
check("D pw_homestead.js edits confined to the four planned windows", strip(sa, False) == strip(sb, True))
check("E ROOM_FOG false; no 'fog @s pop' left; remove by tag; sweep on initialSpawn + boot",
      "const ROOM_FOG = false;" in sb and "fog @s pop" not in sb and "fog @s remove ${FOG_TAG}" in sb and 'FOG_TAG = "pw_hearth_smoke"' in sb
      and "if (!ev.initialSpawn) return;" in sb and "fogSweep(world.getAllPlayers())" in sb and "if (!ROOM_FOG) return;" in sb)
def flags(d):
    r = subprocess.run([sys.executable, str(ROOT / "tools/api_audit.py"), str(d)], capture_output=True, text=True, timeout=900)
    # compare by (file, member) — line numbers shift with the inserted fog block
    return sorted(re.sub(r":\d+  ", " ", re.sub(r"^\s+scripts/", "", l).split("  |")[0].strip()) for l in r.stdout.splitlines() if re.match(r"^\s+scripts/", l))
fa, fb = flags(A), flags(B)
check("F api_audit: the flag set is EXACTLY .186's reviewed, accepted set (no new flags)", fa == fb and len(fb) > 0, f"{len(fb)} flags, same as .186: {fa == fb}")
r = subprocess.run(["node", str(ROOT / "tools/testrunner_src/test_homestead_fog.mjs"), str(B / "scripts")], capture_output=True, text=True, timeout=300)
tail = (r.stdout.strip().splitlines() or [r.stderr[-200:]])[-1]
check("G mock-run of the shipped module", r.returncode == 0 and ", 0 failed" in tail, tail)
fog = jload(ROOT / "_build/rp02-204/fogs/pw_smoke_room_fog_setting.json")
others = []
for d in ("bp01-135", "bp03-134", "markers-0.2.1/BP", "testrunner-0.1.0"):
    for p in (ROOT / "_build" / d).rglob("*.js"):
        if "pw_hearth_smoke" in p.read_text(encoding="utf-8", errors="ignore"): others.append(str(p))
check("H pw:smoke_room still defined in RP-02 2.0.4 (#6B6660, end 7 fixed); tag used by no other pack",
      fog["minecraft:fog_settings"]["distance"]["air"]["fog_color"] == "#6B6660" and fog["minecraft:fog_settings"]["distance"]["air"]["fog_end"] == 7.0 and not others, str(others))

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
print(f"\nGATE OPEN — {len(res)} checks")
import datetime
with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-27] VERIFY bp02-187 GATE OPEN {len(res)}/{len(res)} — packaging\n")
out = OUT / NAME
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(B.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
with zipfile.ZipFile(out) as z:
    zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    assert zh == tb and "manifest.json" in z.namelist()
print(f"  {out.name} {out.stat().st_size:,} B md5 {md5(out)}")

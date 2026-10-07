#!/usr/bin/env python3
"""verify_stack_api.py — gate for the D-C231 API fixes: BP-02 v1.3.186 · BP-01 v1.3.35 · BP-03 v1.3.34.
Packages all three on GATE OPEN.  Mock tests run the SHIPPED scripts (tools/stack_src/test_stack.mjs on
tools/stack_src/mock_mc.mjs), and the same tests run on the OLD builds must fail (proof the tests see the bugs)."""
import json, re, sys, hashlib, zipfile, subprocess, shutil, tempfile, difflib
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import api_audit as AA
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); DATE = "2026-09-22"
SP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad")
PACKS = {  # key: (base dir, new dir, version, output name, expected pins)
    "BP-02": (ROOT / "_build/bp02-185", ROOT / "_build/bp02-186", "1.3.186", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_186.mcpack",
              {"@minecraft/server": "2.3.0", "@minecraft/server-ui": "2.0.0"}),
    "BP-01": (ROOT / "_build/bp01-134", ROOT / "_build/bp01-135", "1.3.35", "BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_35.mcpack",
              {"@minecraft/server": "2.3.0"}),
    "BP-03": (ROOT / "_build/bp03-133", ROOT / "_build/bp03-134", "1.3.34", "BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_34.mcpack",
              {"@minecraft/server": "2.0.0"}),
}
res = []
def check(n, ok, d=""): res.append((n, bool(ok))); print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {str(d)[:500]}"))
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
def code(p): return AA.strip_comments_and_strings(Path(p).read_text(encoding="utf-8"))
def hunks(a, b):
    sm = difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(), autojunk=False)
    return [op for op in sm.get_opcodes() if op[0] != "equal"]
def windows(text, anchors):
    """line windows [first, last] (0-based, inclusive) in the OLD file, one per (start anchor, end anchor|None)."""
    L = text.splitlines(); out = []
    for s, e in anchors:
        i = next(n for n, l in enumerate(L) if s in l)
        j = next(n for n, l in enumerate(L) if n > i and e in l) if e else i
        out.append((i, j))
    return out
def confined(a, b, anchors):
    """every changed region of b vs a lies inside a declared edit window of a, and every window was edited."""
    ws = windows(a, anchors); used = set(); stray = []
    for op, i1, i2, j1, j2 in hunks(a, b):
        hit = [k for k, (s, e) in enumerate(ws) if s <= i1 and (i2 - 1 if i2 > i1 else i1) <= e + 1]
        if hit: used.add(hit[0])
        else: stray.append((op, i1 + 1, i2))
    return not stray and used == set(range(len(ws))), (stray, sorted(set(range(len(ws))) - used))

# A manifests
for k, (A, B, VER, _, pins) in PACKS.items():
    m0, m1 = load(A / "manifest.json"), load(B / "manifest.json"); vv = [int(x) for x in VER.split(".")]
    check(f"A {k} manifest v{VER}: header+modules versioned, stamp dated, uuids + min_engine unchanged, pins {pins}",
          m1["header"]["version"] == vv and all(m["version"] == vv for m in m1["modules"]) and m1["header"]["description"].startswith(f"v{VER} ({DATE})")
          and m1["header"]["uuid"] == m0["header"]["uuid"] and [m["uuid"] for m in m1["modules"]] == [m["uuid"] for m in m0["modules"]]
          and m1["header"]["min_engine_version"] == m0["header"]["min_engine_version"] and m1["header"]["name"].endswith(f"v{VER}")
          and {d["module_name"]: d["version"] for d in m1["dependencies"]} == pins)
# B syntax
for k, (_, B, *_r) in PACKS.items():
    bad = [p.name for p in (B / "scripts").glob("*.js") if subprocess.run(["node", "--check", str(p)], capture_output=True).returncode]
    check(f"B {k} every script passes node --check", not bad, bad)
# C api audit at the NEW pins
reps = {k: AA.audit(PACKS[k][1]) for k in PACKS}
names = {k: sorted({f["name"] for f in r["flags"]}) for k, r in reps.items()}
check("C api_audit BP-01 v1.3.35 at 2.3.0: 0 flags (getWeather + runCommandAsync gone)", names["BP-01"] == [] and "runCommandAsync" not in code(PACKS["BP-01"][1] / "scripts/main.js"), names["BP-01"])
check("C api_audit BP-03 v1.3.34 at 2.0.0: 0 flags (chatSend + sender gone)", names["BP-03"] == [], names["BP-03"])
check("C api_audit BP-02 v1.3.186 at 2.3.0: only the reviewed accepted set remains {airSupply feature-detect, path/count own fields}; getWeather/getBiome/isSolid clear",
      set(names["BP-02"]) <= {"airSupply", "path", "count"} and not {"getWeather", "getBiome", "isSolid"} & set(names["BP-02"]), names["BP-02"])
# D shared weather module
W = (ROOT / "tools/weather_src/pw_weather.js").read_bytes()
check("D pw_weather.js in BP-01 and BP-02 is byte-identical to tools/weather_src (the tested source)",
      (PACKS["BP-01"][1] / "scripts/pw_weather.js").read_bytes() == W and (PACKS["BP-02"][1] / "scripts/pw_weather.js").read_bytes() == W)
# E BP-03 source identity + announceBreak untouched
n3, o3 = (PACKS["BP-03"][1] / "scripts/main.js").read_text(encoding="utf-8"), (PACKS["BP-03"][0] / "scripts/main.js").read_text(encoding="utf-8")
seg = lambda t: t[t.index("// Announce a broken block"):t.index("\n}\n", t.index("function announceBreak(")) + 3]
check("E BP-03 main.js == tools/stack_src/bp03_main.js, and announceBreak (the block-break announcer) is byte-identical to v1.3.33",
      n3.encode() == (ROOT / "tools/stack_src/bp03_main.js").read_bytes() and seg(n3) == seg(o3))
# F mock runs of the SHIPPED scripts + mutation runs on the OLD builds
def stage(td, b01, b02, b03, b02name="bp02"):
    nm = td / "node_modules/@minecraft/server"; nm.mkdir(parents=True)
    shutil.copy(ROOT / "tools/stack_src/mock_mc.mjs", nm / "index.js"); (nm / "package.json").write_text('{"name":"@minecraft/server","type":"module","main":"index.js"}')
    for sub_, src in (("bp01", b01), ("bp03", b03)):
        (td / sub_).mkdir(); [shutil.copy(p, td / sub_ / p.name) for p in (src / "scripts").glob("*.js")]
    (td / b02name).mkdir(); shutil.copy(b02 / "scripts/main.js", td / b02name / "main.js"); shutil.copy(ROOT / "tools/weather_src/pw_weather.js", td / b02name / "pw_weather.js")
    shutil.copy(ROOT / "tools/stack_src/test_stack.mjs", td / "test_stack.mjs")
def run(td, mode, extra=()):
    r = subprocess.run(["node", "test_stack.mjs", mode, *extra], cwd=td, capture_output=True, text=True, timeout=120)
    m = re.search(r"(\d+) passed, (\d+) failed", r.stdout)
    return (int(m.group(1)), int(m.group(2))) if m else (0, -1), r.stdout + r.stderr
EXPECT = {"bp01": 17, "bp01-reload": 1, "weather": 7, "bp02": 11, "bp03": 14}
with tempfile.TemporaryDirectory() as td:
    td = Path(td); stage(td, PACKS["BP-01"][1], PACKS["BP-02"][1], PACKS["BP-03"][1])
    tot = 0
    for mode, n in EXPECT.items():
        (p, f), out = run(td, mode); tot += p
        check(f"F mock-run {mode}: {p}/{n} on the SHIPPED scripts", p == n and f == 0, out[-600:])
with tempfile.TemporaryDirectory() as td:
    td = Path(td); stage(td, PACKS["BP-01"][0], PACKS["BP-02"][0], PACKS["BP-03"][0])
    (p1, f1), _ = run(td, "bp01"); (p3, f3), _ = run(td, "bp03"); (p2, f2), _ = run(td, "bp02")
    check(f"F mutation: the same tests on the OLD builds FAIL (BP-01 v1.3.34: {f1} fails, BP-03 v1.3.33: {f3}, BP-02 v1.3.185: {f2}) — the tests see the bugs",
          f1 >= 10 and f3 >= 10 and f2 == 4, (f1, f3, f2))
# G BP-02 homestead untouched (its .185 gate — unit 21 + roomFor harness — carries over byte-for-byte)
check("G BP-02 homestead scripts byte-identical to v1.3.185 (room-smoke fix carried unchanged) and to tools/homestead_src",
      all((PACKS["BP-02"][1] / "scripts" / f).read_bytes() == (PACKS["BP-02"][0] / "scripts" / f).read_bytes() == (ROOT / "tools/homestead_src" / f).read_bytes()
          for f in ("pw_homestead.js", "pw_homestead_logic.js")))
# H diff hygiene
EXP = {"BP-02": ({"scripts/main.js", "manifest.json", "PW-DEPENDENCIES.md"}, {"scripts/pw_weather.js"},
                 [('import "./pw_furniture.js"', None), ("const PW_BUILD =", None), ("  // Biome check (with graceful fallback)", "  if (!biomeOk) return;"),
                  ("function _leafWind(", "function _isLeafId(")]),
       "BP-01": ({"scripts/main.js", "manifest.json"}, {"scripts/pw_weather.js"},
                 [(" * @minecraft/server module dependency", "// CONFIGURATION"), ("function getDimensionWeather(", "// MAIN POLLING LOOP"),
                  ("// Robust weather read.", "function arDimensionKind("), ("// Push/pop helper", "function arApplyFog("), ("[PW-VERSION]", None)]),
       "BP-03": ({"scripts/main.js", "manifest.json"}, set(), None)}
for k, (A, B, *_r) in PACKS.items():
    h0, h1 = th(A), th(B); ch = {x for x in h0 if x in h1 and h0[x] != h1[x]}; add = set(h1) - set(h0); rem = set(h0) - set(h1)
    chg, added, anchors = EXP[k]
    cf, why = confined((A / "scripts/main.js").read_text(encoding="utf-8"), (B / "scripts/main.js").read_text(encoding="utf-8"), anchors) if anchors else (True, None)
    check(f"H {k} diff: changed {sorted(chg)}, added {sorted(added) or '-'}, nothing removed" + (f"; every main.js change lies inside its {len(anchors)} declared edit windows and each window was edited" if anchors else ""),
          ch == chg and add == added and not rem and cf, (sorted(ch), sorted(add), sorted(rem), why))
led0, led1 = (PACKS["BP-02"][0] / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"), (PACKS["BP-02"][1] / "PW-DEPENDENCIES.md").read_text(encoding="utf-8")
check("H BP-02 ledger: only the version stamp moved", led0.replace("v1.3.185 ·", "v1.3.186 ·", 1) == led1)
m01 = (PACKS["BP-01"][1] / "scripts/main.js").read_text(encoding="utf-8"); o01 = (PACKS["BP-01"][0] / "scripts/main.js").read_text(encoding="utf-8")
pool = lambda t: t[t.index("const BIOME_SOUND_POOLS = {"):t.index("function isPlayerInCave(")]
check("H BP-01 sound pools, helpers, cave/weather pools and the fog-state resolver are byte-identical (only the API calls changed)",
      pool(m01) == pool(o01) and m01[m01.index("function arResolveTimeState("):m01.index("// Weather read.")] == o01[o01.index("function arResolveTimeState("):o01.index("// Robust weather read.")]
      and m01[m01.index("function arDimensionKind("):m01.index("// Push/pop helper")] == o01[o01.index("function arDimensionKind("):o01.index("// Push/pop helper")])
# I sounds exist in the RP that ships them
sd = load(ROOT / "_build/rp02-204/sounds/sound_definitions.json"); defs = sd.get("sound_definitions", sd)
ids = sorted(set(re.findall(r'"(pw:ambient\.[a-z0-9_.]+)"', m01)))
miss = [i for i in ids if i not in defs]
nofile = [(i, s["name"] if isinstance(s, dict) else s) for i in ids if i in defs for s in defs[i].get("sounds", [])
          if not any((ROOT / "_build/rp02-204" / ((s["name"] if isinstance(s, dict) else s) + e)).exists() for e in (".ogg", ".wav", ".fsb"))]
check(f"I every ambient sound BP-01 can play ({len(ids)}) is defined in RP-02 v2.0.4 and its audio file exists", len(ids) >= 100 and not miss and not nofile, (miss[:5], nofile[:5]))
# J (INFO) where are the ar_sky fogs?
hits = [str(p.relative_to(ROOT)) for d in ("rp01-104", "rp02-204", "rp03-59", "rp04-138", "rp05-48", "rp07-1410") for p in (ROOT / "_build" / d).rglob("*.json")
        if "ar_sky_" in p.read_text(encoding="utf-8", errors="ignore")]
print(f"INFO J ar_sky fog definitions in the RPs we build (RP-01 .104, RP-02 v2.0.4, RP-03 .59, RP-04 .138, RP-05 .48, RP-07 .1410): {hits or 'NONE'}")

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
print(f"\nGATE OPEN — {len(res)} checks")
for k, (A, B, VER, name, _) in PACKS.items():
    out = OUT / name
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(B.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
    with zipfile.ZipFile(out) as z:
        zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
        assert zh == th(B) and "manifest.json" in z.namelist()
    print(f"  {out.name} {out.stat().st_size:,} B md5 {hashlib.md5(out.read_bytes()).hexdigest()}")

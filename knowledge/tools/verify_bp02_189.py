#!/usr/bin/env python3
"""verify_bp02_189.py — gate for BP-02 v1.3.189 (D-C260). Packages on GATE OPEN.
  A manifest: name/version/module versions 1.3.189, uuids unchanged from 1.3.188
  B every JSON parses; node --check on every script
  C the diff against 1.3.188 is exactly main.js + pw_homestead.js + manifest.json (nothing else touched)
  D main.js: interval 1200, idle heartbeat 6000, pw:stats handler with off/on/now, emitStats(force), PW_BUILD 1.3.189; no '100t (5s)' string left
  E pw_homestead.js: the boot line no longer starts with a version; the sweep still runs
  F mock-run: the pw:stats handler flips the flag and 'now' prints a [BIGCANOPY-STATS] line (scripts loaded against the stack mock)
  P package -> /mnt/user-data/outputs/BP-02-AbsolutRealism-Tectonic-BP-v1_3_189.mcpack + md5"""
import hashlib, json, os, re, subprocess, sys, time, zipfile
from pathlib import Path

ROOT = Path("/home/claude")
OLD, NEW, VER = ROOT / "_build/bp02-188", ROOT / "_build/bp02-189", "1.3.189"
OUT = Path("/mnt/user-data/outputs/BP-02-AbsolutRealism-Tectonic-BP-v1_3_189.mcpack")
res = []

def check(name, ok, detail=""):
    res.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))

def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

# A
mo = json.loads((OLD / "manifest.json").read_text()); mn = json.loads((NEW / "manifest.json").read_text())
check("A manifest 1.3.189, uuids unchanged", mn["header"]["version"] == [1, 3, 189] and all(x["version"] == [1, 3, 189] for x in mn["modules"])
      and mn["header"]["uuid"] == mo["header"]["uuid"] and [x["uuid"] for x in mn["modules"]] == [x["uuid"] for x in mo["modules"]] and mn["header"]["name"].endswith(VER)
      and mn["header"]["description"].startswith(f"v{VER} (2026-09-27) STATS CADENCE"))
# B
bad = []
for p in NEW.rglob("*.json"):
    try: json.loads(re.sub(r"^\s*//.*$", "", p.read_text(encoding="utf-8-sig"), flags=re.M))
    except Exception as e: bad.append(f"{p.name}: {e}")
check("B every JSON parses", not bad, "; ".join(bad[:3]))
nc = [subprocess.run(["node", "--check", str(p)], capture_output=True).returncode for p in (NEW / "scripts").glob("*.js")]
check("B node --check on every script", nc and all(c == 0 for c in nc), f"{len(nc)} scripts")
# C
def tree(d): return {str(p.relative_to(d)): md5(p) for p in d.rglob("*") if p.is_file()}
to, tn = tree(OLD), tree(NEW)
changed = sorted(k for k in set(to) | set(tn) if to.get(k) != tn.get(k))
check("C diff vs 1.3.188 = main.js + pw_homestead.js + manifest.json only", changed == ["manifest.json", "scripts/main.js", "scripts/pw_homestead.js"], str(changed))
# D
t = (NEW / "scripts/main.js").read_text(encoding="utf-8")
check("D main.js: PW_BUILD, interval 1200, idle 6000, emitStats(force), pw:stats off/on/now, old '100t (5s)' gone",
      'const PW_BUILD = "1.3.189";' in t and "const PW_STATS_LOG_INTERVAL = 1200;" in t and "(now - _lastStatsHeartbeatTick) < 6000" in t
      and "function emitStats(force)" in t and 'ev.id !== "pw:stats"' in t and 'a === "off"' in t and 'a === "on"' in t and "else emitStats(true);" in t
      and "100t (5s) cadence" not in t and "if (_statsEnabled) emitStats(false)" in t)
# E
h = (NEW / "scripts/pw_homestead.js").read_text(encoding="utf-8")
check("E homestead boot line reworded, sweep intact", "stuck-fog sweep (since v1.3.187) at boot" in h and "v1.3.187 stuck-fog sweep at boot" not in h and "fogSweep(world.getAllPlayers())" in h)
# F  focused mock: the stats section of main.js (interval + pw:stats handler) runs standalone against a fake system/console
t_all = (NEW / "scripts/main.js").read_text(encoding="utf-8")
i0 = t_all.index("let _lastLoggedMarked = 0;"); i1 = t_all.index("log(`[pw_stats] v${PW_BUILD} periodic stats logger active")
section = t_all[i0:i1]
i2 = t_all.index("const PW_STATS_LOG_INTERVAL = 1200;"); i3 = t_all.index("\n", t_all.index("let _statsEnabled = true;"))
consts = t_all[i2:i3]
harness = ("const warns = []; const console = { warn: (m) => warns.push(String(m)) };\n"
           "const subs = []; const intervals = [];\n"
           "const system = { currentTick: 100, runInterval: (fn, t) => { intervals.push([fn, t]); return 1; }, afterEvents: { scriptEventReceive: { subscribe: (cb) => subs.push(cb) } } };\n"
           "const log = (m) => warns.push(String(m)); const PW_BUILD = '1.3.189'; const PW_BOOT_ID = 'boot';\n"
           "const _scanStats = { cyclesRun: 0, totalMarked: 0, totalRandomized: 0, totalRevertedFar: 0, perSpecies: {}, perVariant: {}, lastFireTick: 0 };\n"
           "const _appliedRegistry = new Map(); const _verifyStats = { cyclesRun: 0, totalReEnqueued: 0 }; const _reverseStats = { cyclesRun: 0, totalReverted: 0 };\n"
           "const _taStats = { totalLogsScanned: 0, totalTreesWalked: 0, totalLeavesMarkedByTreeAssoc: 0, lastFireTick: 0 };\n"
           + consts + "\n" + section +
           "const fire = (id, message) => subs.forEach((cb) => cb({ id, message }));\n"
           "const nStats = () => warns.filter((w) => w.includes('[BIGCANOPY-STATS]')).length;\n"
           "const t0 = nStats(); intervals[0][0](); const idleSkipped = nStats() === t0 + 1;   // first tick: heartbeat elapsed (100 > 6000? no) -> 100-0 < 6000 skips\n"
           "fire('pw:stats', 'now'); const now = nStats() === t0 + 1 || nStats() === t0 + 2;\n"
           "const n1 = nStats(); _scanStats.totalMarked = 5; fire('pw:stats', 'off'); intervals[0][0](); const off = nStats() === n1 && warns.some((w) => w.includes('periodic line OFF'));\n"
           "fire('pw:stats', 'on'); intervals[0][0](); const on = nStats() === n1 + 1 && warns.some((w) => w.includes('periodic line ON'));\n"
           "process.stdout.write(JSON.stringify({ interval: intervals[0][1] === 1200, idleSkipped: !idleSkipped, now, off, on, handlers: subs.length === 1 }));\n")
hp = Path("/tmp/bp02_189_stats_harness.mjs"); hp.write_text(harness)
r = subprocess.run(["node", str(hp)], capture_output=True, text=True, timeout=120)
try:
    f = json.loads(r.stdout.strip().splitlines()[-1])
except Exception:
    f = {"error": (r.stderr or r.stdout)[-400:]}
check("F stats section mock: interval 1200, idle tick skipped, pw:stats now prints, off silences the interval, on restores it", all(f.get(k) for k in ("interval", "idleSkipped", "now", "off", "on", "handlers")), json.dumps(f)[:300])
# P
ok = all(o for _, o, _ in res)
if ok:
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(NEW.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(NEW)))
    with zipfile.ZipFile(OUT) as z: badz = z.testzip()
    check("P package", badz is None, f"{OUT.name} {OUT.stat().st_size:,} B md5 {md5(OUT)}")
stamp = f"BP-02 {VER} GATE {'OPEN' if all(o for _, o, _ in res) else 'CLOSED'} {sum(1 for _, o, _ in res if o)}/{len(res)}" + (f" -> {OUT.name} {OUT.stat().st_size:,} B md5 {md5(OUT)}" if ok and OUT.exists() else "")
with open(ROOT / "_logs/phase_log.md", "a") as fh: fh.write(f"[{time.strftime('%H:%M')} CT 09-27] VERIFY {stamp}\n")
print(stamp); sys.exit(0 if all(o for _, o, _ in res) else 1)

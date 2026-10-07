#!/usr/bin/env python3
"""build_bp02_189.py — BP-02 AbsolutRealism Tectonic BP v1.3.189 (D-C260, Abs0lum 21:56 'All go' item D):
   the [BIGCANOPY-STATS] content-log line flooded the P0 run (every 100 t while the scanner was busy) and buried the
   [PW-TEST] lines.  v1.3.189: stats every 1200 t (60 s) while active, idle heartbeat every 6000 t (5 min), and the
   scriptevent  /scriptevent pw:stats off | on | now  to silence / restore / force one line.  Cosmetic: the homestead
   boot line said 'v1.3.187 stuck-fog sweep' on every build — it now says 'stuck-fog sweep (since v1.3.187)'.
   Everything else byte-identical to v1.3.188 (the gate asserts the diff)."""
import json, shutil, time
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST, VER, DATE = ROOT / "_build/bp02-188", ROOT / "_build/bp02-189", "1.3.189", "2026-09-27"

def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD {m}\n")

def sub(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{what}: expected exactly 1 match, found {n}")
    return s.replace(old, new)

if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

m = DST / "scripts/main.js"; t = m.read_text(encoding="utf-8")
t = sub(t, 'const PW_BUILD = "1.3.188";', 'const PW_BUILD = "1.3.189";', "PW_BUILD")
t = sub(t, "const PW_STATS_LOG_INTERVAL = 100;       // 5s — log scanner activity to content log",
        "const PW_STATS_LOG_INTERVAL = 1200;      // v1.3.189: 60 s (was 5 s — it flooded the P0 content log); /scriptevent pw:stats off|on|now\n"
        "let _statsEnabled = true;                 // v1.3.189: pw:stats off silences the periodic line (pw:stats now still prints one)", "interval")
t = sub(t, "let _lastStatsHeartbeatTick = 0;  // v1.3.60\nsystem.runInterval(() => {\n  const now = system.currentTick;\n  // Skip if no new activity since last log\n"
           "  if (_scanStats.totalMarked === _lastLoggedMarked && _scanStats.totalRandomized === _lastLoggedRandomized\n"
           "      && (now - _lastStatsHeartbeatTick) < 600) return;  // v1.3.60: 30s heartbeat even when idle\n",
        "let _lastStatsHeartbeatTick = 0;  // v1.3.60\n"
        "function emitStats(force) {                 // v1.3.189: the periodic body, callable by pw:stats now\n"
        "  const now = system.currentTick;\n"
        "  // Skip if no new activity since last log\n"
        "  if (!force && _scanStats.totalMarked === _lastLoggedMarked && _scanStats.totalRandomized === _lastLoggedRandomized\n"
        "      && (now - _lastStatsHeartbeatTick) < 6000) return;  // v1.3.189: 5 min heartbeat when idle (was 30 s)\n", "emitStats head")
t = sub(t, "  } catch {}\n}, PW_STATS_LOG_INTERVAL);\n\nlog(`[pw_stats] v${PW_BUILD} periodic stats logger active — 100t (5s) cadence, content log output`);",
        "  } catch {}\n}\n"
        "system.runInterval(() => { if (_statsEnabled) emitStats(false); }, PW_STATS_LOG_INTERVAL);\n"
        "system.afterEvents.scriptEventReceive.subscribe((ev) => {      // v1.3.189: /scriptevent pw:stats off | on | now\n"
        "  if (ev.id !== \"pw:stats\") return;\n"
        "  const a = String(ev.message || \"\").trim().toLowerCase();\n"
        "  if (a === \"off\") { _statsEnabled = false; log(`[pw_stats] periodic line OFF (pw:stats on restores it; pw:stats now prints one)`); }\n"
        "  else if (a === \"on\") { _statsEnabled = true; log(`[pw_stats] periodic line ON (every ${PW_STATS_LOG_INTERVAL}t)`); }\n"
        "  else emitStats(true);\n"
        "});\n\n"
        "log(`[pw_stats] v${PW_BUILD} periodic stats logger active — 1200t (60s) cadence while active, 5 min idle heartbeat; /scriptevent pw:stats off|on|now`);",
        "interval tail")
m.write_text(t, encoding="utf-8")

h = DST / "scripts/pw_homestead.js"; s = h.read_text(encoding="utf-8")
s = sub(s, "room FOG off + stuck-fog sweep in v1.3.187; ember SPARKS in v1.3.188): hearth · flue · dual wall · rafter.",
        "room FOG off + stuck-fog sweep in v1.3.187; ember SPARKS in v1.3.188; boot line wording v1.3.189): hearth · flue · dual wall · rafter.", "homestead header")
s = sub(s, "log(`v1.3.187 stuck-fog sweep at boot: ${n} player(s); room fog push ${ROOM_FOG ? \"ON\" : \"OFF\"}`);",
        "log(`stuck-fog sweep (since v1.3.187) at boot: ${n} player(s); room fog push ${ROOM_FOG ? \"ON\" : \"OFF\"}`);", "sweep line")
h.write_text(s, encoding="utf-8")

man = json.loads((DST / "manifest.json").read_text(encoding="utf-8")); v = [int(x) for x in VER.split(".")]
man["header"]["name"] = f"AbsolutRealism Tectonic BP v{VER}"; man["header"]["version"] = v
for mod in man["modules"]:
    mod["version"] = v
man["header"]["description"] = (f"v{VER} ({DATE}) STATS CADENCE (D-C260): the [BIGCANOPY-STATS] content-log line fires every 60 s while the scanner is "
                                "busy (was 5 s — it buried the [PW-TEST] lines of the P0 run) and every 5 min when idle; /scriptevent pw:stats off | on | now. "
                                "Homestead boot line reworded (stuck-fog sweep since v1.3.187). Everything else byte-identical to v1.3.188.")
(DST / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
log(f"BP-02 v{VER}: main.js stats 1200t + pw:stats off|on|now + PW_BUILD; pw_homestead.js boot wording; manifest stamped")

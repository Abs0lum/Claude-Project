#!/usr/bin/env python3
"""build_stack_api.py — the API-audit fixes (D-C231 findings a–d), Abs0lum 21:38 "Fix all, build, pack, and deliver".

  BP-02 v1.3.186  (from _build/bp02-185)
      manifest @minecraft/server 2.0.0 -> 2.3.0 (Dimension.getBiome is stable from 2.3.0 -> fireflies keep to
      swamp/mangrove); + scripts/pw_weather.js; main.js: _leafWind reads pw_weather (Dimension.getWeather is
      beta-only -> leaves were always calm); firefly biome gate no longer switches itself off on one bad
      location; PW_BUILD flag 1.3.174 -> 1.3.186 (version-flag law).
  BP-01 v1.3.35   (from _intake/stack-bps BP-01 v1.3.34)
      manifest @minecraft/server 1.16.0 -> 2.3.0 (getBiome existed nowhere before -> no ambient sound ever
      played); + scripts/pw_weather.js; weather reads -> pw_weather; runCommandAsync (removed in 2.x) ->
      runCommand; version flag.
  BP-03 v1.3.34   (from _intake/stack-bps BP-03 v1.3.33)
      scripts/main.js <- tools/stack_src/bp03_main.js: /scriptevent pw:diag <verb> (chatSend is beta-only, so
      "!diag" never worked); pin stays 2.0.0.
Everything else byte-identical to the source packs."""
import json, shutil, datetime, zipfile
from pathlib import Path
ROOT = Path("/home/claude"); DATE = "2026-09-22"
W = ROOT / "tools/weather_src/pw_weather.js"
def log(m):
    print(m); open(ROOT / "_logs/phase_log.md", "a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
def sub(text, old, new, label):
    n = text.count(old)
    assert n == 1, f"{label}: expected exactly 1 match, found {n}"
    return text.replace(old, new)
def extract(mcpack, dst):
    if dst.exists(): shutil.rmtree(dst)
    dst.mkdir(parents=True)
    with zipfile.ZipFile(mcpack) as z: z.extractall(dst)
def stamp(man, ver, name, desc, pins=None):
    vv = [int(x) for x in ver.split(".")]
    man["header"]["name"] = name; man["header"]["version"] = vv; man["header"]["description"] = desc
    for m in man["modules"]: m["version"] = vv
    for d in man.get("dependencies", []):
        if pins and d.get("module_name") in pins: d["version"] = pins[d["module_name"]]

# ------------------------------------------------------------------ BP-02 v1.3.186
def bp02():
    SRC, DST, VER = ROOT / "_build/bp02-185", ROOT / "_build/bp02-186", "1.3.186"
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    shutil.copy(W, DST / "scripts/pw_weather.js")
    p = DST / "scripts/main.js"; t = p.read_text(encoding="utf-8")
    t = sub(t, 'const PW_BUILD = "1.3.174";', 'const PW_BUILD = "1.3.186";', "PW_BUILD")
    t = sub(t, 'import "./pw_furniture.js"; // FURNITURE: 12 pieces x 3 woods, sit + table auto-join (v1.3.183)\n',
            'import "./pw_furniture.js"; // FURNITURE: 12 pieces x 3 woods, sit + table auto-join (v1.3.183)\n'
            'import { weatherIn } from "./pw_weather.js"; // v1.3.186: weather via world.afterEvents.weatherChange (stable); Dimension.getWeather is beta-only\n',
            "import")
    t = sub(t, '''function _leafWind(dim) {
  try {
    const w = dim.getWeather && dim.getWeather();
    if (w === "Thunder") return 1.6;
    if (w === "Rain") return 0.8;
  } catch {}
  return 0.15;
}''', '''function _leafWind(dim) {
  // v1.3.186: the weather comes from pw_weather.js (world.afterEvents.weatherChange, stable API). The old
  // dim.getWeather() is beta-only, so on our stable pin it was always missing and leaves drifted at the
  // calm speed through every storm.
  let w = "Clear";
  try { w = weatherIn(dim); } catch {}
  if (w === "Thunder") return 1.6;
  if (w === "Rain") return 0.8;
  return 0.15;
}''', "_leafWind")
    t = sub(t, '''  // Biome check (with graceful fallback)
  let biomeOk = true;
  if (fireflyBiomeApiOk !== false) {
    try {
      const biome = player.dimension.getBiome(player.location);
      const biomeId = biome?.id ?? biome?.typeId ?? null;
      if (biomeId !== null) {
        const idLower = String(biomeId).toLowerCase();
        biomeOk = FIREFLY_AMBIENT_BIOMES.includes(biomeId) || idLower.includes("swamp") || idLower.includes("mangrove");
        fireflyBiomeApiOk = true;
      } else {
        fireflyBiomeApiOk = false;
      }
    } catch {
      fireflyBiomeApiOk = false;
    }
  }
  if (fireflyBiomeApiOk === false) {
    // Fallback: spawn anyway at night so the user still sees fireflies (better than nothing)
    biomeOk = true;
  }''', '''  // Biome check. v1.3.186: the pack now pins @minecraft/server 2.3.0, where Dimension.getBiome is stable, so
  // fireflies keep to swamps and mangroves as designed (on the 2.0.0 pin the call did not exist and the
  // fallback below spawned them in every biome). A throw at ONE location (above the build limit, an unloaded
  // chunk) now skips this beat only, instead of switching the biome gate off for the rest of the session.
  let biomeOk = true;
  if (fireflyBiomeApiOk !== false) {
    if (typeof player.dimension.getBiome !== "function") {
      fireflyBiomeApiOk = false;
    } else {
      let biome;
      try { biome = player.dimension.getBiome(player.location); } catch { return; }
      const biomeId = biome?.id ?? biome?.typeId ?? null;
      if (biomeId !== null) {
        const idLower = String(biomeId).toLowerCase();
        biomeOk = FIREFLY_AMBIENT_BIOMES.includes(biomeId) || idLower.includes("swamp") || idLower.includes("mangrove");
        fireflyBiomeApiOk = true;
      } else {
        fireflyBiomeApiOk = false;
      }
    }
  }
  if (fireflyBiomeApiOk === false) {
    // Fallback (API missing): spawn anyway at night so the user still sees fireflies
    biomeOk = true;
  }''', "firefly gate")
    p.write_text(t, encoding="utf-8")
    log(f"BP-02 {VER} — scripts/pw_weather.js (new) + main.js: import, _leafWind -> weatherIn, firefly gate, PW_BUILD 1.3.186")
    man = jload(DST / "manifest.json")
    stamp(man, VER, f"AbsolutRealism Tectonic BP v{VER}",
          f"v{VER} ({DATE}) STABLE-API FIXES (D-C231 audit, Abs0lum 21:38): pins @minecraft/server 2.3.0 (was 2.0.0) so Dimension.getBiome "
          "exists and the ambient fireflies keep to swamps and mangroves at night (before: every biome); leaf drift blows harder in rain "
          "and storms (weather now read from world.afterEvents.weatherChange via scripts/pw_weather.js; Dimension.getWeather is beta-only). "
          "Includes v1.3.185 (hearth room-smoke wall test). Everything else byte-identical to v1.3.185. "
          "Requires RP-04 v1.3.138; pair with RP-02 v2.0.4.",
          {"@minecraft/server": "2.3.0"})
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; lt = led.read_text(encoding="utf-8")
    led.write_text(sub(lt, "v1.3.185 ·", f"v{VER} ·", "ledger stamp"), encoding="utf-8")
    log(f"BP-02 {VER} — manifest (server 2.3.0, server-ui 2.0.0 kept) + ledger stamp")

# ------------------------------------------------------------------ BP-01 v1.3.35
def bp01():
    BASE, DST, VER = ROOT / "_build/bp01-134", ROOT / "_build/bp01-135", "1.3.35"
    extract(ROOT / "_intake/stack-bps/BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_34.mcpack", BASE)
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(BASE, DST)
    shutil.copy(W, DST / "scripts/pw_weather.js")
    p = DST / "scripts/main.js"; t = p.read_text(encoding="utf-8")
    t = sub(t, " * @minecraft/server module dependency: 1.16.0+\n */\n\nimport { world, system } from \"@minecraft/server\";\n",
            " * @minecraft/server module dependency: 2.3.0 (v1.3.35). On the old 1.16.0 pin Dimension.getBiome did not\n"
            " * exist, so every beat skipped and no ambient sound ever played; getBiome is stable from 2.3.0.\n"
            " * Weather: ./pw_weather.js (world.afterEvents.weatherChange) — Dimension.getWeather is beta-only.\n"
            " */\n\nimport { world, system } from \"@minecraft/server\";\nimport { weatherIn } from \"./pw_weather.js\";\n", "header+import")
    t = sub(t, '''function getDimensionWeather(player) {
    // Returns "clear", "rain", or "thunder" — best-effort detection.
    // Bedrock script API does not expose dimension weather directly; we approximate
    // by checking world properties. Fallback: assume clear.
    try {
        const dim = player.dimension;
        // Attempt various API paths
        if (typeof dim.getWeather === "function") {
            const w = dim.getWeather();
            if (w && w.type) return w.type;
        }
    } catch (e) { /* fall through */ }
    return "clear";
}''', '''function getDimensionWeather(player) {
    // Returns "clear", "rain", or "thunder". v1.3.35: read from pw_weather.js, which listens to
    // world.afterEvents.weatherChange (stable). The old Dimension.getWeather probe is beta-only,
    // so it always fell through to "clear" and the rain/storm pools never played.
    try { return weatherIn(player.dimension).toLowerCase(); } catch (e) { return "clear"; }
}''', "getDimensionWeather")
    t = sub(t, '''// Robust weather read. Bedrock's script weather API has historically been
// limited; try the typed API, then fall back to clear. (Rain/thunder still
// resolve via this when the runtime exposes it; safe default = clear.)
function arResolveWeather(player) {
    try {
        const dim = player.dimension;
        if (typeof dim.getWeather === "function") {
            const w = dim.getWeather();
            if (typeof w === "string") return w;          // "Clear"|"Rain"|"Thunder"
            if (w && w.type) return w.type;
        }
    } catch (e) { /* fall through */ }
    return "Clear";
}''', '''// Weather read. v1.3.35: from pw_weather.js (world.afterEvents.weatherChange, stable API) —
// "Clear" | "Rain" | "Thunder". The old Dimension.getWeather probe is beta-only and always read
// "Clear", so the rain/thunder sky states below never engaged until now.
function arResolveWeather(player) {
    try { return weatherIn(player.dimension); } catch (e) { return "Clear"; }
}''', "arResolveWeather")
    old_cmd = t[t.index("// Push/pop helper using the /fog command via the v1-compatible"):t.index("function arApplyFog(player, fogId) {")]
    assert "runCommandAsync" in old_cmd and t.count(old_cmd) == 1
    t = t.replace(old_cmd, '''// Push/pop helper using the /fog command. v1.3.35: @minecraft/server 2.x removed runCommandAsync;
// Entity.runCommand runs the command synchronously in the player's own context (@s works). There is
// no typed script fog API, so the command is the only mechanism. We always remove our previous tagged
// entry before pushing the new one so the per-player stack never accumulates duplicates.
//   Syntax: fog <target> push <fogID> <userProvidedId>
//           fog <target> remove <userProvidedId>
// runCommand THROWS when a command fails (e.g. a fog id that no loaded pack defines, or a remove with
// nothing to remove). A failed PUSH is written to the content log once per fog id — the discriminator for
// "is the sky scheduler doing anything?" — and every attempt still counts as done, so the cadence stays
// exactly as before: one attempt per state change plus the 15 s re-assert, never a retry storm.
const _arPushFailLogged = new Set();
function arRunCmd(player, cmd) {
    try {
        player.runCommand(cmd);
    } catch (e) {
        const m = /\\bpush\\s+"?([^"\\s]+)"?/.exec(cmd);
        if (m && !_arPushFailLogged.has(m[1])) {
            _arPushFailLogged.add(m[1]);
            try { console.warn(`[AbsolutRealism Sky] fog push failed: ${m[1]} — ${e && e.message ? e.message : e}`); } catch (_) {}
        }
    }
    return true;
}

''')
    t = sub(t, 'console.warn("[PW-VERSION] BP-01 Atmospheric Effects v1.3.33 \\u2014 version-flag law")',
            'console.warn("[PW-VERSION] BP-01 Atmospheric Effects v1.3.35 \\u2014 version-flag law")', "version flag")
    p.write_text(t, encoding="utf-8")
    log(f"BP-01 {VER} — scripts/pw_weather.js (new) + main.js: header/import, both weather reads -> weatherIn, arRunCmd runCommandAsync -> runCommand, version flag")
    man = jload(DST / "manifest.json")
    stamp(man, VER, f"AbsolutRealism Atmospheric Effects BP v{VER}",
          f"v{VER} ({DATE}) STABLE-API MIGRATION (D-C231 audit, Abs0lum 21:38): pins @minecraft/server 2.3.0 (was 1.16.0). "
          "Biome ambient sounds now PLAY (Dimension.getBiome did not exist on 1.16.0, so every beat was skipped); rain and storm sounds "
          "and the rain/thunder sky states follow the real weather (scripts/pw_weather.js, world.afterEvents.weatherChange; "
          "Dimension.getWeather is beta-only); fog commands use runCommand (runCommandAsync was removed in 2.x). "
          "Sounds come from RP-02 (v2.0.4 carries all 107).",
          {"@minecraft/server": "2.3.0"})
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; lt = led.read_text(encoding="utf-8")
    if "v1.3.34 ·" in lt: led.write_text(lt.replace("v1.3.34 ·", f"v{VER} ·", 1), encoding="utf-8")
    log(f"BP-01 {VER} — manifest (server 2.3.0) {'+ ledger stamp' if 'v1.3.34 ·' in lt else '(ledger carries no version stamp: unchanged)'}")

# ------------------------------------------------------------------ BP-03 v1.3.34
def bp03():
    BASE, DST, VER = ROOT / "_build/bp03-133", ROOT / "_build/bp03-134", "1.3.34"
    extract(ROOT / "_intake/stack-bps/BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_33.mcpack", BASE)
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(BASE, DST)
    shutil.copy(ROOT / "tools/stack_src/bp03_main.js", DST / "scripts/main.js")
    log(f"BP-03 {VER} — scripts/main.js <- tools/stack_src/bp03_main.js (/scriptevent pw:diag; chatSend removed)")
    man = jload(DST / "manifest.json")
    stamp(man, VER, f"AbsolutRealism Identification Diagnostics BP v{VER}",
          f"v{VER} ({DATE}) COMMANDS THAT WORK (D-C231 audit, Abs0lum 21:38): the diag mode is set with /scriptevent pw:diag on|off|brief|verbose|status|help "
          "(shortcut ids diag:off etc.). The old '!diag' chat commands relied on world.beforeEvents.chatSend, which is beta-only, so they never ran "
          "on the stable 2.0.0 pin. Block-break announcements unchanged.")
    for m in man["modules"]:
        if m.get("type") == "script": m["description"] = "Diagnostic script \u2014 playerBreakBlock subscription + /scriptevent pw:diag"
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; lt = led.read_text(encoding="utf-8")
    if "v1.3.33 ·" in lt: led.write_text(lt.replace("v1.3.33 ·", f"v{VER} ·", 1), encoding="utf-8")
    log(f"BP-03 {VER} — manifest {'+ ledger stamp' if 'v1.3.33 ·' in lt else '(ledger carries no version stamp: unchanged)'}")

if __name__ == "__main__":
    bp02(); bp01(); bp03()

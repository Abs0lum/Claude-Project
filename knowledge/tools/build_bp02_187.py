#!/usr/bin/env python3
"""build_bp02_187.py — BP-02 v1.3.187 (D-C251, Abs0lum 03:44 09-27 "MUCH TOO smokey … revert any changes that might effect this").

Root cause: the room-smoke FOG (pw:smoke_room, #6B6660, fog_end 7 fixed) is pushed onto the player by pw_homestead.js when a
closed room fills with smoke, and only popped for players the script REMEMBERS (a Map). The fog stack lives in the player's
saved data, so a relog / reload / pack change makes the script forget while the fog stays — forever, everywhere.
This build (from _build/bp02-186; every other file byte-identical):
  scripts/pw_homestead.js
    ROOM_FOG = false           the room fog push is OFF (his revert); room-smoke particles + the cough stay
    fogClear(player)           "fog @s remove pw_hearth_smoke" — removes EVERY entry with that id, remembered or not
    fogPop -> fogClear         (pop removed one entry; remove takes them all)
    fogPush                    no-op while ROOM_FOG is false; when on, never leaves two entries on the stack
    STUCK-FOG SWEEP            at boot for every online player, and 20 ticks after every initial player spawn
  scripts/main.js              PW_BUILD "1.3.186" -> "1.3.187" (version-flag law)
  manifest.json                1.3.187 + stamped description
"""
import json, shutil, datetime
from pathlib import Path
ROOT = Path("/home/claude"); SRC = ROOT / "_build/bp02-186"; DST = ROOT / "_build/bp02-187"
VER = "1.3.187"; DATE = "2026-09-27"


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-27] BUILD {m}\n")


def sub(text, old, new, label):
    n = text.count(old); assert n == 1, f"{label}: expected exactly 1 match, found {n}"; return text.replace(old, new)


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    p = DST / "scripts/pw_homestead.js"; s = p.read_text(encoding="utf-8")
    s = sub(s, "// pw_homestead.js — HOMESTEAD family runtime (BP-02 v1.3.182; room wall test fixed in v1.3.185): hearth · flue · dual wall · rafter.",
            "// pw_homestead.js — HOMESTEAD family runtime (BP-02 v1.3.182; room wall test fixed in v1.3.185; room FOG off + stuck-fog sweep in v1.3.187): hearth · flue · dual wall · rafter.", "header")
    s = sub(s, "const FOG_ON = 8, FOG_OFF = 5;   // hysteresis for the room fog push/pop\n",
            "const FOG_ON = 8, FOG_OFF = 5;   // hysteresis for the room fog push/pop\n"
            "const ROOM_FOG = false;          // v1.3.187 (D-C251): the room fog push is OFF — the pushed fog outlived the script's memory of it\n"
            "                                 // (the stack persists in the player's data across relogs; the Map does not) and greyed the whole world.\n"
            "const FOG_TAG = \"pw_hearth_smoke\";  // userProvidedId of every fog entry this module ever pushed (v1.3.178+)\n", "consts")
    s = sub(s, '''function fogPush(player, key) {
  if (fogged.get(player.id) === key) return;
  try { player.runCommand("fog @s push pw:smoke_room pw_hearth_smoke"); fogged.set(player.id, key); } catch { /* ignore */ }
}
function fogPop(player) {
  if (!fogged.has(player.id)) return;
  try { player.runCommand("fog @s pop pw_hearth_smoke"); } catch { /* ignore */ }
  fogged.delete(player.id);
}''', '''/** Removes EVERY pw_hearth_smoke entry from the player's fog stack, remembered or not (the stack survives relogs; the Map does not). */
export function fogClear(player) {
  try { player.runCommand(`fog @s remove ${FOG_TAG}`); } catch { /* nothing on the stack — fine */ }
  fogged.delete(player.id);
}
export function fogPush(player, key) {
  if (!ROOM_FOG) return;
  if (fogged.has(player.id)) { if (fogged.get(player.id) === key) return; fogClear(player); }   // never two entries
  try { player.runCommand(`fog @s push pw:smoke_room ${FOG_TAG}`); fogged.set(player.id, key); } catch { /* ignore */ }
}
export function fogPop(player) {
  if (!fogged.has(player.id)) return;
  fogClear(player);
}
export function _fogged() { return fogged; }
/** v1.3.187 stuck-fog sweep: a fog this module pushed in an earlier session is still on the player; take it off. */
function fogSweep(who) {
  let n = 0;
  for (const p of who) { try { fogClear(p); n++; } catch { /* ignore */ } }
  return n;
}
world.afterEvents.playerSpawn.subscribe((ev) => {
  if (!ev.initialSpawn) return;
  const p = ev.player;
  system.runTimeout(() => { try { fogSweep([p]); log(`stuck-fog sweep on join: ${p.name}`); } catch (e) { log(`fog sweep: ${e}`); } }, 20);
});''', "fog functions")
    s = sub(s, '''  loadLedger();
  system.runInterval(hearthCycle, CYCLE_TICKS);''', '''  loadLedger();
  try { const n = fogSweep(world.getAllPlayers()); log(`v1.3.187 stuck-fog sweep at boot: ${n} player(s); room fog push ${ROOM_FOG ? "ON" : "OFF"}`); } catch (e) { log(`boot fog sweep: ${e}`); }
  system.runInterval(hearthCycle, CYCLE_TICKS);''', "boot sweep")
    p.write_text(s, encoding="utf-8")
    m = DST / "scripts/main.js"; t = m.read_text(encoding="utf-8")
    t = sub(t, 'const PW_BUILD = "1.3.186";', 'const PW_BUILD = "1.3.187";', "version flag")
    m.write_text(t, encoding="utf-8")
    man = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig"))
    v = [1, 3, 187]; man["header"]["version"] = v; man["header"]["name"] = f"AbsolutRealism Tectonic BP v{VER}"
    for mod in man["modules"]: mod["version"] = v
    man["header"]["description"] = (f"v{VER} ({DATE}) ROOM FOG OFF + STUCK-FOG SWEEP (D-C251, Abs0lum 03:44 'MUCH TOO smokey'): the hearth room-smoke fog "
        "(pw:smoke_room) stayed on the player after a relog because only the script's memory was cleared, not the fog stack — the world "
        "went flat grey (#6B6660) beyond 7 blocks. Now: the room fog push is OFF (smoke particles + cough remain), every player's "
        "pw_hearth_smoke fog entries are removed at boot and on every join, and a push can never leave two entries. Everything else "
        "byte-identical to v1.3.186 (stable-API fixes, room smoke wall test, furniture). Requires RP-04 v1.3.138; pair with RP-02 v2.0.4.")
    (DST / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"BP-02 v{VER} built (_build/bp02-187)")


if __name__ == "__main__":
    main()

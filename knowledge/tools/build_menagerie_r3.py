#!/usr/bin/env python3
"""build_menagerie_r3.py — D-C356: PW-StripMine BP 1.3.9 -> 1.3.10, behaviour-only fixes from his 23:44 content log + his W1/W2.
  - every ported entity file re-ported through addon_port.fix_schema + convert_events (staging from tools/run_p3.sh R2):
    WS breeding, boostable damage, reach_multiplier, unknown components, ostrich egg item; natural event commands ON
    (queue_command), blessings / curse / missing summons + blocks OFF; files that gain a queue_command raised to format 1.20.0.
  - RP-07 is NOT rebuilt: the staged RP must equal the delivered RP-07 1.4.34 byte for byte (asserted).
Only files under pw_menagerie may differ from 1.3.9 (asserted); manifest version 1.3.10."""
import hashlib, json, shutil, sys, time
from pathlib import Path

ROOT = Path("/home/claude"); STAGE = ROOT / "_build/menagerie-stage"
VER = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1.3.10").split(".")]   # D-C356: one BP version per load round
PREV = {(1, 3, 10): "stripmine-bp-139", (1, 3, 11): "stripmine-bp-1310"}[tuple(VER)] if tuple(VER) in {(1, 3, 10), (1, 3, 11)} else f"stripmine-bp-1{VER[1]}{VER[2] - 1}"
BP0, BP1 = ROOT / "_build" / PREV, ROOT / "_build" / f"stripmine-bp-1{VER[1]}{VER[2]}"
RP = ROOT / "_build/rp07-1437"


def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main():
    # 1 RP unchanged: every staged RP file (bar the fragments, merged earlier) is already in 1.4.34, byte-identical
    rp_diff = [str(p.relative_to(STAGE / "RP")) for p in (STAGE / "RP").rglob("*") if p.is_file() and "_fragments" not in p.parts
               and (not (RP / p.relative_to(STAGE / "RP")).exists() or md5(p) != md5(RP / p.relative_to(STAGE / "RP")))]
    if "--rp-round" not in sys.argv: assert not rp_diff, f"RP would change: {rp_diff[:5]}"   # an RP round of its own may accompany (D-C363)
    # 2 BP
    if BP1.exists(): shutil.rmtree(BP1)
    shutil.copytree(BP0, BP1)
    added, improved = [], []
    for p in (STAGE / "BP").rglob("*"):
        if not p.is_file(): continue
        rel = p.relative_to(STAGE / "BP"); o = BP1 / rel
        if o.exists():
            if md5(o) == md5(p): continue
            assert "pw_menagerie" in rel.parts, f"would change {rel}"; improved.append(str(rel))
        else: added.append(str(rel))
        o.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, o)
    rep = json.loads((STAGE / "PORT-REPORT.json").read_text()); ev = rep.get("event_commands", {})
    m = json.loads((BP1 / "manifest.json").read_text(encoding="utf-8-sig"))
    V = ".".join(map(str, VER)); PV = ".".join(map(str, VER[:2] + [VER[2] - 1]))
    m["header"]["version"] = VER; m["header"]["name"] = f"PW StripMine BP v{V}"
    m["header"]["description"] = (f"v{V} (2026-10-01) MENAGERIE behaviour fixes from his content logs (load-by-load): legacy camelCase fields, "
                                  f"YSav breeding + breathing, Wildlife Sanctuary breeding works, "
                                  f"riding field / attack reach / unknown components fixed ({rep.get('schema_fixed', 0)} fixes); add-on event commands: "
                                  f"{ev.get('on', 0)} natural ones ON (sounds, particles, grazing regen, self effects, baby clean-up), "
                                  f"{ev.get('off_blessing', 0)} blessings / curses OFF, {ev.get('off_missing', 0)} that summon or place things we do not have OFF. "
                                  f"Pairs with RP-07 v1.4.34. Includes all of v{PV}.")
    for mod in m["modules"]: mod["version"] = VER
    (BP1 / "manifest.json").write_text(json.dumps(m, indent=1))
    (ROOT / f"_logs/menagerie_bp{V}_improved.json").write_text(json.dumps({"improved": improved, "added": added}, indent=1))
    line = f"BUILD StripMine BP {V}: {len(improved)} ported behaviour files improved, {len(added)} added; RP-07 1.4.34 unchanged (staging == delivered)"
    print(line)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-30] {line}\n")


if __name__ == "__main__":
    main()

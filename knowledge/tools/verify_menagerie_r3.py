#!/usr/bin/env python3
"""verify_menagerie_r3.py — gate for PW-StripMine BP 1.3.10 (D-C356). Static checks only rule OUT (P1); his next load log rules in."""
import hashlib, json, re, sys, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import addon_port as P

ROOT = Path("/home/claude"); RP = ROOT / "_build/rp07-1434"
VER = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1.3.10").split(".")]
B0 = ROOT / "_build" / ("stripmine-bp-139" if VER == [1, 3, 10] else f"stripmine-bp-1{VER[1]}{VER[2] - 1}"); B1 = ROOT / "_build" / f"stripmine-bp-1{VER[1]}{VER[2]}"
res = []
SIZED = set()                                                       # D-C363: our own creatures the size law v2 resized (scale values only)
try: SIZED = {"entities/" + x["file"] for x in json.loads((ROOT / "_docs/sizes/size_v2_ours_report.json").read_text())["stripmine"]} if VER >= [1, 3, 12] else set()
except FileNotFoundError: pass
def check(n, ok, d=""): res.append(ok); print(f"{'PASS' if ok else 'FAIL'}  {n}" + (f" — {d}" if d else ""))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def jl(p): return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
def walk(o, path=()):
    if isinstance(o, dict):
        for k, v in o.items(): yield path + (k,), v; yield from walk(v, path + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk(v, path + (i,))

m0, m1 = jl(B0 / "manifest.json"), jl(B1 / "manifest.json")
check(f"A manifest {VER}, uuids / dependencies unchanged", m1["header"]["version"] == VER and m1["header"]["uuid"] == m0["header"]["uuid"]
      and [x["uuid"] for x in m1["modules"]] == [x["uuid"] for x in m0["modules"]] and m1.get("dependencies") == m0.get("dependencies"))
f0 = {str(p.relative_to(B0)): p for p in B0.rglob("*") if p.is_file()}; f1 = {str(p.relative_to(B1)): p for p in B1.rglob("*") if p.is_file()}
changed = [k for k in f0 if k in f1 and md5(f0[k]) != md5(f1[k])]
check("B only ported behaviour files (entities/pw_menagerie) + the manifest changed; nothing added or removed",
      set(f0) == set(f1) and all(k == "manifest.json" or k.startswith(("entities/pw_menagerie/", "items/pw_menagerie/")) or k in SIZED for k in changed), f"{len(changed)} changed")
errs = []
for p in B1.rglob("*.json"):
    try: jl(p)
    except Exception as e: errs.append(str(p.relative_to(B1)))
check("C every JSON parses", not errs, str(errs[:3]))
z = Path(tempfile.mkdtemp()) / "bp.mcpack"
with zipfile.ZipFile(z, "w") as zf:
    for p in B1.rglob("*.json"): zf.write(p, str(p.relative_to(B1)))
n, e = ML.lint_pack(z); check("C Molang lint", not e, f"{n} strings, {len(e)} errors")
ents = {}
for p in B1.glob("entities/pw_menagerie/**/*.json"):
    d = jl(p); ents[d["minecraft:entity"]["description"]["identifier"]] = (p, d)
bad = {"run_command": [], "breeds_with": [], "item_damage": [], "reach_multiplier": [], "unknown_component": [], "ostrich_egg": [], "fmt": [], "not_natural": [], "event_missing": []}
for i, (p, d) in ents.items():
    has_q = False
    events = set(d["minecraft:entity"].get("events", {}))
    for path, v in walk(d):
        k = path[-1]
        if k == "run_command": bad["run_command"].append(i)
        if k == "breeds_with" and isinstance(v, dict) and v and all(":" in a and b == {} for a, b in v.items()): bad["breeds_with"].append(i)
        if k == "item_damage": bad["item_damage"].append(i)
        if k == "reach_multiplier" and "minecraft:behavior.melee_box_attack" in path: bad["reach_multiplier"].append(i)
        if k in ("minecraft:celebrate", "minecraft:fall_damage"): bad["unknown_component"].append(i)
        if v == "minecraft:ostrich_egg": bad["ostrich_egg"].append(i)
        if k == "queue_command" and isinstance(v, dict):
            has_q = True
            cmds = v.get("command"); cmds = [cmds] if isinstance(cmds, str) else cmds
            for c in cmds:
                if P.command_kind(c) != "natural": bad["not_natural"].append((i, c))
                mm = re.match(r"event entity @s (\S+)", c)
                if mm and mm.group(1) not in events: bad["event_missing"].append((i, mm.group(1)))
    if has_q and tuple(int(x) for x in str(d.get("format_version")).split(".")[:3]) < (1, 20, 0): bad["fmt"].append(i)
check("D no run_command left (not valid in entity events today)", not bad["run_command"], str(bad["run_command"][:3]))
check("D WS breeding: no breeds_with with the id as a key", not bad["breeds_with"], str(bad["breeds_with"][:3]))
camel = [(i, path[-1]) for i, (p, d) in ents.items() for path, v in walk(d["minecraft:entity"]) if P.in_component(path) and re.match(r"^[a-z]+[A-Z]", str(path[-1])) and path[-1] not in P.CAMEL_OK]
check("D (his 00:03 log) no legacy camelCase field inside any component (breedsWith, mateType, totalSupply, ...)", not camel, f"{len(camel)} e.g. {camel[:3]}")
strl = [(i, path[-1]) for i, (p, d) in ents.items() for path, v in walk(d["minecraft:entity"]) if path[-1] in ("breed_items", "feed_items") and isinstance(v, str)]
check("D breed_items / feed_items are lists (a bare string is refused)", not strl, str(strl[:3]))
beefe = [i for i, (p, d) in ents.items() for path, v in walk(d) if isinstance(v, str) and v.endswith("_beefe")]
check("D no ycreatures_savanna giant_beefe / mob_beefe left (-> minecraft:beef)", not beefe, str(beefe[:3]))
foreign = [(i, v) for i, (p, d) in ents.items() for path, v in walk(d) if isinstance(v, str) and v in set(P.ITEM_FIX)]
check("D no item / block id that no pack defines (giant_beefe, larvae, fire_ant_item, gold_bone_meal, baobab, termite nest, fortniteaddon)", not foreign, str(foreign[:4]))
check("D no item_damage / reach_multiplier / celebrate / fall_damage / minecraft:ostrich_egg",
      not (bad["item_damage"] or bad["reach_multiplier"] or bad["unknown_component"] or bad["ostrich_egg"]), str({k: v[:2] for k, v in bad.items() if v})[:200])
check("E his W1/W2: every queue_command is natural (no effect on players, no summon / block we lack)", not bad["not_natural"], str(bad["not_natural"][:3]))
check("E every file with a queue_command is format >= 1.20.0", not bad["fmt"], str(bad["fmt"][:3]))
check("E every 'event entity @s X' names an event the creature has", not bad["event_missing"], str(bad["event_missing"][:3]))
anims = set()
for p in RP.rglob("animations/**/*.json"):
    try: anims |= set((jl(p).get("animations") or {}))
    except Exception: pass
pa = [(i, c) for i, (p, d) in ents.items() for path, v in walk(d) if path[-1] == "queue_command" and isinstance(v, dict)
      for c in ([v["command"]] if isinstance(v["command"], str) else v["command"]) if c.startswith("playanimation")]
pa_bad = [(i, c) for i, c in pa if c.split()[2] not in anims]
check("E every playanimation in a command names an animation RP-07 1.4.34 has", not pa_bad, f"{len(pa)} commands; bad {pa_bad[:3]}")
print(("GATE OPEN" if all(res) else "GATE CLOSED") + f" — {sum(res)}/{len(res)}")

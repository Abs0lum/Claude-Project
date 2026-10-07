#!/usr/bin/env python3
"""addon_port.py — P0 of the menagerie port plan (D-C349/D-C351): copy add-on creatures into STAGING packs, every id renamed.

Usage (staging only — nothing here is shipped; the wave builds merge staging into RP-07 / StripMine BP after his GO):
  addon_port.py <SRC>:<entity id>=<new id> [...]        e.g. YSav:ycreatures_savanna:savanna_guepardo=pw:cheetah
Output: _build/menagerie-stage/{BP,RP}/ + _build/menagerie-stage/PORT-REPORT.json

What it does per creature (file set from addon_port_scan.Source.closure):
  - files land under source-prefixed paths: textures/entity/pw_menagerie/<src>/..., models/entity/pw_menagerie/<src>/...,
    animations / controllers / render controllers / loot tables / spawn rules likewise (a shared add-on file is copied once per source)
  - renames, applied to every copied JSON as exact quoted tokens:
      entity ids old -> new (only the ones being ported; other ids of that add-on stay and are reported)
      geometry.X -> geometry.pwm.<src>.X ; animation.X -> animation.pwm.<src>.X ; controller.animation.X -> controller.animation.pwm.<src>.X ;
      controller.render.X -> controller.render.pwm.<src>.X (only ids DEFINED by that add-on; vanilla ids are left alone)
      textures/... and loot_tables/... paths -> their new staging paths
  - dead references the game skips today are listed (not invented): see PORT-SCAN for the census
Namespace default pw: (his Q2 still open — the new id is whatever the caller passes)."""
import io, json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import addon_port_scan as S

ROOT = Path("/home/claude"); STAGE = ROOT / "_build/menagerie-stage"


def inner(n): return n.split("!")[-1]


def ascii_path(rp):
    """D-C353: a path every platform takes — non-ASCII letters folded (savanna_le\u2560o -> savanna_leo), no space before the extension"""
    import unicodedata
    out = unicodedata.normalize("NFKD", rp).encode("ascii", "ignore").decode()
    return re.sub(r" +(\.[a-z0-9]+)$", r"\1", out)


def rel_in_pack(n):
    """path inside its pack: strip the archive prefix and the pack folder (first segment that holds a manifest sibling)"""
    p = inner(n)
    parts = p.split("/")
    for i, seg in enumerate(parts):
        if seg in ("entities", "entity", "models", "animations", "animation_controllers", "render_controllers", "textures", "loot_tables",
                   "spawn_rules", "items", "sounds", "particles", "attachables", "trading", "functions", "recipes"):
            return "/".join(parts[i:])
    return parts[-1]


def rename_str(s, m):
    if s in m: return m[s]
    if "<" in s and s.endswith(">"):                              # D-C353: 'id<event>' (transformation targets, spawn events)
        a, ev = s.split("<", 1)
        if a in m: return m[a] + "<" + ev
    if s.endswith("_spawn_egg") and s[:-10] in m: return m[s[:-10]] + "_spawn_egg"   # an entity's own spawn egg item
    base = re.sub(r"\.(png|tga)$", "", s)
    if base != s and base in m: return m[base] + s[len(base):]
    if ":" in s and s.startswith("geometry."):                   # legacy 'geometry.child:geometry.parent' keys
        a, b = s.split(":", 1); return f"{m.get(a, a)}:{m.get(b, b)}"
    return s


def rename(o, m):
    if isinstance(o, dict): return {rename_str(k, m): rename(v, m) for k, v in o.items()}
    if isinstance(o, list): return [rename(v, m) for v in o]
    if isinstance(o, str): return rename_str(o, m)
    return o


SAT = {"poor": 0.1, "low": 0.3, "normal": 0.6, "good": 0.8, "max": 1.0, "supernatural": 1.2}
MEDAL = re.compile(r"medalha|medal", re.I)


def modern_item(d, new, icon_key, name):
    """an add-on item (format 1.10-1.16.100) rewritten in today's format; returns (item json, dropped event notes)"""
    c = d.get("minecraft:item", {}).get("components", {}); notes = []
    comp = {"minecraft:icon": {"textures": {"default": icon_key}}, "minecraft:display_name": {"value": name}}
    if "minecraft:max_stack_size" in c: comp["minecraft:max_stack_size"] = c["minecraft:max_stack_size"]
    food = c.get("minecraft:food")
    if isinstance(food, dict):
        sm = food.get("saturation_modifier", 0.6); sm = SAT.get(sm, 0.6) if isinstance(sm, str) else sm
        nut = food.get("nutrition", 0); nut = max(1, round(nut)) if isinstance(nut, float) else nut   # BDS 00:11: nutrition must be a whole number
        comp["minecraft:food"] = {"nutrition": nut, "saturation_modifier": sm, "can_always_eat": bool(food.get("can_always_eat", False))}
        comp["minecraft:use_modifiers"] = {"use_duration": 1.6, "movement_modifier": 0.35}
        comp["minecraft:use_animation"] = c.get("minecraft:use_animation", "eat")
        if food.get("on_consume") or food.get("effects") or d.get("minecraft:item", {}).get("events"): notes.append("on-eat effect not ported (needs a script)")
    elif "minecraft:use_animation" in c and c["minecraft:use_animation"] in ("eat", "drink"): pass
    if "minecraft:hand_equipped" in c: comp["minecraft:hand_equipped"] = bool(c["minecraft:hand_equipped"])
    if "minecraft:foil" in c or "minecraft:glint" in c: comp["minecraft:glint"] = True
    return {"format_version": "1.21.40", "minecraft:item": {"description": {"identifier": new, "menu_category": {"category": "items"}}, "components": comp}}, notes


def clean_loot(d, m, report):
    """loot entries: medals out (his Q5), entries naming an add-on item we did not port out (an unknown item id breaks the table)"""
    ported = set(m.values())
    for pool in d.get("pools", []) or []:
        keep = []
        for e in pool.get("entries", []) or []:
            nm = str(e.get("name", ""))
            if MEDAL.search(nm): report.setdefault("dropped_loot", []).append(nm); continue
            if e.get("type", "item") == "item" and ":" in nm and not nm.startswith("minecraft:") and nm not in ported:
                report.setdefault("dropped_loot", []).append(nm); continue
            keep.append(e)
        pool["entries"] = keep
    d["pools"] = [p for p in d.get("pools", []) or [] if p.get("entries")]
    return d


LEFTOVER = {"ycreatures_savanna:giant_beef": "minecraft:beef", "ycreatures_savanna:mob_beef": "minecraft:beef", "ycreatures_savanna:beetroot": "minecraft:beetroot",
            "ycreatures_savanna:strata": None}
DROP_RE = re.compile(r"^ycreatures_savanna:[a-z]+_egg_block\d+s\d+$")
GROUND = {"minecraft:grass": ["minecraft:grass_block", "pw:grass_block"], "grass": ["minecraft:grass_block", "pw:grass_block"],
          "minecraft:grass_block": ["minecraft:grass_block", "pw:grass_block"], "grass_block": ["minecraft:grass_block", "pw:grass_block"],
          "ycreatures_savanna:strata": ["minecraft:sand", "minecraft:red_sand", "minecraft:grass_block", "pw:grass_block"]}


def fix_leftovers(o, m, report):
    """after the rename: add-on ids that were not ported -> a vanilla twin, or out (unported egg blocks); typo'd mate ids -> the port"""
    if isinstance(o, list):
        out = []
        for x in o:
            if isinstance(x, str) and (DROP_RE.match(x) or (x in LEFTOVER and LEFTOVER[x] is None)): report["leftovers_fixed"] = report.get("leftovers_fixed", 0) + 1; continue
            out.append(fix_leftovers(x, m, report))
        return out
    if isinstance(o, dict): return {k: fix_leftovers(v, m, report) for k, v in o.items()}
    if isinstance(o, str):
        if o in LEFTOVER and LEFTOVER[o]: report["leftovers_fixed"] = report.get("leftovers_fixed", 0) + 1; return LEFTOVER[o]
        if o.startswith("ycreatures_savannaa:"):                     # a typo in the source (mabeco's mate) -> the ported id
            fixed = m.get(o.replace("ycreatures_savannaa:", "ycreatures_savanna:", 1))
            if fixed: report["leftovers_fixed"] = report.get("leftovers_fixed", 0) + 1; return fixed
    return o


UNKNOWN_COMPONENTS = {"minecraft:celebrate", "minecraft:fall_damage"}      # his 23:44 log: 'not present in the Schema'
ITEM_FIX = {"minecraft:ostrich_egg": "pw:egg_ostrich_anf",                  # an item that never existed -> the ostrich egg we ported (AnF)
            "ycreatures_savanna:giant_beefe": "minecraft:beef", "ycreatures_savanna:mob_beefe": "minecraft:beef"}   # his 00:03 log (source typos)
ITEM_FIX.update({"fortniteaddon:sweet_berries": "minecraft:sweet_berries",                  # D-C356 pre-emptive (independent check list)
                 "ycreatures_savanna:baobab_leaves": "minecraft:acacia_leaves", "ycreatures_savanna:baobab_log": "minecraft:acacia_log"})
DROP_IDS = {"skinscraft:larvae", "skinscraft:fire_ant_item", "worldanimals:gold_bone_meal",          # items / blocks no pack defines
            "ycreatures_savanna:termite_nest", "ycreatures_savanna:termite_nest_disocupate"}
LIST_FIELDS = {"breed_items", "feed_items"}
CAMEL_OK = {"randomInterval"}                                                # minecraft:timer's own field name IS camelCase (BDS 00:15)                                  # 'Allowed types: object, array' (a bare string is refused)


def snake(k): return re.sub(r"(?<=[a-z0-9])([A-Z])", lambda mm: "_" + mm.group(1).lower(), k)


def in_component(path):
    """True when path is INSIDE a component's value (not a component / group / event name)"""
    if "events" in path: return False
    for i, seg in enumerate(path):
        if seg == "components": return len(path) > i + 1
        if seg == "component_groups": return len(path) > i + 2
    return False


def fix_schema(o, report, path=()):
    """D-C356 (his 23:44 content log), inherited add-on errors the game rejects today:
       breedable.breeds_with {"<id>": {}} (the id as a key)  -> {"mate_type": id, "baby_type": id}   (WS: breeding never worked)
       boostable.boost_items[].item_damage                    -> damage
       behavior.melee_box_attack.reach_multiplier             -> removed
       components the schema does not know (celebrate, fall_damage) -> removed
       item ids that never existed (minecraft:ostrich_egg)    -> our ported item"""
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if in_component(path) and re.match(r"^[a-z]+[A-Z]", k) and k not in CAMEL_OK:   # his 00:03 log: legacy camelCase (breedsWith, mateType, ...)
                k = snake(k); report["schema_fixed"] = report.get("schema_fixed", 0) + 1
            if k in LIST_FIELDS and isinstance(v, str) and in_component(path): v = [v]
            if k in out and k == "breeds_with":                          # breedsWith + breeds_with both present: one list
                prev = out[k] if isinstance(out[k], list) else [out[k]]; v2 = fix_schema(v, report, path + (k,))
                out[k] = prev + (v2 if isinstance(v2, list) else [v2]); continue
            if k in UNKNOWN_COMPONENTS: report["schema_fixed"] = report.get("schema_fixed", 0) + 1; continue
            if k == "reach_multiplier" and path and path[-1] == "minecraft:behavior.melee_box_attack":
                report["schema_fixed"] = report.get("schema_fixed", 0) + 1; continue
            if k == "item_damage" and "minecraft:boostable" in path: k = "damage"; report["schema_fixed"] = report.get("schema_fixed", 0) + 1
            if k == "breeds_with" and isinstance(v, dict) and v and all(":" in kk and vv == {} for kk, vv in v.items()):
                mates = [{"mate_type": kk, "baby_type": kk} for kk in v]
                v = mates[0] if len(mates) == 1 else mates; report["schema_fixed"] = report.get("schema_fixed", 0) + 1
            out[k] = fix_schema(v, report, path + (k,))
        return out
    if isinstance(o, list):
        def dead(x):
            if isinstance(x, str): return x in DROP_IDS
            return isinstance(x, dict) and (str(x.get("item")) in DROP_IDS or str(x.get("name")) in DROP_IDS)
        keep = [x for x in o if not dead(x)]
        if len(keep) != len(o): report["schema_fixed"] = report.get("schema_fixed", 0) + len(o) - len(keep)
        return [fix_schema(x, report, path) for x in keep]
    if isinstance(o, str) and o in ITEM_FIX: report["schema_fixed"] = report.get("schema_fixed", 0) + 1; return ITEM_FIX[o]
    return o


PLAYER_FX = re.compile(r"^\s*/?(effect|give|tp|teleport|damage|kill|xp|clear|enchant)\s+@(p|a|e|r)")
UNPORTED = re.compile(r"\b(worldanimals|ycreatures_savanna|ycreatures|cyd_ulta|skinscraft|tayi):|\bm:|minecraft:ostrich_egg")


def command_kind(cmd):
    """his W2 (23:52): 'natural' = what the animal does to itself or to the air around it (sounds, particles, self effects, self
    animations / events, removing itself); off = blessings / curses on players, summons or blocks we do not have."""
    c = cmd.strip().lstrip("/")
    if UNPORTED.search(c): return "missing"
    if PLAYER_FX.match(c): return "blessing"
    if re.match(r"^(playsound|particle)\b", c): return "natural"
    if re.match(r"^(effect|playanimation|event entity|kill|tag|scoreboard players \w+) @s\b", c): return "natural"
    return "other"


def convert_events(o, report, path=(), m=None):
    """D-C356: run_command (not valid in entity events today) -> queue_command when EVERY command in it is natural; else removed
    (his W1 whale curse OFF, W2 blessings OFF; summons / blocks we do not have can't run). Returns (new, made_queue)."""
    made = False
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k == "run_command" and isinstance(v, dict):
                cmds = v.get("command"); cmds = [cmds] if isinstance(cmds, str) else list(cmds or [])
                kinds = [command_kind(c) for c in cmds]
                rep = report.setdefault("event_commands", {"on": 0, "off_blessing": 0, "off_missing": 0, "off_other": 0, "off_examples": []})
                if cmds and all(x == "natural" for x in kinds):
                    if m: cmds = [" ".join(rename_str(w, m) for w in c.split(" ")) for c in cmds]   # ids inside the command text
                    nv = {"command": cmds}
                    if v.get("target"): nv["target"] = v["target"]
                    out["queue_command"] = nv; made = True; rep["on"] += 1
                else:
                    why = "blessing" if "blessing" in kinds else "missing" if "missing" in kinds else "other"
                    rep[f"off_{why}"] += 1
                    if len(rep["off_examples"]) < 40: rep["off_examples"].append([why, cmds[:3]])
                continue
            nv, mk = convert_events(v, report, path + (k,), m); out[k] = nv; made |= mk
        return out, made
    if isinstance(o, list):
        res = [convert_events(x, report, path, m) for x in o]
        return [r[0] for r in res], any(r[1] for r in res)
    return o, False


VANILLA_RENAMED = {"controller.animation.polarbear.move": "controller.animation.polar_bear.move"}   # 1.26 vanilla name (WA hyena walk)
BAD_SOUND_EVENTS = {"ask", "sniff", "spit"}     # his 00:29 full log: 'not a valid LevelSoundEvent'


def fix_client(d, dead, report, ported=frozenset()):
    """D-C359 (his 00:29 full log): a client entity's animation entries that its own pack never shipped ('can't find animation
    baby_transform') are removed, with every scripts.animate line that plays them."""
    desc = d.get("minecraft:client_entity", {}).get("description", {})
    anims = desc.get("animations") or {}
    dead = {x for x in dead if x not in vanilla_ids()}                # his 00:40 log: vanilla animations (fox move, ...) are NOT dead
    gone = {k for k, v in anims.items() if v in dead}
    for k in gone: anims.pop(k)
    sc = desc.get("scripts") or {}
    if isinstance(sc.get("animate"), list):                       # also lines naming a short name the map never had (platypus / emu baby_transform)
        keep = [x for x in sc["animate"] if (x if isinstance(x, str) else next(iter(x), None)) in anims]
        report["dead_anims_removed"] = report.get("dead_anims_removed", 0) + len(gone) + (len(sc["animate"]) - len(keep))
        sc["animate"] = keep
        if not keep: sc.pop("animate")                                # 'Array too small (0 < 1)'
    if "animation_controllers" in desc:                            # D-C361 (his L1/L2): the old-style controller list
        alive = vanilla_ids() | set(ported)
        for x in desc["animation_controllers"]:                   # vanilla renamed some controllers since the add-on was made
            if isinstance(x, dict):
                for kk, vv in list(x.items()):
                    if vv in VANILLA_RENAMED: x[kk] = VANILLA_RENAMED[vv]; report["vanilla_renamed"] = report.get("vanilla_renamed", 0) + 1
        lst = desc["animation_controllers"] if desc.get("animations") else []   # nothing to drive (WA eggs) -> no line
        keep = [x for x in lst if isinstance(x, dict) and all(v in alive for v in x.values())]
        report["legacy_controllers_dropped"] = report.get("legacy_controllers_dropped", 0) + len(desc["animation_controllers"]) - len(keep)
        if keep: desc["animation_controllers"] = keep
        else: desc.pop("animation_controllers")
    if "scripts" in desc and not desc["scripts"]: desc.pop("scripts")
    if "animations" in desc and not desc["animations"]: desc.pop("animations")   # 'Node has too few children (0 < 1)'
    return d


_VAN = None
def vanilla_ids():
    """ids that resolve without the add-on: vanilla + every animation / controller RP-07 itself defines (our fox has
    animation.fox.baby_transform, so the YTri coyote's line plays — his 00:40 regression check)"""
    global _VAN
    if _VAN is None:
        _VAN = set(S.vanilla_refs())
        base = ROOT / "_build/rp07-1434"
        for sub, key in (("animations", "animations"), ("animation_controllers", "animation_controllers")):
            for f in base.rglob(f"{sub}/**/*.json"):
                if "pw_menagerie" in str(f): continue
                try: _VAN |= set((S.parse(f.read_bytes()) or {}).get(key) or {})
                except Exception: pass
    return _VAN


def fix_molang_text(o, report):
    """'loop': 'true' (a string) -> true; query.is_flying (not a query) -> (!query.is_on_ground)"""
    if isinstance(o, dict) and isinstance(o.get("states"), dict) and o["states"] and o.get("initial_state", "default") not in o["states"]:
        o = dict(o); o["initial_state"] = next(iter(o["states"])); report["rp_fixed"] = report.get("rp_fixed", 0) + 1   # his D1 (deer.baby)
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k == "loop" and v in ("true", "false"): v = (v == "true"); report["rp_fixed"] = report.get("rp_fixed", 0) + 1
            out[k] = fix_molang_text(v, report)
        return out
    if isinstance(o, list): return [fix_molang_text(x, report) for x in o]
    if isinstance(o, str) and re.search(r"\b(query|q)\.is_flying\b", o):
        report["rp_fixed"] = report.get("rp_fixed", 0) + 1
        return re.sub(r"\b(query|q)\.is_flying\b", "(!query.is_on_ground)", o)
    return o


def fix_spawn_ground(d, report):
    for cond in d.get("minecraft:spawn_rules", {}).get("conditions", []) or []:
        f = cond.get("minecraft:spawns_on_block_filter")
        if f is None: continue
        lst = f if isinstance(f, list) else [f]; out = []
        for b in lst:
            name = b if isinstance(b, str) else b.get("name") if isinstance(b, dict) else b
            out += GROUND.get(name, [b])
        out = list(dict.fromkeys(json.dumps(x) for x in out)); out = [json.loads(x) for x in out]
        if out != lst: report["spawn_ground_fixed"] = report.get("spawn_ground_fixed", 0) + 1
        cond["minecraft:spawns_on_block_filter"] = out
    return d


def scrub_medals(o, report):
    """his Q5: no medals. Behaviour files tame / share / drop the yCreatures medal; every list element and every small value that
    mentions one is removed (the rest of the component stays: an interact keeps its other interactions)."""
    dump = lambda x: json.dumps(x)
    if isinstance(o, list):
        out = []
        for x in o:
            if MEDAL.search(dump(x)): report["medal_refs_removed"] = report.get("medal_refs_removed", 0) + 1; continue
            out.append(scrub_medals(x, report))
        return out
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            s = dump(v)
            if MEDAL.search(s) and (isinstance(v, str) or len(s) < 400):
                report["medal_refs_removed"] = report.get("medal_refs_removed", 0) + 1; continue
            out[k] = scrub_medals(v, report)
        return out
    return o


MAT, MAT_USED = {}, {}


def materials_of(s, low):
    """the add-on's own entity materials: an empty 'name:base' is just another name for base (-> base); one with a body becomes ours
    ('pwm_<pack>_<name>:base', body kept) and is written to RP-07 materials/entity.material"""
    alias, custom = {}, {}
    for n, b in s.files.items():
        if not n.endswith(".material"): continue
        d = S.parse(b)
        if not isinstance(d, dict): continue
        for k, v in (d.get("materials") or {}).items():
            if ":" not in k: continue
            name, base = k.split(":", 1)
            if not v: alias[name] = base
            else: custom[name] = (f"pwm_{low}_{name}", {f"pwm_{low}_{name}:{base}": v})
    return {"alias": alias, "custom": custom}


def egg_colours(s, desc, inv):
    from PIL import Image
    import io as _io
    cols = ["#7A6A52", "#4A3A2A"]
    try:
        t = next(iter((desc.get("textures") or {}).values())); t = re.sub(r"\.(png|tga)$", "", t); n = s.tex.get(inv.get(t, t).lower())
        if n:
            im = Image.open(_io.BytesIO(s.files[n])).convert("RGBA"); px = [p for p in im.getdata() if p[3] > 128]
            px.sort(key=lambda p: sum(p[:3])); lo, hi = px[len(px) // 4], px[3 * len(px) // 4]
            cols = ["#%02X%02X%02X" % hi[:3], "#%02X%02X%02X" % lo[:3]]
    except Exception: pass
    return {"base_color": cols[0], "overlay_color": cols[1]}


def lang_of(s):
    out = {}
    for n, b in s.files.items():
        if n.endswith("en_US.lang"):
            for line in b.decode("utf-8", "replace").splitlines():
                if "=" in line and not line.startswith("#"): k, v = line.split("=", 1); out[k.strip()] = v.split("\t#")[0].strip()
    return out


_VS = None
def vanilla_sounds():
    """every sound file path vanilla's own sound definitions play (1.21 intake + the current bedrock-samples)"""
    global _VS
    if _VS is None:
        _VS = set()
        for f in (ROOT / "_intake/vanilla-1.21/sound_definitions.json", ROOT / "_intake/bedrock-samples/resource_pack/sounds/sound_definitions.json"):
            try: d = json.loads(f.read_text(encoding="utf-8-sig"))
            except Exception: continue
            for v in (d.get("sound_definitions", d)).values():
                if isinstance(v, dict):
                    for x in v.get("sounds", []): _VS.add(x.get("name") if isinstance(x, dict) else x)
    return _VS


def port(jobs, items=()):
    srcs = {}
    for tag, _, _ in list(jobs) + list(items):
        if tag not in srcs: srcs[tag] = S.Source(tag, S.SOURCES[tag])
    for tag, s in srcs.items(): MAT[tag] = materials_of(s, tag.lower())
    STAGE.mkdir(parents=True, exist_ok=True)
    report = {"creatures": [], "files": 0}
    plan = {}                                                    # (tag, file) -> (side, new rel path)
    idmap = {}                                                   # tag -> {old token: new token}
    for tag, old, new in jobs:
        s = srcs[tag]; r = s.closure(old)
        m = idmap.setdefault(tag, {})
        m[old] = new
        for f in r["files"]:
            side = s.side.get(f, "?"); rp = rel_in_pack(f)
            low = tag.lower()
            first = rp.split("/")[0]
            if first == "textures": rp = rp.replace("textures/", f"textures/entity/pw_menagerie/{low}/", 1) if not rp.startswith("textures/entity/") else rp.replace("textures/entity/", f"textures/entity/pw_menagerie/{low}/", 1)
            elif first == "models":                              # D-C355 (his 23:30 log): the game loads entity geometry only under models/entity/
                rest = rp.split("/")[1:]
                if rest and rest[0] == "entity": rest = rest[1:]
                rp = f"models/entity/pw_menagerie/{low}/" + "/".join(rest)
            else: rp = f"{first}/pw_menagerie/{low}/" + "/".join(rp.split("/")[1:])
            rp = ascii_path(rp)
            plan[(tag, f)] = (side, rp)
        report["creatures"].append({"src": tag, "old": old, "new": new, "files": len(r["files"]), "dead_refs": r["missing"], "other_ids": r["others"]})
    # id renames for everything those files DEFINE
    for (tag, f), (side, rp) in plan.items():
        s = srcs[tag]; d = s.json.get(f); low = tag.lower(); m = idmap[tag]
        if not isinstance(d, dict): continue
        for g in d.get("minecraft:geometry", []) or []:
            gid = g.get("description", {}).get("identifier")
            if gid: m[gid] = gid.replace("geometry.", f"geometry.pwm.{low}.", 1)
        for k in list(d):
            if k.startswith("geometry."): m[k.split(":")[0]] = k.split(":")[0].replace("geometry.", f"geometry.pwm.{low}.", 1)
        pe = d.get("particle_effect")
        if isinstance(pe, dict):                                   # D-C353: a particle the add-on defines (a ported entity's id keeps its map)
            pid = pe.get("description", {}).get("identifier")
            if pid and pid not in m: m[pid] = f"pwm_{low}:{pid.split(':', 1)[1]}"
        for key, pre in (("animations", "animation."), ("animation_controllers", "controller.animation."), ("render_controllers", "controller.render.")):
            if isinstance(d.get(key), dict) and "minecraft:client_entity" not in d and "minecraft:entity" not in d:
                for aid in d[key]:
                    if aid.startswith(pre): m[aid] = aid.replace(pre, f"{pre}pwm.{low}.", 1)
    # path renames (textures / loot tables)
    for (tag, f), (side, rp) in plan.items():
        orig = rel_in_pack(f); m = idmap[tag]
        if orig.startswith("textures/"): m[re.sub(r"\.(png|tga)$", "", orig)] = re.sub(r"\.(png|tga)$", "", rp)
        if orig.startswith("loot_tables/"): m[orig] = rp
    # items: today's format, icon texture copied, map old id -> new id (loot tables / interact components follow the map)
    item_frag, item_lang, item_notes = {}, [], {}
    for tag, old, new in items:
        s = srcs[tag]; low = tag.lower(); idmap.setdefault(tag, {})[old] = new
        f = s.items.get(old)
        if not f: item_notes[new] = ["item file not found"]; continue
        # 1.10-era items are split in two files (BP: food / stack, RP: icon / animation): merge every file of this id
        d = json.loads(json.dumps(s.json[f])); c = d.setdefault("minecraft:item", {}).setdefault("components", {})
        for n_, dd in s.json.items():
            if n_ != f and isinstance(dd, dict) and dd.get("minecraft:item", {}).get("description", {}).get("identifier") == old:
                for k_, v_ in (dd["minecraft:item"].get("components") or {}).items(): c.setdefault(k_, v_)
        ic = c.get("minecraft:icon"); key = ic.get("texture") if isinstance(ic, dict) else ic
        tex = None
        for n_, dd in s.json.items():
            if n_.endswith("item_texture.json") and isinstance(dd, dict) and key in dd.get("texture_data", {}):
                tt = dd["texture_data"][key]["textures"]; tex = tt if isinstance(tt, str) else (tt[0] if isinstance(tt, list) else tt.get("path"))
        newkey = f"pwm_{low}_{old.split(':')[1]}"
        if tex:
            src_png = s.tex.get(re.sub(r"\.(png|tga)$", "", tex.lower()))
            if src_png:
                rp = f"textures/items/pw_menagerie/{low}/" + src_png.split("textures/items/")[-1].split("textures/")[-1]
                o = STAGE / "RP" / rp; o.parent.mkdir(parents=True, exist_ok=True); o.write_bytes(s.files[src_png])
                item_frag[newkey] = {"textures": re.sub(r"\.(png|tga)$", "", rp)}
        dn = c.get("minecraft:display_name", {}); name = dn.get("value") if isinstance(dn, dict) else None
        if name and re.match(r"^[a-z_.]+\.name$", name): name = lang_of(s).get(name) or name      # a lang key -> the add-on's own English name
        if not name or re.match(r"^[a-z_.]+\.name$", name or ""): name = lang_of(s).get(f"item.{old}.name") or old.split(":")[1].replace("_", " ").title()
        name = re.sub(r"\s*§.\(.*?\)§r", "", name).replace("§r", "").replace("[WWA]", "").strip()
        name = re.sub(r"_", " ", name).strip(); name = name[:1].upper() + name[1:]
        js, notes = modern_item(d, new, newkey if newkey in item_frag else key, name)   # no own texture: the key is a vanilla icon
        o = STAGE / "BP" / f"items/pw_menagerie/{low}/{old.split(':')[1]}.json"; o.parent.mkdir(parents=True, exist_ok=True)
        o.write_text(json.dumps(js, indent=1)); item_lang.append(f"item.{new}.name={name}")
        if newkey not in item_frag: notes.append(f"vanilla icon '{key}' kept")
        item_notes[new] = notes
    report["items"] = item_notes
    # write
    DEADS = {c["new"]: set(c["dead_refs"]) for c in report["creatures"]}
    PORTED = {v for mm in idmap.values() for v in mm.values() if isinstance(v, str) and v.startswith(("animation.pwm.", "controller.animation.pwm."))}
    n = 0
    for (tag, f), (side, rp) in plan.items():
        out = STAGE / ("RP" if side == "RP" else "BP") / rp
        out.parent.mkdir(parents=True, exist_ok=True)
        b = srcs[tag].files[f]
        if f.endswith(".json"):
            # parsed + re-written (some add-ons \u-escape every character, so text replacement would miss them); keys AND values renamed
            d = srcs[tag].json.get(f)
            if d is None: out.write_bytes(b); n += 1; continue
            d2 = rename(d, idmap[tag])
            if rp.startswith("loot_tables/"): d2 = clean_loot(d2, idmap[tag], report)
            if rp.startswith("entities/"):
                d2 = fix_schema(fix_leftovers(scrub_medals(d2, report), idmap[tag], report), report)
                d2, made = convert_events(d2, report, m=idmap[tag])
                if made and tuple(int(x) for x in str(d2.get("format_version", "1.0.0")).split(".")[:3]) < (1, 20, 0):
                    d2["format_version"] = "1.20.0"; report["format_raised"] = report.get("format_raised", 0) + 1   # queue_command needs it
            if rp.startswith("spawn_rules/"): d2 = fix_spawn_ground(d2, report)
            if side == "RP": d2 = fix_molang_text(d2, report)
            if rp.startswith("entity/") and "minecraft:client_entity" in d2:
                d2 = fix_client(d2, DEADS.get(d2["minecraft:client_entity"]["description"].get("identifier"), set()), report, PORTED)
                desc = d2["minecraft:client_entity"]["description"]
                mats = desc.get("materials") or {}
                for k_, v_ in list(mats.items()):
                    if v_ in MAT[tag]["alias"]: mats[k_] = MAT[tag]["alias"][v_]
                    elif v_ in MAT[tag]["custom"]: mats[k_] = MAT[tag]["custom"][v_][0]; MAT_USED[MAT[tag]["custom"][v_][0]] = MAT[tag]["custom"][v_][1]
                egg = desc.get("spawn_egg")
                if isinstance(egg, dict) and egg.get("texture"):
                    desc["spawn_egg"] = egg_colours(srcs[tag], desc, {v: k for k, v in idmap[tag].items()}); report["eggs_recoloured"] = report.get("eggs_recoloured", 0) + 1
                if isinstance(egg, dict) and isinstance(egg.get("base_color"), str) and len(egg["base_color"]) not in (4, 7):
                    egg["base_color"] = egg["base_color"][:7]; report["egg_colour_typos"] = report.get("egg_colour_typos", 0) + 1
            out.write_text(json.dumps(d2, indent=1, ensure_ascii=False), encoding="utf-8")
        else:
            out.write_bytes(b)
        n += 1
    # pack-level fragments (merged into the target pack's own files by the wave build): sounds, sound definitions + .ogg, names, eggs
    frag = STAGE / "RP/_fragments"; frag.mkdir(parents=True, exist_ok=True)
    sounds, sdefs, lang, itex, oggs = {}, {}, [], {}, 0
    for tag, old, new in jobs:
        s = srcs[tag]; low = tag.lower()
        ent = None; defs = {}
        for n_, d in s.json.items():
            if not isinstance(d, dict): continue
            if n_.endswith("sounds.json"): ent = ent or (d.get("entity_sounds", {}).get("entities", {}).get(old))
            if n_.endswith("sound_definitions.json"): defs.update(d.get("sound_definitions", d))
        if ent:
            ent = json.loads(json.dumps(ent))
            for bad in BAD_SOUND_EVENTS & set(ent.get("events") or {}):
                ent["events"].pop(bad); report["bad_sound_events"] = report.get("bad_sound_events", 0) + 1
            for ev, name in list((ent.get("events") or {}).items()):
                nm = name.get("sound") if isinstance(name, dict) else name
                if nm in defs:                                       # the add-on's own sound: copy it under our prefix + its files
                    newnm = f"pwm.{low}.{nm}"; sd = json.loads(json.dumps(defs[nm]))
                    keep_s = [snd for snd in sd.get("sounds", []) if s.ogg.get(str(snd.get("name") if isinstance(snd, dict) else snd).lower())
                              or str(snd.get("name") if isinstance(snd, dict) else snd) in vanilla_sounds()]
                    if len(keep_s) != len(sd.get("sounds", [])):     # a file the add-on never shipped (and vanilla lacks) = a silent pick; leave it out
                        report.setdefault("sound_files_missing", []).extend(str(x.get("name") if isinstance(x, dict) else x) for x in sd["sounds"] if x not in keep_s)
                        sd["sounds"] = keep_s
                    for i, snd in enumerate(sd.get("sounds", [])):
                        path = snd.get("name") if isinstance(snd, dict) else snd
                        f = s.ogg.get(str(path).lower())
                        if f:
                            np_ = f"sounds/pw_menagerie/{low}/" + str(path).split("sounds/", 1)[-1]
                            (STAGE / "RP" / (np_ + ".ogg")).parent.mkdir(parents=True, exist_ok=True)
                            (STAGE / "RP" / (np_ + ".ogg")).write_bytes(s.files[f]); oggs += 1
                            if isinstance(snd, dict): snd["name"] = np_
                            else: sd["sounds"][i] = np_
                    sdefs[newnm] = sd
                    if isinstance(name, dict): name["sound"] = newnm
                    else: ent["events"][ev] = newnm
            sounds[new] = ent
        names = {}
        for n_, b_ in s.files.items():
            if n_.endswith("en_US.lang"):
                for line in b_.decode("utf-8", "replace").splitlines():
                    if "=" in line: k, v = line.split("=", 1); names[k.strip()] = re.sub(r"\s*§.\(.*?\)§r", "", v).replace("§r", "").strip()
        nice = new.split(":")[1].rsplit("_", 1)[0].replace("_", " ").title()   # our English id names it, without the pack suffix
        lang += [f"entity.{new}.name={nice}", f"item.spawn_egg.entity.{new}.name=Spawn {nice}"]
    (frag / "sounds.json").write_text(json.dumps({"entity_sounds": {"entities": sounds}}, indent=1))
    (frag / "sound_definitions.json").write_text(json.dumps({"format_version": "1.20.20", "sound_definitions": sdefs}, indent=1))
    (frag / "en_US.lang").write_text("\n".join(lang + item_lang) + "\n", encoding="utf-8")
    (frag / "entity.material").write_text(json.dumps({"materials": {"version": "1.0.0", **{k: v for d_ in MAT_USED.values() for k, v in d_.items()}}}, indent=1))
    report["custom_materials"] = sorted(MAT_USED)
    (frag / "item_texture.json").write_text(json.dumps({"resource_pack_name": "pw_menagerie", "texture_name": "atlas.items", "texture_data": item_frag}, indent=1))
    report.update({"sound_entities": len(sounds), "sound_definitions": len(sdefs), "ogg_files": oggs, "names": len(lang) // 2})
    report["files"] = n
    (STAGE / "PORT-REPORT.json").write_text(json.dumps(report, indent=1))
    return report


if __name__ == "__main__" and len(sys.argv) == 3 and sys.argv[1] == "--jobs":
    J = json.loads(Path(sys.argv[2]).read_text())
    r = port([tuple(x) for x in J["entities"]], [tuple(x) for x in J["items"]])
    print(json.dumps({k: (v if k not in ("creatures", "items") else len(v)) for k, v in r.items()}, indent=1)); sys.exit(0)
if __name__ == "__main__":
    jobs = []
    for a in sys.argv[1:]:
        tag, rest = a.split(":", 1); old, new = rest.rsplit("=", 1); jobs.append((tag, old, new))
    r = port(jobs)
    print(json.dumps({"files": r["files"], "creatures": [(c["old"], c["new"], c["files"], len(c["dead_refs"])) for c in r["creatures"]]}, indent=1))

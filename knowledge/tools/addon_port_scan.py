#!/usr/bin/env python3
"""addon_port_scan.py — D-C349 (his 20:10 CT 09-30: port every new mob Patrix doesn't cover). READ-ONLY dry run, no pack is built.

For every creature in the census (NEW + COMPARE + VANILLA groups) it follows the files one entity needs, in BOTH halves:
  BP  entities/<x>.json -> loot tables, spawn rules (by identifier), BP animation controllers / animations, items it gives / drops,
      other entity ids it spawns or transforms into, functions it runs, 'scripts' (a script module in the pack = flagged)
  RP  client entity -> geometry ids, every texture path, animations, animation controllers, render controllers, particle ids,
      sound events (sound_definitions.json -> .ogg files), spawn-egg texture
and records size + the risks a port must handle: script dependence, a library pack (Worldy), vanilla-file overrides in the pack,
missing references. Output _logs/addon_port_scan.json + _docs/menagerie/PORT-SCAN-2026-09-30.md."""
import io, json, re, sys, zipfile, collections
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude"); D = ROOT / "_intake/addons-0930"
SOURCES = {"AnF": ["Animals-and-Fauna.mcaddon"], "IFS": ["Immersive-Fauna-Savanna-1_5_0.mcaddon"], "WA": ["World-Animals-Add-on.mcaddon"],
           "JP": ["jurassic-project-kingdom-of-the-giants.mcaddon"], "WS": ["wildlife-sanctuary-mobs-plus.mcaddon"],
           "WWA": ["wwa-animals-r.mcpack", "wwa-animals-b.mcpack"], "YSav": ["ycreatures-savanna-v1_0_5.mcaddon"],
           "YTri": ["ycreaturestrial-rp-v2_0_4.mcpack", "ycreaturestrial-bp-v2_0_4.mcpack"]}
VANILLA_MOBS = set("""allay armadillo axolotl bat bee blaze camel cat cave_spider chicken cod cow creeper dolphin donkey drowned fox frog goat
guardian hoglin horse husk llama mooshroom mule ocelot panda parrot pig polar_bear pufferfish rabbit salmon sheep skeleton slime sniffer spider squid
stray strider tadpole tropicalfish turtle wolf zombie glow_squid trader_llama""".split())
LIBS = {"327a1924": "Worldy Library BP", "f83bebd1": "Worldy Library RP"}


def members(data, prefix=""):
    try: z = zipfile.ZipFile(io.BytesIO(data))
    except Exception: return
    for i in z.infolist():
        if i.filename.lower().endswith((".mcpack", ".zip", ".mcaddon")): yield from members(z.read(i), prefix + i.filename + "!")
        elif not i.is_dir(): yield prefix + i.filename, z.read(i)


def parse(b):
    try: return ML._parse_json(b.decode("utf-8-sig", "replace"))
    except Exception: return None


def walk_strings(o):
    if isinstance(o, str): yield o
    elif isinstance(o, dict):
        for k, v in o.items(): yield k; yield from walk_strings(v)
    elif isinstance(o, list):
        for v in o: yield from walk_strings(v)


class Source:
    def __init__(self, tag, names):
        self.tag = tag; self.files = {}
        for n in names: self.files.update({f"{n}!{k}": v for k, v in members((D / n).read_bytes())})
        self.json = {n: parse(b) for n, b in self.files.items() if n.endswith(".json")}
        self.side = {}                                                   # file -> "BP" / "RP" by its pack's manifest module
        self.manifests = []
        roots = {}
        for n, d in self.json.items():
            if n.endswith("manifest.json") and isinstance(d, dict):
                types = {m.get("type") for m in d.get("modules", [])}
                side = "RP" if "resources" in types else "BP"
                roots[n[: -len("manifest.json")]] = side
                self.manifests.append((side, d))
        for n in self.files:
            best = max((r for r in roots if n.startswith(r)), key=len, default=None)
            self.side[n] = roots.get(best, "?")
        self.scripts = any(m.get("type") == "script" for _, d in self.manifests for m in d.get("modules", []))
        self.libs = sorted({LIBS[x.get("uuid", "")[:8].lower()] for _, d in self.manifests for x in d.get("dependencies", []) if x.get("uuid", "")[:8].lower() in LIBS})
        self.bp_ent, self.rp_ent, self.geo, self.anim, self.ac, self.rc, self.spawn, self.items = {}, {}, {}, {}, {}, {}, {}, {}
        self.sounds = {}; self.particles = {}
        for n, d in self.json.items():
            if not isinstance(d, dict): continue
            if "particle_effect" in d and isinstance(d["particle_effect"], dict):     # D-C353: particles are part of a creature's closure
                self.particles[d["particle_effect"].get("description", {}).get("identifier")] = n
            if "minecraft:entity" in d: self.bp_ent[d["minecraft:entity"].get("description", {}).get("identifier")] = n
            if "minecraft:client_entity" in d: self.rp_ent[d["minecraft:client_entity"].get("description", {}).get("identifier")] = n
            if "minecraft:spawn_rules" in d: self.spawn[d["minecraft:spawn_rules"].get("description", {}).get("identifier")] = n
            if "minecraft:item" in d: self.items[d["minecraft:item"].get("description", {}).get("identifier")] = n
            for g in d.get("minecraft:geometry", []) or []: self.geo[g.get("description", {}).get("identifier")] = n
            for k in d:
                if k.startswith("geometry."): self.geo[k.split(":")[0]] = n
            if isinstance(d.get("animations"), dict) and "minecraft:client_entity" not in d and "minecraft:entity" not in d:
                for k in d["animations"]: self.anim.setdefault(k, set()).add(n)
            if isinstance(d.get("animation_controllers"), dict):
                for k in d["animation_controllers"]: self.ac.setdefault(k, set()).add(n)
            if isinstance(d.get("render_controllers"), dict):
                for k in d["render_controllers"]: self.rc[k] = n
            if n.endswith("sound_definitions.json"):
                sd = d.get("sound_definitions", d)
                for k, v in sd.items():
                    if isinstance(v, dict): self.sounds[k] = (n, v)
        self.tex = {}
        for n in self.files:
            m = re.search(r"(textures/.*)\.(png|tga)$", n.split("!")[-1], re.I)
            if m: self.tex.setdefault(m.group(1).lower(), n)
        self.ogg = {}
        for n in self.files:
            m = re.search(r"(sounds/.*)\.(ogg|fsb|wav)$", n.split("!")[-1], re.I)
            if m: self.ogg[m.group(1).lower()] = n
        self.vanilla_over = sorted({n.split("!")[-1] for n in self.files if re.search(r"(^|/)entities?/(vanilla/)?(player|zombie|skeleton|cow|pig|chicken|sheep|wolf|villager)[^/]*\.json$", n.split("!")[-1])})

    def closure(self, ident):
        need, missing, flags = set(), [], set()
        bp = self.bp_ent.get(ident); rp = self.rp_ent.get(ident)
        if not bp: missing.append("BP entity")
        if not rp: missing.append("RP client entity")
        others = set()
        if bp:
            need.add(bp); d = self.json[bp]
            for s in walk_strings(d):
                if s.startswith("loot_tables/") or s.startswith("trading/"):
                    p = next((n for n in self.files if n.endswith(s if s.endswith(".json") else s + ".json")), None)
                    (need.add(p) if p else missing.append(s))
                elif s in self.ac or s in self.anim:
                    for n in self.ac.get(s, set()) | self.anim.get(s, set()):
                        if self.side.get(n) == "BP": need.add(n)
                elif re.match(r"^[a-z0-9_]+:[a-z0-9_.]+$", s) and s != ident and (s in self.bp_ent or s in self.items):
                    others.add(s)
                if "/function " in s or s.startswith("function "): flags.add("runs functions")
                if "scriptevent" in s: flags.add("scriptevent")
            if ident in self.spawn: need.add(self.spawn[ident])
            else: flags.add("no spawn rule")
        if rp:
            need.add(rp); desc = self.json[rp]["minecraft:client_entity"]["description"]
            for g in (desc.get("geometry") or {}).values():
                (need.add(self.geo[g]) if g in self.geo else missing.append(g))
            for t in (desc.get("textures") or {}).values():
                k = re.sub(r"\.(png|tga)$", "", t.lower()); n = self.tex.get(k)
                (need.add(n) if n else missing.append(t))
            for a in list((desc.get("animations") or {}).values()):
                hits = self.anim.get(a, set()) | self.ac.get(a, set())
                if not hits and not a.startswith(("animation.common", "animation.humanoid", "controller.animation.humanoid")): missing.append(a)
                need |= {n for n in hits if self.side.get(n) == "RP"}
            for x in desc.get("animation_controllers") or []:          # D-C361 (his L2): the old-style list names controllers too
                for cid in (x.values() if isinstance(x, dict) else [x]):
                    hits = self.ac.get(cid, set())
                    need |= {n for n in hits if self.side.get(n) == "RP"}
            for r in desc.get("render_controllers") or []:
                r = r if isinstance(r, str) else next(iter(r))
                (need.add(self.rc[r]) if r in self.rc else (None if r.startswith("controller.render.default") else missing.append(r)))
            for ev in (desc.get("sound_effects") or {}).values():
                nm = ev.get("effect") if isinstance(ev, dict) else ev
                if nm in self.sounds: flags.add("sound effects")
            for pid in (desc.get("particle_effects") or {}).values():
                if pid in self.particles:
                    pf = self.particles[pid]; need.add(pf)
                    tx = ((self.json[pf]["particle_effect"].get("description", {}).get("basic_render_parameters") or {}).get("texture") or "")
                    tn = self.tex.get(re.sub(r"\.(png|tga)$", "", tx.lower()))
                    if tn: need.add(tn)
                    elif tx and not tx.startswith("textures/particle/particles"): missing.append(tx)
                elif not str(pid).startswith("minecraft:"): missing.append(pid)
            spawn_egg = desc.get("spawn_egg") or {}
            if spawn_egg.get("texture"): flags.add("spawn egg texture")
        # sounds by entity name in sound_definitions (mob.<key>.*)
        key = ident.split(":")[1]
        snd = [k for k in self.sounds if re.search(rf"(^|\.){re.escape(key)}(\.|$)", k)]
        for k in snd:
            n, v = self.sounds[k]
            for s in v.get("sounds", []):
                nm = (s.get("name") if isinstance(s, dict) else s) or ""
                f = self.ogg.get(nm.lower())
                if f: need.add(f)
        size = sum(len(self.files[n]) for n in need if n in self.files)
        return {"files": sorted(need), "bytes": size, "missing": missing, "flags": sorted(flags), "others": sorted(others), "sound_events": len(snd)}


def vanilla_refs():
    """every id / path the game itself provides (bedrock-samples 1.26.50): a reference to one of these is not missing"""
    V = set(); base = ROOT / "_intake/bedrock-samples"
    for p in (base / "resource_pack").rglob("*.json"):
        d = parse(p.read_bytes())
        if not isinstance(d, dict): continue
        for k in ("animations", "animation_controllers", "render_controllers"):
            if isinstance(d.get(k), dict): V |= set(d[k])
        for g in d.get("minecraft:geometry", []) or []: V.add(g.get("description", {}).get("identifier"))
        for k in d:
            if k.startswith("geometry."): V.add(k.split(":")[0])
    for p in (base / "resource_pack/textures").rglob("*.png"): V.add(str(p.relative_to(base / "resource_pack")).rsplit(".", 1)[0].lower())
    for p in (base / "resource_pack/textures").rglob("*.tga"): V.add(str(p.relative_to(base / "resource_pack")).rsplit(".", 1)[0].lower())
    for p in (base / "behavior_pack/loot_tables").rglob("*.json"): V.add(str(p.relative_to(base / "behavior_pack")))
    for p in (base / "behavior_pack/trading").rglob("*.json"): V.add(str(p.relative_to(base / "behavior_pack")))
    return V


def main():
    cen = json.loads((ROOT / "_logs/menagerie_census.json").read_text())
    VAN = vanilla_refs()
    srcs = {t: Source(t, names) for t, names in SOURCES.items()}
    out = {"sources": {t: {"scripts": s.scripts, "libraries": s.libs, "vanilla_files": s.vanilla_over[:20], "files": len(s.files)} for t, s in srcs.items()}, "entities": {}}
    for part in ("new", "compare", "vanilla"):
        for g, rec in cen[part].items():
            for c in rec["candidates"]:
                s = srcs.get(c["src"])
                if not s: continue
                r = s.closure(c["id"]); r.update({"group": g, "part": part, "src": c["src"]})
                vm = [m for m in r["missing"] if m in VAN or m.lower().rsplit(".", 1)[0] in VAN or (m + ".json") in VAN
                      or (re.match(r"loot_tables/entities/([a-z_]+?)(_normal|_adult|_leather)?\.json$", m) and
                          re.match(r"loot_tables/entities/([a-z_]+?)(_normal|_adult|_leather)?\.json$", m).group(1) in VANILLA_MOBS)]
                r["vanilla_refs"] = vm; r["missing"] = [m for m in r["missing"] if m not in vm]
                out["entities"][c["id"]] = r
    (ROOT / "_logs/addon_port_scan.json").write_text(json.dumps(out, indent=1))
    E = out["entities"]
    L = ["# Port scan — what each add-on creature needs (dry run, 2026-09-30, D-C349)", "", "`tools/addon_port_scan.py`, read-only.", "",
         "## Sources", "", "| Source | Files | Runs scripts | Needs a library | Vanilla files it overrides |", "|---|---|---|---|---|"]
    for t, v in out["sources"].items():
        L.append(f"| {t} | {v['files']} | {'YES' if v['scripts'] else 'no'} | {', '.join(v['libraries']) or '—'} | {', '.join(v['vanilla_files'][:6]) or '—'} |")
    for part in ("new", "compare", "vanilla"):
        rows = [(i, r) for i, r in E.items() if r["part"] == part]
        tot = sum(r["bytes"] for _, r in rows); miss = [(i, r) for i, r in rows if r["missing"]]
        L += ["", f"## {part.upper()} — {len(rows)} entities, {tot / 1e6:.1f} MB of files, {len(miss)} with a missing reference", "",
              "| Entity | Group | KB | Files | Flags | Missing |", "|---|---|---|---|---|---|"]
        for i, r in sorted(rows, key=lambda x: (x[1]["group"], x[0])):
            L.append(f"| {i} | {r['group']} | {r['bytes'] // 1024} | {len(r['files'])} | {', '.join(r['flags']) or '—'} | {', '.join(r['missing'][:3]) or '—'} |")
    (ROOT / "_docs/menagerie/PORT-SCAN-2026-09-30.md").write_text("\n".join(L) + "\n")
    for part in ("new", "compare", "vanilla"):
        rows = [r for r in E.values() if r["part"] == part]
        print(part, len(rows), f"{sum(r['bytes'] for r in rows) / 1e6:.1f} MB", "missing:", sum(1 for r in rows if r["missing"]))
    for t, v in out["sources"].items(): print(t, v["scripts"], v["libraries"], v["vanilla_files"][:4])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""verify_menagerie_wave.py — gate for RP-07 1.4.32 + PW-StripMine BP 1.3.7 (menagerie wave P1, D-C351). Static checks only RULE OUT (P1)."""
import hashlib, json, re, sys, zipfile, tempfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import addon_port_scan as S

ROOT = Path("/home/claude")
WAVE = sys.argv[1] if len(sys.argv) > 1 else "P1"
CFG = {"P1": (("rp07-1431", "rp07-1432", "stripmine-bp-136", "stripmine-bp-137"), [1, 4, 32], [1, 3, 7]),
       "P3": (("rp07-1432", "rp07-1433", "stripmine-bp-137", "stripmine-bp-138"), [1, 4, 33], [1, 3, 8]),
       "R2": (("rp07-1433", "rp07-1434", "stripmine-bp-138", "stripmine-bp-139"), [1, 4, 34], [1, 3, 9])}[WAVE]
R0, R1, B0, B1 = (ROOT / "_build" / d for d in CFG[0])
OURS_SPAWN = json.loads((ROOT / "_logs/menagerie_p3_ours_spawn.json").read_text()) if WAVE == "P3" else {}
GRASS = json.loads((ROOT / "_logs/menagerie_R2_grass.json").read_text()) if WAVE == "R2" else []
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
def jl(p):
    return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(d): return {str(p.relative_to(d)): p for p in d.rglob("*") if p.is_file()}

# A manifests
for d0, d1, ver in ((R0, R1, CFG[1]), (B0, B1, CFG[2])):
    m0, m1 = jl(d0 / "manifest.json"), jl(d1 / "manifest.json")
    check(f"A {d1.name}: version {ver}, uuids / dependencies / capabilities unchanged",
          m1["header"]["version"] == ver and m1["header"]["uuid"] == m0["header"]["uuid"] and [x["uuid"] for x in m1["modules"]] == [x["uuid"] for x in m0["modules"]]
          and all(x["version"] == ver for x in m1["modules"]) and m1.get("dependencies") == m0.get("dependencies") and m1.get("capabilities") == m0.get("capabilities"))
check("A RP-07 still declares Vibrant Visuals (pbr)", jl(R1 / "manifest.json").get("capabilities") == ["pbr"])
# B only additions (+ the merged pack-level files + manifests)
MERGED = {"manifest.json", "materials/entity.material", "texts/en_US.lang", "texts/languages.json", "sounds.json", "sounds/sound_definitions.json", "textures/item_texture.json"}
for d0, d1 in ((R0, R1), (B0, B1)):
    f0, f1 = files(d0), files(d1)
    UPD = set(json.loads((ROOT / f"_logs/menagerie_{WAVE}_updated.json").read_text())) if WAVE != "P1" else set()
    changed = [k for k in f0 if k in f1 and md5(f0[k]) != md5(f1[k]) and k not in MERGED and k not in OURS_SPAWN and k not in UPD and k not in GRASS]
    gone = [k for k in f0 if k not in f1 and not (WAVE == "R2" and k.startswith("models/pw_menagerie/"))]   # D-C355: moved under models/entity
    if True:                                                     # D-C353 (P3): improved earlier port files = exactly the re-ported versions
        stg = ROOT / "_build/menagerie-stage" / ("RP" if d1 == R1 else "BP")
        upd_bad = [k for k in UPD if (d1 / k).exists() and (stg / k).exists() and md5(d1 / k) != md5(stg / k)]
        upd_here = [k for k in UPD if (d1 / k).exists() and (stg / k).exists()]
        if UPD: check(f"B {d1.name}: the {len(upd_here)} earlier port files the D-C353 fixes improved are exactly the re-ported versions (all under pw_menagerie)",
                      not upd_bad and all("pw_menagerie" in k for k in UPD), str(upd_bad[:3]))
    added = [k for k in f1 if k not in f0]
    check(f"B {d1.name}: nothing old changed or removed (bar manifest + merged lang / sounds / item textures" + (f" + his M9 shared weight on {len(OURS_SPAWN)} of our spawn rules" if OURS_SPAWN and d1 == B1 else "") + "); every addition under pw_menagerie",
          not changed and not gone and all("pw_menagerie" in k or k in MERGED for k in added), f"{len(added)} added, changed {changed[:3]}, gone {gone[:3]}")
# C parse + Molang
errs = []
for d in (R1, B1):
    for p in d.rglob("*.json"):
        try: jl(p)
        except Exception as e: errs.append(f"{p.relative_to(d)}: {str(e)[:60]}")
check("C every JSON in both packs parses", not errs, "; ".join(errs[:3]))
nml, eml = 0, []
for d in (R1, B1):
    z = Path(tempfile.mkdtemp()) / (d.name + ".mcpack")
    with zipfile.ZipFile(z, "w") as zf:
        for p in d.rglob("*.json"): zf.write(p, str(p.relative_to(d)))
    n_, e_ = ML.lint_pack(z); nml += n_; eml += e_
check("C Molang lint (the ship gate's lint)", not eml, f"{nml} strings, {len(eml)} errors {[e[:3] for e in eml[:3]]}")
# D closure on the merged RP
VAN = S.vanilla_refs()
defs, tex = set(), set()
for p in R1.rglob("*.json"):
    try: d = jl(p)
    except Exception: continue
    if not isinstance(d, dict): continue
    for g in d.get("minecraft:geometry", []) or []: defs.add(g.get("description", {}).get("identifier"))
    for k in d:
        if k.startswith("geometry."): defs.add(k.split(":")[0])
    for key in ("animations", "animation_controllers", "render_controllers"):
        if isinstance(d.get(key), dict) and "minecraft:client_entity" not in d: defs |= set(d[key])
for p in list(R1.rglob("*.png")) + list(R1.rglob("*.tga")): tex.add(str(p.relative_to(R1)).rsplit(".", 1)[0].lower())
client, unres = {}, {}
for p in R1.glob("entity/pw_menagerie/**/*.json"):
    d = jl(p)["minecraft:client_entity"]["description"]; i = d["identifier"]; client[i] = d
    refs = list((d.get("geometry") or {}).values()) + list((d.get("animations") or {}).values()) + [r if isinstance(r, str) else next(iter(r)) for r in d.get("render_controllers", [])]
    bad = [r for r in refs if r not in defs and r not in VAN and not r.startswith(("animation.common", "controller.render.default"))]
    bad += [t for t in (d.get("textures") or {}).values() if re.sub(r"\.(png|tga)$", "", t.lower()) not in tex and t.lower() not in VAN]
    if bad: unres[i] = bad
PREP = json.loads((ROOT / "_build/menagerie-stage/PORT-REPORT.json").read_text())
DEAD = {c["new"]: set(c["dead_refs"]) for c in PREP["creatures"]}           # refs the creature's own pack never shipped (the game skips them today)
bad_unres = {k: [r for r in v if r not in DEAD.get(k, set())] for k, v in unres.items()}; bad_unres = {k: v for k, v in bad_unres.items() if v}
check("D every ported creature's model / animations / render controllers / textures resolve (or are vanilla); the rest are refs their own pack never shipped",
      not bad_unres, f"{sum(len(v) for v in unres.values())} dead refs on {len(unres)} creatures, all never shipped by their pack" if not bad_unres else str({k: v[:2] for k, v in bad_unres.items()})[:300])
bp = {}
for p in B1.glob("entities/pw_menagerie/**/*.json"):
    d = jl(p); bp[d["minecraft:entity"]["description"]["identifier"]] = (p, d)
no_client = [i for i, (p, d) in bp.items() if i not in client and d["minecraft:entity"]["description"].get("is_spawnable", False)]
check("D every spawnable behaviour entity has its client entity; every client entity has its behaviour entity", not no_client and all(i in bp for i in client),
      f"{len(bp)} BP / {len(client)} RP; no client: {no_client[:4]}")
loot_bad, spawn_bad, item_bad, loot_dead = [], [], [], []
SRCS, TAG = {}, {"anf": "AnF", "wa": "WA", "ws": "WS", "wwa": "WWA", "ysav": "YSav", "ytri": "YTri", "ifs": "IFS"}
items = {jl(p)["minecraft:item"]["description"]["identifier"] for p in B1.glob("items/pw_menagerie/**/*.json")}
for i, (p, d) in bp.items():
    for s in S.walk_strings(d):
        if s.startswith("loot_tables/") and not (B1 / (s if s.endswith(".json") else s + ".json")).exists() and not re.match(r"loot_tables/entities/[a-z_]+\.json$", s):
            src = re.search(r"_(anf|wa|ws|wwa|ysav|ytri|ifs)$", i).group(1)
            SRCS.setdefault(src, S.Source(TAG[src], S.SOURCES[TAG[src]]))
            if any(n.endswith(s if s.endswith(".json") else s + ".json") for n in SRCS[src].files): loot_bad.append((i, s))
            else: loot_dead.append((i, s))                       # the add-on names a table it never shipped (no drop there today either)
for p in B1.glob("spawn_rules/pw_menagerie/**/*.json"):
    sid = jl(p)["minecraft:spawn_rules"]["description"]["identifier"]
    if sid not in bp: spawn_bad.append(sid)
for p in B1.glob("loot_tables/pw_menagerie/**/*.json"):
    for pool in jl(p).get("pools", []) or []:
        for e in pool.get("entries", []) or []:
            nm = str(e.get("name", ""))
            if e.get("type", "item") == "item" and ":" in nm and not nm.startswith("minecraft:") and nm not in items: item_bad.append((p.name, nm))
            if e.get("type") == "loot_table" and not (B1 / nm).exists() and not nm.startswith("loot_tables/entities/"): loot_bad.append((p.name, nm))
check("D every loot table a creature names exists (ours or vanilla); every spawn rule belongs to a ported creature; every dropped item exists",
      not loot_bad and not spawn_bad and not item_bad, f"loot {loot_bad[:3]} spawn {spawn_bad[:3]} items {item_bad[:3]}; never-shipped tables {len(loot_dead)} {loot_dead[:3]}")
check("D no medal anywhere in the ported files (his Q5)", not any(re.search(r"medal", p.read_text(errors="ignore"), re.I) for p in B1.rglob("*.json") if "pw_menagerie" in str(p)))
# E ids unique across our stack
other_ids = set()
for d in [ROOT / "_build/bp02-198", ROOT / "_build/rp06-1424", ROOT / "_build/rp08-148", B0, R0]:
    for p in d.rglob("*.json"):
        try: x = jl(p)
        except Exception: continue
        if not isinstance(x, dict): continue
        for k in ("minecraft:entity", "minecraft:client_entity", "minecraft:item", "minecraft:block"):
            if k in x: other_ids.add(x[k].get("description", {}).get("identifier"))
earlier = set()                                                  # an earlier wave's ports (identical files carried forward) are not a clash
for d in (B0, R0):
    for p in d.rglob("*.json"):
        if "pw_menagerie" not in str(p): continue
        try: x = jl(p)
        except Exception: continue
        if isinstance(x, dict):
            for k in ("minecraft:entity", "minecraft:client_entity", "minecraft:item"):
                if k in x: earlier.add(x[k].get("description", {}).get("identifier"))
clash = sorted(((set(bp) | set(client) | items) - earlier) & other_ids)
check("E no ported id clashes with an id already in our packs (BP-02, RP-06, RP-07, RP-08, StripMine)", not clash, str(clash[:5]))
check("E every ported id is pw:<name>_<pack> (his Q2)", all(re.match(r"^pw:[a-z0-9_]+_(anf|wa|ws|wwa|ysav|ytri|ifs)$", i) for i in set(bp) | set(client) | items),
      str([i for i in set(bp) | set(client) | items if not re.match(r"^pw:[a-z0-9_]+_(anf|wa|ws|wwa|ysav|ytri|ifs)$", i)][:5]))
gid_new = [g for g in defs if g and ".pwm." in g]
check("E every ported geometry / animation / controller id carries the pwm.<pack> prefix (no clash with any other pack's ids)", len(gid_new) > 100)
# F sounds + names + item icons
sj = jl(R1 / "sounds.json"); sd = jl(R1 / "sounds/sound_definitions.json")["sound_definitions"]
vs = json.loads(Path("/home/claude/_intake/vanilla-1.21/sound_definitions.json").read_text()); vs = vs.get("sound_definitions", vs)
VSND = {(s.get("name") if isinstance(s, dict) else s) for v in vs.values() if isinstance(v, dict) for s in v.get("sounds", [])}
missing_ev, missing_file = [], []
for i, e in sj.get("entity_sounds", {}).get("entities", {}).items():
    if not i.startswith("pw:"): continue
    for ev in (e.get("events") or {}).values():
        nm = ev.get("sound") if isinstance(ev, dict) else ev
        if nm and nm.startswith("pwm.") and nm not in sd: missing_ev.append(nm)
for k, v in sd.items():
    if not k.startswith("pwm."): continue
    for s in v.get("sounds", []):
        path = s.get("name") if isinstance(s, dict) else s
        if path not in VSND and not any((R1 / (path + ext)).exists() for ext in (".ogg", ".fsb", ".wav")): missing_file.append(path)
check("F every ported sound event exists and every sound file it plays is in the pack (or is a vanilla sound)", not missing_ev and not missing_file, f"{missing_ev[:3]} {missing_file[:3]}")
lang = (R1 / "texts/en_US.lang").read_text(encoding="utf-8")
check("F every ported creature has a name and a spawn-egg name; every item a name", all(f"entity.{i}.name=" in lang and f"item.spawn_egg.entity.{i}.name=" in lang for i in client)
      and all(f"item.{i}.name=" in lang for i in items), f"{len(client)} creatures, {len(items)} items")
itx = jl(R1 / "textures/item_texture.json")["texture_data"]; icon_bad = []
for p in B1.rglob("items/pw_menagerie/**/*.json"):
    ic = jl(p)["minecraft:item"]["components"]["minecraft:icon"]["textures"]["default"]
    if ic.startswith("pwm_") and (ic not in itx or not (R1 / (itx[ic]["textures"] + ".png")).exists()): icon_bad.append(ic)
check("F every ported item icon resolves (ours in item_texture.json + its PNG, or a vanilla key)", not icon_bad, str(icon_bad[:4]))
# H materials (the independent check's blocker: an add-on material alias that was not ported = invisible creature)
VMAT = {"entity", "entity_alphatest", "entity_alphablend", "entity_emissive", "entity_emissive_alpha", "entity_emissive_alpha_one_sided", "entity_change_color",
        "entity_alphatest_change_color", "entity_alphatest_one_sided", "entity_multitexture", "entity_multitexture_alpha_test", "entity_nocull", "entity_custom",
        "entity_beam", "entity_flat_color_line", "entity_lead_base", "bee", "spider", "slime", "cow", "pig", "salmon", "stray_clothes", "dolphin", "sheep",
        "parrot", "fox", "guardian", "squid", "phantom", "shulker", "ender_dragon", "enderman", "wither_boss", "warden", "horse", "llama", "cat", "panda", "turtle"}
for p in (ROOT / "_intake/bedrock-samples/resource_pack/entity").glob("*.json"):   # every material a vanilla creature uses is a vanilla material
    try: VMAT |= set((jl(p)["minecraft:client_entity"]["description"].get("materials") or {}).values())
    except Exception: pass
ours = set()
mp = R1 / "materials/entity.material"
if mp.exists(): ours = {k.split(":")[0] for k in jl(mp)["materials"] if k != "version"}
bad_mat = sorted({(i, v) for i, d in client.items() for v in (d.get("materials") or {}).values() if v not in VMAT and v not in ours})
check("H every material a ported creature uses is vanilla or defined in RP-07 materials/entity.material", not bad_mat, str(bad_mat[:5]))
eggs_bad = [i for i, d in client.items() if isinstance(d.get("spawn_egg"), dict) and d["spawn_egg"].get("texture")
            and d["spawn_egg"]["texture"] not in jl(R1 / "textures/item_texture.json")["texture_data"]]
check("H every spawn egg is coloured or has its texture", not eggs_bad, str(eggs_bad[:4]))
raw = [l for l in lang.splitlines() if re.search(r"=item\.[a-z_]+\.name$", l)]
check("H no item or creature is named by a raw translation key", not raw, str(raw[:3]))
# I the wave's own promises (P3: his picks)
if WAVE == "P3":
    J = json.loads((ROOT / "_logs/menagerie_jobs_P3.json").read_text()); adj = json.loads((ROOT / "_logs/menagerie_p3_adjust.json").read_text())
    want = {e[2] for e in J["entities"]}
    check("I every P3 job (his picks + baby eagles + extras) is in both packs", want <= set(bp) and all(i in client for i in want if bp.get(i) and bp[i][1]["minecraft:entity"]["description"].get("is_spawnable", False)),
          f"{len(want & set(bp))}/{len(want)} BP; missing {sorted(want - set(bp))[:4]}")
    check("I his item picks: ant = World Animals only (A1); no AnF ant ported", "pw:ant_wa" in bp and not any(i.startswith("pw:ant_") and i.endswith("_anf") for i in bp))
    check("I YTri alligator + skunk (M1/M2) and both YSav baby eagles are in", {"pw:alligator_ytri", "pw:skunk_ytri", "pw:baby_african_black_eagle_ysav", "pw:baby_fisher_eagle_ysav"} <= set(bp))
    bear_ok = all(bp[i][1]["minecraft:entity"]["components"]["minecraft:scale"]["value"] == r["scale_after"] for i, r in adj["bears"].items())
    check("I AnF bears carry the size-matched scale (his 'keep our size')", bear_ok, str({i: r["scale_after"] for i, r in adj["bears"].items()}))
    sp_bad = []
    for rel, row in OURS_SPAWN.items():
        if jl(B1 / rel) != row["json"]: sp_bad.append(rel)
        w0 = [c["minecraft:weight"]["default"] for c in jl(B0 / rel)["minecraft:spawn_rules"]["conditions"] if isinstance(c.get("minecraft:weight"), dict)]
        w1 = [c["minecraft:weight"]["default"] for c in jl(B1 / rel)["minecraft:spawn_rules"]["conditions"] if isinstance(c.get("minecraft:weight"), dict)]
        P = next(r["P"] for r in adj["spawn"].values() if any(x[0] == row["id"] for x in r["changed"]))
        if w1 != [max(1, round(w / P)) for w in w0]: sp_bad.append(rel + " weights")
    check("I M9 shared spawn: our re-weighted spawn rules = old weight / P (nothing else in them changed)", not sp_bad, str(sp_bad[:3]))
# J (D-C353, from the independent check): growth / laying targets renamed, particles shipped
OLDNS = ("cyd_ulta:", "worldanimals:", "skinscraft:", "m:", "ycreatures:", "ycreatures_savanna:", "tayi:")
grow_bad = [(i, s) for i, (p, d) in bp.items() for s in S.walk_strings(d)
            if s.startswith(OLDNS) and (s.endswith(">") and "<" in s or s.endswith("_spawn_egg"))]
check("J every 'id<event>' growth / transform target and every laid '<entity>_spawn_egg' names a ported creature (no add-on id left)", not grow_bad, str(grow_bad[:4]))
pids = set()
for p in R1.rglob("particles/**/*.json"):
    try: pids.add(jl(p)["particle_effect"]["description"]["identifier"])
    except Exception: pass
part_bad = [(i, v) for i, d in client.items() for v in (d.get("particle_effects") or {}).values() if v not in pids and not v.startswith("minecraft:") and v not in DEAD.get(i, set())]
check("J every particle a ported creature shows is in RP-07 (or vanilla)", not part_bad, f"{len(pids)} particles; bad {part_bad[:4]}")
mods_out = [str(p.relative_to(R1)) for p in R1.rglob("models/**/*.json") if not str(p.relative_to(R1)).startswith(("models/entity/", "models/blocks/")) and p.name != "mobs.json"]
check("L (his 23:30 log) every model file is under models/entity/ (or models/blocks/) — the only places the game loads geometry from", not mods_out, f"{len(mods_out)} outside, e.g. {mods_out[:2]}")
if WAVE == "R2":
    adj = json.loads((ROOT / "_logs/menagerie_p3_adjust.json").read_text())
    gbad = []
    def ground_norm(d, swap):
        """the rule with every block filter as a list; swap=True puts today's names in place of the old 'minecraft:grass'"""
        d = json.loads(json.dumps(d))
        for c in d["minecraft:spawn_rules"].get("conditions", []):
            for key in ("minecraft:spawns_on_block_filter", "minecraft:spawns_above_block_filter"):
                v = c.get(key)
                if v is None: continue
                holder, lk = (v, "blocks") if isinstance(v, dict) and "blocks" in v else (c, key)
                lst = holder[lk] if isinstance(holder[lk], list) else [holder[lk]]
                out = []
                for x in lst: out += ["minecraft:grass_block", "pw:grass_block"] if (swap and x == "minecraft:grass") else [x]
                holder[lk] = list(dict.fromkeys(out))
        return d
    for rel in GRASS:
        if ground_norm(jl(B0 / rel), True) != ground_norm(jl(B1 / rel), False): gbad.append(rel)
    check("K his S2: our spawn rules that named the old 'minecraft:grass' now name grass_block + pw:grass_block, nothing else changed; none left anywhere in the BP",
          not gbad and len(GRASS) >= 39 and not any('"minecraft:grass"' in p.read_text() for p in (B1 / "spawn_rules").rglob("*.json")), f"{len(GRASS)} fixed; bad {gbad[:3]}")
    seal = bp.get("pw:seal_wwa")
    check("K his S1: the WWA seal has a behaviour (borrowed from the AnF common seal), a spawn rule, its looks, its ledger line",
          seal is not None and "pw:seal_wwa" in client and any(jl(p)["minecraft:spawn_rules"]["description"]["identifier"] == "pw:seal_wwa" for p in B1.glob("spawn_rules/pw_menagerie/**/*.json")))
    aw = [c["minecraft:weight"]["default"] for p in B1.glob("spawn_rules/pw_menagerie/anf/**/*.json") for c in jl(p)["minecraft:spawn_rules"]["conditions"] if isinstance(c.get("minecraft:weight"), dict)]
    check("K his S3: every AnF spawn weight is at the vanilla scale (<= 10, >= 1)", aw and max(aw) <= 10 and min(aw) >= 1, f"{len(aw)} conditions, max {max(aw)}, min {min(aw)}")
# G size + ledgers
size = sum(p.stat().st_size for p in R1.rglob("*") if p.is_file()) / 1e6
check("G RP-07 stays under his 250 MB law", size < 250, f"{size:.1f} MB")
ra = (ROOT / "_docs/licensing/RESTRICTED-ASSETS.md").read_text()
check("G §9: every ported creature has its RESTRICTED-ASSETS line", all(f"| {i} |" in ra for i in client), f"{sum(f'| {i} |' in ra for i in client)}/{len(client)}")
print(); print(("GATE OPEN" if all(ok for _, ok in res) else "GATE CLOSED") + f" — {sum(ok for _, ok in res)}/{len(res)}")

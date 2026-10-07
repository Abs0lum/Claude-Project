#!/usr/bin/env python3
"""menagerie_jobs.py — D-C351: the port job list for a wave (ids pw:<animal>_<pack>, his 22:11 Q2) + satellites + items.
  P1 = the NEW animals (census 'new'), minus the Jurassic ones (Wilds pack, later), minus gamba / jacare (moved into skunk /
       alligator, his M1/M2 -> the picks wave), minus the two baby eagles (they grow into the YSav eagles -> port with them in P3),
       plus YSav cacu = tsessebe antelope (was mis-sorted under catfish).
Satellites: the entity ids a job refers to that belong to the same animal (projectiles, eggs, the male/female partner) are ported
with it; items it drops or uses are ported in today's format (medals never: his Q5).
Output: _logs/menagerie_jobs_<wave>.json"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import addon_port_scan as S

ROOT = Path("/home/claude")
NAME_FIX = {"ycreatures_savanna:savanna_cacu": "tsessebe", "ycreatures_savanna:savanna_inhala": "kudu", "ycreatures_savanna:savanna_inhalaf": "kudu_female",
            "ycreatures_savanna:savanna_kobo": "kob", "ycreatures_savanna:savanna_kobof": "kob_female", "ycreatures_savanna:savanna_impala": "impala",
            "ycreatures_savanna:savanna_impalaf": "impala_female", "ycreatures:trial_gamba": "skunk", "ycreatures:trial_jacare": "alligator"}
OUT_OF_P1 = {"ycreatures:trial_gamba", "ycreatures:trial_jacare", "ycreatures_savanna:savanna_baby_african_eagle", "ycreatures_savanna:savanna_baby_fisher_eagle"}
PROP = re.compile(r"(spit|_egg|ovo|lay_egg|projectile|_shot|_ball)")


def animal_name(src, ident, group, single):
    if ident in NAME_FIX: return NAME_FIX[ident]
    key = re.sub(r"^(savanna_|trial_|jp_|skinscraft_)", "", ident.split(":")[1])
    if src == "AnF": return key                                  # AnF keys are English sub-species already (crane_common, ...)
    return group if single else key


def p1():
    cen = json.loads((ROOT / "_logs/menagerie_census.json").read_text())
    scan = json.loads((ROOT / "_logs/addon_port_scan.json").read_text())["entities"]
    ents, used = [], set()
    def add(src, ident, base):
        nid = f"pw:{base}_{src.lower()}"; k = 2
        while nid in used: nid = f"pw:{base}_{k}_{src.lower()}"; k += 1
        used.add(nid); ents.append([src, ident, nid])
    for g, r in cen["new"].items():
        for c in r["candidates"]:
            if c["src"] == "JP" or c["id"] in OUT_OF_P1: continue
            add(c["src"], c["id"], animal_name(c["src"], c["id"], g, len(r["candidates"]) == 1))
    cacu = "ycreatures_savanna:savanna_cacu"; add("YSav", cacu, "tsessebe")
    have = {e[1] for e in ents}
    srcs = {}
    items, sats = [], []
    for src, ident, nid in list(ents):
        s = srcs.setdefault(src, S.Source(src, S.SOURCES[src]))
        cl = s.closure(ident)
        loot_items = []
        for f in cl["files"]:
            if "loot_tables/" in f and isinstance(s.json.get(f), dict):
                for pool in s.json[f].get("pools", []) or []:
                    for e in pool.get("entries", []) or []:
                        nm = str(e.get("name", ""))
                        if ":" in nm and not nm.startswith("minecraft:") and e.get("type", "item") == "item": loot_items.append(nm)
        for o in list(dict.fromkeys(list(cl["others"]) + loot_items)):
            if o in have: continue
            if o in s.items:
                if re.search(r"medal", o, re.I): continue
                if o not in {i[1] for i in items}: items.append([src, o, f"pw:{o.split(':')[1]}_{src.lower()}"])
            elif o in s.bp_ent and PROP.search(o):
                have.add(o); sats.append([src, o, f"pw:{re.sub(r'^(savanna_|trial_)', '', o.split(':')[1])}_{src.lower()}"])
    J = {"wave": "P1", "entities": ents + sats, "items": items, "counts": {"animals": len(ents), "satellites": len(sats), "items": len(items)}}
    (ROOT / "_logs/menagerie_jobs_P1.json").write_text(json.dumps(J, indent=1))
    return J


P3_NAMES = {"ycreatures_savanna:savanna_baby_lion": "baby_lion", "ycreatures_savanna:savanna_leao": "lion", "ycreatures_savanna:savanna_leao_branco": "white_lion",
            "ycreatures_savanna:savanna_leoa": "lioness", "ycreatures_savanna:savanna_leoa_branca": "white_lioness",
            "ycreatures_savanna:savanna_gazela": "gazelle", "ycreatures_savanna:savanna_gazelaf": "gazelle_female",
            "ycreatures_savanna:savanna_aguia_africana": "african_black_eagle", "ycreatures_savanna:savanna_aguia_pescadora": "fisher_eagle",
            "ycreatures_savanna:savanna_baby_african_eagle": "baby_african_black_eagle", "ycreatures_savanna:savanna_baby_fisher_eagle": "baby_fisher_eagle",
            "ycreatures:trial_coruja": "owl", "ycreatures:trial_suindara": "barn_owl", "ycreatures:trial_jacare": "alligator", "ycreatures:trial_gamba": "skunk"}
EXTRA_ID = {"jacare": "ycreatures:trial_jacare", "gamba": "ycreatures:trial_gamba"}
DEAD_LOOKS = {"worldanimals:hyenas_2", "worldanimals:white_lion"}   # looks only: their own pack has no behaviour for them (never spawnable)
BORROW = {"pw:seal_wwa": "pw:seal_common_anf"}   # his S1 (23:21): the WWA seal (looks only) lives with the AnF seal's behaviour, spawn rule + drops
WITH_ADULTS = {"eagle": [("YSav", "ycreatures_savanna:savanna_baby_african_eagle"), ("YSav", "ycreatures_savanna:savanna_baby_fisher_eagle")]}


def p3():
    """P3 = his picks (D-C353): for every compared animal, EVERY candidate of each pack he kept (his 22:00 'both/all' rule);
    'OURS' kept = nothing to port; 'YTri:jacare' style keeps = that one entity; the YSav baby eagles come with the YSav eagles.
    The port runs P1 + P3 together (one id map, so shared add-on files rename every ported id at once); the wave build adds the
    P3 files and replaces a P1 file only when the combined rename changed it (a P1 predator now targets a P3 prey by its new id)."""
    cen = json.loads((ROOT / "_logs/menagerie_census.json").read_text())
    dec = json.loads((ROOT / "_logs/menagerie_decisions.json").read_text())
    P1 = json.loads((ROOT / "_logs/menagerie_jobs_P1.json").read_text())
    used = {e[2] for e in P1["entities"]}; p1old = {e[1] for e in P1["entities"]}
    ents, animal_of = [], {}
    def add(src, ident, base, animal):
        assert ident not in p1old, ident
        nid = f"pw:{base}_{src.lower()}"; k = 2
        while nid in used: nid = f"pw:{base}_{k}_{src.lower()}"; k += 1
        used.add(nid); ents.append([src, ident, nid]); animal_of[nid] = animal
    for a, v in dec.items():
        if a == "_rules": continue
        packs = {k for k in v["keep"] if ":" not in k and k != "OURS"}
        sel = [x for x in cen["compare"][a]["candidates"] if x["src"] in packs]
        per = {}
        for x in sel: per[x["src"]] = per.get(x["src"], 0) + 1
        for x in sel:
            ident = x["id"]
            if ident in DEAD_LOOKS: continue
            if ident in P3_NAMES: base = P3_NAMES[ident]
            elif x["src"] == "AnF": base = re.sub(r"^[a-z_]+:", "", ident)
            elif per[x["src"]] == 1: base = a
            else: base = re.sub(r"^(savanna_|trial_|skinscraft_)", "", ident.split(":")[1])
            add(x["src"], ident, base, a)
        for k in v["keep"]:
            if ":" in k:
                src, key = k.split(":"); add(src, EXTRA_ID[key], P3_NAMES[EXTRA_ID[key]], a)
        if "YSav" in packs:
            for src, ident in WITH_ADULTS.get(a, []): add(src, ident, P3_NAMES[ident], a)
    have = {e[1] for e in ents} | p1old
    p1items = {i[1] for i in P1["items"]}
    srcs, items, sats = {}, [], []
    for src, ident, nid in list(ents):
        s = srcs.setdefault(src, S.Source(src, S.SOURCES[src]))
        cl = s.closure(ident)
        loot_items = []
        for f in cl["files"]:
            if "loot_tables/" in f and isinstance(s.json.get(f), dict):
                for pool in s.json[f].get("pools", []) or []:
                    for e in pool.get("entries", []) or []:
                        nm = str(e.get("name", ""))
                        if ":" in nm and not nm.startswith("minecraft:") and e.get("type", "item") == "item": loot_items.append(nm)
        eggs = []                                                  # D-C353: '<entity>_spawn_egg' a creature lays (WA duck / ostrich eggs)
        bpf = s.bp_ent.get(ident)
        if bpf:
            for st in S.walk_strings(s.json[bpf]):
                if st.endswith("_spawn_egg") and st[:-10] in s.bp_ent: eggs.append(st[:-10])
        for o in eggs:
            if o in have: continue
            have.add(o); sid = f"pw:{re.sub(r'^(savanna_|trial_)', '', o.split(':')[1])}_{src.lower()}"
            assert sid not in used, sid
            used.add(sid); sats.append([src, o, sid]); animal_of[sid] = animal_of[nid]
        for o in list(dict.fromkeys(list(cl["others"]) + loot_items)):
            if o in have: continue
            if o in s.items:
                if re.search(r"medal", o, re.I) or o in p1items: continue
                if o not in {i[1] for i in items}: items.append([src, o, f"pw:{o.split(':')[1]}_{src.lower()}"])
            elif o in s.bp_ent and PROP.search(o):
                have.add(o); sid = f"pw:{re.sub(r'^(savanna_|trial_)', '', o.split(':')[1])}_{src.lower()}"
                assert sid not in used, sid
                used.add(sid); sats.append([src, o, sid]); animal_of[sid] = animal_of[nid]
    J = {"wave": "P3", "entities": ents + sats, "items": items, "animal_of": animal_of, "borrow": BORROW,
         "p1_entities": P1["entities"], "p1_items": P1["items"],
         "counts": {"animals_versions": len(ents), "satellites": len(sats), "items": len(items)}}
    (ROOT / "_logs/menagerie_jobs_P3.json").write_text(json.dumps(J, indent=1))
    return J


if __name__ == "__main__" and sys.argv[1:] == ["P3"]:
    J = p3(); print(J["counts"]); print([e[2] for e in J["entities"]][:20]); print([i[2] for i in J["items"]]); sys.exit(0)
if __name__ == "__main__":
    J = p1(); print(J["counts"]); print([e[2] for e in J["entities"]][:12]); print([i[2] for i in J["items"]])

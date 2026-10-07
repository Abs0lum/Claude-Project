#!/usr/bin/env python3
"""build_p20.py — the JUDGING PASS lineups for PW-TestRunner BP 0.5.8 (his P20 / P21 / P22 / BT1 rulings, 10-01):
  p20   EVERY entity in our packs (735, the 72 objects included — his P22), held in sized pens (roofed land pens / pools for
        water creatures), grouped by body plan then animal so versions of one animal stand together; name tag = name (PACK).
        Unsafe ones (they explode, wreck terrain or hurt) are NOT summoned: one step lists them with the reason.
  p21   EVERY creature x EVERY animation (his P21 = a): per creature a row of copies, each copy PLAYING one animation
        (rig `play`, re-started every 3 s), name tag = the animation's short name (shared_<kind> = a same-species candidate,
        D-C389). Long creatures / many animations spill over several steps (k / n in the title).
  bump  the MR3 / BT1 bump-map test on its own: pw:nbump x 8 (warden / dolphin / turtle / parrot, normal ON / OFF).
Reads the BUILT resource packs (their client entities name the final animations) and _docs/sizes/size_law_v2_plan.json
(drawn size -> pen size). Writes tools/testrunner_src/pw_testrunner_p20.js, _p21.js, _bump.js."""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

PACKN = {"anf": "AnF", "wa": "WA", "ws": "WS", "wwa": "WWA", "ysav": "YSav", "ytri": "YTri", "ifs": "IFS"}
WATER_PLANS = {"fish", "cetacean", "cephalopod", "jellyfish"}
UNSAFE = {
    "minecraft:tnt": "explodes", "minecraft:tnt_minecart": "explodes", "minecraft:ender_crystal": "explodes when hit",
    "minecraft:fireball": "explodes", "minecraft:small_fireball": "sets fire", "minecraft:dragon_fireball": "acid cloud",
    "minecraft:wither_skull": "explodes", "minecraft:wither_skull_dangerous": "explodes", "minecraft:lightning_bolt": "fire + damage",
    "minecraft:ender_dragon": "breaks blocks, flies off", "minecraft:wither": "explodes on spawn, breaks blocks",
    "minecraft:evocation_fang": "bites the player", "minecraft:area_effect_cloud": "invisible effect cloud",
    "minecraft:agent": "Education Edition helper", "minecraft:npc": "Education Edition NPC", "minecraft:player": "not summonable",
    "minecraft:fishing_hook": "needs a player rod", "minecraft:leash_knot": "needs a fence", "minecraft:shulker_bullet": "homing hit",
    "minecraft:llama_spit": "projectile hit", "minecraft:wind_charge_projectile": "knockback blast",
    "minecraft:breeze_wind_charge_projectile": "knockback blast", "minecraft:lingering_potion": "effect cloud",
    "minecraft:splash_potion": "breaks on spawn", "minecraft:elder_guardian_ghost": "effect only",
}


def name_of(i):
    pk = i.rsplit("_", 1)[-1] if i.startswith("pw:") else ""
    base = i.split(":", 1)[1]
    if pk in PACKN:
        base = base[: -len(pk) - 1]
        tag = PACKN[pk]
    else:
        tag = "OURS" if i.startswith("sf_nba:") else ("PATRIX / VANILLA" if i.startswith("minecraft:") else "OURS")
    return f"{base.replace('_', ' ').title()} ({tag})"


def entities(rp_dirs):
    """id -> (desc, pack dir) from the built resource packs (later packs in the list win — the stack order)."""
    out = {}
    for d in rp_dirs:
        P = S.Pack(d)
        for i, (f, desc) in P.entities.items():
            out[i] = (desc, d)
    return out


def width(row):
    m = row.get("drawn_new") or row.get("drawn") or row.get("model")
    if not m:
        return 1.0
    sc = 1.0 if row.get("drawn_new") else (row.get("new_scale") or row.get("current_scale") or 1.0)
    return max(float(m[0]), float(m[-1])) * float(sc)


def pen_for(ids, I, water, cap):
    s = {5: 4, 4: 5, 3: 7, 2: 9, 1: 0}[cap] if not water else {3: 3, 2: 8, 1: 0}[min(cap, 3)]
    offs = [0]
    k = 1
    while len(offs) < len(ids):
        offs.append(-k * s)
        if len(offs) < len(ids):
            offs.append(k * s)
        k += 1
    offs = sorted(offs)
    centre = ids[offs.index(0)]
    spec = {"mob": centre["mob"], "label": centre["label"], "name": centre["name"],
            "half": 10 if cap > 1 else 4, "halfz": 3 if cap > 2 else 5, "height": 7 if cap <= 3 else 5,
            "row": []}
    for it, dx in zip(ids, offs):
        if it is centre:
            if it.get("play"):
                spec["play"] = it["play"]
            continue
        r = {"mob": it["mob"], "dx": dx, "label": it["label"], "name": it["name"]}
        if it.get("play"):
            r["play"] = it["play"]
        spec["row"].append(r)
    if water:
        spec.update({"water": True, "depth": 4 if cap <= 2 else 3})
    else:
        spec["roof"] = True
    return spec


def cap_for(w, water):
    if water:
        return 1 if w > 4.0 else (2 if w > 1.2 else 3)
    return 1 if w > 6.0 else (2 if w > 3.2 else (3 if w > 1.6 else 5))


def build(rp_dirs, runner_ver, packs_line):
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    plan = {r["id"]: r for r in json.loads((ROOT / "_docs/sizes/size_law_v2_plan.json").read_text())}
    E = entities(rp_dirs)
    order = ["quadruped", "bird", "insect_flying", "insect_walking", "arachnid", "crustacean", "lizard_croc", "amphibian",
             "turtle", "snake", "biped_ape", "macropod", "pinniped", "cetacean", "fish", "cephalopod", "jellyfish",
             "humanoid", "fantasy", "bat", "object"]
    rows = sorted(census, key=lambda c: (order.index(c["body_plan"]) if c["body_plan"] in order else 99,
                                         c.get("species") or c["id"], c["id"]))
    skipped = [(c["id"], UNSAFE[c["id"]]) for c in rows if c["id"] in UNSAFE]
    rows = [c for c in rows if c["id"] not in UNSAFE and c["id"] in E]
    # ---------------- p20
    p20, cur = [], None

    def flush():
        nonlocal cur
        if cur and cur["ids"]:
            p20.append(cur)
        cur = None
    for c in rows:
        water = c["body_plan"] in WATER_PLANS
        w = width(plan.get(c["id"], {}))
        cap = cap_for(w, water)
        it = {"mob": c["id"], "label": name_of(c["id"]).lower(), "name": name_of(c["id"]), "plan": c["body_plan"]}
        if cur and cur["water"] == water and cur["cap"] == cap and cur["plan"] == c["body_plan"] and len(cur["ids"]) < cap:
            cur["ids"].append(it)
            continue
        flush()
        cur = {"ids": [it], "water": water, "cap": cap, "plan": c["body_plan"]}
    flush()
    data20 = []
    for n, st in enumerate(p20, 1):
        names = [i["name"].upper() for i in st["ids"]]
        data20.append({"id": f"e{n:03d}", "group": f"P20 {st['plan'].upper().replace('_', ' ')}",
                       "title": " · ".join(names)[:120], "look": f"LEFT to RIGHT: {', '.join(names)}.",
                       "rig": pen_for(st["ids"], None, st["water"], st["cap"])})
    if skipped:
        data20.append({"id": "e999", "group": "P20 NOT SUMMONED", "title": "NOT SUMMONED (UNSAFE) — READ ONLY",
                       "look": "These are in our packs but are NOT summoned (they explode, wreck terrain or hurt): " +
                               "; ".join(f"{i} ({why})" for i, why in skipped) + ".", "rig": None})
    # ---------------- p21
    data21 = []
    n = 0
    dropped = []
    ANIM_IDS = set()
    LIB = {}
    for d in rp_dirs:
        P_ = S.Pack(d)
        ANIM_IDS |= set(P_.anims)
        LIB.update(P_.anims)
    MOVE = re.compile(r"(modified_distance_moved|modified_move_speed|ground_speed|walk_distance|is_moving|movement_direction|horizontal_speed|limb_swing)", re.I)

    def moving(aid):
        a = LIB.get(aid)
        return isinstance(a, dict) and bool(MOVE.search(str(a.get("anim_time_update", ""))) or MOVE.search(json.dumps(a.get("bones", {}))))
    for c in rows:
        if c["body_plan"] == "object":
            continue
        desc, d = E[c["id"]]
        anims = [(s, a) for s, a in (desc.get("animations") or {}).items() if not a.startswith("controller.")]
        # 14:4x 10-01: a clip no pack defines would stand still in its pen (a false FAIL) -> not summoned, named in the step
        gone = [s for s, a in anims if a not in ANIM_IDS]
        anims = [(s, a) for s, a in anims if a in ANIM_IDS]
        if gone:
            dropped.append((c["id"], gone))
        if not anims:
            continue
        water = c["body_plan"] in WATER_PLANS
        cap = cap_for(width(plan.get(c["id"], {})), water)
        cap = max(cap, 1)
        chunks = [anims[k:k + cap] for k in range(0, len(anims), cap)]
        for ci, ch in enumerate(chunks, 1):
            n += 1
            ids = [{"mob": c["id"], "label": f"{name_of(c['id']).lower()} {s}", "name": s, "play": a} for s, a in ch]
            tail = f" ({ci} / {len(chunks)})" if len(chunks) > 1 else ""
            data21.append({"id": f"a{n:04d}", "group": f"P21 {c['body_plan'].upper().replace('_', ' ')}",
                           "title": f"{name_of(c['id']).upper()}{tail}"[:120],
                           "look": f"{name_of(c['id']).upper()} — LEFT to RIGHT each copy plays ONE animation (its name tag): "
                                   f"{', '.join(s for s, _ in ch)}. shared_<kind> = the same animal's best clip from another "
                                   f"creator (a candidate: keep / drop in a note)."
                                   + (f" Not shown: {', '.join(gone)} (named by the entity, defined in no pack)." if gone and ci == 1 else "")
                                   + (f" FROZEN HERE (they animate only while the animal moves; the pen holds it still) = skip, not fail: "
                                      f"{', '.join(s for s, a in ch if moving(a))}." if any(moving(a) for s, a in ch) else ""),
                           "rig": pen_for(ids, None, water, cap)})
    (ROOT / "_docs/standard/P21-NOT-SHOWN.md").write_text("# p21 — clips named by an entity but defined in no pack (not summoned)\n\n"
        + "\n".join(f"- {m}: {', '.join(g)}" for m, g in dropped) + "\n")
    # ---------------- bump
    bump_row = json.loads((ROOT / "_staging/bump/rig_row.json").read_text())
    bump = [{"id": "m01", "group": "BUMP", "title": "BUMP MAPS: SAME MOB WITH / WITHOUT THE NORMAL MAP",
             "look": "LEFT to RIGHT in pairs (ON / OFF): warden, dolphin, turtle, blue parrot. Colour and shine are identical; only the "
                     "normal (bump) map differs. Look at them in sun and in shade, close up: do the ON copies show raised / sunken detail "
                     "that the OFF copies lack? PASS = a visible, useful difference. FAIL = no difference (bump maps not worth it).",
             "rig": {"mob": bump_row[0]["mob"], "event": bump_row[0].get("event"), "name": bump_row[0]["name"],
                     "label": bump_row[0]["name"].lower(), "half": 13, "halfz": 3, "height": 5, "roof": False,
                     "row": [{"mob": r["mob"], "dx": r["dx"], "event": r.get("event"), "name": r["name"],
                              "label": r["name"].lower()} for r in bump_row[1:]]}}]
    write_js("p20", data20, runner_ver, packs_line, "THE JUDGING PASS: every entity in our packs, held in pens with name tags",
             "Look for: each one drawn whole (no missing parts, no purple-black checker, no floating), the right texture, a sensible size next to you. "
             "They are held still (idle animation only).")
    write_js("p21", data21, runner_ver, packs_line, "THE JUDGING PASS: every creature x every animation, one copy per animation",
             "Look for: each copy moves as its name tag says; parts stay joined; the motion fits the animal. A clip that looks wrong: note its "
             "name tag. shared_ clips: keep or drop.")
    write_js("bump", bump, runner_ver, packs_line, "THE BUMP-MAP TEST (its own lineup, his BT1)", "")
    print(f"p20 {len(data20)} steps ({sum(1 + len(d['rig']['row']) for d in data20 if d['rig'])} entities, "
          f"{len(skipped)} not summoned) · p21 {len(data21)} steps · bump {len(bump)}")
    return data20, data21, bump


def write_js(key, data, runner_ver, packs_line, title, look):
    K = key.upper()
    js = (ROOT / "tools/testrunner_src/pw_testrunner_p19.js").read_text()
    head = js.split("export const P19_DATA")[0]
    head = re.sub(r"^// pw_testrunner_p19\.js.*?\nfunction lines",
                  f"// pw_testrunner_{key}.js — lineup \"{key}\" {title} (PW-TestRunner BP v{runner_ver}).\n"
                  f"// /scriptevent pw:test start {key} — {packs_line}. Generated by tools/build_p20.py.\nfunction lines", head, flags=re.S)
    if look:
        head = re.sub(r'const LOOK = ".*?";\n', "const LOOK = " + json.dumps(look) + ";\n", head, flags=re.S)
    body = f"export const {K}_DATA = " + json.dumps(data, indent=1) + ";\n"
    tail = js[js.index("const Q0 = {"):]
    tail = re.sub(r"Packs \(on the phone\): .*?- always together; PW-TestRunner BP v0\.5\.7 at the bottom\. ",
                  f"Packs (on the phone): {packs_line} - always together; PW-TestRunner BP v{runner_ver} at the bottom. ", tail, flags=re.S)
    tail = (tail.replace("P19 SETUP", f"{K} SETUP").replace("P19 HIS PICKS: PHONE HOSTS", f"{K}: PHONE HOSTS")
            .replace("'PW Test Runner BP v0.5.7'", f"'PW Test Runner BP v{runner_ver}'")
            .replace("STEPS19 = P19_DATA", f"STEPS{K} = {K}_DATA").replace("P19 DONE", f"{K} DONE").replace("P19: ALL CLEAR", f"{K}: ALL CLEAR")
            .replace("report p19", f"report {key}").replace("P19_STEPS = [Q0, ...STEPS19, Q9]", f"{K}_STEPS = [Q0, ...STEPS{K}, Q9]")
            .replace("P19_INDEX = Object.fromEntries(P19_STEPS", f"{K}_INDEX = Object.fromEntries({K}_STEPS"))
    # a READ-ONLY step (no rig) keeps only the clear
    tail = tail.replace("setup: [{ cmd: CLEAR }, { rig: d.rig }] }));", "setup: d.rig ? [{ cmd: CLEAR }, { rig: d.rig }] : [{ cmd: CLEAR }] }));")
    assert "P19" not in tail and "STEPS19" not in tail, tail[:300]
    (ROOT / f"tools/testrunner_src/pw_testrunner_{key}.js").write_text(head + body + tail, encoding="utf-8")


if __name__ == "__main__":
    a = sys.argv[1:]
    build([Path(x) for x in a[2:]], a[0], a[1])

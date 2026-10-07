#!/usr/bin/env python3
"""build_p19.py — D-C353: lineup p19 = THE PICKS PARADE (menagerie wave P3: RP-07 1.4.33 + PW-StripMine BP 1.3.8).
Every version he kept (318 creatures), grouped by animal so the versions of one animal stand side by side; whole animals packed
into pens of up to 5 (land, roofed, 4 blocks apart; 3 apart and fewer per pen for wide ones) or pools of 3 (water).
Comparison pens carry OUR creature too (his asks): gorilla (WA + YTri + ours), boar (IFS + WA + YSav + ours: 'better than our
current'), bear (AnF bears scaled to ours, next to ours). Each name tag = name + pack, so a note can name it exactly.
Writes tools/testrunner_src/pw_testrunner_p19.js (the lineup + its data)."""
import json, glob, math, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
ROOT = Path("/home/claude"); B = ROOT / "_build/stripmine-bp-139"; R = ROOT / "_build/rp07-1434"
PACK = {"anf": "AnF", "wa": "WA", "ws": "WS", "wwa": "WWA", "ysav": "YSav", "ytri": "YTri", "ifs": "IFS", "ours": "OURS"}
WITH_OURS = {"gorilla": ["sf_nba:gorilla"], "boar": ["sf_nba:boar"], "bear": ["sf_nba:black_bear", "sf_nba:grizzly_bear"]}


def info():
    J = json.loads((ROOT / "_logs/menagerie_jobs_P3.json").read_text())
    want = {e[2] for e in J["entities"]}; out = {}
    lang = dict(l.split("=", 1) for l in (R / "texts/en_US.lang").read_text(encoding="utf-8").splitlines() if "=" in l)
    for f in glob.glob(str(B / "entities/**/*.json"), recursive=True):
        try: e = ML._parse_json(Path(f).read_text(encoding="utf-8-sig"))["minecraft:entity"]
        except Exception: continue
        i = e["description"]["identifier"]
        if i not in want and not any(i in v for v in WITH_OURS.values()): continue
        if i in want and not e["description"].get("is_spawnable", False): continue   # the YSav egg-layers' helper entities (ours: summoned)
        comps = [e.get("components", {})] + list(e.get("component_groups", {}).values()); allc = {}
        for c in comps:
            for k, v in c.items(): allc.setdefault(k, v)
        br = allc.get("minecraft:breathable") or {}
        walks = any(k in allc for k in ("minecraft:navigation.walk", "minecraft:navigation.climb"))
        swim_only = any(isinstance(c.get(k), dict) and c[k].get("can_swim") and c[k].get("can_walk") is False
                        for c in comps for k in ("minecraft:navigation.generic", "minecraft:navigation.swim"))
        water = br.get("breathes_air") is False or (not walks and (swim_only or "minecraft:navigation.swim" in allc))
        cb = e.get("components", {}).get("minecraft:collision_box") or next((c["minecraft:collision_box"] for c in comps if "minecraft:collision_box" in c), {"width": 1})
        sc = (e.get("components", {}).get("minecraft:scale") or {}).get("value", 1)
        pk = i.rsplit("_", 1)[1] if i.startswith("pw:") else "ours"
        nm = lang.get(f"entity.{i}.name") or i.split(":")[1].replace("_", " ").title()
        out[i] = {"water": bool(water), "w": cb.get("width", 1) * sc, "fly": "minecraft:navigation.fly" in allc, "pack": PACK[pk],
                  "name": f"{nm} ({PACK[pk]})", "animal": J["animal_of"].get(i)}
    for a, ids in WITH_OURS.items():
        for i in ids: out[i]["animal"] = a
    return out


def offsets(n, s):
    o = [0]; k = 1
    while len(o) < n: o.append(-k * s); o.append(k * s) if len(o) < n else None; k += 1
    return sorted(o)


def pens():
    I = info(); by = {}
    for i, v in I.items(): by.setdefault(v["animal"], []).append(i)
    steps, cur = [], None
    def flush():
        nonlocal cur
        if cur and cur["ids"]: steps.append(cur)
        cur = None
    for water, a in [(w, a) for w in (False, True) for a in sorted(by)]:
        ids = sorted(by[a], key=lambda i: (I[i]["pack"] == "OURS", I[i]["pack"], i))
        if a == "bear" and not water:                                   # his size check: ours black, AnF black, AnF grizzly, ours grizzly
            flush(); steps.append({"kind": "L4", "ids": ["sf_nba:black_bear", "pw:bear_black_anf", "pw:bear_grizzly_anf", "sf_nba:grizzly_bear"],
                                   "animals": ["bear"], "water": False, "cap": 4}); continue
        if True:
            group = [i for i in ids if I[i]["water"] == water]
            if not group: continue
            wide = max(I[i]["w"] for i in group)
            cap = (2 if wide > 1.2 else 3) if water else (2 if wide > 3.2 else 3 if wide > 1.6 else 5)
            if a in WITH_OURS: flush()                                  # his comparison pens stand alone
            kind = ("W" if water else "L") + str(cap)
            chunks = [group[k:k + cap] for k in range(0, len(group), cap)]
            for ch in chunks:
                if cur and cur["kind"] == kind and len(cur["ids"]) + len(ch) <= cap and len(chunks) == 1: cur["ids"] += ch; cur["animals"].append(a); continue
                flush(); cur = {"kind": kind, "ids": list(ch), "animals": [a], "water": water, "cap": cap}
                if len(chunks) > 1 or a in WITH_OURS: flush()
    flush()
    return I, steps


def rig(I, st, n):
    cap, water = st["cap"], st["water"]
    s = {5: 4, 4: 5, 3: 7, 2: 9}[cap] if not water else {3: 3, 2: 8}[cap]
    offs = offsets(len(st["ids"]), s)
    if cap == 4: offs = [-10, -5, 0, 5]
    order = st["ids"]                                                   # left to right as listed
    centre = order[offs.index(0)]
    spec = {"mob": centre, "label": I[centre]["name"].lower(), "name": I[centre]["name"],
            "half": 11 if cap == 4 else 10 if (not water or cap == 2) else 5, "halfz": 5 if (water and cap == 2) or cap == 2 else 3,
            "height": 7 if cap <= 3 else 5,
            "row": [{"mob": i, "dx": dx, "label": I[i]["name"].lower(), "name": I[i]["name"]} for i, dx in zip(order, offs) if i != centre]}
    if water: spec.update({"water": True, "depth": 4 if cap == 2 else 3})
    else: spec["roof"] = True
    if any(I[i]["fly"] for i in order) and not water: spec["height"] = max(spec["height"], 6)
    return spec


def write():
    I, steps = pens()
    data = []
    for n, st in enumerate(steps, 1):
        names = [I[i]["name"].upper() for i in st["ids"]]
        title = " · ".join(dict.fromkeys(a.replace("_", " ").upper() for a in st["animals"]))
        extra = ""
        if "bear" in st["animals"]: extra = " The AnF bears were scaled to OUR bears' length (his 'keep our size'): compare them with ours (OURS)."
        if "boar" in st["animals"]: extra = " His three boars next to ours (OURS): is each better than ours?"
        if "gorilla" in st["animals"]: extra = " World Animals and yCreatures gorillas next to ours (OURS)."
        data.append({"id": f"b{n:02d}", "group": "P19 WATER" if st["water"] else "P19 HIS PICKS", "title": title[:120],
                     "look": f"LEFT to RIGHT: {', '.join(names)}.{extra}", "rig": rig(I, st, n)})
    js = Path(ROOT / "tools/testrunner_src/pw_testrunner_p18.js").read_text()
    head = js.split("export const P18_DATA")[0]
    head = re.sub(r"^// pw_testrunner_p18\.js.*?\nfunction lines", "// pw_testrunner_p19.js — lineup \"p19\" THE PICKS PARADE (PW-TestRunner BP v0.5.7, D-C353/D-C355; menagerie wave P3, his picks 22:00-22:42 CT 09-30).\n"
                  "// /scriptevent pw:test start p19 — RP-07 v1.4.34 + PW-StripMine BP v1.3.9: every version he kept (ids pw:<animal>_<pack>), grouped by\n"
                  "// animal so the versions stand side by side; name tags = name (PACK); gorilla / boar / bear pens also hold OUR creature.\n"
                  "// Generated by tools/build_p19.py. The rig (pw_testrunner_rig.js) spawns them; a missing creature is logged ('RIG ... FAILED').\nfunction lines", head, flags=re.S)
    head = head.replace("Look for: each animal drawn whole", "Look for: each animal drawn whole").replace(
        "PASS = all right. FAIL + note = which one and what (use all 3 note boxes if needed).",
        "PASS = all right. FAIL + note = which one (its name tag) and what (use all 3 note boxes if needed). A preference (keep / drop one) also goes in a note.")
    body = "export const P19_DATA = " + json.dumps(data, indent=1) + ";\n"
    tail = js.split("];\n", 1)[1] if False else js[js.index("const Q0 = {"):]
    tail = (tail.replace("P18 SETUP", "P19 SETUP").replace("P18 NEW ANIMALS: PHONE HOSTS", "P19 HIS PICKS: PHONE HOSTS")
            .replace("RP-07 v1.4.32 (replaces v1.4.31) + PW-StripMine BP v1.3.7 (replaces v1.3.6)", "RP-07 v1.4.34 (replaces v1.4.33 / v1.4.32) + PW-StripMine BP v1.3.9 (replaces v1.3.8 / v1.3.7)")
            .replace("PW-TestRunner BP v0.5.5", "PW-TestRunner BP v0.5.7").replace("'PW Test Runner BP v0.5.5'", "'PW Test Runner BP v0.5.7'")
            .replace("STEPS18 = P18_DATA", "STEPS19 = P19_DATA").replace("P18 DONE", "P19 DONE").replace("P18: ALL CLEAR", "P19: ALL CLEAR")
            .replace("report p18", "report p19").replace("P18_STEPS = [Q0, ...STEPS18, Q9]", "P19_STEPS = [Q0, ...STEPS19, Q9]")
            .replace("P18_INDEX = Object.fromEntries(P18_STEPS", "P19_INDEX = Object.fromEntries(P19_STEPS"))
    assert "P18" not in tail and "v0.5.5" not in tail, tail[:400]
    out = ROOT / "tools/testrunner_src/pw_testrunner_p19.js"
    out.write_text(head + body + tail, encoding="utf-8")
    land = sum(1 for d in data if not d["rig"].get("water")); creatures = sum(1 + len(d["rig"]["row"]) for d in data)
    print(f"p19: {len(data)} pens ({land} land, {len(data) - land} water), {creatures} creatures ({creatures - 4} his + 4 ours)")
    return data


if __name__ == "__main__":
    write()

#!/usr/bin/env python3
"""build_rp06_1413.py — D-C278 (R4 witness round). RP-06 Hostile Mobs RP v1.4.13 from v1.4.12:
  1. GUARDIAN + ELDER GUARDIAN spikes smooth (his R4 n04-n06 "spikes animation doesn't seem smooth"):
       - the spike SHAKE (Mojang's Bedrock-only sin(t*2000)/50, +-0.23 px at 5.6 Hz on every spike, always) now only OUT of the
         water — Java has no in-water shake (GuardianModel: 1 + cos(age*1.5 + i)*0.01 - extension);
       - "moving" is no longer query.is_moving (recomputed from motion every tick: it flickers for a hovering or held guardian,
         so the spikes twitched in 25 %/tick and out 6 %/tick) but a smoothed swim-speed signal (0 below 0.4 b/s, 1 above 1.2 b/s,
         ~0.2 per tick), the spikes easing toward it at Java's rates (in 0.25/tick, out 0.06/tick); the tail's speed changes use
         the same signal and are tick-rate independent.
  2. SPIDER walk (his R4 n08 "the legs don't seem to leave the ground"): the Patrix spider's own walk (spider.jem, the
     knee/ankle terms of every leg) ported to Molang (spider_walk.py) — 2-4 legs lift 1.5-3 px at every phase; the April walk
     animations no longer turn the new hips (their leg channels were built for the April legs: the feet never left the
     ground) or drop the whole spider 2 px (Root); April body/head/fang motion stays.
  3. RAVAGER + PILLAGER: `anim_nose` (the villager nose controller plays it; neither entity defined it -> content-log error).
  4. UP/DOWN FACES of the geometries our converters wrote (updown_fix.py; same fix as RP-07 1.4.20).
  manifest 1.4.13, uuid kept. verify: verify_rp06_1413.py."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from updown_fix import flip_pack, check_turned
from updown_census import used_geometries
from spider_walk import walk_animation

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
APRIL = ROOT / "_build/rp07-1420/animations/spider.v1.8.animation.json"

GUARDIAN_INIT = ["variable.spike_animation_speed = 0.0;", "variable.tail_animation_speed = 0.0;", "variable.tail_swim = 0.0;",
                 "variable.pw_move_s = 0.0;"]
GUARDIAN_PRE = [
    "variable.pw_speed = math.sqrt(query.ground_speed * query.ground_speed + query.vertical_speed * query.vertical_speed);",
    "variable.pw_move_s = query.life_time < 0.1 ? 0.0 : variable.pw_move_s + (math.clamp((variable.pw_speed - 0.4) / 0.8, 0.0, 1.0) - variable.pw_move_s) * (1.0 - math.pow(0.8, query.delta_time * 20.0));",
    "variable.spike_shake = !query.is_in_water ? math.sin(query.life_time * 2000) / 50 : 0.0;",
    "variable.spike_animation_speed = query.life_time < 0.1 ? 0.0 : (!query.is_in_water ? (math.round(math.sin(query.life_time * 2000)) == 0.0 ? math.random(0.0, 1.0) : variable.spike_animation_speed) : variable.spike_animation_speed + ((1.0 - variable.pw_move_s) - variable.spike_animation_speed) * (1.0 - math.pow(((1.0 - variable.pw_move_s) < variable.spike_animation_speed) ? 0.75 : 0.94, query.delta_time * 20.0)));",
    "variable.spike_extension = (1.0 - variable.spike_animation_speed) * 0.55;",
    "variable.tail_animation_speed = query.life_time < 0.1 ? 0.0 : (!query.is_in_water ? 2.0 : (variable.pw_move_s > 0.5 ? (variable.tail_animation_speed < 0.5 ? 4.0 : variable.tail_animation_speed + (0.5 - variable.tail_animation_speed) * (1.0 - math.pow(0.9, query.delta_time * 20.0))) : variable.tail_animation_speed + (0.125 - variable.tail_animation_speed) * (1.0 - math.pow(0.8, query.delta_time * 20.0))));",
    "variable.tail_swim = query.life_time < 0.1 ? 0.0 : variable.tail_swim + variable.tail_animation_speed * query.delta_time * 20.0;",
    "variable.tail_base_angle = math.sin(variable.tail_swim * 57.29578);",
]
SPIDER_MAP = {"base": "animation.pw_spider.base", "walking": "animation.pw_spider.walking", "walking_legs": "animation.pw_spider.walk",
              "walking_legs2": "animation.pw_spider.walk", "attack_walk": "animation.pw_spider.walk",
              "swimming": "animation.pw_spider.swimming", "climbing": "animation.pw_spider.climbing"}
SPIDER_PRE = ["variable.pw_ls = query.modified_distance_moved * 1.0769;"]   # var.ls = limb_swing/1.3 * (1 - var.scale*2), median 1.4


def guardians(dst):
    for stem in ("guardian", "elder_guardian"):
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); s = d["minecraft:client_entity"]["description"]["scripts"]
        assert s["pre_animation"][0].startswith("variable.spike_shake = math.sin"), s["pre_animation"][0]
        s["initialize"] = GUARDIAN_INIT; s["pre_animation"] = GUARDIAN_PRE
        R.wj(pe, d); CHANGED.append(f"entity/{stem}.entity.json")
    return "guardian + elder guardian: in-water shake off, smoothed moving signal"


def _strip(anim, drop_bones, drop_body_pos):
    a = json.loads(json.dumps(anim))
    a["bones"] = {k: v for k, v in a.get("bones", {}).items() if k not in drop_bones}
    if drop_body_pos and "body" in a["bones"]:
        a["bones"]["body"].pop("position", None)
        if not a["bones"]["body"]: del a["bones"]["body"]
    return a


def spider(dst):
    april = R.jl(APRIL)["animations"]
    legs = {f"leg{i}" for i in range(1, 9)}
    anims = {"animation.pw_spider.walk": walk_animation(),
             "animation.pw_spider.base": _strip(april["animation.spider.v1.8.base"], legs, False),
             "animation.pw_spider.walking": _strip(april["animation.spider.v1.8.walking"], legs | {"Root"}, True),
             "animation.pw_spider.swimming": _strip(april["animation.spider.v1.8.swimming"], legs | {"Root"}, True),
             "animation.pw_spider.climbing": _strip(april["animation.spider.v1.8.climbing"], legs | {"Root"}, True)}
    pa = dst / "animations/pw_spider.animation.json"; R.wj(pa, {"format_version": "1.8.0", "animations": anims}); ADDED.append(pa.relative_to(dst).as_posix())
    pe = dst / "entity/spider.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    for k, v in SPIDER_MAP.items():
        assert desc["animations"][k].startswith("animation.spider.v1.8."), (k, desc["animations"][k])
        desc["animations"][k] = v
    assert not desc.get("scripts")
    desc["scripts"] = {"pre_animation": SPIDER_PRE}
    R.wj(pe, d); CHANGED.append("entity/spider.entity.json")
    return f"Patrix walk on {len(anims['animation.pw_spider.walk']['bones'])} leg bones; April base/walking/swimming/climbing without legs/Root"


def nose(dst):
    for stem in ("ravager", "pillager"):
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); a = d["minecraft:client_entity"]["description"]["animations"]
        assert "anim_nose" not in a and a.get("nose_yaw") == "animation.villager.nose_yaw"
        a["anim_nose"] = "animation.villager.nose_yaw"; R.wj(pe, d); CHANGED.append(f"entity/{stem}.entity.json")
    return "anim_nose -> animation.villager.nose_yaw on ravager + pillager"


def updown(dst):
    used = set(used_geometries().keys())
    done, notes = flip_pack(dst, used_only=used)
    for ident, (n, f) in done.items():
        if f not in CHANGED: CHANGED.append(f)
    json.dump({"turned": {k: v[0] for k, v in done.items()}, "notes": notes}, open(ROOT / "_docs/convb/updown_rp06_1413.json", "w"), indent=1)
    return f"{sum(v[0] for v in done.values())} faces turned in {len(done)} geometries (own-JEM match; skipped: {[k for k, v in notes.items() if k not in done]})"


def verify_extra(cfg, check):
    NEW, OLD = cfg["dst"], cfg["src"]
    ok = True; rows = []
    for stem in ("guardian", "elder_guardian"):
        s = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]["scripts"]
        pre = " ".join(s["pre_animation"])
        good = (s["pre_animation"] == GUARDIAN_PRE and "query.is_moving" not in pre and "!query.is_in_water ? math.sin" in pre
                and "variable.pw_move_s = 0.0;" in s["initialize"])
        ok &= good; rows.append(f"{stem} {'ok' if good else 'BAD'}")
    check("GS1 guardian smoothing scripts", ok, "; ".join(rows))
    # GS2: numeric: a held guardian whose speed flickers 0 / 1.0 b/s every tick -> spike extension moves < 0.02 per frame
    import math
    def run(speeds, dt=1 / 60):
        ms = sa = 0.0; ext = []; t = 0.0
        for v in speeds:
            t += dt
            ms = 0.0 if t < 0.1 else ms + (min(1, max(0, (v - 0.4) / 0.8)) - ms) * (1 - 0.8 ** (dt * 20))
            tgt = 1 - ms; sa = 0.0 if t < 0.1 else sa + (tgt - sa) * (1 - (0.75 if tgt < sa else 0.94) ** (dt * 20))
            ext.append((1 - sa) * 0.55)
        return ext
    flick = [1.0 if (i // 3) % 2 else 0.0 for i in range(600)]   # moving flag flips every 3 frames (a held/hovering guardian)
    e = run(flick); steps = [abs(e[i + 1] - e[i]) for i in range(120, len(e) - 1)]
    e_old = []; sa = 0.0
    for i, v in enumerate(flick):     # 1.4.12 rule: query.is_moving flag directly
        t = (i + 1) / 60; mv = v > 0.1
        sa = 0.0 if t < 0.1 else (sa * 0.75 ** (20 / 60) if mv else 1 - (1 - sa) * 0.94 ** (20 / 60)); e_old.append((1 - sa) * 0.55)
    st_old = [abs(e_old[i + 1] - e_old[i]) for i in range(120, len(e_old) - 1)]
    check("GS2 flicker test", max(steps) < 0.01 and max(steps) < max(st_old) / 3,
          f"largest per-frame spike slide {max(steps) * 11.31:.3f} px (1.4.12 rule {max(st_old) * 11.31:.3f} px) under a 10 Hz moving flicker")
    d = R.jl(NEW / "entity/spider.entity.json")["minecraft:client_entity"]["description"]
    a = R.jl(NEW / "animations/pw_spider.animation.json")["animations"]
    _, g = R.geo_file(ROOT / "_build/rp07-1420", "geometry.spider"); bones = {b["name"] for b in g["bones"]}
    walk_bones = set(a["animation.pw_spider.walk"]["bones"])
    leg_free = all(not ({f"leg{i}" for i in range(1, 9)} | {"Root"}) & set(a[k]["bones"]) for k in ("animation.pw_spider.base", "animation.pw_spider.walking",
                                                                                                      "animation.pw_spider.swimming", "animation.pw_spider.climbing") if k != "animation.pw_spider.base") \
        and not ({f"leg{i}" for i in range(1, 9)} & set(a["animation.pw_spider.base"]["bones"]))
    check("SP1 spider walk", all(d["animations"][k] == v for k, v in SPIDER_MAP.items()) and d["scripts"] == {"pre_animation": SPIDER_PRE}
          and walk_bones <= bones and len(walk_bones) == 32 and leg_free,
          f"{len(walk_bones)} walk bones all in geometry.spider {walk_bones <= bones}; April copies leg/Root-free {leg_free}")
    from spider_walk import eval_add_rot, LEGS
    from equine_compare import bone_affines
    from bb_truth import truth_posed_faces
    kids = {}
    for b in g["bones"]: kids.setdefault(b.get("parent"), []).append(b["name"])
    def sub(n):
        out = [n]
        for c in kids.get(n, []): out += sub(c)
        return out
    dsub = {q: set(sub(f"leg_{q}_d")) for q in LEGS}
    def feet(add):
        F = truth_posed_faces(g["bones"], 64, 32, bone_affines(g["bones"], add_rot=add))
        return {q: min(p[1] for f in F if f.bone in dsub[q] for p in f.pts) for q in LEGS}
    rest = feet({}); lifts = []
    for k in range(8):
        ft = feet(eval_add_rot(k * math.pi / 4, 0.6)); lifts.append(sum(1 for q in LEGS if ft[q] - rest[q] > 1.0))
    check("SP2 feet lift while walking", min(lifts) >= 2, f"legs lifted > 1 px at 8 phases: {lifts}")
    ok = all(R.jl(NEW / f"entity/{s}.entity.json")["minecraft:client_entity"]["description"]["animations"].get("anim_nose") == "animation.villager.nose_yaw"
             for s in ("ravager", "pillager"))
    check("N1 anim_nose", ok, "ravager + pillager define anim_nose")
    used = set(__import__("updown_census").used_geometries().keys())
    ok, msgs, counts = check_turned(OLD, NEW, used)
    rep = json.load(open(ROOT / "_docs/convb/updown_rp06_1413.json"))
    check("U1 up/down faces turned from each geometry's OWN JEM, nothing else changed", ok,
          f"{sum(rep['turned'].values())} faces in {len(rep['turned'])} geometries; {msgs[:3]}")
    check("U2 the April humanoids pw_zombie / pw_drowned are untouched (their UVs come from no JEM)",
          all(k not in rep["turned"] for k in ("geometry.pw_zombie", "geometry.pw_drowned")), f"turned: {sorted(rep['turned'])}")


CFG = {
    "src": ROOT / "_build/rp06-1412", "dst": ROOT / "_build/rp06-1413", "version": "1.4.13",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.13",
    "desc": ("v1.4.13 (2026-09-29) R4 FIXES (D-C278): guardian spikes glide smoothly (no constant shake in the water, no twitching); "
             "the Patrix spider walk (legs lift and step); ravager/pillager nose animation error fixed; top/bottom faces of the "
             "Patrix-converted mobs the right way round."),
    "jobs": [], "look": {},
    "post": [guardians, spider, nose, updown],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "verify_hooks": [verify_extra], "unbound_ok": {}, "placement": {},
    "report": ROOT / "_docs/convb/build_rp06_1413_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED}, open(ROOT / "_docs/convb/build_rp06_1413_files.json", "w"), indent=1)

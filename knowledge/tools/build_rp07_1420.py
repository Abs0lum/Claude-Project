#!/usr/bin/env python3
"""build_rp07_1420.py — D-C278 (his 09-29 02:58 "let's fix all of these ... let's keep going", R4 witness round).
RP-07 Neutral Mobs RP v1.4.20 from v1.4.19:
  1. CONVERTER B re-bakes (jem_convert.bedrock_uv: up/down faces in the Bedrock form):
       rabbit  — the Java rest pose of every part the Patrix rabbit leaves to Java (classic RabbitModel): hind feet ON the ground
                 (they sat 3 px up), haunches -21 deg, body -20 deg (front raised, as Java), front legs -11 deg, tail.
       dolphin — the Java flipper pose FreshLX copies (60 deg down, 120 deg out): the flippers no longer lie flat along the belly.
  2. UP/DOWN FACES of every other geometry our converters wrote, turned into the Bedrock form (updown_fix.py): Bedrock reads a
     box's top/bottom face turned 180 deg against the JEM — chicken + frog toes pointed backwards, the panda's rump (the top face
     of its turned body box) was upside down, the tropical fish's bottom fins drew 2 px off the belly.
  3. SPIDER: textures/entity/spider/spider.tga removed — inside one pack the game took the old 64x32 .tga over the Patrix
     512x256 .png of the same name (the white leg segments and abdomen strips in his R4 shots).
  4. MOOSHROOM A/B (the floating mushrooms are the GAME's own mushroom blocks, hung on the bones named body/head):
       red   (variant 0) -> geometry.pw_mooshroom: our bones renamed pw_body / pw_head (no body/head bone for the game to use)
       brown (variant 1) -> geometry.pw_mooshroom_anchored: the same + empty anchor bones body (vanilla pivot 0,19,2) and head
                            (0,18.5,-8: our head top is 1.5 px under vanilla's) so the game's blocks sit on the back / head.
       + the render controller's texture index fixed (a BROWN mooshroom drew the red skin: index 1 was variant_0 = red).
  5. SIZES (his asks): bee 0.5x, axolotl 0.8x (client scripts.scale).
  6. MOTION: the do-nothing shims that removed real motion are dropped — animation.humanoid.move / .attack.rotations,
     animation.zombie.attack_bare_hand, animation.silverfish.move (enderman / giant / parched / legacy zombie villager /
     silverfish get their walk + attack back), animation.tadpole.swim (the vanilla tail wag); squid + glow squid get the
     tentacle pulse (animation.pw_squid.swim: tentacle1-8 x += variable.squid.tentacle_angle, the engine's own value);
     the dolphin's body follows where it swims (animation.pw_dolphin.steer, vanilla dolphin.move's body line) instead of a
     head-only look, turning about the middle of its body.
  manifest 1.4.20, uuid kept. verify: verify_rp07_1420.py."""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
from updown_fix import flip_pack, check_turned
from updown_census import used_geometries

ROOT = Path("/home/claude")
REBUILT = {"geometry.rabbit.patrix", "geometry.dolphin.patrix"}
SCALES = {"bee": "0.5", "axolotl": "0.8"}
SHIMS_DROP = ["animation.humanoid.move", "animation.humanoid.attack.rotations", "animation.zombie.attack_bare_hand",
              "animation.silverfish.move", "animation.tadpole.swim"]
CHANGED = []          # filled by the hooks (relative paths), read by the gate
ADDED = []
REMOVED = []


def rel(dst, p): return str(Path(p).relative_to(dst))


# ------------------------------------------------------------------------------------------------------------ hooks
def updown(dst):
    used = set(used_geometries().keys())
    done, notes = flip_pack(dst, skip=REBUILT, used_only=used)
    for ident, (n, f) in done.items():
        if f not in CHANGED: CHANGED.append(f)
    json.dump({"turned": {k: v[0] for k, v in done.items()}, "notes": notes}, open(ROOT / "_docs/convb/updown_1420.json", "w"), indent=1)
    return f"{sum(v[0] for v in done.values())} faces turned in {len(done)} geometries (own-JEM match; skipped: {[k for k, v in notes.items() if k not in done]})"


def spider_tga(dst):
    p = dst / "textures/entity/spider/spider.tga"
    assert p.exists() and (dst / "textures/entity/spider/spider.png").exists()
    p.unlink(); REMOVED.append("textures/entity/spider/spider.tga")
    return "spider.tga removed (spider.png is now the only spider texture)"


def _rename_bones(bones, ren):
    for b in bones:
        if b["name"] in ren: b["name"] = ren[b["name"]]
        if b.get("parent") in ren: b["parent"] = ren[b["parent"]]
    return bones


def _rekey_anim(doc, aid, ren):
    a = doc["animations"][aid]
    a["bones"] = {ren.get(k, k): v for k, v in a.get("bones", {}).items()}


def mooshroom(dst):
    ren = {"body": "pw_body", "head": "pw_head"}
    p, g = R.geo_file(dst, "geometry.pw_mooshroom")
    doc = R.jl(p); geo = doc["minecraft:geometry"][0]
    names = [b["name"] for b in geo["bones"]]
    assert "body" in names and "head" in names and "pw_body" not in names
    _rename_bones(geo["bones"], ren); R.wj(p, doc)
    # anchored variant: empty body/head anchor bones where the game hangs its mushroom blocks
    anc = json.loads(json.dumps(doc)); ga = anc["minecraft:geometry"][0]
    ga["description"]["identifier"] = "geometry.pw_mooshroom_anchored"
    ga["bones"].append({"name": "body", "parent": "pw_body", "pivot": [0.0, 19.0, 2.0], "rotation": [0.0, 0.0, 0.0]})
    ga["bones"].append({"name": "head", "parent": "pw_head", "pivot": [0.0, 18.5, -8.0], "rotation": [0.0, 0.0, 0.0]})
    pa = dst / "models/entity/pw_mooshroom_anchored.geo.json"; R.wj(pa, anc); ADDED.append(rel(dst, pa))
    # animations that name body/head for the mooshroom only (checked: ar_mooshroom + pw_mooshroom_ambient_v2 are mooshroom-only)
    for f, ids in (("animations/ar_mooshroom.animation.json", ("animation.ar_mooshroom.walk", "animation.ar_mooshroom.idle")),
                   ("animations/pw_mooshroom_ambient_v2.animation.json", ("animation.pw_mooshroom.ambient",))):
        d = R.jl(dst / f)
        for aid in ids: _rekey_anim(d, aid, ren)
        R.wj(dst / f, d); CHANGED.append(f)
    look = {"format_version": "1.8.0", "animations": {"animation.pw_mooshroom.look": {"loop": True, "bones": {
        "pw_head": {"rotation": ["query.target_x_rotation", "query.target_y_rotation", 0.0]}}}}}
    pl = dst / "animations/pw_mooshroom_look.animation.json"; R.wj(pl, look); ADDED.append(rel(dst, pl))
    pe = dst / "entity/mooshroom.entity.json"; e = R.jl(pe); desc = e["minecraft:client_entity"]["description"]
    assert desc["animations"]["look_at_target"] == "animation.pw_convb.look"
    desc["animations"]["look_at_target"] = "animation.pw_mooshroom.look"
    desc["geometry"] = {"default": "geometry.pw_mooshroom", "anchored": "geometry.pw_mooshroom_anchored", "baby": "geometry.pw_mooshroom"}
    R.wj(pe, e); CHANGED.append("entity/mooshroom.entity.json")
    rc = {"format_version": "1.10.0", "render_controllers": {"controller.render.pw_mooshroom": {
        "arrays": {"geometries": {"Array.geos": ["Geometry.default", "Geometry.anchored"]},
                   "textures": {"Array.skins": ["Texture.variant_0", "Texture.variant_1"]}},
        "geometry": "Array.geos[math.clamp(query.variant, 0, 1)]",
        "materials": [{"*": "Material.default"}],
        "textures": ["Array.skins[math.clamp(query.variant, 0, 1)]"]}}}
    R.wj(dst / "render_controllers/pw_mooshroom.render.json", rc); CHANGED.append("render_controllers/pw_mooshroom.render.json")
    return "red = no body/head bones (pw_body/pw_head); brown = + anchors body (0,19,2) / head (0,18.5,-8); RC geometry by variant, brown skin fixed"


def sizes(dst):
    out = {}
    for stem, s in SCALES.items():
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        assert "scale" not in desc.get("scripts", {}), (stem, desc["scripts"].get("scale"))
        desc.setdefault("scripts", {})["scale"] = s; R.wj(pe, d); CHANGED.append(f"entity/{stem}.entity.json"); out[stem] = s
    return out


def shims(dst):
    f = "animations/pw_animation_shims.animation.json"; d = R.jl(dst / f)
    for aid in SHIMS_DROP:
        assert aid in d["animations"], aid
        del d["animations"][aid]
    R.wj(dst / f, d); CHANGED.append(f)
    return f"dropped {SHIMS_DROP}; {len(d['animations'])} shims left"


def aquatic(dst):
    # squid + glow squid: the tentacle pulse (engine value, degrees; additive on the Patrix ring pose: x first, then the ring yaw)
    sq = {"format_version": "1.8.0", "animations": {"animation.pw_squid.swim": {"loop": True, "bones": {
        f"tentacle{i}": {"rotation": ["variable.squid.tentacle_angle", 0.0, 0.0]} for i in range(1, 9)}}}}
    ps = dst / "animations/pw_squid_swim.animation.json"; R.wj(ps, sq); ADDED.append(rel(dst, ps))
    for stem in ("squid", "glow_squid"):
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        assert "pw_swim" not in desc["animations"]
        desc["animations"]["pw_swim"] = "animation.pw_squid.swim"; desc["scripts"]["animate"].append("pw_swim")
        R.wj(pe, d); CHANGED.append(f"entity/{stem}.entity.json")
    # dolphin: vanilla dolphin.move's BODY line (pitch/yaw toward where it swims + the slow bob) on our body bone; the head-only
    # look is dropped (the head rides the body, as in vanilla); body pivot moved to the middle of the torso (rotation 0 -> no
    # geometry moves)
    dl = {"format_version": "1.8.0", "animations": {"animation.pw_dolphin.steer": {"loop": True, "bones": {
        "body": {"rotation": ["query.target_x_rotation - 2.865 - 2.865 * math.cos(query.life_time * 343.8)", "query.target_y_rotation", 0.0]}}}}}
    pd = dst / "animations/pw_dolphin_steer.animation.json"; R.wj(pd, dl); ADDED.append(rel(dst, pd))
    pe = dst / "entity/dolphin.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert desc["animations"]["swim"] == "animation.dolphin.move"
    desc["animations"]["swim"] = "animation.pw_dolphin.steer"
    desc["scripts"]["animate"] = [a for a in desc["scripts"]["animate"] if a != "look_at_target"]
    R.wj(pe, d); CHANGED.append("entity/dolphin.entity.json")
    p, g = R.geo_file(dst, "geometry.dolphin.patrix"); doc = R.jl(p); geo = doc["minecraft:geometry"][0]
    by = {b["name"]: b for b in geo["bones"]}; body = by["body"]; torso = by["body2"]["cubes"][0]
    assert not any(abs(v) > 1e-6 for v in (body.get("rotation") or [0, 0, 0]))
    o, s = torso["origin"], torso["size"]; body["pivot"] = [0.0, round(o[1] + s[1] / 2, 3), round(o[2] + s[2] / 2, 3)]
    R.wj(p, doc)
    return f"squid/glow squid tentacle pulse; dolphin steer about {body['pivot']}"


def verify_extra(cfg, check):
    NEW, OLD = cfg["dst"], cfg["src"]
    # U1: own-JEM check (updown_fix.check_turned): every literal face of each converter-written used geometry turned exactly,
    # nothing else changed (pw_mooshroom compared after undoing its bone renames and without the new anchor bones); rabbit +
    # dolphin (rebuilt) entirely in the Bedrock form
    used = set(__import__("updown_census").used_geometries().keys())
    ok, msgs, counts = check_turned(OLD, NEW, used, skip=REBUILT, renames={"geometry.pw_mooshroom": {"pw_body": "body", "pw_head": "head"}})
    rep = json.load(open(ROOT / "_docs/convb/updown_1420.json"))
    check("U1 up/down faces turned from each geometry's OWN JEM, nothing else changed", ok,
          f"{sum(rep['turned'].values())} faces in {len(rep['turned'])} geometries; {msgs[:3]}; e.g. " + "; ".join(f"{k.replace('geometry.', '')} {v}" for k, v in list(counts.items())[:4]))
    check("U2 the April/vanilla/third-party geometries are untouched", all(k not in rep["turned"] for k in ("geometry.creeper.v1.8", "geometry.parrot", "geometry.zombie.villager_v2")),
          "creeper.v1.8 / parrot / zombie.villager_v2 not in the turned list")
    # S1 sizes
    rows = []; ok = True
    for stem, s in SCALES.items():
        d = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]; ok &= d["scripts"].get("scale") == s
        rows.append(f"{stem} {d['scripts'].get('scale')}")
    check("S1 sizes", ok, "; ".join(rows))
    # M1 mooshroom
    e = R.jl(NEW / "entity/mooshroom.entity.json")["minecraft:client_entity"]["description"]
    _, gr = R.geo_file(NEW, "geometry.pw_mooshroom"); _, ga = R.geo_file(NEW, "geometry.pw_mooshroom_anchored")
    nr = {b["name"] for b in gr["bones"]}; na = {b["name"] for b in ga["bones"]}
    anims = R.jl(NEW / "animations/ar_mooshroom.animation.json")["animations"]; amb = R.jl(NEW / "animations/pw_mooshroom_ambient_v2.animation.json")["animations"]
    bone_refs = set()
    for a in list(anims.values()) + list(amb.values()): bone_refs |= set(a.get("bones", {}))
    ok = ("body" not in nr and "head" not in nr and {"pw_body", "pw_head", "body", "head"} <= na and bone_refs <= nr and "body" not in bone_refs
          and e["geometry"].get("anchored") == "geometry.pw_mooshroom_anchored" and e["animations"]["look_at_target"] == "animation.pw_mooshroom.look")
    rc = R.jl(NEW / "render_controllers/pw_mooshroom.render.json")["render_controllers"]["controller.render.pw_mooshroom"]
    ok &= rc["textures"] == ["Array.skins[math.clamp(query.variant, 0, 1)]"] and rc["arrays"]["textures"]["Array.skins"] == ["Texture.variant_0", "Texture.variant_1"]
    check("M1 mooshroom A/B", ok, f"red bones body/head absent {('body' not in nr and 'head' not in nr)}; anchored has anchors {({'body', 'head'} <= na)}; "
          f"animation bones {sorted(bone_refs)} all in the red geometry {bone_refs <= nr}; RC skins {rc['arrays']['textures']['Array.skins']}")
    # H1 shims
    sh = R.jl(NEW / "animations/pw_animation_shims.animation.json")["animations"]; sho = R.jl(OLD / "animations/pw_animation_shims.animation.json")["animations"]
    check("H1 shims dropped", all(a not in sh for a in SHIMS_DROP) and set(sho) - set(sh) == set(SHIMS_DROP) and all(sh[k] == sho[k] for k in sh),
          f"{len(sho)} -> {len(sh)}; dropped {sorted(set(sho) - set(sh))}")
    # Q1 aquatic
    sq = R.jl(NEW / "entity/squid.entity.json")["minecraft:client_entity"]["description"]; gs = R.jl(NEW / "entity/glow_squid.entity.json")["minecraft:client_entity"]["description"]
    dd = R.jl(NEW / "entity/dolphin.entity.json")["minecraft:client_entity"]["description"]
    _, gsq = R.geo_file(NEW, "geometry.squid.patrix"); tn = {b["name"] for b in gsq["bones"]}
    ok = (all(x["animations"].get("pw_swim") == "animation.pw_squid.swim" and "pw_swim" in x["scripts"]["animate"] for x in (sq, gs))
          and all(f"tentacle{i}" in tn for i in range(1, 9)) and dd["animations"]["swim"] == "animation.pw_dolphin.steer" and "look_at_target" not in dd["scripts"]["animate"])
    check("Q1 squid pulse + dolphin steer", ok, f"squid tentacles bound {all(f'tentacle{i}' in tn for i in range(1, 9))}; dolphin animate {dd['scripts']['animate']}")
    # T1 spider texture
    check("T1 spider texture", not (NEW / "textures/entity/spider/spider.tga").exists() and (NEW / "textures/entity/spider/spider.png").exists(),
          "spider.tga removed, spider.png kept")


CFG = {
    "src": ROOT / "_build/rp07-1419", "dst": ROOT / "_build/rp07-1420", "version": "1.4.20",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.20",
    "desc": ("v1.4.20 (2026-09-29) R4 FIXES (D-C278): top/bottom faces of every Patrix-converted mob the right way round (chicken and "
             "frog toes forward, panda rump, tropical fish fins on the belly); rabbit in the Java pose with its back feet on the ground; "
             "dolphin flippers angled like Java; the Patrix spider texture (the old .tga was winning); mooshroom mushroom test (red vs "
             "brown); bee half size, axolotl 0.8x; squid tentacles pulse, the dolphin turns its body toward where it swims; enderman, "
             "silverfish, giant and the tadpole get their own motion back."),
    "jobs": [("rabbit", "rabbit", "default", "rabbit", "default"), ("dolphin", "dolphin", "default", "dolphin", "default")],
    "look": {},
    "post": [updown, spider_tga, mooshroom, sizes, shims, aquatic],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "verify_hooks": [verify_extra],
    "unbound_ok": {"dolphin": set(), "rabbit": set()},
    "placement": {"rabbit": ("ground",), "dolphin": ("old",)},
    "report": ROOT / "_docs/convb/build_1420_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED}, open(ROOT / "_docs/convb/build_1420_files.json", "w"), indent=1)

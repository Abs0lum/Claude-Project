#!/usr/bin/env python3
"""build_rp07_1423.py — D-C285 (R8 witness round: his first load of the 1.4.22 stack, p4 re-run, p5; Round 11 GO 16:1x CT 09-29).
RP-07 Neutral Mobs RP v1.4.23 from v1.4.22.

  1. TADPOLE UPRIGHT (p4 a18 "oriented on his side … or maybe just his head", p5 b18 "sidewaysish"). tadpole.jem:
       body2.rz = if(is_in_water, 0, torad(20) - torad(40)*clamp(limb_speed*6,0,1) + … - torad(90))   (Patrix: flops on land)
     Converter B (1.4.19) baked the DRY branch — convb.AQUATIC had no "tadpole" — so body2 carries rz -70 and the tail -69.3:
     the whole tadpole, tail included, lies on its side. convb.AQUATIC now lists the tadpole (in water): body2 0, tail2 -5 deg.
  2. PUFFERFISH SPIKES ROOTED (p5 b18 "spikes seem disconnected at fully grown size"). The large + medium geometries were the old
     Converter A files: every spike card mirrored in x with its u NOT flipped, so the opaque spike roots sit on the card's far edge
     (tools/spike_root_gap.py: nearest opaque texel 0.43-1.13 px off the body, x1.2 in game) and the body sat 8-10 px below the
     origin. Rebuilt by Converter B from puffer_fish_big / puffer_fish_medium.jem (in water): gaps <= 0.08 px, body where the
     JEM puts it (body.ty 22, body2.ty -3.5 / -2). The small form (same both ways, passed) is untouched.
  3. SQUID TILT RUNS (p5 b12 "both vertically oriented"; a14/a15). The game rejected `variable.squid.swim_rotation ?? 0.0` ("left-
     hand-side of ?? … isn't a direct-variable reference") and dropped tilt_a / tilt_b whole. variable.squid.* is the engine's own
     struct (vanilla animation.squid.rotate uses it bare) -> the `?? 0.0` goes. molang_lint now enforces the rule.
  4. ENDERMAN JAW RUNS. The April entity is format 1.8.0: the game rejected scripts.animate / scripts.initialize ("child … not
     valid here"), so the ported jaw never played. Now: controller.animation.pw_enderman.jaw in the entity's animation_controllers
     (its state plays pw_jaw; on_entry seeds v.pw_em_rid); scripts.animate / initialize removed; pre_animation unchanged.
  5. MOOSHROOM PROBE REMOVED (his 16:1x "keep today's look"): entity + render controller back to 1.4.20, probe files deleted.
     The probe answered: our model's layer changed with the name (Moo D dotted caps, Moo C none) while the tall tier stayed on all
     four — the game's own mushroom blocks ignore the model (no bones in B, zero-scaled anchors in D).
  6. SIZES (p5 b15 "wolf needs to be a little bigger, sheep a tiny bit smaller"): size_rule REAL wolf 1.30 -> 1.43 m (+10 %),
     sheep 1.30 -> 1.20 m (-7.7 %), both inside the cited real ranges; the 8 % deadband does not apply to his explicit request.
verify: python3 tools/verify_rp07_1423.py"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
R1420 = ROOT / "_build/rp07-1420"
STRIPMINE_RP = ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"
RP06 = ROOT / "_build/rp06-1416"


# ------------------------------------------------------------------------------------------------ 3. squid tilt
SQUID_TILT = {"squid": ("animation.pw_squid.tilt_a", "query.body_x_rotation"),
              "glow_squid": ("animation.pw_squid.tilt_b", "-query.body_x_rotation")}
SWIM_ROT = "variable.squid.swim_rotation"


def squid_tilt(dst):
    pa = dst / "animations/pw_squid_tilt.animation.json"; d = R.jl(pa)
    for stem, (aid, x) in SQUID_TILT.items():
        rot = d["animations"][aid]["bones"]["body"]["rotation"]
        assert rot == [x, SWIM_ROT + " ?? 0.0", 0.0], rot
        d["animations"][aid]["bones"]["body"]["rotation"] = [x, SWIM_ROT, 0.0]
    R.wj(pa, d); CHANGED.append("animations/pw_squid_tilt.animation.json")
    return f"tilt_a / tilt_b: `{SWIM_ROT} ?? 0.0` -> `{SWIM_ROT}` (the game rejected the ?? and dropped both animations)"


# ------------------------------------------------------------------------------------------------ 4. enderman jaw controller
JAW_CTRL = "controller.animation.pw_enderman.jaw"
JAW_CTRL_DOC = {"format_version": "1.10.0", "animation_controllers": {JAW_CTRL: {
    "initial_state": "default",
    "states": {"default": {"on_entry": ["v.pw_em_rid = math.random(0.0, 1.0);"], "animations": ["pw_jaw"]}}}}}


def enderman_jaw(dst):
    pe = dst / "entity/enderman.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    assert d["format_version"] == "1.8.0", d["format_version"]
    sc = desc["scripts"]
    assert sc.pop("animate") == ["pw_jaw"] and sc.pop("initialize") == ["v.pw_em_rid = math.random(0.0, 1.0);"], sc
    assert desc["animations"]["pw_jaw"] == "animation.pw_enderman.jaw"
    ac = desc["animation_controllers"]; assert not any("pw_jaw" in x for x in ac)
    ac.append({"pw_jaw": JAW_CTRL})
    R.wj(pe, d); CHANGED.append("entity/enderman.entity.json")
    pc = dst / "animation_controllers/pw_enderman_jaw.animation_controllers.json"; assert not pc.exists()
    R.wj(pc, JAW_CTRL_DOC); ADDED.append("animation_controllers/pw_enderman_jaw.animation_controllers.json")
    return f"enderman (format 1.8.0): scripts.animate / initialize removed; {JAW_CTRL} plays pw_jaw (on_entry seeds v.pw_em_rid)"


# ------------------------------------------------------------------------------------------------ 5. mooshroom probe out
PROBE_FILES = ["models/entity/pw_mooshroom_bare.geo.json", "models/entity/pw_mooshroom_bare_anchored.geo.json",
               "animations/pw_mooshroom_probe.animation.json"]


def mooshroom_unprobe(dst):
    pe = dst / "entity/mooshroom.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
    for k in ("bare", "bare_anchored"): assert desc["geometry"].pop(k).startswith("geometry.pw_mooshroom_bare")
    assert desc["animations"].pop("pw_probe_hide") == "animation.pw_mooshroom.probe_hide"
    desc["scripts"]["animate"].remove("pw_probe_hide")
    assert d == R.jl(R1420 / "entity/mooshroom.entity.json"), "mooshroom entity != 1.4.20 after removing the probe"
    R.wj(pe, d); CHANGED.append("entity/mooshroom.entity.json")
    pr = dst / "render_controllers/pw_mooshroom.render.json"; rc = R.jl(pr)
    rc["render_controllers"]["controller.render.pw_mooshroom"]["geometry"] = "Array.geos[math.clamp(query.variant, 0, 1)]"
    assert rc == R.jl(R1420 / "render_controllers/pw_mooshroom.render.json"), "mooshroom RC != 1.4.20"
    R.wj(pr, rc); CHANGED.append("render_controllers/pw_mooshroom.render.json")
    for f in PROBE_FILES:
        (dst / f).unlink(); REMOVED.append(f)
    return "mooshroom entity + render controller == 1.4.20 (probe removed); 3 probe files deleted"


# ------------------------------------------------------------------------------------------------ 6. sizes
SIZE_STACK = [ROOT / "_build/rp08-148", RP06, ROOT / "_build/rp05-51"]
FORCE = ("wolf", "sheep")
SIZE_PLAN = []


def sizes(dst):
    import size_rule as SR
    rows = SR.plan(dst, SIZE_STACK, force=FORCE); SIZE_PLAN[:] = rows
    json.dump(rows, open(ROOT / "_docs/convb/size_plan_1423.json", "w"), indent=1)
    done = []
    for r in rows:
        if r["factor"] == 1.0: continue
        pe = dst / f"entity/{r['stem']}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        sc = desc.setdefault("scripts", {})
        sc["scale"] = SR.scaled_script(sc.get("scale"), r["factor"])
        R.wj(pe, d)
        if f"entity/{r['stem']}.entity.json" not in CHANGED: CHANGED.append(f"entity/{r['stem']}.entity.json")
        done.append(f"{r['stem']} x{r['factor']} ({r['action']})")
    return "client scale: " + (", ".join(done) or "no change")


# ------------------------------------------------------------------------------------------------ gate
def verify_extra(cfg, check):
    import math, numpy as np
    OLD, NEW = cfg["src"], cfg["dst"]
    import molang_lint as ML
    d = R.jl(NEW / "animations/pw_squid_tilt.animation.json")
    rots = {aid: d["animations"][aid]["bones"]["body"]["rotation"] for aid, _ in SQUID_TILT.values()}
    errs = [ML.check(e) for r in rots.values() for e in r if isinstance(e, str)]
    old_errs = [ML.check(e) for aid in rots for e in R.jl(OLD / "animations/pw_squid_tilt.animation.json")["animations"][aid]["bones"]["body"]["rotation"] if isinstance(e, str)]
    check("SQ1 squid tilt: no ?? left; A = +pitch, B = -pitch, spin = variable.squid.swim_rotation; lint flags the 1.4.22 text",
          all(e is None for e in errs) and rots == {a: [x, SWIM_ROT, 0.0] for a, x in SQUID_TILT.values()} and sum(e is not None for e in old_errs) == 2,
          f"{rots}; 1.4.22 lint errors {sum(e is not None for e in old_errs)}")
    for stem, (aid, _) in SQUID_TILT.items():
        an = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]["animations"]
        check(f"SQ2 {stem} plays {aid}", an.get("rotate") == aid, str(an.get("rotate")))
    import entity_schema_lint as ES
    en = R.jl(NEW / "entity/enderman.entity.json"); de = en["minecraft:client_entity"]["description"]
    ctl = R.jl(NEW / "animation_controllers/pw_enderman_jaw.animation_controllers.json")["animation_controllers"][JAW_CTRL]
    eo = R.jl(OLD / "entity/enderman.entity.json")["minecraft:client_entity"]["description"]
    check("EN1 enderman: no 1.8.0-invalid scripts; the jaw controller is listed and plays pw_jaw; pre_animation unchanged",
          ES.check_entity(en) == ([], []) and {"pw_jaw": JAW_CTRL} in de["animation_controllers"]
          and ctl["states"]["default"]["animations"] == ["pw_jaw"] and de["scripts"]["pre_animation"] == eo["scripts"]["pre_animation"]
          and len(ES.check_entity(R.jl(OLD / "entity/enderman.entity.json"))[0]) == 2,
          f"controllers {[list(x.values())[0] for x in de['animation_controllers']]}; scripts keys {sorted(de['scripts'])}")
    import build_rp07_1421 as B21
    worst, seen = B21.jaw_frames_check()
    check("EN2 jaw port still equals the JEM frame by frame (calm -> angry -> calm)", worst < 1e-3 and seen[0] < 0.05 and seen[1] > 0.95,
          f"worst {worst:.2e}; aggro b at frames 99/299/399 {seen}")
    for f in ("entity/mooshroom.entity.json", "render_controllers/pw_mooshroom.render.json"):
        check(f"MO1 {f} == 1.4.20 (probe out)", R.jl(NEW / f) == R.jl(R1420 / f), "")
    check("MO2 probe files gone", not any((NEW / f).exists() for f in PROBE_FILES), str(PROBE_FILES))
    # tadpole: level body, upright tail fin (the witnessed 70 deg roll gone)
    from equine_compare import bone_affines
    _, g = R.geo_file(NEW, "geometry.tadpole.patrix"); aff = bone_affines(g["bones"])
    _, go = R.geo_file(OLD, "geometry.tadpole.patrix"); affo = bone_affines(go["bones"])
    def roll(bones, aff):
        return max(math.degrees(math.asin(min(1.0, abs(float((aff[b["name"]][0] @ np.array([1.0, 0, 0]))[1]))))) for b in bones if b.get("cubes"))
    check("TP1 tadpole: every cube's side axis level (roll <= 3 deg) — 1.4.22 rolled", roll(g["bones"], aff) <= 3.0 and roll(go["bones"], affo) > 60,
          f"max roll now {roll(g['bones'], aff):.1f} deg; 1.4.22 {roll(go['bones'], affo):.1f} deg")
    # pufferfish: spike roots on the body
    from spike_root_gap import gaps
    from face_alpha_census import resolve_texture
    tp = resolve_texture("textures/entity/fish/pufferfish")
    for gid in ("geometry.pufferfish_large.patrix", "geometry.pufferfish_medium.patrix"):
        _, gn = R.geo_file(NEW, gid); _, go = R.geo_file(OLD, gid)
        gn_ = gaps(gn["bones"], gn["description"]["texture_width"], gn["description"]["texture_height"], tp)
        go_ = gaps(go["bones"], go["description"]["texture_width"], go["description"]["texture_height"], tp)
        check(f"PF1 {gid}: every spike card's nearest opaque texel <= 0.25 px from the body (1.4.22: up to {max(go_.values()):.2f})",
              len(gn_) == 8 and max(gn_.values()) <= 0.25 and max(go_.values()) >= 0.4, f"now max {max(gn_.values()):.2f} px over {len(gn_)} cards")
    _, gs = R.geo_file(NEW, "geometry.pufferfish_small.patrix"); _, gso = R.geo_file(OLD, "geometry.pufferfish_small.patrix")
    check("PF2 small pufferfish untouched", gs == gso, "")
    rows = {r["stem"]: r for r in (SIZE_PLAN or json.load(open(ROOT / "_docs/convb/size_plan_1423.json")))}
    import size_rule as SR
    after = {r["stem"]: r for r in SR.plan(NEW, SIZE_STACK, force=FORCE)}
    ok = all(abs(after[s]["current_blocks"] / after[s]["target_blocks"] - 1) < 0.01 for s in FORCE)
    moved = sorted(s for s, r in rows.items() if r["factor"] != 1.0)
    check("SZ1 wolf + sheep at the new targets (within 1 %); report every other planned mob that moved",
          ok, f"wolf {after['wolf']['current_blocks']} / {after['wolf']['target_blocks']}, sheep {after['sheep']['current_blocks']} / {after['sheep']['target_blocks']}; changed {moved}")


CFG = {
    "src": ROOT / "_build/rp07-1422", "dst": ROOT / "_build/rp07-1423", "version": "1.4.23",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.23",
    "desc": ("v1.4.23 (2026-09-29) R8 FIXES (D-C285): tadpole swims upright (was built in its on-land flop pose); pufferfish spikes grow "
             "out of the body (big + medium rebuilt from the Patrix models); squids tilt as they swim (the game had rejected the tilt); "
             "the Patrix enderman jaw actually runs; mooshroom probe removed; wolf a little bigger, sheep a little smaller."),
    "pre": [],
    "jobs": [("tadpole", "tadpole", "default", "tadpole", "default"),
             ("pufferfish large", "pufferfish", "large", "puffer_fish_big", "default"),
             ("pufferfish medium", "pufferfish", "medium", "puffer_fish_medium", "default")],
    "look": {},
    # the entity plays all three ar_pufferfish_*.swim animations on whichever form is drawn, so each form lacks the other forms'
    # bone names (tail3 = the small form's, top_back_spikes2 = the medium form's) — as the 1.4.22 geometries did
    "unbound_ok": {"pufferfish large": {"tail3", "top_back_spikes2"}, "pufferfish medium": {"tail3"}},
    "placement": {"tadpole": ("old",), "pufferfish large": ("centre", 5.5, 0.0), "pufferfish medium": ("centre", 4.0, 0.0)},
    "post": [squid_tilt, enderman_jaw, mooshroom_unprobe, sizes],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-07", "ars_stack": [RP06],
    "prec_order": [("StripMine RP 3.0.1", STRIPMINE_RP), ("RP-08", ROOT / "_build/rp08-148"), ("RP-07", ROOT / "_build/rp07-1423"), ("RP-06", RP06)],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp07_1423_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp07_1423_files.json", "w"), indent=1)

#!/usr/bin/env python3
"""build_rp07_1426.py — FA-1 (D-C294/D-C296/D-C298/D-C299). RP-07 Neutral Mobs RP v1.4.26 from v1.4.25.
  PARROT   Patrix model + FreshLX's whole animation ported (perch, flight with the second wing set, dance, shoulder, sitting);
           the dance legs + flight wings kept in the geometry and switched by the JEM's `visible` (bone scale 0/1); Java
           ParrotModel's party pose seeded (right_leg.rz = 20 deg while dancing: the JEM reads it to know it dances);
           the Patrix 1.21.11 256 px sheets (5 colours). Size (per colour) lives in BP-02 1.3.192 (model + hitbox).
  BAT      Patrix model on Mojang's bat_v2 resting / flying animations (head -> Head, wings -> leftWing / leftWingTip ...);
           the Patrix 512 px sheet already in the pack (it sat at textures/entity/bat, a path the vanilla bat_v2 never reads).
           Size in BP-02 1.3.192.
  ALLAY    Patrix model + the JEM animation ported, with Java AllayModel seeds (holding pose right_arm.rx, dancing head.rz);
           rightItem hand point (enable_attachables kept); the Patrix 1.21.11 256 px sheet.
  SNIFFER  Patrix model baked at its NEUTRAL pose (the JEM is an additive layer over Java's keyframes: it reads body.rx, head.*,
           ears — stripped for the bake) on Mojang's sniffer animations (sniff, dig, search, stand up, happy); baby = vanilla.
Texture tier: Patrix 1.21.11 128x. manifest 1.4.26, uuid kept. verify: verify_rp07_1426.py."""
import copy, io, json, math, shutil, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb_build as CB
import convb
import jem_anim_port as P
import molang_lint as ML
from convb import bake
import build_rp06_1420 as B6          # shared helpers (vgeo, placeholder, new_entity, ptex, put_png) — their file lists are B6's

ROOT = Path("/home/claude")
VRP = B6.VRP
CHANGED, ADDED, REMOVED = [], [], []


def _redirect():
    """B6 helpers append to B6's lists; this build owns its own"""
    B6.CHANGED, B6.ADDED, B6.REMOVED = CHANGED, ADDED, REMOVED


# ======================================================================================================================= PARROT
PA = {"prefix": "pw_pa", "anim": "animation.pw_parrot.jem"}
convb.KEEP_HIDDEN["parrot"] = {"left_leg", "right_leg", "left_wing_fly", "right_wing_fly"}     # switched at run time, not dropped
# a Bedrock parrot on a shoulder RIDES the player; the JEM tests shoulder first, then riding (a vehicle): riding -> 0
PX_PA = {"is_on_shoulder": "q.is_riding", "is_riding": "0.0", "is_sitting": "q.is_sitting", "time": "(q.life_time * 20.0)"}
# Java ParrotModel.prepare(PARTY): leftLeg.zRot = -0.34906584, rightLeg.zRot = 0.34906584 (the JEM: var.dance = right_leg.rz != 0)
PA_SEEDS = {"right_leg": {"rz": "q.is_dancing ? 0.34906584 : 0.0"}, "left_leg": {"rz": "q.is_dancing ? -0.34906584 : 0.0"}}


def pa_java(c):
    d = 0.34906584 if c.get("_dance") else 0.0
    return {"right_leg": {"rz": d}, "left_leg": {"rz": -d}}


def pa_env(c):
    return {"q.is_riding": 1.0 if c.get("is_on_shoulder") else 0.0, "q.is_sitting": 1.0 if c.get("is_sitting") else 0.0,
            "q.is_dancing": 1.0 if c.get("_dance") else 0.0}


def pa_port():
    b, _, _, _ = bake("parrot")
    return P.port("parrot", [x["name"] for x in b], PA["prefix"], params_extra=PX_PA, seeds=PA_SEEDS)


def parrot_setup(dst):
    _redirect()
    init, pre, anim, rep = pa_port()
    B6.port_anim(dst, "parrot", PA["anim"], init, pre, anim)
    v = ML._parse_json((VRP / "entity/parrot.entity.json").read_text(encoding="utf-8"))
    desc = v["minecraft:client_entity"]["description"]
    assert desc["geometry"] == {"default": "geometry.parrot"}, desc["geometry"]
    desc["geometry"] = {"default": "geometry.pw_parrot"}
    desc["animations"] = {"pw_jem": PA["anim"]}
    desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem"]}
    desc.pop("animation_controllers", None)
    if tuple(int(x) for x in v["format_version"].split(".")) < (1, 10, 0): v["format_version"] = "1.10.0"
    pe = dst / "entity/parrot.entity.json"; assert pe.exists()
    R.wj(pe, v); CHANGED.append("entity/parrot.entity.json")
    B6.placeholder(dst, "geometry.pw_parrot", "geometry.parrot", "pw_parrot")
    for c in ("blue", "green", "grey", "red_blue", "yellow_blue"):
        B6.put_png(dst, f"textures/entity/parrot/parrot_{c}.png", B6.ptex(f"parrot/parrot_{c}.png"))
    return f"RP-07's parrot rewritten from Mojang's definition onto geometry.pw_parrot + {PA['anim']} ({len(pre)} statements); Patrix 256 px sheets"


# ========================================================================================================================== BAT
CB.EXPLICIT["bat"] = {"Head": "head", "leftWing": "left_wing", "leftWingTip": "outer_left_wing",
                      "rightWing": "right_wing", "rightWingTip": "outer_right_wing"}
CB.PARENT_OF["bat"] = {"leftWing": "body", "rightWing": "body", "leftWingTip": "leftWing", "rightWingTip": "rightWing"}


def bat_setup(dst):
    _redirect()
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.bat_v2"} and desc["textures"] == {"default": "textures/entity/bat_v2"}, desc
        desc["geometry"] = {"default": "geometry.pw_bat"}
        desc["textures"] = {"default": "textures/entity/bat"}           # the Patrix 512 px sheet (pixel-exact, already shipped)
    B6.new_entity(dst, "bat", mut)
    B6.placeholder(dst, "geometry.pw_bat", "geometry.bat_v2", "pw_bat")
    return "RP-07 owns minecraft:bat (Mojang's definition) on geometry.pw_bat + the Patrix sheet"


# ======================================================================================================================== ALLAY
AL = {"prefix": "pw_al", "anim": "animation.pw_allay.jem"}
PX_AL = {"is_riding": "q.is_riding", "death_time": "q.death_ticks", "frame_time": "q.delta_time", "pos_y": "q.position(1)"}
_K = "math.min(q.modified_move_speed / 0.3, 1.0)"
_HOLD = "(((v.is_holding_right ?? 0.0) || (v.is_holding_left ?? 0.0)) ? 1.0 : 0.0)"
# Java AllayModel.setupAnim: rightArm.xRot = m * lerp(k, -1.0471976, -1.134464) (m = holding progress, k = min(limbSwingAmount/0.3, 1));
# dancing: head.zRot = cos(ageInTicks * 8 deg + limbSwingAmount) * 14 deg
AL_SEEDS = {"right_arm": {"rx": f"{_HOLD} * (-1.0471976 + (-1.134464 + 1.0471976) * {_K})"},
            "head": {"rz": "q.is_dancing ? math.cos(q.life_time * 20.0 * 8.0 + q.modified_move_speed * 57.2957795) * 0.2443461 : 0.0"}}


def al_java(c):
    k = min(c.get("limb_speed", 0.0) / 0.3, 1.0); m = 1.0 if c.get("_hold") else 0.0
    rz = math.cos(math.radians(c.get("age", 0.0) * 8.0) + c.get("limb_speed", 0.0)) * math.radians(14.0) if c.get("_dance") else 0.0
    return {"right_arm": {"rx": m * (-1.0471976 + (-1.134464 + 1.0471976) * k)}, "head": {"rz": rz}}


def al_env(c):
    return {**B6.common_env(c), "v.is_holding_right": 1.0 if c.get("_hold") else 0.0, "q.is_dancing": 1.0 if c.get("_dance") else 0.0}


def al_port():
    b, _, _, _ = bake("allay")
    return P.port("allay", [x["name"] for x in b], AL["prefix"], params_extra=PX_AL, seeds=AL_SEEDS)


def allay_setup(dst):
    _redirect()
    init, pre, anim, rep = al_port()
    B6.port_anim(dst, "allay", AL["anim"], init, pre, anim)
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.allay"} and desc.get("enable_attachables"), desc
        desc["geometry"] = {"default": "geometry.pw_allay"}
        desc["animations"] = {"pw_jem": AL["anim"]}
        desc.pop("animation_controllers", None)
        desc["scripts"] = {"initialize": init, "pre_animation": desc["scripts"]["pre_animation"] + pre, "animate": ["pw_jem"]}
    B6.new_entity(dst, "allay", mut)
    B6.placeholder(dst, "geometry.pw_allay", "geometry.allay", "pw_allay")
    B6.put_png(dst, "textures/entity/allay/allay.png", B6.ptex("allay/allay.png"))
    return f"RP-07 owns minecraft:allay on geometry.pw_allay + {AL['anim']} ({len(pre)} statements); Patrix 256 px sheet"


def allay_hand(dst):
    """Mojang: rightItem under body at (0, 0, -2) rot (-80, 0, 0) = 1 px below and 1 px in front of the body box. Ours: the same
    offset from the Patrix body box (between the hands when they raise to hold)."""
    from verify_rp07_1415_rp06_1410 import world_boxes
    p, g = R.geo_file(dst, "geometry.pw_allay"); by = {b["name"]: b for b in g["bones"]}
    assert "rightItem" not in by and "body" in by
    Pt = np.array([q for x in world_boxes(g["bones"]) if x[0] == "body" for q in x[2]])
    piv = [round(float((Pt[:, 0].min() + Pt[:, 0].max()) / 2), 3), round(float(Pt[:, 1].min()) - 1.0, 3), round(float(Pt[:, 2].min()) - 1.0, 3)]
    g["bones"].append({"name": "rightItem", "parent": "body", "pivot": piv, "rotation": [-80.0, 0.0, 0.0], "cubes": []})
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return f"allay rightItem {piv} rot [-80, 0, 0] under body"


# ====================================================================================================================== SNIFFER
CB.EXPLICIT["sniffer"] = {"lower_beak": "beak", "left_front_leg": "front_left_leg", "right_front_leg": "front_right_leg",
                          "left_mid_leg": "middle_left_leg", "right_mid_leg": "middle_right_leg",
                          "left_hind_leg": "back_left_leg", "right_hind_leg": "back_right_leg"}
NEUTRAL_CEM = ROOT / "_build/_cem_fa1"     # the Patrix CEM folder (symlinks) + sniffer_neutral.jem


def sniffer_neutral_cem():
    """sniffer.jem with every animation stripped (the neutral pose Java's keyframes start from), next to symlinks of every
    other Patrix JEM so ONE CEM folder serves the bake, the port and the gate"""
    src = Path(convb.CEM)
    NEUTRAL_CEM.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.jem"):
        l = NEUTRAL_CEM / f.name
        if not l.exists(): l.symlink_to(f)
    j = json.loads((src / "sniffer.jem").read_text())
    for m in j["models"]: m.pop("animations", None)
    (NEUTRAL_CEM / "sniffer_neutral.jem").write_text(json.dumps(j, indent=1))
    return j


sniffer_neutral_cem()
convb.CEM = R.CEM = P.CEM = NEUTRAL_CEM
convb.TEMPLATE_KEY["sniffer_neutral"] = "sniffer"
CB.EXPLICIT["sniffer_neutral"] = CB.EXPLICIT["sniffer"]


def sniffer_setup(dst):
    _redirect()
    def mut(desc):
        assert desc["geometry"] == {"default": "geometry.sniffer", "baby": "geometry.sniffer.baby"}, desc["geometry"]
        desc["geometry"] = {"default": "geometry.pw_sniffer", "baby": "geometry.sniffer.baby"}
    B6.new_entity(dst, "sniffer", mut)
    B6.placeholder(dst, "geometry.pw_sniffer", "geometry.sniffer", "pw_sniffer")
    return "RP-07 owns minecraft:sniffer (Mojang's definition) on geometry.pw_sniffer (neutral bake); the baby stays Mojang's"


# ========================================================================================================================= JOBS
JOBS = [("parrot", "parrot", "default", "parrot", "default"),
        ("bat", "bat", "default", "bat", "default"),
        ("allay", "allay", "default", "allay", "default"),
        ("sniffer", "sniffer", "default", "sniffer_neutral", "default")]
PRE = [parrot_setup, bat_setup, allay_setup, sniffer_setup]
def sniffer_body_pivot(dst):
    """Mojang's sniffer animations turn `body` about (0, 0, 0) (its pivot under bone (0, 19, 0)); the bake's body pivot is the
    JEM's (0, 19, 0). Cubes are absolute, so moving the pivot keeps the rest pose and makes dig / stand-up turn as authored."""
    p, g = R.geo_file(dst, "geometry.pw_sniffer"); by = {b["name"]: b for b in g["bones"]}
    assert by["body"]["pivot"] == [0.0, 19.0, 0.0] and not any(by["body"].get("rotation", [0, 0, 0])), by["body"]
    by["body"]["pivot"] = [0.0, 0.0, 0.0]
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return "sniffer body pivot (0, 19, 0) -> Mojang's (0, 0, 0)"


LOCATOR_MOBS = {"parrot": ("geometry.pw_parrot", "geometry.parrot"), "allay": ("geometry.pw_allay", "geometry.allay"),
                "sniffer": ("geometry.pw_sniffer", "geometry.sniffer")}


def carry_locators(dst):
    """D-C301: Mojang's locators (lead / lead_hold / multi_lead_1..4) onto the same-named bones of our geometry, same coordinates
    (these three sit where Mojang's do: the placement gate C). A Mojang bone our geometry lacks is logged and skipped."""
    out, skipped = {}, []
    for stem, (ours_id, van_id) in LOCATOR_MOBS.items():
        p, g = R.geo_file(dst, ours_id); by = {b["name"]: b for b in g["bones"]}
        for vb in B6.vgeo(van_id)[0]:
            for loc, xyz in (vb.get("locators") or {}).items():
                if vb["name"] not in by: skipped.append(f"{stem}:{vb['name']}.{loc}"); continue
                by[vb["name"]]["locators"] = {**(by[vb["name"]].get("locators") or {}), loc: [float(v) for v in xyz]}
                out.setdefault(stem, []).append(f"{vb['name']}.{loc}")
        d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    return f"locators carried {out}; skipped (no such bone) {skipped}"


POST = [allay_hand, sniffer_body_pivot, carry_locators]
UNBOUND_OK = {"bat": {"feet", "rightEar", "leftEar"}, "allay": {"rightItem", "look_at", "root"}, "sniffer": set()}


def _jem_parts(j):
    return {t.split(".")[0] for t, _ in P.assignments(P.rest_of(j)[0]) if not t.startswith(("var.", "varb.", "render."))}


FRAME_EXEMPT = {m: _jem_parts(m) for m in ("parrot", "allay")}
PLACEMENT = {"bat": ("centre", 5.5, 0.0), "sniffer": ("ground",), "parrot": ("ground",), "allay": ("centre", 4.0, 0.0)}
PNG_CHECKED = [f"textures/entity/parrot/parrot_{c}.png" for c in ("blue", "green", "grey", "red_blue", "yellow_blue")] + ["textures/entity/allay/allay.png"]

CFG = {
    "src": ROOT / "_build/rp07-1425", "dst": ROOT / "_build/rp07-1426", "version": "1.4.26",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.26",
    "desc": ("v1.4.26 (2026-09-29) FA-1: the parrot (perch, flight, dance, shoulder), bat, allay and sniffer on their Patrix models; "
             "parrot + allay move with Patrix's own motion, bat + sniffer with Mojang's; allay holds items; the Patrix 1.21.11 sheets. "
             "Includes all of 1.4.25."),
    "pre": PRE, "jobs": JOBS, "look": {}, "frame_exempt": FRAME_EXEMPT, "unbound_ok": UNBOUND_OK, "placement": PLACEMENT,
    "ground_bones": {"parrot": ["left_foot2", "right_foot2"]},   # the Patrix perched tail + folded wing tips droop 1.6 px below the feet (Java too)
    "post": POST, "png_checked_elsewhere": PNG_CHECKED, "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-07", "ars_stack": [ROOT / "_build/rp06-1420"],
    "verify_hooks": [], "report": ROOT / "_docs/convb/build_rp07_1426_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp07_1426_files.json", "w"), indent=1)

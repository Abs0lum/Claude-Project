#!/usr/bin/env python3
"""parrot_wing_check.py — D-C302 (his 22:31 directive): "Make sure we marry with parent/sibling connections for the parrots
wings and that they animate and move correctly."

Reads the SHIPPED RP-07 build (entity + animation + geometry), runs the parrot's pre_animation in molang_eval for each state
and moment, poses the bones (posed_preview: rotation + position channels), applies the scale channels the port uses for
visibility (0 = hidden subtree), then checks in WORLD space:
  H  hierarchy: both wing sets (folded left_wing2 / right_wing2, flight left_wing_fly / right_wing_fly) are children of body;
     each flight wing's outer segment (…_fly2) is a child of its inner segment's chain
  V  visibility: perched / sitting / dancing / shoulder = folded wings shown, flight wings hidden; flying = the reverse
  J  joints: every shown wing cube touches the body (folded, flight inner) or its inner segment (flight outer), every pose
  M  mirror: the right wing = the left wing mirrored in x (siblings move together), every pose, within MIRROR_TOL px
  S  the flight-wing fold scales (…_fly_rot sy / sz) stay in (0, 1]
Renders a sheet (front + side per state) for his eyes. Static checks only rule OUT (P1): his in-game witness rules IN.
Usage: parrot_wing_check.py [build_dir] [out.png]"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_eval as ME
import posed_preview as PP
from verify_rp07_1415_rp06_1410 import world_boxes, inside_frac
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

DST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/claude/_build/rp07-1426")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/home/claude/_docs/fa/PARROT-WINGS-CHECK.png")
GID = "geometry.pw_parrot"; TEX = "textures/entity/parrot/parrot_red_blue.png"
MIRROR_TOL = 0.05
FOLDED = {"left": "left_wing2", "right": "right_wing2"}
FLIGHT = {"left": "left_wing_fly", "right": "right_wing_fly"}
OUTER = {"left": "left_wing_fly2", "right": "right_wing_fly2"}
STATES = {                                       # state -> (env, moments in seconds)
    "perched": ({"q.is_on_ground": 1.0}, [0.0, 0.35, 0.7]),
    "walking": ({"q.is_on_ground": 1.0, "q.modified_move_speed": 0.6}, [0.0, 0.25, 0.5]),
    "flying": ({"q.is_on_ground": 0.0, "q.modified_move_speed": 0.4}, [round(0.05 * k, 2) for k in range(20)]),
    "sitting": ({"q.is_on_ground": 1.0, "q.is_sitting": 1.0}, [0.0, 0.5]),
    "dancing": ({"q.is_on_ground": 1.0, "q.is_dancing": 1.0}, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]),
    "shoulder": ({"q.is_on_ground": 0.0, "q.is_riding": 1.0}, [0.0, 0.5]),
}


def subtree(bones, root):
    kids = {}
    for b in bones: kids.setdefault(b.get("parent"), []).append(b["name"])
    out, stack = [], [root]
    while stack:
        n = stack.pop(); out.append(n); stack += kids.get(n, [])
    return out


def scales(dst, env_state, t):
    """the animation's scale channels evaluated after pre_animation (the same env pose() builds)"""
    ent = R.jl(dst / "entity/parrot.entity.json")["minecraft:client_entity"]["description"]
    env = {"q.life_time": t, "q.delta_time": 0.05, "q.is_on_ground": 1.0, "q.is_alive": 1.0, **env_state}
    for s in ent["scripts"].get("initialize", []): ME.run(s, env)
    for _ in range(3):
        for s in ent["scripts"].get("pre_animation", []): ME.run(s, env)
    a = R.jl(dst / "animations/pw_parrot.animation.json")["animations"][ent["animations"]["pw_jem"]]
    return {bn: [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in ch["scale"]]
            for bn, ch in a["bones"].items() if "scale" in ch}


def posed(dst, env_state, t):
    bones, tw, th = PP.pose(dst, "parrot", GID, t, extra_env=env_state)
    sc = scales(dst, env_state, t)
    hidden = set()
    for bn, s in sc.items():
        if min(abs(v) for v in s) < 1e-6: hidden |= set(subtree(bones, bn))
    return bones, tw, th, sc, hidden


def boxes(bones, names, hidden):
    return [x[2] for x in world_boxes(bones) if x[0] in names and x[0] not in hidden]


def touching(A, B):
    return any(inside_frac(a, b) or inside_frac(b, a) for a in A for b in B)


def mirror_err(bones, left_root, right_root, hidden):
    L = [np.array(x[2]) for x in world_boxes(bones) if x[0] in subtree(bones, left_root) and x[0] not in hidden]
    Rr = [np.array(x[2]) for x in world_boxes(bones) if x[0] in subtree(bones, right_root) and x[0] not in hidden]
    if not L and not Rr: return 0.0
    if len(L) != len(Rr): return float("inf")
    PL = np.concatenate(L) * np.array([-1, 1, 1]); PR = np.concatenate(Rr)
    # the same point set, order free: each mirrored left corner to its nearest right corner, and back
    d1 = np.sqrt(((PL[:, None, :] - PR[None, :, :]) ** 2).sum(-1)).min(1).max()
    d2 = np.sqrt(((PR[:, None, :] - PL[None, :, :]) ** 2).sum(-1)).min(1).max()
    return float(max(d1, d2))


def main():
    res, fails = [], []
    def check(tag, ok, msg=""):
        res.append((tag, ok)); print(("PASS " if ok else "FAIL ") + tag + (f" — {msg}" if msg else ""))
        if not ok: fails.append(tag)
    _, g = R.geo_file(DST, GID); by = {b["name"]: b for b in g["bones"]}
    par = lambda n: by[n].get("parent")
    chain = lambda n: [n] + (chain(par(n)) if par(n) else [])
    check("H folded + flight wings of both sides are children of body",
          all(par(FOLDED[s]) == "body" and par(FLIGHT[s]) == "body" for s in ("left", "right")),
          str({s: (par(FOLDED[s]), par(FLIGHT[s])) for s in ("left", "right")}))
    check("H each flight wing's outer segment hangs under its inner segment (…_fly -> …_fly_rot -> …_fly2)",
          all(FLIGHT[s] in chain(OUTER[s]) for s in ("left", "right")), str({s: chain(OUTER[s]) for s in ("left", "right")}))
    worst = {"J": [], "M": 0.0, "S": []}; vis_bad = []; renders = {}
    for state, (env, moments) in STATES.items():
        for t in moments:
            bones, tw, th, sc, hidden = posed(DST, env, t)
            fl_shown = {s: FLIGHT[s] not in hidden for s in ("left", "right")}
            fo_shown = {s: FOLDED[s] not in hidden for s in ("left", "right")}
            want_flight = state == "flying"
            if any(fl_shown[s] != want_flight or fo_shown[s] == want_flight for s in ("left", "right")):
                vis_bad.append((state, t, fl_shown, fo_shown))
            body = boxes(bones, {"body"}, hidden)
            for s in ("left", "right"):
                if fo_shown[s]:
                    w = boxes(bones, set(subtree(bones, FOLDED[s])), hidden)
                    if not touching(w, body): worst["J"].append((state, t, f"{s} folded wing ~ body"))
                if fl_shown[s]:
                    inner_names = set(subtree(bones, FLIGHT[s])) - set(subtree(bones, OUTER[s]))
                    inner = boxes(bones, inner_names, hidden); outer = boxes(bones, set(subtree(bones, OUTER[s])), hidden)
                    if not touching(inner, body): worst["J"].append((state, t, f"{s} flight inner ~ body"))
                    if outer and not touching(outer, inner): worst["J"].append((state, t, f"{s} flight outer ~ inner"))
                    for bn in (f"{s}_wing_fly_rot",):
                        v = sc.get(bn)
                        if v and not all(0.0 < x <= 1.0 + 1e-6 for x in v): worst["S"].append((state, t, bn, [round(x, 3) for x in v]))
            for a, b in ((FOLDED["left"], FOLDED["right"]), (FLIGHT["left"], FLIGHT["right"])):
                if a in hidden and b in hidden: continue
                worst["M"] = max(worst["M"], mirror_err(bones, a, b, hidden))
            if t == moments[0] or (state == "flying" and t in (0.1, 0.25, 0.4)) or (state == "dancing" and t == 0.4):
                renders[f"{state} t={t}"] = (bones, tw, th, hidden)
    check("V folded wings shown + flight wings hidden when not flying; the reverse in flight (both sides, every moment)",
          not vis_bad, str(vis_bad[:3]))
    check(f"J every shown wing touches its parent (folded ~ body, flight inner ~ body, flight outer ~ inner) in all "
          f"{sum(len(m) for _, m in STATES.values())} poses", not worst["J"], str(worst["J"][:4]))
    check(f"M left and right wings are mirror images in every pose (max {worst['M']:.3f} px, tol {MIRROR_TOL})", worst["M"] <= MIRROR_TOL)
    check("S the flight-wing fold scales stay in (0, 1]", not worst["S"], str(worst["S"][:3]))
    # the sheet: front + east per chosen moment
    W, H = 250, 230
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    keys = list(renders)
    sheet = Image.new("RGB", (2 * (W + 4), len(keys) * (H + 4)), (255, 255, 255))
    for i, k in enumerate(keys):
        bones, tw, th, hidden = renders[k]
        shown = [dict(b, cubes=[] if b["name"] in hidden else b.get("cubes", [])) for b in bones]
        f = truth_posed_faces(shown, tw, th, bone_affines(shown))
        for j, v in enumerate(("front", "east")):
            e, tt = camera(f, v); fl = min(0.0, min(q[1] for x in f for q in x.pts))
            im = render_entity(f, DST / TEX, e, tt, W, H, fov=FOV, floor_y=fl).convert("RGB")
            ImageDraw.Draw(im).text((4, 4), f"{k} - {v}", fill=(0, 0, 0), font=F)
            sheet.paste(im, (j * (W + 4), i * (H + 4)))
    OUT.parent.mkdir(parents=True, exist_ok=True); sheet.save(OUT)
    print(f"\n{'ALL PASS' if not fails else 'FAILS: ' + str(fails)} {len(res) - len(fails)}/{len(res)} · sheet {OUT}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

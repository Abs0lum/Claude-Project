#!/usr/bin/env python3
"""convb_build.py — turn a Converter B bake (tools/convb.py) into a SHIPPABLE geometry for one of our client entities:
the bones our animations / render controllers address keep working.

Binding rules (applied in order, per name the entity's animations or render controllers use):
  1 legs `leg0..leg3` — matched by body quadrant to the baked leg parts (Java leg1..4 / front_right_leg ... / left_arm ...),
    rotation zeroed and pivot moved to the hip (the witnessed equine rule; our walk animations swing them).
  2 EXPLICIT per-mob map (below) — reviewed by hand against the JEM part tree.
  3 the April-converter pattern: our `<n>` was the JEM submodel `<n>2` (the JEM's `<n>` is an empty vanilla placeholder):
       - if both `<n>` and `<n>2` are bound: a WRAPPER bone `<n>` is inserted as the parent of `<n>2` (pivot = `<n>2`'s,
         rotation 0) so the look rotates the whole head and the ambient wobble still reaches `<n>2`;
       - else `<n>2` is renamed `<n>`.
     The displaced empty placeholder becomes `<n>_jem`.
  4 same name, when the baked bone carries geometry in its subtree.
Anything still unbound is reported (those animation channels become no-ops, as the engine ignores missing bones).
"""
import re, sys
sys.path.insert(0, "/home/claude/tools")
from convb import bake, relocate_leg_pivots

EXPLICIT = {
    "turtle": {"right_front_leg": "right_front_fin", "left_front_leg": "left_front_fin", "right_back_leg": "right_back_fin", "left_back_leg": "left_back_fin"},
    "frog": {"body_main": "body2", "head_main": "head2", "head": "head3"},
    "panda": {"left_ear": "bone", "right_ear": "bone2"},
    # Phase B (D-C274)
    "zombie_pigman": {"rightArm": "right_arm", "leftArm": "left_arm", "rightLeg": "right_leg", "leftLeg": "left_leg"},
    "rabbit": {"nose": "bone4", "leg2_foot": "right_foot", "leg3_foot": "left_foot"},
    # D-C277
    **{m: {"rightArm": "right_arm", "leftArm": "left_arm", "rightLeg": "right_leg", "leftLeg": "left_leg"} for m in ("piglin", "piglin_brute", "bogged")},
    "guardian": {"head": "body"}, "elder_guardian": {"head": "body"},
    # spider (D-C277): our RP-07 spider.v1.8 set drives Root / body / body0 / body1 / head / left / right / leg1..8 (the April
    # rig: legs 1-4 on the -x side front->back, 5-8 on +x). Patrix: neck (scaled 0.8) > body2 > front (head, jaws, palps),
    # middle (thorax + the 8 hip stubs), back (abdomen); the 8 leg chains hang from FOOT anchors on the ground (IK style).
    "spider": {"Root": "neck", "head": "front", "body0": "middle", "body1": "back", "right": "right_jaw", "left": "left_jaw",
               "leg1": "leg_RF", "leg2": "leg_RFm", "leg3": "leg_RBm", "leg4": "leg_RB",
               "leg5": "leg_LF", "leg6": "leg_LFm", "leg7": "leg_LBm", "leg8": "leg_LB"},
    "bee": {"body1": "torso", "feeler_left": "left_antenna2", "feeler_right": "right_antenna2", "leftwing_bone": "left_wing2", "rightwing_bone": "right_wing2"},
}
# our bone that GROUPS several Patrix parts (one vanilla bone animates a pair the Patrix model splits): name -> members;
# inserted under the members' common parent, pivot = the members' mean pivot, rotation 0 (rest pose unchanged)
GROUP = {"bee": {"leg_front": ["front_right_leg", "front_left_leg"], "leg_mid": ["middle_right_leg", "middle_left_leg"],
                 "leg_back": ["back_right_leg", "back_left_leg"]}}
# our bone that should be CREATED as a child of another at the same pivot, taking over its cubes and children (the animation
# drives a "wobble" bone the Patrix part does not have): camel head2 = the whole head+neck part below the look bone
SPLIT = {"camel": {"head2": "head"}}
# Java parent the flat JEM part list loses (the part must follow its parent's animation): re-parented keeping the rest pose
PARENT_OF = {
    "camel": {"left_ear": "head2", "right_ear": "head2"},
    "rabbit": {"left_ear": "head", "right_ear": "head", "leg2_foot": "leg2", "leg3_foot": "leg3"},
    "squid": {f"tentacle{i}": "body" for i in range(1, 9)}, "glow_squid": {f"tentacle{i}": "body" for i in range(1, 9)},
    "zombie_pigman": {"head": "body", "rightArm": "body", "leftArm": "body", "rightLeg": "body", "leftLeg": "body"},
    "bee": {"body1": "body"},   # Java: bone > body (D-C277) — our bee body animations bob the whole bee (torso is bound as body1)
    # spider: hips out of the thorax (our body pitch must not lift the legs, as in the rig the animations were written for),
    # then every foot-anchored leg chain under its hip, so the walk swings the whole leg at the hip (FK; Java's FreshLX legs
    # are IK-planted — Bedrock cannot solve that)
    "spider": {**{f"leg{i}": "Root" for i in range(1, 9)},
               **{f"leg_{q}_foot": f"leg{i}" for i, q in zip(range(1, 9), ("RF", "RFm", "RBm", "RB", "LF", "LFm", "LBm", "LB"))}},
    # guardians: Java head > eye, spikes, tail0 > tail1 > tail2 — the look turns the whole guardian (EMF: OptiFine body = head)
    **{m: {"eye_part": "head", "tail1": "head", "tail2": "tail1", "tail3": "tail2", **{f"spine{i}": "head" for i in range(1, 13)}}
       for m in ("guardian", "elder_guardian")},
}
# Patrix parts renamed BEFORE binding so a vanilla animation written for a different rig does not grab them (guardian: the
# legacy move_eye / spikes / swim set absolute 1.8-format positions — "- this" — that would throw the Patrix parts; the spikes
# and tail stay static as in the shipped geometry, the look turns the whole body)
RENAME_FIRST = {m: {"eye": "eye_part"} for m in ("guardian", "elder_guardian")}
# legs whose FreshLX rest lean is kept (a compensating foot below): our leg bone becomes a hinge at the top of the leg
HINGE_LEGS = {"chicken", "ravager"}
# D-C314 (R16b full JEM ports): legs whose rest pose + pivot the port's animation is computed against - never re-pivoted / straightened
NO_LEG_RELOCATE = set()
NESTED_LEGS = {"ravager"}
# whole-model offset (px) where the Java renderer moves the model and Bedrock does not: SquidRenderer translates the model
# 1.2 blocks down about a pivot 0.5 up (net -11.2 px); vanilla Bedrock sits ~2.7 px above Java -> -8.5; the witnessed old
# squid mantle bottom (y 8) vs the new bake (y 17) -> -9 (D-C274)
MODEL_OFFSET = {"squid": [0.0, -9.0, 0.0], "glow_squid": [0.0, -9.0, 0.0]}
LEG_NAME = re.compile(r"leg\d")
LEG_CANDIDATE = re.compile(r"(^leg\d$|_leg$|^leg_|_arm$|_thigh$)")


def _subtree_has_cubes(bones, name):
    kids = {}
    for b in bones: kids.setdefault(b.get("parent"), []).append(b["name"])
    by = {b["name"]: b for b in bones}
    stack = [name]
    while stack:
        n = stack.pop()
        if by[n].get("cubes"): return True
        stack += kids.get(n, [])
    return False


def _rename(bones, old, new):
    for b in bones:
        if b["name"] == old: b["name"] = new
        if b.get("parent") == old: b["parent"] = new


def bind(bones, bind_names, ours, mob):
    """Mutates + returns bones; returns (bones, mapping, missing)."""
    by = lambda: {b["name"]: b for b in bones}
    mapping, missing = {}, []
    ob = {b["name"]: b for b in ours}
    # 1 legs by quadrant (only when our geometry has leg0..3 and the bake has leg-like root parts)
    legs = sorted(n for n in bind_names if LEG_NAME.fullmatch(n) and n in ob)
    if legs:
        cands = [b["name"] for b in bones if b.get("parent") in (None,) and LEG_CANDIDATE.search(b["name"]) and _subtree_has_cubes(bones, b["name"])]
        if mob in NESTED_LEGS:   # the Patrix legs hang inside one part (ravager: leg4 > legs > four legs)
            cands = [b["name"] for b in bones if LEG_CANDIDATE.search(b["name"]) and b.get("cubes")]
        chosen = {}
        for n in legs:
            op = ob[n].get("pivot", [0, 0, 0])
            pool = [c for c in cands if c not in chosen.values()]
            if not pool: missing.append(n); continue
            B = by()
            best = min(pool, key=lambda c: ((B[c]["pivot"][0] > 0) != (op[0] > 0)) * 100 + ((B[c]["pivot"][2] > 0) != (op[2] > 0)) * 100
                       + abs(B[c]["pivot"][0] - op[0]) + abs(B[c]["pivot"][2] - op[2]))
            chosen[n] = best
        # two-phase rename so a Java `leg1` can become our `leg0` while our `leg1` comes from Java `leg4`
        for n, c in chosen.items(): _rename(bones, c, f"__leg_tmp_{n}")
        for n in chosen:
            if n in by(): _rename(bones, n, n + "_jem")
            _rename(bones, f"__leg_tmp_{n}", n); mapping[n] = chosen[n]
    # 2 explicit
    for n, target in EXPLICIT.get(mob, {}).items():
        if n not in bind_names or n in mapping: continue
        if target not in by(): missing.append(n); continue
        if n in by() and n != target: _rename(bones, n, n + "_jem")
        _rename(bones, target, n); mapping[n] = target
    # 3 the `<n>2` pattern / 4 same name
    for n in sorted(bind_names):
        if n in mapping or n == "placeholder_bone": continue
        B = by()
        has = n in B and _subtree_has_cubes(bones, n)
        n2 = n + "2"
        if has: mapping[n] = n; continue
        if n2 in B and _subtree_has_cubes(bones, n2):
            if n in B: _rename(bones, n, n + "_jem")
            if n2 in bind_names:                                    # wrapper
                t = by()[n2]
                w = {"name": n, "parent": t.get("parent"), "pivot": list(t["pivot"]), "rotation": [0.0, 0.0, 0.0], "cubes": []}
                if w["parent"] is None: w.pop("parent")
                t["parent"] = n
                bones.insert(bones.index(t), w); mapping[n] = f"wrapper({n2})"
            else:
                _rename(bones, n2, n); mapping[n] = n2
            continue
        missing.append(n)
    names = [b["name"] for b in bones]
    dup = {x for x in names if names.count(x) > 1}
    assert not dup, (mob, dup)
    return bones, mapping, missing


FRAME_LIMIT = 45.0   # degrees: an animated bone whose rest PARENT frame is further than this from the entity frame gets a frame bone


def euler_of(M):
    """Bedrock bone rotation [rx, ry, rz] (file frame: v' = Rz(-rz) Ry(ry) Rx(-rx) v) for a rotation matrix M."""
    from scipy.spatial.transform import Rotation as Rot
    g, b, a = Rot.from_matrix(M).as_euler("ZYX", degrees=True)
    return [float(-a), float(b), float(-g)]


def _angle(M):
    import numpy as np, math
    return math.degrees(math.acos(max(-1.0, min(1.0, (float(np.trace(M)) - 1.0) / 2.0))))


LOOK_FRAME_LIMIT = 5.0   # degrees: the look bone's parent frame must be (nearly) the entity frame, or its yaw axis tilts


def align_frames(bones, animated, look=()):
    """D-C273: our animations were written for entity-aligned parent frames. For every animated bone (top-down) whose rest
    parent frame is >= FRAME_LIMIT from the entity frame, insert `<n>_frame` (pivot = the bone's pivot, rotation = the inverse
    of the parent's world rotation) and re-express the bone's own rest rotation in that entity-aligned frame. World rest pose
    of every original bone is unchanged (checked by the gate)."""
    import numpy as np
    from equine_compare import bone_affines, rot_matrix
    added = {}
    by = {b["name"]: b for b in bones}
    depth = {}
    def dep(n):
        if n not in depth: depth[n] = 0 if not by[n].get("parent") else dep(by[n]["parent"]) + 1
        return depth[n]
    for n in sorted((x for x in animated if x in by), key=dep):
        b = by[n]; par = b.get("parent")
        if not par: continue
        aff = bone_affines(bones)
        Wp = aff[par][0]; Wb = aff[n][0]
        if _angle(Wp) < (LOOK_FRAME_LIMIT if n in look else FRAME_LIMIT): continue
        f = {"name": n + "_frame", "parent": par, "pivot": list(b["pivot"]), "rotation": [round(v, 4) for v in euler_of(Wp.T)], "cubes": []}
        bones.insert(bones.index(b), f); by[f["name"]] = f; depth[f["name"]] = dep(par) + 1
        b["parent"] = f["name"]; b["rotation"] = [round(v, 4) for v in euler_of(Wb)]
        depth.clear()
        added[n] = {"parent_frame_deg": round(_angle(Wp), 1), "frame_rot": f["rotation"], "new_rest": b["rotation"]}
    return bones, added


def _subtree(bones, name):
    out, stack = [], [name]
    while stack:
        n = stack.pop(); out.append(n); stack += [b["name"] for b in bones if b.get("parent") == n]
    return out


def _shift_subtree(bones, name, d):
    names = set(_subtree(bones, name))
    for b in bones:
        if b["name"] in names:
            b["pivot"] = [b["pivot"][k] + d[k] for k in range(3)]
            for c in b.get("cubes", []):
                c["origin"] = [c["origin"][k] + d[k] for k in range(3)]
                if "pivot" in c: c["pivot"] = [c["pivot"][k] + d[k] for k in range(3)]


def reparent(bones, child, parent):
    """Make `parent` the parent of `child` keeping every world rest transform: the child's local rotation becomes
    W_parent^T W_child, its file-frame pivot the parent-frame image of its world pivot, and its whole subtree is translated
    by the same amount (Bedrock pivots / cube origins are file-frame coordinates)."""
    import numpy as np
    from equine_compare import bone_affines
    aff = bone_affines(bones); by = {b["name"]: b for b in bones}
    Ap, tp = aff[parent]; Wc = aff[child][0]
    c = by[child]; old_par = c.get("parent")
    A0, t0 = aff[old_par] if old_par else (np.eye(3), np.zeros(3))
    pw = A0 @ np.array(c["pivot"], float) + t0
    piv_new = Ap.T @ (pw - tp)
    d = [float(piv_new[k] - c["pivot"][k]) for k in range(3)]
    _shift_subtree(bones, child, d)
    c["rotation"] = [round(v, 4) for v in euler_of(Ap.T @ Wc)]
    c["parent"] = parent
    return bones


def split_bone(bones, new, base):
    """Create `new` as a child of `base` at the same pivot, rotation 0, taking over base's cubes and children."""
    by = {b["name"]: b for b in bones}; b = by[base]
    nb = {"name": new, "parent": base, "pivot": list(b["pivot"]), "rotation": [0.0, 0.0, 0.0], "cubes": b.get("cubes", [])}
    if b.get("mirror"): nb["mirror"] = True
    b["cubes"] = []
    for x in bones:
        if x.get("parent") == base: x["parent"] = new
    bones.insert(bones.index(b) + 1, nb)
    return bones


def hinge_legs(bones, names):
    """Our leg bone -> a hinge at the top-centre of the leg's boxes (rotation 0); the posed Patrix leg becomes `<leg>_pose`."""
    import numpy as np
    from verify_rp07_1415_rp06_1410 import world_boxes
    for n in sorted(names):
        by = {b["name"]: b for b in bones}
        if n not in by: continue
        sub = set(_subtree(bones, n))
        P = np.array([p for x in world_boxes(bones) if x[0] in sub for p in x[2]])
        top = [float((P[:, 0].min() + P[:, 0].max()) / 2), float(P[:, 1].max()), float((P[:, 2].min() + P[:, 2].max()) / 2)]
        b = by[n]; pose = n + "_pose"
        for x in bones:
            if x.get("parent") == n: x["parent"] = pose
        h = {"name": n, "pivot": top, "rotation": [0.0, 0.0, 0.0], "cubes": []}
        if b.get("parent"): h["parent"] = b["parent"]
        b["name"] = pose; b["parent"] = n
        bones.insert(bones.index(b), h)
    return bones


def build_mob(jname, mob_key, bind_names, ours, look_bones=()):
    import numpy as np
    from equine_compare import bone_affines
    bones, tw, th, info = bake(jname)
    for a_, b_ in RENAME_FIRST.get(mob_key, {}).items(): _rename(bones, a_, b_)
    if mob_key in MODEL_OFFSET:
        for b in bones:
            if not b.get("parent"): _shift_subtree(bones, b["name"], MODEL_OFFSET[mob_key])
    bones, mapping, missing = bind(bones, set(bind_names) - set(SPLIT.get(mob_key, {})) - set(GROUP.get(mob_key, {})), ours, mob_key)
    for gname, members in GROUP.get(mob_key, {}).items():
        by_ = {b["name"]: b for b in bones}
        if gname not in bind_names or not all(m_ in by_ for m_ in members): continue
        pars = {by_[m_].get("parent") for m_ in members}; assert len(pars) == 1, (mob_key, gname, pars)
        piv = [sum(by_[m_]["pivot"][k] for m_ in members) / len(members) for k in range(3)]
        g = {"name": gname, "pivot": piv, "rotation": [0.0, 0.0, 0.0], "cubes": []}
        if pars != {None}: g["parent"] = pars.pop()
        bones.insert(min(bones.index(by_[m_]) for m_ in members), g)
        for m_ in members: by_[m_]["parent"] = gname
        mapping[gname] = f"group({'+'.join(members)})"
    for new, base in SPLIT.get(mob_key, {}).items():
        if base in {b["name"] for b in bones}: bones = split_bone(bones, new, base); mapping[new] = f"split({base})"
    from verify_rp07_1415_rp06_1410 import world_boxes
    w0 = {(x[0], x[1]): np.array(x[2]) for x in world_boxes(bones)}
    for child, parent in PARENT_OF.get(mob_key, {}).items():
        names_now = {b["name"] for b in bones}
        if child in names_now and parent in names_now: bones = reparent(bones, child, parent)
    w1 = {(x[0], x[1]): np.array(x[2]) for x in world_boxes(bones)}
    reparent_err = max((float(np.abs(w0[k] - w1[k]).max()) for k in w0), default=0.0)
    assert set(w0) == set(w1) and reparent_err < 1e-3, (mob_key, reparent_err)
    legs = {n for n in bind_names if LEG_NAME.fullmatch(n)}
    if mob_key in HINGE_LEGS: bones = hinge_legs(bones, legs)
    elif mob_key in NO_LEG_RELOCATE: pass
    else: bones = relocate_leg_pivots(bones, legs)
    before = bone_affines(bones)
    bones, frames = align_frames(bones, set(bind_names) | set(look_bones), look=set(look_bones))
    after = bone_affines(bones)
    frame_err = max((float(np.abs(before[n][0] - after[n][0]).max() + np.abs(before[n][1] - after[n][1]).max()) for n in before), default=0.0)
    for b in bones:
        if b.get("parent") is None: b.pop("parent", None)
        b["pivot"] = [round(float(v), 4) + 0.0 for v in b["pivot"]]
        b["rotation"] = [round(float(v), 3) + 0.0 for v in b.get("rotation", [0, 0, 0])]
    have = {b["name"] for b in bones}
    missing = [m for m in dict.fromkeys(missing) if m not in SPLIT.get(mob_key, {}) and not (m in have and _subtree_has_cubes(bones, m))]
    return bones, tw, th, {"mapping": mapping, "missing": missing, "frames": frames, "frame_err": frame_err, "reparent_err": reparent_err,
                           **{k: info[k] for k in ("hidden_at_rest", "dropped", "rotations", "pivot_shift")}}

#!/usr/bin/env python3
"""std_flight.py — Phase 3a (D-C369): the FLIGHT wing for folded-wing birds (his T2: Patrix's two-wing system).

For a FLIGHT-class bird whose wings rest FOLDED (span not mostly sideways), the staged standard wing chain becomes the
FOLD system (every bone prefixed `fold_`), and a COPY of it becomes the FLIGHT wing under the template names, re-posed:
a new joint `shoulder_spread_<s>` (cubeless, at the shoulder pivot, between the shoulder and its parent) carries a BIND
rotation that turns the folded wing out to the side:   span -> (±1, -0.15, 0) (slight droop), plate normal -> up,
chord -> backward. Visibility: the flight wing is drawn only while !q.is_on_ground, the fold wing only on the ground
(animation `animation.std.<slug>.wing_mode`, always played).
Spread-resting birds (AnF eagles / gulls / terns / hawks / vultures, bat, phantom …) keep one chain: it IS the flight wing.
"""
import copy
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
from equine_compare import bone_affines, rot_matrix  # noqa: E402
import std_cube as CU  # noqa: E402

DROOP = -0.15


def subtree(bones, top):
    names, stack = [], [top]
    while stack:
        n = stack.pop(0)
        names.append(n)
        stack += [b["name"] for b in bones if b.get("parent") == n]
    return names


def world_point(aff, name, p):
    A, t = aff[name]
    return A @ np.array(p, float) + t


def wing_frame(bones, side):
    """(span, normal, chord) unit vectors of the bind-pose wing in world space, and the shoulder pivot."""
    aff = bone_affines(bones)
    by = {b["name"]: b for b in bones}
    sh = f"shoulder_{side}"
    sp = world_point(aff, sh, by[sh].get("pivot", [0, 0, 0]))
    pts, normals = [], []
    for n in subtree(bones, sh):
        b = by[n]
        for c in b.get("cubes") or []:
            s = np.array(c["size"], float)
            pts.append(world_point(aff, n, CU.centre(c)))           # cube rotation applied
            if n.startswith("wing_inner"):
                k = int(np.argmin(np.abs(s)))
                normals.append(aff[n][0] @ CU.axis(c, k))
    tip = max(pts, key=lambda p: np.linalg.norm(p - sp))
    span = (tip - sp) / np.linalg.norm(tip - sp)
    nrm = normals[0] if normals else np.array([0.0, 1.0, 0.0])
    nrm = nrm - span * (nrm @ span)
    nrm /= np.linalg.norm(nrm)
    # the wing's TOP surface: a folded wing's dorsal side faces AWAY from the body (it becomes the top in flight); a wing
    # lying flat on the back faces up
    sgn = 1.0 if side == "l" else -1.0
    if abs(nrm[0]) >= abs(nrm[1]):
        if nrm[0] * sgn < 0:
            nrm = -nrm
    elif nrm[1] < 0:
        nrm = -nrm
    chord = np.cross(span, nrm)  # right-handed frame (the target frame is built the same way -> a proper rotation)
    return span, nrm, chord, sp


def is_spread(span):
    return abs(span[0]) > max(abs(span[1]), abs(span[2]))


def euler_for(R):
    """Bedrock-convention euler (degrees) whose rot_matrix equals R (least squares, a few starts)."""
    best = None
    for start in ([0, 0, 0], [90, 0, 0], [0, 90, 0], [0, 0, 90], [180, 0, 0], [0, 180, 0], [-90, 0, 0], [0, -90, 0]):
        r = least_squares(lambda e: (rot_matrix(list(e)) - R).ravel(), start)
        if best is None or r.cost < best.cost:
            best = r
    assert best.cost < 1e-8, f"no euler for the spread rotation (cost {best.cost})"
    return [round(float(x), 4) for x in best.x]


def add_flight_wing(bones, side):
    """returns (bones, info). Fold system renamed fold_*, flight copy re-posed spread under shoulder_spread_<s>."""
    bones = copy.deepcopy(bones)
    span, nrm, chord, sp = wing_frame(bones, side)
    sh = f"shoulder_{side}"
    chain = subtree(bones, sh)
    by = {b["name"]: copy.deepcopy(b) for b in bones}  # snapshot BEFORE the fold rename (the copies keep these names)
    # 1) the resting chain becomes the fold system
    fold = {n: f"fold_{n}" for n in chain}
    for b in bones:
        if b["name"] in fold:
            b["name"] = fold[b["name"]]
        if b.get("parent") in fold:
            b["parent"] = fold[b["parent"]]
    # 2) the flight copy under a spread joint
    sgn = 1.0 if side == "l" else -1.0
    t_span = np.array([sgn, DROOP, 0.0])
    t_span /= np.linalg.norm(t_span)
    t_nrm = np.array([0.0, 1.0, 0.0])
    t_nrm -= t_span * (t_nrm @ t_span)
    t_nrm /= np.linalg.norm(t_nrm)
    t_chord = np.cross(t_span, t_nrm)
    R_world = np.column_stack([t_span, t_nrm, t_chord]) @ np.column_stack([span, nrm, chord]).T
    parent = by[sh].get("parent")
    aff = bone_affines([b for b in bones])
    Ap = aff[fold.get(parent, parent)][0] if parent else np.eye(3)
    R_local = Ap.T @ R_world @ Ap
    spread = {"name": f"shoulder_spread_{side}", "pivot": list(by[sh].get("pivot", [0, 0, 0])),
              "rotation": euler_for(R_local)}
    if parent:
        spread["parent"] = parent
    copies = []
    for n in chain:
        b = copy.deepcopy(by[n])
        if n == sh:
            b["parent"] = spread["name"]
        copies.append(b)
    bones = bones + [spread] + copies
    return bones, {"span": [round(float(x), 3) for x in span], "spread_rotation": spread["rotation"]}


def wing_mode_animation(sides):
    bones = {}
    for s in sides:
        bones[f"shoulder_spread_{s}"] = {"scale": "q.is_on_ground ? 0.0 : 1.0"}
        bones[f"fold_shoulder_{s}"] = {"scale": "q.is_on_ground ? 1.0 : 0.0"}
    return {"loop": True, "bones": bones}


# ====================================================================== the standard flight animation (Phase 3a)
import math  # noqa: E402
import std_stepc as SC  # noqa: E402

PARROT_WS, PARROT_T = 1.0, 0.35          # macaw wingspan ≈ 1.0 m flaps once per 7 ticks (0.35 s) — the reference
GLIDE_FROM = 1.5                          # wingspan (m) from which a bird glides between flap bursts (his A2)


def wingspan(row):
    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            import re
            m = re.findall(r"[0-9.]+", str(x))
            return float(m[0]) if m else None
    real = (row or {}).get("real") or {}
    if num(real.get("WS")):
        return num(real["WS"])
    L = num(real.get("L")) or num(real.get("max")) or 0.35
    return 1.6 * L


def flap_period(ws):
    """his A2: size-scaled flap speed — period ∝ wingspan^0.6 through the parrot's 0.35 s at 1.0 m, clamped."""
    return max(0.14, min(0.9, PARROT_T * (ws / PARROT_WS) ** 0.6))


def local_axes(bones, joint):
    """(span_k, chord_k): local axis indices of the plate hanging from `joint` — span = the axis its child piece reaches
    along from the joint, chord = the plate's in-plane axis across it (the hinge line), normal = its thinnest axis."""
    piece, frontier = None, [joint]
    while frontier and piece is None:  # the first cube-carrying descendant (breadth first)
        kids = [b for b in bones if b.get("parent") in frontier]
        piece = next((b for b in kids if b.get("cubes")), None)
        frontier = [b["name"] for b in kids]
    if piece is None:
        return None
    jp = np.array(next(b for b in bones if b["name"] == joint).get("pivot", [0, 0, 0]), float)
    import std_wingsplit as W
    span = W.span_axis(piece["cubes"], jp)
    size = np.array([max(abs(c["size"][k]) for c in piece["cubes"]) for k in range(3)])
    others = [k for k in range(3) if k != span]
    normal = min(others, key=lambda k: size[k])
    chord = [k for k in others if k != normal][0]
    return span, chord


def sign_for(bones, joint, axis, tip_bone, want_world):
    """+1 / -1: the sign of a rotation about local `axis` of `joint` that moves `tip_bone`'s centre along
    `want_world` (a world direction), measured numerically on the bind pose."""
    by = {b["name"]: b for b in bones}

    def centre(add):
        aff = bone_affines(bones, add_rot={joint: add})
        A, t = aff[tip_bone]
        cs = by[tip_bone]["cubes"]
        c = np.mean([CU.centre(x) for x in cs], axis=0)
        return A @ c + t
    d = [0.0, 0.0, 0.0]
    d[axis] = 5.0
    move = centre(d) - centre([0.0, 0.0, 0.0])
    return 1.0 if move @ np.array(want_world, float) >= 0 else -1.0


def wing_axes(bones, side):
    """(span_k, chord_k) for the whole flight wing of `side`, in the wing's own local frame: span = the axis along which
    the wing's pieces lie farthest from the shoulder pivot (their mean), normal = the thinnest, chord = the remaining
    in-plane axis = the direction of every cut line = the hinge axis for elbow / wrist / primary joints."""
    names = {b["name"] for b in bones}
    sh = f"shoulder_{side}"
    chain = subtree(bones, sh)
    by = {b["name"]: b for b in bones}
    piv = np.array(by[sh].get("pivot", [0, 0, 0]), float)
    cubes = [c for n in chain for c in by[n].get("cubes") or []]
    cen = np.mean([CU.centre(c) for c in cubes], axis=0)
    span = int(np.argmax(np.abs(cen - piv)))
    size = np.array([max(abs(c["size"][k]) for c in cubes) for k in range(3)])
    others = [k for k in range(3) if k != span]
    normal = min(others, key=lambda k: size[k])
    chord = [k for k in others if k != normal][0]
    return span, chord


def flight_animation(bones, sides, T, glide, gate="1.0", hinges=None):
    """Molang for the standard flight. p = phase (deg) = 360·(q.life_time + v.std_r)/T.
    shoulder_fly: flap ±A (wing tip up at p = 90), sweep ±15 (a quarter-beat late), twist ±18 (leading edge down on
    the downstroke); elbow / wrist / primaries bend ONLY about their hinge (chord) line — tip lags on the upstroke, a
    travelling curl outward along the primaries. Bend = amp·(1 + cos(p − lag))/2: full at mid-UPSTROKE (p = 0, wing
    rising through level), zero at mid-downstroke (p = 180: the wing straight while it pushes down). [12:40 fix: v2.0
    had (1 − cos), which peaked the curl mid-downstroke and rolled the tips under the body.] Big birds (glide) beat in bursts: amplitude × the glide envelope.
    gate: a Molang factor on every amplitude (v2: the unfold's flap envelope).
    hinges: {joint: file-frame unit axis} for wings whose plates carry cube rotations — those joints bend by an exact
    rotation about that axis (std_cube.hinge_molang) instead of one local channel."""
    A = 55.0 if T < 0.25 else (50.0 if T < 0.5 else 40.0)
    ph = f"((q.life_time + v.std_r) * {360.0 / T:.3f})"
    env = (f"math.clamp(0.5 + 1.6 * math.sin((q.life_time + v.std_r) * {360.0 / (T * 6):.3f}), 0.15, 1.0)"
           if glide else "1.0")
    g = "" if gate == "1.0" else f" * {gate}"
    hinges = hinges or {}
    out = {}
    for s in sides:
        up = [0.0, 1.0, 0.0]
        tip = f"primary_{s}_3" if any(b["name"] == f"primary_{s}_3" for b in bones) else f"wing_inner_{s}"
        sh = f"shoulder_fly_{s}"
        # flap about the body's forward axis (z), sweep about y, twist about x — signs measured on the rig
        sf = sign_for(bones, sh, 2, tip, up)
        ss = sign_for(bones, sh, 1, tip, [0, 0, -1])           # + = tip forward
        out[sh] = {"rotation": [f"({18.0:.1f} * math.cos({ph}) * {env}){g}",
                                f"({ss * 15.0:.1f} * math.sin({ph} - 60) * {env}){g}",
                                f"({sf * A:.1f} * math.sin({ph}) * {env} + {sf * 6.0:.1f} * (1 - {env})){g}"]}
        lag = 0
        for j in [f"elbow_{s}", f"wrist_{s}", f"primary_base_{s}_1", f"primary_base_{s}_2", f"primary_base_{s}_3"]:
            jb = next((b for b in bones if b["name"] == j), None)
            if jb is None or any(jb.get("rotation") or [0, 0, 0]):
                continue  # only zero-bind joints are bent (a pure rotation about one local axis)
            amp = {f"elbow_{s}": 10.0, f"wrist_{s}": 15.0}.get(j, 7.0)
            if j in hinges:
                u = hinges[j]
                sg = sign_for_axis(bones, j, u, tip, [0, -1, 0])  # + = tip down
                theta = f"{sg * amp:.1f} * (1 + math.cos({ph} - {lag})) * 0.5 * {env}{g}"
                out[j] = {"rotation": CU.hinge_molang(u, theta)}
            else:
                span_k, chord_k = wing_axes(bones, s)
                sg = sign_for(bones, j, chord_k, tip, [0, -1, 0])     # + = tip down
                rot = ["0", "0", "0"]
                rot[chord_k] = f"({sg * amp:.1f} * (1 + math.cos({ph} - {lag})) * 0.5 * {env}){g}"
                out[j] = {"rotation": rot}
            lag += 25
    return {"loop": True, "bones": out}


def sign_for_axis(bones, joint, u, tip_bone, want_world):
    """+1 / -1: the sign of a rotation about the file-frame axis u (through the joint pivot) that moves the tip along
    want_world (measured on the bind pose; the joint has zero bind, so the euler of the rotation is exact)."""
    by = {b["name"]: b for b in bones}

    def centre(deg):
        aff = bone_affines(bones, add_rot={joint: CU.euler_of(CU.rodrigues(u, deg))})
        A, t = aff[tip_bone]
        return A @ np.mean([CU.centre(x) for x in by[tip_bone]["cubes"]], axis=0) + t
    move = centre(5.0) - centre(0.0)
    return 1.0 if move @ np.array(want_world, float) >= 0 else -1.0


def rotated_wing(bones, side):
    """True when any plate of the wing carries a cube rotation that is not a multiple of 90 degrees."""
    by = {b["name"]: b for b in bones}
    return any(not CU.axis_aligned(c) for n in subtree(bones, f"shoulder_{side}") for c in by[n].get("cubes") or [])


def hinge_plan(bones, side, top_world):
    """for a wing with rotated plates: {joint: (pivot or None, file-frame axis)}. Each hinge lies on the edge the two
    neighbouring pieces share (cube rotation applied); on thick plates the edge on the TOP face (the face that is up in
    flight). The tip only bends down: hinged on the top face the top edges stay touching and the lower edges press
    together; hinged mid-plate or below, the top face opens (measured v1: 0.54 px; cardinal mid-plate 0.27 px). Pieces that share no edge (a curved,
    overlapping wing) bend about the outer piece's own chord axis at the joint's own pivot."""
    by = {b["name"]: b for b in bones}
    aff = bone_affines(bones)
    pieces = [f"wing_inner_{side}"] + sorted([n for n in by if n.startswith(f"primary_{side}_") and
                                              n.rsplit("_", 1)[1].isdigit()], key=lambda n: int(n.rsplit("_", 1)[1]))
    pairs = {f"elbow_{side}": (0, 1), f"wrist_{side}": (0, 1), f"primary_base_{side}_1": (0, 1)}
    for k in range(2, len(pieces)):
        pairs[f"primary_base_{side}_{k}"] = (k - 1, k)
    plan = {}
    for j, (ia, ib) in pairs.items():
        if j not in by or ib >= len(pieces) or any(by[j].get("rotation") or [0, 0, 0]):
            continue
        a, b = pieces[ia], pieces[ib]
        ca = [p for c in by[a].get("cubes") or [] for p in CU.corners(c)]
        cb = [p for c in by[b].get("cubes") or [] for p in CU.corners(c)]
        shared = []
        for p in ca:
            if any(np.linalg.norm(p - q) < 1e-3 for q in cb) and not any(np.linalg.norm(p - x) < 1e-3 for x in shared):
                shared.append(p)
        if len(shared) >= 2:
            # the plate's own normal (its thinnest cube axis) splits the shared face into its two face edges; the one
            # on the side that is UP in flight is the hinge line
            # (the wing's thinnest extent, in the inner plate's cube frame: a small cut piece can be thinner along
            # its span than through the plate — the cardinal's primary 0.88 px vs 1 px)
            cpl = max(by[pieces[0]]["cubes"], key=lambda c: np.prod(np.abs(c["size"]) + 1e-3))
            Rp = CU.cube_R(cpl)
            allp = np.array([Rp.T @ p for n in pieces for c in by[n].get("cubes") or [] for p in CU.corners(c)])
            k_thin = int(np.argmin(allp.max(axis=0) - allp.min(axis=0)))
            n_f = CU.axis(cpl, k_thin)
            if (aff[a][0] @ n_f) @ np.array(top_world, float) < 0:
                n_f = -n_f
            h = [float(p @ n_f) for p in shared]
            low = [p for p, v in zip(shared, h) if v >= max(h) - 1e-3]   # the TOP-face edge (name kept from v2.0)
            if len(low) < 2:
                low = shared
            p0 = low[0]
            p1 = max(low, key=lambda x: np.linalg.norm(x - p0))
            u = (p1 - p0) / np.linalg.norm(p1 - p0)
            plan[j] = ([round(float(x), 5) for x in (p0 + p1) / 2], u)
        else:
            c = max(by[b]["cubes"], key=lambda c: np.prod(np.abs(c["size"]) + 1e-3))
            piv = np.array(by[j].get("pivot", [0, 0, 0]), float)
            reach = CU.centre(c) - piv
            span_k = int(np.argmax([abs(CU.axis(c, k) @ reach) for k in range(3)]))
            others = [k for k in range(3) if k != span_k]
            normal_k = min(others, key=lambda k: abs(c["size"][k]))
            chord_k = [k for k in others if k != normal_k][0]
            plan[j] = (None, CU.axis(c, chord_k))
    return plan


def build(mob, P, plan_row, census_row):
    """Stage the flight system for one FLIGHT bird. Returns a report dict."""
    rp = P.path.name
    st = SC.Staged(rp, mob)
    geo = st.geo["minecraft:geometry"][0]
    assert not any(b["name"].startswith(("shoulder_fly_", "fold_shoulder_")) for b in geo["bones"]), "already built"
    sides = [s for s in ("l", "r") if any(b["name"] == f"shoulder_{s}" for b in geo["bones"])]
    folded = False
    rep = {"mob": mob}
    for s in sides:
        span, nrm, chord, sp = wing_frame(geo["bones"], s)
        if not is_spread(span):
            folded = True
    if folded:
        snap = copy.deepcopy(geo["bones"])
        for s in sides:
            for n in subtree(snap, f"shoulder_{s}"):
                st.rename(n, f"fold_{n}")
        geo = st.geo["minecraft:geometry"][0]
        for s in sides:
            # the flight copy is built from the snapshot (template names), placed under shoulder_spread_<s>
            fb, info = add_flight_wing(snap, s)
            spread = next(b for b in fb if b["name"] == f"shoulder_spread_{s}")
            chain = subtree(snap, f"shoulder_{s}")
            copies = [copy.deepcopy(b) for b in snap if b["name"] in chain]
            for b in copies:
                if b["name"] == f"shoulder_{s}":
                    b["parent"] = spread["name"]
            geo["bones"] += [spread] + copies
            rep[f"spread_{s}"] = info["spread_rotation"]
    # the animated root of each flight wing: zero bind, body-aligned axes
    for s in sides:
        top = f"shoulder_spread_{s}" if folded else f"shoulder_{s}"
        SC.insert_above(geo, top, f"shoulder_fly_{s}")
    # hinge lines on the UNDERSIDE of thick plates: the tip only bends down, so with the hinge on the lower face the lower
    # edges stay touching (WING-CONTACT) and the upper edges close together instead of opening a gap
    aff = bone_affines(geo["bones"])
    for s in sides:
        span_k, chord_k = wing_axes(geo["bones"], s)
        normal_k = [k for k in range(3) if k not in (span_k, chord_k)][0]
        chain = subtree(geo["bones"], f"shoulder_{s}")
        by = {b["name"]: b for b in geo["bones"]}
        cubes = [c for n in chain for c in by[n].get("cubes") or []]
        lo = min(min(c["origin"][normal_k], c["origin"][normal_k] + c["size"][normal_k]) for c in cubes)
        hi = max(max(c["origin"][normal_k], c["origin"][normal_k] + c["size"][normal_k]) for c in cubes)
        if hi - lo < 1e-6:
            continue
        for j in (f"elbow_{s}", f"wrist_{s}", f"primary_base_{s}_1", f"primary_base_{s}_2", f"primary_base_{s}_3"):
            b = by.get(j)
            if b is None or any(b.get("rotation") or [0, 0, 0]):
                continue
            A, t = aff[j]
            e = np.zeros(3)
            e[normal_k] = 1.0
            down_is_lo = (A @ e)[1] > 0          # +normal points up in the world -> the underside is the low end
            pv = list(b.get("pivot", [0, 0, 0]))
            pv[normal_k] = hi if down_is_lo else lo   # (measured: the other face opened a 0.54 px gap)
            b["pivot"] = pv
    ws = wingspan(plan_row)
    T = flap_period(ws)
    glide = ws >= GLIDE_FROM
    anim = flight_animation(geo["bones"], sides, T, glide)
    slug = S.slug_of(mob)
    st.anim["animations"][f"animation.std.{slug}.flight"] = anim
    if folded:
        st.anim["animations"][f"animation.std.{slug}.wing_mode"] = wing_mode_animation(sides)
    st.save()
    # entity: play the flight while airborne, wing_mode always, a per-mob phase offset
    ef = S.STAGE / rp / f"entity/std/{slug}.entity.json"
    ent = S.jload(ef)
    d = ent["minecraft:client_entity"]["description"]
    d.setdefault("animations", {})["std_flight"] = f"animation.std.{slug}.flight"
    sc = d.setdefault("scripts", {})
    sc.setdefault("animate", [])
    sc["animate"] = [a for a in sc["animate"] if not (isinstance(a, dict) and "std_flight" in a) and a != "std_wing_mode"]
    sc["animate"].append({"std_flight": "!q.is_on_ground"})
    if folded:
        d["animations"]["std_wing_mode"] = f"animation.std.{slug}.wing_mode"
        sc["animate"].append("std_wing_mode")
    init = sc.setdefault("initialize", [])
    if not any("v.std_r" in x for x in init):
        init.append("v.std_r = math.random(0.0, 1.0);")
    ef.write_text(json.dumps(ent, indent=1))
    rep.update({"folded": folded, "wingspan": round(ws, 2), "period": round(T, 3), "glide": glide,
                "bent_joints": sorted(k for k in anim["bones"] if not k.startswith("shoulder_fly"))})
    return rep


# ====================================================================== v2 (his 11:52 rulings): one wing, double hinge
# on a TRACK SLIDE at the wing's north-edge centre, unfold transition, flight stretch, leg tuck
U_EXPR = "v.std_u"
TARGET_ASPECT = 3.0   # wing length / chord in flight (his H3: "more rectangular than square")


def ease(a, b, x=U_EXPR):
    t = f"math.clamp(({x} - {a}) / {b - a}, 0, 1)"
    return f"({t} * {t} * (3 - 2 * {t}))"


def to_frame(aff, parent, p_world):
    if not parent:
        return np.array(p_world, float)
    A, t = aff[parent]
    return np.linalg.solve(A, np.array(p_world, float) - t)


def fit_fwd_out(R):
    """R ≈ rot_matrix([0, b, 0]) @ rot_matrix([g, 0, a]): forward swing b (about y) after an out-lift a (z) + roll g (x).
    Of all exact solutions (angles wrapped to ±180) the SMALLEST total turn is taken — the unfold path stays short."""
    def wrap(x):
        return (x + 180.0) % 360.0 - 180.0
    sols = []
    for b0 in (-150, -90, -45, 0, 45, 90, 150):
        for a0 in (-120, -60, 0, 60, 120):
            for g0 in (-120, -60, 0, 60, 120):
                r = least_squares(lambda e: (rot_matrix([0, e[0], 0]) @ rot_matrix([e[2], 0, e[1]]) - R).ravel(), [b0, a0, g0])
                if r.cost < 1e-12:
                    sols.append(tuple(wrap(float(x)) for x in r.x))
    assert sols, "no exact forward / out decomposition"
    # his motion: OUT first, then FORWARD — roll only orients the surface: least roll first, then the shortest path
    b, a, g = min(sols, key=lambda t: (round(abs(t[2]) / 5.0), abs(t[0]) + abs(t[1])))
    return round(b, 3), round(a, 3), round(g, 3), 0.0


def leg_tuck_from(anims, slug):
    """the bird's own airborne leg pose (its fly-type animation's constant leg rotations) — the library's tuck."""
    import re
    out = {}
    for aid, a in anims.items():
        if not re.search(r"fly|flying|flap|glide|soar", aid):
            continue
        for k, ch in (a.get("bones") or {}).items():
            if not re.match(r"(hip|thigh|knee|shin|ankle|foot|toe|thighs|shins|feet|toes|legs)", k):
                continue
            r = ch.get("rotation")
            if isinstance(r, list) and all(isinstance(x, (int, float)) for x in r):
                out.setdefault(k, r)
            elif isinstance(r, dict):  # keyframes: take the first
                v = next(iter(r.values()))
                v = v.get("post", v.get("pre")) if isinstance(v, dict) else v
                if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                    out.setdefault(k, v)
    return out


def strip_airborne(anims, slug, bone_names):
    """remove wing + leg channels from the bird's own airborne animations (the standard flight drives them now)."""
    import re
    n = 0
    for aid, a in anims.items():
        if aid.startswith(f"animation.std.{slug}.flight") or not re.search(r"fly|flying|flap|glide|soar", aid):
            continue
        for k in list((a.get("bones") or {})):
            if k in bone_names:
                del a["bones"][k]
                n += 1
    return n


def slide_point(bones, aff, chain, span, sp):
    """his track-slide point (11:52): the centre of the wing's ROOT edge in the resting pose — the end of the wing's span
    nearest the shoulder. On a folded wing that is its north (front) edge, as he described; on a wing resting spread it
    is the edge against the body (the middle of its long leading edge would rock the wing about its middle).
    v3 (13:30): read EXACTLY on the root piece's largest cube — its own axis nearest the span gives the root face, whose
    corners all project the same (a shoulder->tip span vector is a little tilted against the plate: a fixed band kept
    only the top corners on the AnF eagle; a wide band pulled in corners of other cubes on the YTRI owl)."""
    by = {b["name"]: b for b in bones}
    pieces = [n for n in chain if by[n].get("cubes")]
    root_piece = next((n for n in pieces if n.startswith("wing_inner")), pieces[0] if pieces else None)
    if root_piece is not None:
        A, t = aff[root_piece]
        c = max(by[root_piece]["cubes"], key=lambda c: np.prod(np.abs(c["size"]) + 1e-3))
        k = int(np.argmax([abs((A @ CU.axis(c, i)) @ span) for i in range(3)]))
        e = A @ CU.axis(c, k)
        pts = np.array([A @ p + t for p in CU.corners(c)])
        proj = (pts - sp) @ e
        end = proj.min() if abs(proj.min()) <= abs(proj.max()) else proj.max()
        sel = pts[np.abs(proj - end) < 1e-3]
        return sel.mean(axis=0)
    corners = []
    for n in chain:
        A, t = aff[n]
        for c in by[n].get("cubes") or []:
            corners += [A @ p + t for p in CU.corners(c)]
    proj = [float((p - sp) @ span) for p in corners]
    lo, hi = min(proj), max(proj)
    tol = max(0.5, 0.1 * (hi - lo))
    if abs(lo) <= abs(hi):
        root = [p for p, d in zip(corners, proj) if d <= lo + tol]
    else:
        root = [p for p, d in zip(corners, proj) if d >= hi - tol]
    return np.mean(root, axis=0)


def north_point(bones, aff, chain):
    """the v2.0 rule (kept for comparison only): centre of the wing's north (world -z) edge."""
    by = {b["name"]: b for b in bones}
    corners = []
    for n in chain:
        A, t = aff[n]
        for c in by[n].get("cubes") or []:
            corners += [A @ p + t for p in CU.corners(c)]
    zmin = min(p[2] for p in corners)
    return np.mean([p for p in corners if p[2] <= zmin + 0.5], axis=0)


def body_obbs(bones):
    """the torso's cubes (bones named body / body_<n>) as world oriented boxes (M, t, lo, hi): world = M @ local + t."""
    aff = bone_affines(bones)
    out = []
    for b in bones:
        if not re.match(r"^body(_\d+)?$", b["name"]):
            continue
        A, t = aff[b["name"]]
        for c in b.get("cubes") or []:
            lo, hi = CU.box(c)
            Rc, tc = CU.cube_affine(c)
            out.append((A @ Rc, A @ tc + t, lo, hi))
    return out


def root_corners(bones, aff, side):
    """world corners of the wing's root edge (the slide_point selection) in the pose `bones` / `aff` describe."""
    by = {b["name"]: b for b in bones}
    sh = f"shoulder_{side}"
    span, nrm, chord, sp = wing_frame(bones, side)
    pts = []
    for n in subtree(bones, sh):
        A, t = aff[n]
        for c in by[n].get("cubes") or []:
            pts += [A @ p + t for p in CU.corners(c)]
    if not pts:
        return np.zeros((0, 3))
    pts = np.array(pts)
    proj = (pts - sp) @ span
    lo, hi = proj.min(), proj.max()
    tol = max(0.5, 0.1 * (hi - lo))
    sel = pts[proj <= lo + tol] if abs(lo) <= abs(hi) else pts[proj >= hi - tol]
    return sel


def slide_target(obbs, side, c_root):
    """the flight attachment point: high on the flank, root-chord centre from the body's front, ON the side surface."""
    corners = np.array([M @ np.array([x, y, z]) + t for M, t, lo, hi in obbs
                        for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    ymax, ymin = corners[:, 1].max(), corners[:, 1].min()
    zmin, zmax = corners[:, 2].min(), corners[:, 2].max()
    H, L = ymax - ymin, zmax - zmin
    y_t = ymax - min(1.0, 0.15 * H)
    z_t = min(zmin + max(c_root / 2.0, 0.3 * L), (zmin + zmax) / 2.0)
    x = surface_x(obbs, side, y_t, z_t)
    if x is None:
        # a turned torso box (AnF owls: body −50°) can miss that line: walk the point toward the box centre until
        # the line meets the surface (the owl's root stood 1 px off the body in flight)
        yc, zc = float(corners[:, 1].mean()), float(corners[:, 2].mean())
        for k in range(1, 11):
            f = k / 10.0
            y2, z2 = (1 - f) * y_t + f * yc, (1 - f) * z_t + f * zc
            x = surface_x(obbs, side, y2, z2)
            if x is not None:
                y_t, z_t = y2, z2
                break
    return None if x is None else np.array([x, y_t, z_t])


def surface_x(obbs, side, y_t, z_t):
    """the torso's side surface on the line (x, y_t, z_t): the outermost x where the line leaves the boxes."""
    best = None
    for M, t, lo, hi in obbs:   # the line (x, y_t, z_t): where does it run inside this box?
        Mi = np.linalg.inv(M)
        a = Mi @ (np.array([0.0, y_t, z_t]) - t)        # local point at x = 0
        d = Mi @ np.array([1.0, 0.0, 0.0])              # local direction per unit x
        xlo, xhi = -np.inf, np.inf
        ok = True
        for k in range(3):
            if abs(d[k]) < 1e-12:
                if not (lo[k] - 1e-6 <= a[k] <= hi[k] + 1e-6):
                    ok = False
                    break
            else:
                x1, x2 = sorted(((lo[k] - a[k]) / d[k], (hi[k] - a[k]) / d[k]))
                xlo, xhi = max(xlo, x1), min(xhi, x2)
        if not ok or xlo > xhi:
            continue
        edge = xhi if side == "l" else xlo
        if best is None or (edge > best if side == "l" else edge < best):
            best = edge
    return best


FOLD_AT_REST = re.compile(r"_anf$")   # his J5 = (c) + J7 = (b): every AnF bird that rests spread folds at rest
FOLD_FAN = 12.0                          # each collapsed piece fans this much further down (deg)
FOLD_LAYER = 0.12                        # px between stacked folded layers (no z-fighting of the flat plates)
FOLD_CHORD = 0.6                         # folded wing chord / spread chord (stacked feathers)
FOLD_LEAN = 15.0                         # upright birds: the folded wing leans in over the back at rest (J10)
FOLD_LEAN_HAWK = 28.0                    # hawks: the stack pressed down onto the back (his J12 = yes, 25-30 deg)
FOLD_ANCHOR = 0.2                        # rest anchor: this far back along the torso from its front-top end


def torso_frame(bones):
    """(centre, long axis toward the tail, half length) of the largest torso cube, world."""
    aff = bone_affines(bones)
    best = None
    for b in bones:
        if re.match(r"^body(_\d+)?$", b["name"]) and b.get("cubes"):
            A, t = aff[b["name"]]
            for c in b["cubes"]:
                vol = abs(c["size"][0] * c["size"][1] * c["size"][2]) + 1e-3
                if best is None or vol > best[0]:
                    k = int(np.argmax(np.abs(c["size"])))
                    v = A @ CU.axis(c, k)
                    v = v if v[2] >= 0 else -v
                    best = (vol, A @ CU.centre(c) + t, v / np.linalg.norm(v), abs(c["size"][k]) / 2.0)
    return best[1:] if best else None


def fold_at_rest(out, bones, meas, s, f, o_e, f_e, hinges):
    """his J5 (c) + J7 (b), 13:27: a wing whose AUTHORED rest is spread COLLAPSES at rest and opens to its authored spread
    in flight (u: 0 -> 1).
      shoulder   the whole wing turns about its root until it lies flush on the flank, its span running along the TORSO
                 toward the tail, top surface out (out / fwd joints).
      anchor     "like the flamingo, but opposite": the root point slides from its flight place to its REST anchor — on
                 the side surface, FOLD_ANCHOR of the torso back from its front-top end (shoulder_fly position).
      collapse   new joints wing_fold_1/2/3_<s> above elbow / primary_base_2 / primary_base_3: each outer piece slides
                 back onto the one before it (its own length along the span), lifts FOLD_LAYER px, fans FOLD_FAN deg
                 down — the pieces stack into a wedge (the prototype he saw, FOLD-PROPOSAL-1).
      chord      x FOLD_CHORD at rest (stacked feathers), on shoulder_stretch."""
    span, nrm, chord, sp = wing_frame(bones, s)
    sgn = 1.0 if s == "l" else -1.0
    tf = torso_frame(bones)
    if tf:
        C, v, h = tf
        pitch0 = float(np.degrees(np.arcsin(min(1.0, abs(v[1])))))
        # J11 (14:02): a level-bodied bird's folded wing "lifts up with the body" (a little up, not drooping)
        vv = v + np.array([0.0, 0.12, 0.0]) if pitch0 < 30.0 else v - np.array([0.0, 0.15, 0.0])
        t_span = vv / np.linalg.norm(vv)
    else:
        t_span = np.array([0.0, -0.2, 1.0]) / np.linalg.norm([0.0, -0.2, 1.0])
    t_nrm = np.array([sgn, 0.0, 0.0])
    t_chord = np.cross(t_span, t_nrm)
    t_nrm = np.cross(t_chord, t_span)
    Rw = np.column_stack([t_span, t_nrm, t_chord]) @ np.column_stack([span, nrm, chord]).T
    aff = bone_affines(bones)
    by = {b["name"]: b for b in bones}
    par = by[f"shoulder_out_{s}"]["parent"]
    Ap = aff[par][0]
    b_, a_, g_, _ = fit_fwd_out(Ap.T @ Rw @ Ap)
    # his 13:34: "rest position should look like unfold; and unfold should look like rest position" — every fold
    # channel reads the progress through W(u): W(0) = 0.5 (rest = the old half-way look), W(0.5) = 0 (the old rest look
    # mid-transition), W(1) = 1 (flight)
    W = f"({U_EXPR} < 0.5 ? 0.5 - {U_EXPR} : 2 * ({U_EXPR} - 0.5))"
    # J9 (13:56): A for the UPRIGHT birds (eagles, hawks, vultures); a horizontal-bodied bird (gulls, terns) looked open
    # in A — it rests with the FULL shoulder turn (option C: the plain clock)
    pitch = float(np.degrees(np.arcsin(min(1.0, abs(v[1]))))) if tf else 0.0
    f["torso_pitch"] = round(pitch, 1)
    if pitch < 30.0:
        W = U_EXPR
    o_e, f_e = ease(0.0, 0.6, W), ease(0.35, 1.0, W)
    f["o_w"], f["f_w"] = o_e, f_e
    ro, rf = f"(1 - {o_e})", f"(1 - {f_e})"
    out[f"shoulder_out_{s}"] = {"rotation": [f"{g_} * {ro}", "0", f"{a_} * {ro}"]}
    out[f"shoulder_fwd_{s}"] = {"rotation": ["0", f"{b_} * {rf}", "0"]}
    f["fold"] = {"fwd": b_, "out": a_, "roll": g_}
    # rest anchor (the slide toward rest)
    if tf:
        top_end = C - v * h
        a_pt = top_end + v * (FOLD_ANCHOR * 2.0 * h)
        xs = surface_x(body_obbs(bones), s, float(a_pt[1]), float(a_pt[2]))
        anchor = np.array([xs if xs is not None else a_pt[0], a_pt[1], a_pt[2]])
        f["rest_d"] = [round(float(x), 4) for x in (anchor - np.array(f["root_w"]))]
    # collapse joints
    pieces = [n for n in [f"wing_inner_{s}"] + [f"primary_{s}_{k}" for k in (1, 2, 3)] if by.get(n, {}).get("cubes")]
    hinges_ = [f"elbow_{s}", f"primary_base_{s}_2", f"primary_base_{s}_3"]
    A_in = aff[pieces[0]][0]
    s_f = A_in.T @ span
    s_f /= np.linalg.norm(s_f)
    n_f = A_in.T @ nrm
    n_f /= np.linalg.norm(n_f)
    # "down" in the ACTUAL rest orientation, seen in the spread pose (J10: measured on the full fold, the fans of an A rest
    # went up and the hawks' pieces stood above the back)
    def ez(t):
        t = min(1.0, max(0.0, t))
        return t * t * (3 - 2 * t)
    w0 = 0.0 if pitch < 30.0 else 0.5
    ko, kf = 1.0 - ez(w0 / 0.6), 1.0 - ez((w0 - 0.35) / 0.65)
    R_rest = Ap @ rot_matrix([0, b_ * kf, 0]) @ rot_matrix([g_ * ko, 0, a_ * ko]) @ Ap.T
    d_spread = R_rest.T @ np.array([0.0, -1.0, 0.0])
    f["rest_factors"] = [round(ko, 3), round(kf, 3)]
    if tf and pitch >= 30.0:
        # J10 (14:02): on an upright bird the wing's upper part folds IN against the back — a lean about the torso axis
        # at rest, on shoulder_stretch (pivot = the wing root)
        A_sh = aff[f"shoulder_{s}"][0]
        a_loc = (R_rest @ A_sh).T @ v
        lean = FOLD_LEAN_HAWK if re.match(r"pw:hawk_", f.get("_mob", "")) else FOLD_LEAN   # J12 (14:20): hawks press harder
        f["lean"] = ([float(x) for x in a_loc / np.linalg.norm(a_loc)], lean * sgn)
    tip = pieces[-1]
    for i, j in enumerate(hinges_):
        if j not in by or i >= len(pieces) - 1:
            continue
        # 14:3x 10-01 (his hawk call "wings must not rise above the body"): slide by the REAL hinge spacing — the piece's
        # start (the previous hinge, or the inner piece's near end) to this hinge — not the piece's projected length:
        # rotated plates project ~1 px longer, so each joint overshot toward the root (cumulative 1/2/3 px; up on an
        # upright bird = the stack climbed above the back)
        h_w = np.array(by[j]["pivot"], float)   # file frame, like the cube corners (same bind chain as the inner piece)
        if i == 0:
            start = min(p @ s_f for c in by[pieces[0]]["cubes"] for p in CU.corners(c))
        else:
            start = float(np.array(by[hinges_[i - 1]]["pivot"], float) @ s_f)
        L = float(h_w @ s_f) - start
        f.setdefault("fold_L", []).append(round(L, 3))
        fj = {"name": f"wing_fold_{i + 1}_{s}", "parent": by[j]["parent"], "pivot": list(by[j]["pivot"])}
        by[j]["parent"] = fj["name"]
        bones.insert(bones.index(by[j]), fj)
        by[fj["name"]] = fj
        mj = copy.deepcopy(fj)
        next(b for b in meas if b["name"] == j)["parent"] = mj["name"]
        meas.insert(next(k for k, b in enumerate(meas) if b["name"] == j), mj)
        A_par = bone_affines(bones)[fj["parent"]][0]
        v_file = -s_f * L + n_f * FOLD_LAYER
        p_ch = A_par.T @ v_file
        sg = sign_for_axis(meas, fj["name"], n_f, tip, d_spread)
        # J8 (b), 13:46: the collapse stays FULLY engaged on the ground and through the first half of the takeoff (the
        # half-engaged stack at rest let the outer pieces stick forward / out), then releases
        rc = f"(1 - {ease(0.5, 1.0)})"
        out[fj["name"]] = {"rotation": CU.hinge_molang(n_f, f"{sg * FOLD_FAN:.1f} * {rc}"),
                           "position": [f"{x:.4f} * {rc}" if abs(x) > 1e-9 else "0" for x in p_ch]}
        f.setdefault("fold_joints", []).append(fj["name"])


def build_v2(mob, P, plan_row):
    rp = P.path.name
    st = SC.Staged(rp, mob)
    slug = S.slug_of(mob)
    geo = st.geo["minecraft:geometry"][0]
    assert not any(b["name"].startswith(("shoulder_fly_", "fold_shoulder_")) for b in geo["bones"]), "already built"
    sides = [s for s in ("l", "r") if any(b["name"] == f"shoulder_{s}" for b in geo["bones"])]
    bones = geo["bones"]
    rep = {"mob": mob, "sides": sides}
    wing_bones, leg_bones = set(), set()
    flight = {}
    hinges = {}
    # bones any of the bird's OWN animations drive (a hinge pivot may only move on a joint nothing else animates)
    import re as _re
    own_driven = {k for aid, a in st.anim["animations"].items() if not aid.startswith(f"animation.std.{slug}.flight")
                  and not _re.search(r"fly|flying|flap|glide|soar", aid)   # airborne clips lose their wing channels below
                  for k in (a.get("bones") or {})}
    aff = bone_affines(bones)
    by = {b["name"]: b for b in bones}
    for s in sides:
        sh = f"shoulder_{s}"
        chain = subtree(bones, sh)
        wing_bones |= set(chain)
        span, nrm, chord, sp = wing_frame(bones, s)
        slide_w = slide_point(bones, aff, chain, span, sp)
        parent = by[sh].get("parent")
        piv = [round(float(x), 4) for x in to_frame(aff, parent, slide_w)]
        # the three identity joints, parent -> fly -> fwd -> out -> shoulder
        for name in (f"shoulder_fly_{s}", f"shoulder_fwd_{s}", f"shoulder_out_{s}"):
            pass
        # the flap / sweep / twist must turn about the ENTITY's axes (forward, up, side), not the parent's: a pitched body
        # (AnF eagle 45 deg, YTRI owl) would tilt the flap into a sweep. When the parent is turned, the fly joint sits
        # between a level joint (bind = parent's inverse) and its undo (bind = parent's turn), same pivot: identity at rest.
        Apar = aff[parent][0] if parent else np.eye(3)
        level = not np.allclose(Apar, np.eye(3), atol=1e-9)
        if level:
            nb = [{"name": f"shoulder_level_{s}", "pivot": piv, "rotation": [round(float(x), 6) for x in CU.euler_of(Apar.T)],
                   **({"parent": parent} if parent else {})},
                  {"name": f"shoulder_fly_{s}", "parent": f"shoulder_level_{s}", "pivot": piv},
                  {"name": f"shoulder_unlevel_{s}", "parent": f"shoulder_fly_{s}", "pivot": piv,
                   "rotation": [round(float(x), 6) for x in CU.euler_of(Apar)]},
                  {"name": f"shoulder_fwd_{s}", "parent": f"shoulder_unlevel_{s}", "pivot": piv}]
        else:
            nb = [{"name": f"shoulder_fly_{s}", "pivot": piv, **({"parent": parent} if parent else {})},
                  {"name": f"shoulder_fwd_{s}", "parent": f"shoulder_fly_{s}", "pivot": piv}]
        nb.append({"name": f"shoulder_out_{s}", "parent": f"shoulder_fwd_{s}", "pivot": piv})
        by[sh]["parent"] = f"shoulder_out_{s}"
        i = bones.index(by[sh])
        bones[i:i] = nb
        # spread target, decomposed into forward(y) after out(z) + roll(x), in the parent's frame
        sgn = 1.0 if s == "l" else -1.0
        t_span = np.array([sgn, DROOP, 0.0]) / np.linalg.norm([1.0, DROOP, 0.0])
        t_nrm = np.array([0.0, 1.0, 0.0]) - t_span * t_span[1]
        t_nrm /= np.linalg.norm(t_nrm)
        t_chord = np.cross(t_span, t_nrm)
        Rw = np.column_stack([t_span, t_nrm, t_chord]) @ np.column_stack([span, nrm, chord]).T
        Ap = aff[parent][0] if parent else np.eye(3)
        if is_spread(span):   # a wing resting spread IS the flight pose: no unfold (its own ground clips fold it)
            b_fwd, a_out, g_roll, cost = 0.0, 0.0, 0.0, 0.0
        else:
            # his double hinge, no roll: OUT (about the body's long axis z) lifts the folded wing until its top surface
            # faces up, then FORWARD (about y) swings its length out to the side; the leading edge falls where the
            # motion puts it
            sp_p, nr_p = Ap.T @ span, Ap.T @ nrm
            ts_p, up_p = Ap.T @ t_span, Ap.T @ np.array([0.0, 1.0, 0.0])

            def resid(e):
                Rm = rot_matrix([0, e[0], 0]) @ rot_matrix([0, 0, e[1]])
                return np.concatenate([Rm @ sp_p - ts_p, 0.7 * (Rm @ nr_p - up_p)])
            best = min((least_squares(resid, [b0, a0]) for b0 in (-90, 0, 90, 180) for a0 in (-90, 0, 90)),
                       key=lambda r: (round(r.cost, 4), abs(r.x[0]) + abs(r.x[1])))
            wrap = lambda x: (x + 180.0) % 360.0 - 180.0  # noqa: E731
            b_fwd, a_out, g_roll, cost = round(wrap(best.x[0]), 3), round(wrap(best.x[1]), 3), 0.0, float(best.cost)
        # flight stretch (H3): span longer, chord narrower (area kept) until the wing is TARGET_ASPECT long
        span_k, chord_k = wing_axes(bones, s)
        cubes = [c for n in chain for c in by[n].get("cubes") or []]
        pts = np.array([p for c in cubes for p in CU.corners(c)])
        ext = pts.max(axis=0) - pts.min(axis=0)
        aspect = ext[span_k] / max(ext[chord_k], 1e-6)
        rot_w = rotated_wing(bones, s)
        # a bone scale stretches along the bone's own axes: on plates turned off those axes it would shear them -> none
        stretch = 1.0 if rot_w else max(1.0, min(1.8, (TARGET_ASPECT / aspect) ** 0.5))
        folds = bool(is_spread(span) and FOLD_AT_REST.search(mob) and not rot_w)
        if stretch > 1.0 or folds:
            # the stretch joint: directly under the shoulder, everything of the wing under it, pivot = root edge centre
            st_piv = [round(float(x), 4) for x in to_frame(aff, sh, slide_w)]
            for b in bones:
                if b.get("parent") == sh:
                    b["parent"] = f"shoulder_stretch_{s}"
            nbs = {"name": f"shoulder_stretch_{s}", "parent": sh, "pivot": st_piv}
            bones.insert(bones.index(by[sh]) + 1, nbs)
            by[nbs["name"]] = nbs
        moved, kept = [], []   # filled after the flight pose is known (the hinge goes on the face that is UP in flight)
        flight[s] = {"fwd": b_fwd, "out": a_out, "roll": g_roll, "fit_cost": cost, "span_k": span_k,
                     "chord_k": chord_k, "stretch": round(stretch, 3), "aspect": round(aspect, 2), "slide": piv,
                     "rotated_plates": rot_w, "hinge_pivots_moved": moved,
                     "root_w": [float(x) for x in slide_w],
                     "spread": bool(is_spread(span)),
                     "hinge_pivots_kept": kept}
        # legs of this side
        for n in [b["name"] for b in bones]:
            if n.endswith(f"_{s}") and n.split("_")[0] in ("hip", "thigh", "knee", "shin", "ankle", "foot", "toe"):
                leg_bones.add(n)
    leg_bones |= {b["name"] for b in bones if b["name"].split("_")[0] in ("thighs", "shins", "feet", "toes", "legs")}
    rep["flight"] = flight
    st.save()  # geometry with the new joints
    # ---- animation
    ws = wingspan(plan_row)
    T = flap_period(ws)
    glide = ws >= GLIDE_FROM
    tuck = leg_tuck_from(st.anim["animations"], slug)
    stripped = strip_airborne(st.anim["animations"], slug, wing_bones | leg_bones)
    # flap / hinge signs are measured on the SPREAD pose (the fwd / out joints carry their flight rotation for the measure)
    meas = copy.deepcopy(bones)
    for b in meas:
        for s in sides:
            if b["name"] == f"shoulder_fwd_{s}":
                b["rotation"] = [0, flight[s]["fwd"], 0]
            if b["name"] == f"shoulder_out_{s}":
                b["rotation"] = [flight[s]["roll"], 0, flight[s]["out"]]
    # ---- the TRACK SLIDE (his 11:52 + 13:04): carry the root point along the body to where the wing attaches in flight
    aff_m = bone_affines(meas)
    obbs = body_obbs(bones)
    for s in sides:
        f = flight[s]
        f["slide_d"] = [0.0, 0.0, 0.0]
        if not obbs:
            continue
        if f["spread"]:
            # a wing resting spread keeps its authored shoulder — unless its root sits INSIDE the torso (YTRI owl /
            # hummingbird, YSav eagle, SF vulture: the flap swung the embedded part through the body): then the slide
            # carries the root straight out to the side surface
            root = np.array(f["root_w"])
            xs = surface_x(obbs, s, float(root[1]), float(root[2]))
            if xs is not None and ((s == "l" and xs > root[0]) or (s == "r" and xs < root[0])):
                f["slide_d"] = [round(float(xs - root[0]), 4), 0.0, 0.0]
            continue
        root = np.array(f["root_w"])
        rc = root_corners(meas, aff_m, s)
        c_root = float(rc[:, 2].max() - rc[:, 2].min()) if len(rc) else 0.0
        target = slide_target(obbs, s, c_root)
        if target is None:
            continue
        par = next(b for b in bones if b["name"] == f"shoulder_fly_{s}").get("parent")
        assert np.allclose(bone_affines(bones)[par][0] if par else np.eye(3), np.eye(3), atol=1e-6), "fly parent not level"
        f["slide_d"] = [round(float(x), 4) for x in (target - root)]
        f["slide_target"] = [round(float(x), 4) for x in target]
    # hinge lines: on the shared edge, on the plate face that is UP in the flight pose (measured on `meas`)
    by_m = {b["name"]: b for b in meas}
    for s in sides:
        chord_k = flight[s]["chord_k"]
        for j, (pv, u) in hinge_plan(meas, s, [0.0, 1.0, 0.0]).items():
            if np.max(np.abs(u)) < 0.9999 or int(np.argmax(np.abs(u))) != chord_k:
                hinges[j] = u                  # off the joint's chord axis: the exact any-axis hinge
            if pv is not None:
                if j in own_driven:
                    flight[s]["hinge_pivots_kept"].append(j)   # the bird's own clips turn it about its old pivot
                elif np.linalg.norm(np.array(pv) - np.array(by[j].get("pivot", [0, 0, 0]), float)) > 1e-6:
                    by[j]["pivot"] = pv
                    by_m[j]["pivot"] = pv
                    flight[s]["hinge_pivots_moved"].append(j)
    flap_env = ease(0.7, 1.0)
    # (the slide channel is written onto shoulder_fly below)
    # flap / sweep / twist + hinge bends (v1 motion), every amplitude gated by the flap envelope
    base = flight_animation(meas, sides, T, glide, gate=flap_env, hinges=hinges)
    out = {k: dict(ch) for k, ch in base["bones"].items()}
    for s in sides:
        f = flight[s]
        o_e, f_e = ease(0.0, 0.6), ease(0.35, 1.0)
        out[f"shoulder_out_{s}"] = {"rotation": [f"{f['roll']} * {o_e}", "0", f"{f['out']} * {o_e}"]}
        # (the 12:59 no-slide fix is superseded by the track slide below — D-C391)
        out[f"shoulder_fwd_{s}"] = {"rotation": ["0", f"{f['fwd']} * {f_e}", "0"]}
        f["_mob"] = mob
        if f["spread"] and FOLD_AT_REST.search(mob):
            fold_at_rest(out, bones, meas, s, f, o_e, f_e, hinges)
        if any(f["slide_d"]) or f.get("rest_d"):   # parent frame is world-aligned: the value IS the world move
            rd = f.get("rest_d") or [0.0, 0.0, 0.0]
            o_w = f.get("o_w", o_e)
            out.setdefault(f"shoulder_fly_{s}", {})["position"] = [
                f"{a} * {o_e} + {b} * (1 - {o_w})" for a, b in zip(f["slide_d"], rd)]
        if f["stretch"] > 1.0 or f.get("fold"):
            sc = ["1", "1", "1"]
            sc[f["span_k"]] = f"(1 + {f['stretch'] - 1:.3f} * {f_e})"
            sc[f["chord_k"]] = f"(1 - {1 - 1 / f['stretch']:.3f} * {f_e})"
            if f.get("fold"):
                # a folded wing's feathers stack: its chord at rest is FOLD_CHORD of the spread chord
                sc[f["chord_k"]] += f" * (1 - {1 - FOLD_CHORD:.2f} * (1 - {f.get('f_w', f_e)}))"
            # on shoulder_stretch_<s>: no rotation, pivot = the root edge centre — the stretch grows the wing OUTWARD
            # from the body (on the shoulder's own pivot it pushed the flamingo's root off the body)
            out.setdefault(f"shoulder_stretch_{s}", {})["scale"] = sc
            if f.get("lean"):
                ax, ang = f["lean"]
                out[f"shoulder_stretch_{s}"]["rotation"] = CU.hinge_molang(ax, f"{ang:.1f} * (1 - {f.get('f_w', f_e)})")
    # the default tuck turns ONLY the top joint of each leg (the leg bone whose parent is not a leg bone): turning the
    # hip AND the thigh piece under it doubled the thigh's turn (130 deg) while knee / shin / foot (siblings of the
    # thigh under the hip) followed the hip alone — the leg came apart (his 12:38 report). The bird's own airborne
    # pose (library tuck) is used as authored.
    tuck_default = {"hip": [65, 0, 0], "thigh": [65, 0, 0], "thighs": [65, 0, 0], "legs": [65, 0, 0]}
    by = {b["name"]: b for b in bones}
    # per side the HIP joint (else the thigh) — a group frame above both legs (WS `legs_frame`) can pivot far from the
    # hips and would swing the legs off the body (desert owl: 3.9 px); only birds with no per-side leg bone use it
    # per side: the DEEPEST common ancestor of all that side's leg pieces that is itself a leg bone (YSav eagle: its
    # per-side legs_frame — the hip only carries the thigh there; the shin hangs from a sibling joint)
    top_legs = set()
    for s_ in ("l", "r"):
        pcs = [n for n in leg_bones if n.endswith(f"_{s_}") and by.get(n, {}).get("cubes")]
        if not pcs:
            continue

        def anc(n):
            out = []
            while n in by:
                out.append(n)
                n = by[n].get("parent")
            return out
        common = set(anc(pcs[0]))
        for n in pcs[1:]:
            common &= set(anc(n))
        cand = [n for n in anc(pcs[0]) if n in common and n in leg_bones]
        pick = cand[0] if cand else next((n for n in (f"hip_{s_}", f"thigh_{s_}") if n in by), None)
        if pick:
            top_legs.add(pick)
    if not top_legs:
        top_legs = {k for k in leg_bones if k in by and by[k].get("parent") not in leg_bones}
    # species-correct carriage (his 12:51 rule): long-legged waders trail their legs straight back (~85 deg at the
    # hip); other birds tuck them up (~65 deg). The bird's own airborne pose (library) is kept; when it does not swing
    # the top joint of the leg by >= 30 deg (crane: only knees 27.5 deg — the legs hung down), the top-joint carriage
    # is added. The direction is MEASURED on the rig: the leg's lowest piece must move back (+z) and up.
    import re as _re
    wader = bool(_re.search(r"crane|heron|egret|stork|flamingo|ibis|spoonbill|secretary|shoebill|bittern|jabiru|"
                            r"avocet|stilt", mob))
    carriage = 85.0 if wader else 65.0
    # waders: legs STRAIGHT back with the feet in line (his 12:58: "the flamingo's legs and feet don't seem to stay lined
    # up during liftoff" — its own fly pose bent the knee, and the foot plate hung at 90 deg to the trailing leg). Their
    # own airborne leg pose is not used; hip 85 deg back, knee straight, ankle a further 90 deg so the toes point back.
    rot = {} if wader else {k: list(v) for k, v in tuck.items()}
    aff_l = bone_affines(bones)
    for k in sorted(top_legs):
        have = rot.get(k)
        if have and max(abs(float(x)) for x in have) >= 30.0:
            continue
        under = [n for n in subtree(bones, k) if by[n].get("cubes")]
        if not under:
            continue
        # the carriage turns about the HIP POINT — the top face centre of the leg's highest piece — on a new joint
        # leg_tuck_<s> under the top joint (authored hip pivots can sit 4-5 px away: YTRI hummingbird / owl, the thigh
        # left the body by 4.3 px); the bird's own clips keep their joints
        wc = [(aff_l[n][0] @ p + aff_l[n][1]) for n in under for c in by[n]["cubes"] for p in CU.corners(c)]
        W = np.array(wc)
        top_pts = W[W[:, 1] >= W[:, 1].max() - 1e-6]
        hp = [round(float(x), 4) for x in to_frame(aff_l, k, top_pts.mean(axis=0))]
        s_ = k.rsplit("_", 1)[-1] if k.rsplit("_", 1)[-1] in ("l", "r") else ("l" if W[:, 0].mean() > 0 else "r")
        tj = {"name": f"leg_tuck_{s_}", "parent": k, "pivot": hp}
        if tj["name"] in by:
            continue
        for b in bones:
            if b.get("parent") == k:
                b["parent"] = tj["name"]
        bones.insert(bones.index(by[k]) + 1, tj)
        by[tj["name"]] = tj
        leg_bones.add(tj["name"])
        tip = min(under, key=lambda n: min((aff_l[n][0] @ CU.centre(c) + aff_l[n][1])[1] for c in by[n]["cubes"]))
        sg = sign_for(bones, tj["name"], 0, tip, [0.0, 0.3, 1.0])
        rot[tj["name"]] = [sg * carriage, 0.0, 0.0]
    if wader:
        # the toes turn about the shin / foot junction — a new cubeless joint ankle_tuck_<s> under the ankle (pivot =
        # the centre of the shin's lowest face): the authored ankle pivot can sit far from the foot (AnF egret: 2 px
        # below the ground — a 90 deg turn there threw the foot 2.2 px off the shin) and the bird's own walk keeps it
        for s_ in ("l", "r"):
            a, shin = f"ankle_{s_}", f"shin_{s_}"
            if a not in by:
                continue
            under = [n for n in subtree(bones, a) if by[n].get("cubes")]
            if not under:
                continue
            src = by.get(shin) if by.get(shin, {}).get("cubes") else None
            if src is None:   # no shin (2-piece leg): the piece whose bottom is lowest among the pieces above the foot
                above = [n for n in leg_bones if n.endswith(f"_{s_}") and by.get(n, {}).get("cubes")
                         and n not in subtree(bones, a)]
                if above:
                    src = by[min(above, key=lambda n: min(p[1] for c in by[n]["cubes"] for p in CU.corners(c)))]
            pts = np.array([p for c in (src or by[under[0]])["cubes"] for p in CU.corners(c)])
            low = pts[pts[:, 1] <= pts[:, 1].min() + 1e-6] if src else pts[pts[:, 1] >= pts[:, 1].max() - 1e-6]
            jp = [round(float(x), 4) for x in low.mean(axis=0)]
            tj = {"name": f"ankle_tuck_{s_}", "parent": a, "pivot": jp}
            for b in bones:
                if b.get("parent") == a:
                    b["parent"] = tj["name"]
            bones.insert(bones.index(by[a]) + 1, tj)
            by[tj["name"]] = tj
            leg_bones.add(tj["name"])
            sg_a = sign_for(bones, tj["name"], 0, under[0], [0.0, -1.0, 0.0])   # toes forward -> down -> back
            rot[tj["name"]] = [sg_a * 90.0, 0.0, 0.0]
    rep["leg_carriage"] = {"wader": wader, "deg": carriage, "joints": sorted(k for k in rot if by.get(k))}
    for k in sorted(leg_bones):
        r = rot.get(k)
        if r and any(r):
            out[k] = {"rotation": [f"{float(x)} * {ease(0.1, 0.8)}" if x else "0" for x in r]}
    st.anim["animations"][f"animation.std.{slug}.flight"] = {"loop": True, "bones": out}
    st.save()
    # ---- entity: unfold progress + always-on standard flight (it is 0 on the ground)
    ef = S.STAGE / rp / f"entity/std/{slug}.entity.json"
    ent = S.jload(ef)
    d = ent["minecraft:client_entity"]["description"]
    d.setdefault("animations", {})["std_flight"] = f"animation.std.{slug}.flight"
    sc_ = d.setdefault("scripts", {})
    sc_["animate"] = [a for a in sc_.get("animate", []) if not (a == "std_flight" or (isinstance(a, dict) and "std_flight" in a))]
    sc_["animate"].append("std_flight")
    init = sc_.setdefault("initialize", [])
    for line in ("v.std_r = math.random(0.0, 1.0);", "v.std_u = 0.0;"):
        if line.split("=")[0] not in "".join(init):
            init.append(line)
    pre = sc_.setdefault("pre_animation", [])
    pre[:] = [x for x in pre if "v.std_u" not in x]
    pre.append("v.std_u = v.std_u + ((q.is_on_ground ? 0.0 : 1.0) - v.std_u) * math.min(1.0, q.delta_time * 4.0);")
    ef.write_text(json.dumps(ent, indent=1))
    rep.update({"period": round(T, 3), "glide": glide, "wingspan": round(ws, 2), "tuck_from_library": sorted(tuck),
                "stripped_channels": stripped})
    return rep


def preview_pose(bones, anim_bones, env):
    """posed bones for the preview: rotation / position by posed_preview, the scale channel applied to the cubes of the
    scaled bone's subtree about its pivot in its file frame (the engine's scale-before-rotation convention — to be
    confirmed in-game)."""
    import posed_preview as PP
    import molang_eval as ME
    b2 = PP.posed_bones(bones, {k: {c: v for c, v in ch.items() if c != "scale"} for k, ch in anim_bones.items()}, dict(env))
    by = {b["name"]: b for b in b2}
    for k, ch in anim_bones.items():
        if "scale" not in ch or k not in by:
            continue
        sc = [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in ch["scale"]]
        piv = np.array(by[k].get("pivot", [0, 0, 0]), float)
        for n in subtree(b2, k):
            if n != k:  # a parent's scale moves its children's pivots too
                by[n]["pivot"] = list(piv + (np.array(by[n].get("pivot", [0, 0, 0]), float) - piv) * np.array(sc))
            for c in by[n].get("cubes") or []:
                o, sz = np.array(c["origin"], float), np.array(c["size"], float)
                c["origin"] = list(piv + (o - piv) * np.array(sc))
                c["size"] = list(sz * np.array(sc))
    return b2

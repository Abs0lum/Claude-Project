#!/usr/bin/env python3
"""wing_contact.py — the WING-CONTACT census (his 01:20 CT 09-30 law, D-C309):
  "I want the edges of the wing pieces to stay in contact with each other as they flap - and I want this to be true of all
   flying mobs with similar wings."

For every mob whose wing is built from more than one piece, pose the SHIPPED geometry with the SHIPPED animations through a
whole flap (sequential ticks: pre_animation runs every tick, like the game) and measure, per hinge (inner piece A, outer
piece B):
  REST    the designed join in the bind pose: the points of B's surface that touch A (<= EPS px), and of A that touch B
  OPEN    per tick, how far those join points have moved away from the other piece (px; 0 = still touching / inside)
          -> max + median over the flap = how far the join opens while it flaps
  AXIS    the mechanism: each piece's rotation relative to its neighbour, split into the part about the join line (a true
          hinge: keeps the join closed) and the part about other axes (swings the join open), + non-uniform scale on the
          chain (shears the outer piece)
Bone transform = Bedrock order: world = parent . T(anim position, x mirrored) . T(pivot) . R(rest + anim) . S(anim) . T(-pivot).
Keyframed channels: linear + catmullrom. Numbers only rule OUT (P1): his in-game witness rules IN.
Usage: wing_contact.py [mob ...]   (default: every mob in SPECS) -> _docs/wings/WING-CONTACT-CENSUS.json + stdout table"""
import copy, json, math, random, re, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_eval as ME
import molang_lint as ML
from equine_compare import rot_matrix
from entity_render import transform

ROOT = Path("/home/claude")
EPS = 0.02                                     # px: "touching" in the bind pose
PASS_PX = 0.10                                 # px: a join that opens less than a tenth of a texel is closed
DT = 0.05
SEED = 20260930                                # fixed seed for math.random (initialize) so shipped vs fix compare the same flap
BASE_ENV = {"q.delta_time": DT, "q.is_on_ground": 0.0, "q.is_alive": 1.0, "q.modified_move_speed": 0.0,
            "q.target_x_rotation": 0.0, "q.target_y_rotation": 0.0, "q.hurt_time": 0.0, "q.death_ticks": 0.0,
            "q.modified_distance_moved": 0.0, "q.position(1)": 173.0, "q.is_riding": 0.0, "q.is_dancing": 0.0,
            "q.is_charging": 0.0, "q.is_resting": 0.0, "q.is_sitting": 0.0, "q.is_baby": 0.0, "q.life_time": 0.0,
            "q.anim_time": 0.0, "q.is_moving": 1.0, "q.ground_speed": 0.0, "q.vertical_speed": 0.0}
RP06, RP07 = ROOT / "_build/rp06-1421", ROOT / "_build/rp07-1427"

# mob -> pack, entity stem, geometry, flap states {name: (env, [animation short names])}, hinges [(label, A root, B root)]
# A = A root's subtree minus B root's subtree (the inner piece); B = B root's subtree (the outer piece)
SPECS = {
    "parrot": dict(pack=RP07, stem="parrot", gid="geometry.pw_parrot",
                   states={"fly slow": ({"q.modified_move_speed": 0.1}, ["pw_jem"]), "fly": ({"q.modified_move_speed": 0.4}, ["pw_jem"]),
                           "fly fast": ({"q.modified_move_speed": 1.0}, ["pw_jem"])},
                   hinges=[("L inner|outer", "left_wing_fly", "left_wing_fly2"), ("R inner|outer", "right_wing_fly", "right_wing_fly2"),
                           ("L body|wing", "body", "left_wing_fly"), ("R body|wing", "body", "right_wing_fly")]),
    "bat": dict(pack=RP07, stem="bat", gid="geometry.pw_bat",
                states={"flying": ({}, ["flying"]), "resting": ({"q.is_resting": 1.0}, ["resting"])},
                hinges=[("L wing|tip", "leftWing", "leftWingTip"), ("R wing|tip", "rightWing", "rightWingTip"),
                        ("L body|wing", "body", "leftWing"), ("R body|wing", "body", "rightWing")]),
    "phantom": dict(pack=RP06, stem="phantom", gid="geometry.pw_phantom",
                    states={"glide": ({"q.modified_move_speed": 0.3}, ["pw_jem"]), "swoop": ({"q.modified_move_speed": 1.0}, ["pw_jem"]),
                            "hover": ({"q.modified_move_speed": 0.0}, ["pw_jem"])},
                    hinges=[("L wing|tip", "left_wing2", "left_wing_tip2"), ("R wing|tip", "right_wing2", "right_wing_tip2"),
                            ("L body|wing", "body2", "left_wing2"), ("R body|wing", "body2", "right_wing2")]),
    "vex": dict(pack=RP06, stem="vex", gid="geometry.pw_vex",
                states={"hover": ({"q.modified_move_speed": 0.0}, ["pw_jem"]), "fly": ({"q.modified_move_speed": 0.5}, ["pw_jem"]),
                        "charge": ({"q.modified_move_speed": 1.0, "q.is_charging": 1.0}, ["pw_jem"])},
                hinges=[("L inner|outer", "left_wing3", "left_wing4"), ("R inner|outer", "right_wing3", "right_wing4"),
                        ("L body|wing", "body", "left_wing2"), ("R body|wing", "body", "right_wing2")]),
    "allay": dict(pack=RP07, stem="allay", gid="geometry.pw_allay",
                  states={"hover": ({"q.modified_move_speed": 0.0}, ["pw_jem"]), "fly": ({"q.modified_move_speed": 0.5}, ["pw_jem"]),
                          "dance": ({"q.is_dancing": 1.0}, ["pw_jem"])},
                  hinges=[("L inner|outer", "left_wing3", "left_wing4"), ("R inner|outer", "right_wing3", "right_wing4"),
                          ("L body|wing", "body", "left_wing2"), ("R body|wing", "body", "right_wing2")]),
    "eagle": dict(pack=RP07, stem="eagle", gid="geometry.sf_nba.eagle",
                  states={"fly": ({}, ["fly"])},
                  hinges=[("L inner|outer", "left_Wing_1", "left_Wing_2"), ("R inner|outer", "right_Wing_1", "right_Wing_2")]),
    "vulture": dict(pack=RP07, stem="vulture", gid="geometry.sf_nba.vulture",
                    states={"fly": ({}, ["fly"])},
                    hinges=[("L wing|tip", "left_wing", "left_wing_tip"), ("R wing|tip", "right_wing", "right_wing_tip")]),
    "butterfly": dict(pack=RP07, stem="butterfly", gid="geometry.sf_nba.butterfly",
                      states={"fly": ({}, ["fly"])},
                      hinges=[("L top|bottom", "leftWingTop", "leftWingBottom"), ("R top|bottom", "rightWingTop", "rightWingBottom")]),
}


# ------------------------------------------------------------------------------------------------------------ loading
def jl(p):
    return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))


def find_geo(pack, gid):
    for p in sorted((pack / "models").rglob("*.json")):
        try: d = jl(p)
        except Exception: continue
        for g in d.get("minecraft:geometry", []) or []:
            if g.get("description", {}).get("identifier") == gid: return p, g
    raise FileNotFoundError(gid)


def anim_library(pack):
    lib = {}
    for base in (R.VAN_RP / "animations", pack / "animations"):          # the pack overrides vanilla
        for f in sorted(base.rglob("*.json")):
            try: lib.update(jl(f).get("animations", {}) or {})
            except Exception: pass
    return lib


def subtree(bones, root):
    kids = {}
    for b in bones: kids.setdefault(b.get("parent"), []).append(b["name"])
    out, stack = [], [root]
    while stack:
        n = stack.pop(); out.append(n); stack += kids.get(n, [])
    return out


# ------------------------------------------------------------------------------------------------------------ channels
def ev(x, env):
    if isinstance(x, (int, float)): return float(x)
    try: return float(ME.run(str(x), dict(env)))
    except Exception: return 0.0


def vec(v, env):
    if isinstance(v, list): return [ev(e, env) for e in v]
    x = ev(v, env); return [x, x, x]


def keyframes(ch, t, env):
    keys = sorted(((float(k), v) for k, v in ch.items()), key=lambda kv: kv[0])
    def pre(v): return vec(v.get("pre", v.get("post")), env) if isinstance(v, dict) else vec(v, env)
    def post(v): return vec(v.get("post", v.get("pre")), env) if isinstance(v, dict) else vec(v, env)
    if t <= keys[0][0]: return post(keys[0][1])
    if t >= keys[-1][0]: return pre(keys[-1][1])
    for i in range(len(keys) - 1):
        (t0, v0), (t1, v1) = keys[i], keys[i + 1]
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            a, b = np.array(post(v0)), np.array(pre(v1))
            if isinstance(v0, dict) and v0.get("lerp_mode") == "catmullrom" or isinstance(v1, dict) and v1.get("lerp_mode") == "catmullrom":
                am = np.array(post(keys[i - 1][1])) if i > 0 else a
                bp = np.array(pre(keys[i + 2][1])) if i + 2 < len(keys) else b
                u2, u3 = u * u, u * u * u
                return list(0.5 * ((2 * a) + (-am + b) * u + (2 * am - 5 * a + 4 * b - bp) * u2 + (-am + 3 * a - 3 * b + bp) * u3))
            return list(a + (b - a) * u)
    return pre(keys[-1][1])


def channel(ch, t_anim, env):
    if isinstance(ch, dict) and ch and all(re.fullmatch(r"-?\d+(\.\d+)?", k) for k in ch): return keyframes(ch, t_anim, env)
    return vec(ch, env)


# ------------------------------------------------------------------------------------------------------------ posing
def anim_channels(anims, t, env):
    """{bone: {"rotation": [..], "position": [..], "scale": [..]}} summed / multiplied over the playing animations"""
    out = {}
    for a in anims:
        ln = float(a.get("animation_length", 0) or 0)
        ta = (t % ln) if (ln > 0 and a.get("loop") is True) else (min(t, ln) if ln > 0 else t)
        e = dict(env); e["q.anim_time"] = ta
        for bn, ch in (a.get("bones") or {}).items():
            o = out.setdefault(bn, {"rotation": [0.0] * 3, "position": [0.0] * 3, "scale": [1.0] * 3})
            if "rotation" in ch: o["rotation"] = [x + y for x, y in zip(o["rotation"], channel(ch["rotation"], ta, e))]
            if "position" in ch: o["position"] = [x + y for x, y in zip(o["position"], channel(ch["position"], ta, e))]
            if "scale" in ch: o["scale"] = [x * y for x, y in zip(o["scale"], channel(ch["scale"], ta, e))]
    return out


def affines(bones, chans):
    """{bone: (A, t)}: world = A @ p + t for p in the geometry file frame (A includes scale)"""
    by = {b["name"]: b for b in bones}; out = {}
    def get(n):
        if n in out: return out[n]
        b = by[n]; p = np.array(b.get("pivot", [0, 0, 0]), float); c = chans.get(n, {})
        rot = [float(v) for v in (b.get("rotation") or [0, 0, 0])]
        rot = [rot[k] + c.get("rotation", [0, 0, 0])[k] for k in range(3)]
        L = rot_matrix(rot) @ np.diag(c.get("scale", [1.0, 1.0, 1.0]))
        # animation position is applied in the geometry FILE frame as written (x NOT mirrored): Mojang's elytra proves it
        # (left_wing cube x -10..0 + position +4.5 = centred on the back, as Java's leftWing.x = 5 on a -10..0 box); the JEM
        # port writes +d tx on the same reading. (posed_preview.py mirrors x - that preview convention is wrong, D-C311.)
        pos = c.get("position", [0.0, 0.0, 0.0]); d = np.array([pos[0], pos[1], pos[2]], float)
        par = b.get("parent")
        A0, t0 = get(par) if par and par in by else (np.eye(3), np.zeros(3))
        out[n] = (A0 @ L, A0 @ (p - L @ p + d) + t0); return out[n]
    for b in bones: get(b["name"])
    return out


def boxes(bones, aff, names):
    """[(bone, cube index, 8 world corners)] — corner order o, +z, +y, +yz, +x, ... (x major)"""
    res = []
    for b in bones:
        if b["name"] not in names: continue
        A, t = aff[b["name"]]
        for i, c in enumerate(b.get("cubes", []) or []):
            o, s = np.array(c["origin"], float), np.array(c["size"], float); inf = float(c.get("inflate", 0) or 0)
            lo, hi = np.minimum(o, o + s) - inf, np.maximum(o, o + s) + inf
            pts = [np.array([x, y, z]) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            if any(c.get("rotation", [0, 0, 0]) or []): pts = [np.array(transform(list(q), c.get("pivot", [0, 0, 0]), c["rotation"])) for q in pts]
            res.append((b["name"], i, np.array([A @ q + t for q in pts])))
    return res


# ------------------------------------------------------------------------------------------------------------ geometry
GRID = np.linspace(0, 1, 11)
FACE_PARAMS = np.array([p for ax in range(3) for side in (0.0, 1.0) for u in GRID for v in GRID
                        for p in [[(side if k == ax else (u if k == (ax + 1) % 3 else v)) for k in range(3)]]])


def surface(B, params=FACE_PARAMS):
    o = B[0]; M = np.stack([B[4] - o, B[2] - o, B[1] - o], 1)
    return (M @ params.T).T + o


def obb_dist(P, B):
    o = B[0]; M = np.stack([B[4] - o, B[2] - o, B[1] - o], 1)
    q = (np.linalg.pinv(M) @ (P - o).T).T; qc = np.clip(q, 0, 1)
    return np.linalg.norm((M @ (q - qc).T).T, axis=1)


def dist_to(P, box_list):
    if not box_list: return np.full(len(P), np.inf)
    return np.min(np.stack([obb_dist(P, b[2]) for b in box_list]), axis=0)


ROOT_PX = 2.0                                  # px of each piece, from its root face, that must stay on the other piece


def params_to_pts(B, params):
    o = B[0]; M = np.stack([B[4] - o, B[2] - o, B[1] - o], 1)
    return (M @ np.asarray(params, float).T).T + o


def face_params(ax, side, n=11):
    g = np.linspace(0, 1, n)
    return [[side if a == ax else (u if a == (ax + 1) % 3 else v) for a in range(3)] for u in g for v in g]


def root_frames(mine, other, hinge):
    """per cube of `mine` in the join: its ROOT face = the face nearest the hinge point (the outer piece's bone pivot), ties
    broken by the face nearest `other`. Fibres run from that face into the piece (ROOT_PX deep), 21 stations along the
    join line (the face's long axis) x 5 across its thickness. Cubes whose root face is > 0.5 px from `other` are not in it."""
    out = []
    for k, (_, _, box) in enumerate(mine):
        o = box[0]; lens = [np.linalg.norm(box[4] - o), np.linalg.norm(box[2] - o), np.linalg.norm(box[1] - o)]
        cands = []
        for ax in range(3):
            for side in (0.0, 1.0):
                P = params_to_pts(box, face_params(ax, side))
                dh = float(np.linalg.norm(P - hinge, axis=1).min()); do = float(dist_to(P, other).min())
                cands.append((round(dh, 3), round(do, 3), ax, side))
        dh, do, ax, side = min(cands)
        near = min(float(dist_to(surface(b2), other).min()) for _, _, b2 in mine)
        if do > near + 0.5: continue                      # only the cubes at the join (a designed gap keeps the nearest)
        rest = [a for a in range(3) if a != ax]
        h, w = (rest[0], rest[1]) if lens[rest[0]] >= lens[rest[1]] else (rest[1], rest[0])
        ext = np.linspace(0, min(1.0, ROOT_PX / max(lens[ax], 1e-6)), 9)
        ext = (1.0 - ext) if side == 1.0 else ext
        fib = {}
        for i, s_ in enumerate(np.linspace(0, 1, 21)):
            for j, w_ in enumerate(np.linspace(0, 1, 5)):
                fib[(i, j)] = [[{ax: e, h: s_, w: w_}[a] for a in range(3)] for e in ext]
        out.append({"k": k, "ax": ax, "side": side, "fib": fib})
    return out


def fibre_dists(fr, mine, other):
    box = mine[fr["k"]][2]
    return {ij: float(dist_to(params_to_pts(box, P), other).min()) for ij, P in fr["fib"].items()}


def join_set(A_boxes, B_boxes, hinge):
    """the bind-pose join: the fibres (stations x thickness) that touch the other piece. If nothing touches (a designed gap),
    the nearest stations are tracked and the gap is reported."""
    # the outer piece's side only: its root region must stay on the inner piece. (The inner piece's own side double-counts
    # the same join and, where a body plate overlaps the wing root coplanar, reports an overlap sliding off, not a gap.)
    js = {"B": root_frames(B_boxes, A_boxes, hinge), "A": []}
    rest = None; best = np.inf
    for side, mine, other in (("B", B_boxes, A_boxes), ("A", A_boxes, B_boxes)):
        for fr in js[side]:
            d = fibre_dists(fr, mine, other); fr["bind"] = d
            best = min(best, min(d.values()))
    tol = EPS if best <= EPS else best + EPS
    if best > EPS: rest = best
    for side in ("B", "A"):
        for fr in js[side]:
            fr["face_keep"] = [ij for ij, v in fr["bind"].items() if v <= tol]
            fr["edge_keep"] = sorted({i for (i, j) in fr["face_keep"]})
    return js, rest


def gaps(js, A_boxes, B_boxes):
    """edge = the worst station along the join line (closed while ANY of that station's thickness still touches);
    face = the worst (station x thickness) fibre that touched in the bind pose: a wedge opening on one side counts here"""
    edge = face = 0.0
    for side, mine, other in (("B", B_boxes, A_boxes), ("A", A_boxes, B_boxes)):
        for fr in js[side]:
            if not fr["face_keep"]: continue
            d = fibre_dists(fr, mine, other)
            for i in fr["edge_keep"]:
                edge = max(edge, min(d[(i, j)] for j in range(5) if (i, j) in fr["face_keep"]))
            face = max(face, max(d[ij] for ij in fr["face_keep"]))
    return {"edge": edge, "face": face}


def opening(js, A_boxes, B_boxes):
    return gaps(js, A_boxes, B_boxes)


SHOULDER_R = 1.5                                # px around the wing's pivot that must stay on the body (shoulder joins)


def shoulder_set(A_boxes, B_boxes, hinge):
    """a wing ROOT on the body: the wing's surface points within SHOULDER_R of its pivot that touch the body in the bind pose
    (a folded wing lies along the body side - only its shoulder is a join; the rest of it lifting off is flight, not a gap)"""
    pts = []
    for k, (_, _, box) in enumerate(B_boxes):
        P = surface(box); near = np.linalg.norm(P - hinge, axis=1) <= SHOULDER_R
        d = dist_to(P, A_boxes)
        pts.append((k, np.where(near & (d <= EPS))[0], np.where(near)[0], d))
    touching = [(k, ix) for k, ix, _, _ in pts if len(ix)]
    if touching: return {"mode": "shoulder", "pts": touching}, None
    near_all = [(k, nx, d) for k, _, nx, d in pts if len(nx)]
    if not near_all: return {"mode": "shoulder", "pts": []}, None
    dmin = min(float(d[nx].min()) for k, nx, d in near_all)
    return {"mode": "shoulder", "pts": [(k, nx[d[nx] <= dmin + EPS]) for k, nx, d in near_all]}, dmin


def shoulder_gap(js, A_boxes, B_boxes):
    worst = 0.0
    for k, ix in js["pts"]:
        if len(ix): worst = max(worst, float(dist_to(surface(B_boxes[k][2])[ix], A_boxes).max()))
    return {"edge": worst, "face": worst}


# ------------------------------------------------------------------------------------------------------------ run
def run_state(spec, env_state, shorts, seconds=4.0, warm=1.0):
    pack = spec["pack"]
    ent = jl(pack / f"entity/{spec['stem']}.entity.json")["minecraft:client_entity"]["description"]
    lib = anim_library(pack)
    anims = [lib[ent["animations"][s]] for s in shorts]
    _, g = find_geo(pack, spec["gid"]); bones = copy.deepcopy(g["bones"]); names = {b["name"] for b in bones}
    env = dict(BASE_ENV); env.update(env_state)
    random.seed(SEED)                               # math.random in initialize: the same phase for every build compared
    for s in ent.get("scripts", {}).get("initialize", []) or []:
        try: ME.run(s, env)
        except Exception: pass
    hinges = [(lab, a, b) for lab, a, b in spec["hinges"] if a in names and b in names]
    parts, joins = {}, {}
    aff0 = affines(bones, {})
    for lab, a, b in hinges:
        Bn = set(subtree(bones, b)); An = (set(subtree(bones, a)) - Bn) if a != "body" and a != "body2" else {a}
        parts[lab] = (An, Bn)
        bb = {x["name"]: x for x in bones}[b]; A_, t_ = aff0[b]
        hinge = A_ @ np.array(bb.get("pivot", [0, 0, 0]), float) + t_
        if " | on " in lab or lab.endswith("body|wing"):
            joins[lab] = shoulder_set(boxes(bones, aff0, An), boxes(bones, aff0, Bn), hinge)
        else:
            joins[lab] = join_set(boxes(bones, aff0, An), boxes(bones, aff0, Bn), hinge)
    rows, n_ticks = [], int(round((seconds + warm) / DT))
    speed = env_state.get("q.modified_move_speed", 0.0)
    for n in range(n_ticks):
        t = n * DT; env["q.life_time"] = t
        env["q.modified_distance_moved"] = t * 4.0 * speed
        for s in ent.get("scripts", {}).get("pre_animation", []) or []:
            if "'" in s: continue
            try: ME.run(s, env)
            except Exception: pass
        if t < warm: continue
        ch = anim_channels(anims, t - warm, env); aff = affines(bones, ch)
        row = {"t": round(t - warm, 2)}
        for lab, (An, Bn) in parts.items():
            Ab, Bb = boxes(bones, aff, An), boxes(bones, aff, Bn)
            hidden = any(abs(np.linalg.det(aff[x][0])) < 1e-9 for x in An | Bn if x in aff)
            js = joins[lab][0]
            if js.get("mode") == "shoulder":
                row[lab] = None if hidden or not Ab or not Bb or not js["pts"] else shoulder_gap(js, Ab, Bb)
            else:
                row[lab] = None if hidden or not Ab or not Bb or not (js["A"] or js["B"]) else opening(js, Ab, Bb)
        rows.append(row)
    return rows, {lab: joins[lab][1] for lab in joins}, bones


def census(mobs):
    out = {}
    for mob in mobs:
        spec = SPECS[mob]; out[mob] = {}
        for st, (env_state, shorts) in spec["states"].items():
            rows, rest_gaps, bones = run_state(spec, env_state, shorts)
            summ = {}
            for lab in [h[0] for h in spec["hinges"]]:
                v = [r.get(lab) for r in rows if r.get(lab) is not None]
                if not v: summ[lab] = {"shown": False}; continue
                e = [x["edge"] for x in v]; f = [x["face"] for x in v]; i = int(np.argmax(e))
                summ[lab] = {"shown": True, "edge_max": round(max(e), 3), "edge_median": round(float(np.median(e)), 3),
                             "face_max": round(max(f), 3), "at_t": [r["t"] for r in rows if r.get(lab) is not None][i],
                             "rest_gap": rest_gaps.get(lab)}
            out[mob][st] = summ
            for lab, s in summ.items():
                if not s["shown"]: print(f"{mob:10s} {st:10s} {lab:16s} (hidden / no join in this state)"); continue
                flag = "CLOSED" if s["edge_max"] <= PASS_PX else "OPENS "
                rg = f" | bind-pose gap {s['rest_gap']:.2f}" if s["rest_gap"] else ""
                print(f"{mob:10s} {st:10s} {lab:16s} {flag} edge max {s['edge_max']:5.2f} px (t {s['at_t']:.2f}) median {s['edge_median']:5.2f}"
                      f" | face max {s['face_max']:5.2f}{rg}")
    return out


if __name__ == "__main__":
    mobs = sys.argv[1:] or list(SPECS)
    res = census(mobs)
    p = ROOT / "_docs/wings/WING-CONTACT-CENSUS.json"; p.parent.mkdir(parents=True, exist_ok=True)
    old = json.load(open(p)) if p.exists() else {}
    old.update(res); json.dump(old, open(p, "w"), indent=1)


# ------------------------------------------------------------------------------------------------------------ renders
def pose_at(spec, env_state, shorts, t_target, warm=1.0, chan_hook=None, geo=None):
    """the posed (bones, affines) at t_target seconds into the flap (same tick loop as run_state)"""
    pack = spec["pack"]
    ent = jl(pack / f"entity/{spec['stem']}.entity.json")["minecraft:client_entity"]["description"]
    lib = anim_library(pack); anims = [lib[ent["animations"][s]] for s in shorts]
    bones = copy.deepcopy(geo["bones"] if geo else find_geo(pack, spec["gid"])[1]["bones"])
    env = dict(BASE_ENV); env.update(env_state)
    random.seed(SEED)
    for s in ent.get("scripts", {}).get("initialize", []) or []:
        try: ME.run(s, env)
        except Exception: pass
    speed = env_state.get("q.modified_move_speed", 0.0)
    n_end = int(round((t_target + warm) / DT))
    for n in range(n_end + 1):
        t = n * DT; env["q.life_time"] = t; env["q.modified_distance_moved"] = t * 4.0 * speed
        for s in ent.get("scripts", {}).get("pre_animation", []) or []:
            if "'" in s: continue
            try: ME.run(s, env)
            except Exception: pass
    ch = anim_channels(anims, t_target, env)
    if chan_hook: ch = chan_hook(ch)
    return bones, affines(bones, ch), ch


def render(spec, bones, aff, views=("front", "top", "back-east"), W_=520, H_=420, title="", tex=None):
    from PIL import Image, ImageDraw, ImageFont
    from bb_truth import truth_posed_faces
    from entity_tex_render import render_entity
    from convb_preview3 import camera, FOV
    _, g = find_geo(spec["pack"], spec["gid"])
    tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    ent = jl(spec["pack"] / f"entity/{spec['stem']}.entity.json")["minecraft:client_entity"]["description"]
    tp = tex or list(ent["textures"].values())[0]
    png = spec["pack"] / (tp + ".png")
    if not png.exists(): png = R.VAN_RP / (tp + ".png")
    faces = truth_posed_faces(bones, tw, th, aff)
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    out = Image.new("RGB", (len(views) * (W_ + 4), H_ + 24), (255, 255, 255))
    ImageDraw.Draw(out).text((4, 4), title, fill=(0, 0, 0), font=F)
    for i, v in enumerate(views):
        e, tt = camera(faces, v, pad=1.05)
        im = render_entity(faces, png, e, tt, W_, H_, fov=FOV).convert("RGB")
        ImageDraw.Draw(im).text((4, 4), v, fill=(0, 0, 0), font=F)
        out.paste(im, (i * (W_ + 4), 24))
    return out


# ------------------------------------------------------------------------------------------------------------ mechanism
def polar_rot(M):
    U, _, Vt = np.linalg.svd(M); Rm = U @ Vt
    if np.linalg.det(Rm) < 0: U[:, -1] *= -1; Rm = U @ Vt
    return Rm


def swing_twist(Rm, u):
    """split rotation Rm into twist about unit axis u and the remaining swing; returns (twist deg, swing deg)"""
    q = rot_to_quat(Rm); v = q[1:]; p = np.dot(v, u) * u
    tw = np.array([q[0], *p]); n = np.linalg.norm(tw)
    if n < 1e-12: return 0.0, math.degrees(2 * math.acos(min(1, abs(q[0]))))
    tw /= n; sw = quat_mul(q, quat_conj(tw))
    ang = lambda qq: math.degrees(2 * math.acos(min(1.0, abs(qq[0]))))
    return ang(tw), ang(sw)


def rot_to_quat(Rm):
    t = np.trace(Rm)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2; return np.array([0.25 * s, (Rm[2, 1] - Rm[1, 2]) / s, (Rm[0, 2] - Rm[2, 0]) / s, (Rm[1, 0] - Rm[0, 1]) / s])
    i = int(np.argmax(np.diag(Rm)))
    if i == 0:
        s = math.sqrt(1.0 + Rm[0, 0] - Rm[1, 1] - Rm[2, 2]) * 2
        return np.array([(Rm[2, 1] - Rm[1, 2]) / s, 0.25 * s, (Rm[0, 1] + Rm[1, 0]) / s, (Rm[0, 2] + Rm[2, 0]) / s])
    if i == 1:
        s = math.sqrt(1.0 + Rm[1, 1] - Rm[0, 0] - Rm[2, 2]) * 2
        return np.array([(Rm[0, 2] - Rm[2, 0]) / s, (Rm[0, 1] + Rm[1, 0]) / s, 0.25 * s, (Rm[1, 2] + Rm[2, 1]) / s])
    s = math.sqrt(1.0 + Rm[2, 2] - Rm[0, 0] - Rm[1, 1]) * 2
    return np.array([(Rm[1, 0] - Rm[0, 1]) / s, (Rm[0, 2] + Rm[2, 0]) / s, (Rm[1, 2] + Rm[2, 1]) / s, 0.25 * s])


def quat_mul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2])


def quat_conj(q): return np.array([q[0], -q[1], -q[2], -q[3]])


def join_line(spec, a_root, b_root, bones, aff0):
    """the bind-pose join line (world, file frame): the long axis of the outer piece's root face through its centre"""
    Bn = set(subtree(bones, b_root)); An = (set(subtree(bones, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    Ab, Bb = boxes(bones, aff0, An), boxes(bones, aff0, Bn)
    bb = {x["name"]: x for x in bones}[b_root]; A_, t_ = aff0[b_root]
    hinge = A_ @ np.array(bb.get("pivot", [0, 0, 0]), float) + t_
    fr = root_frames(Bb, Ab, hinge)
    if not fr: return None
    f = fr[0]; box = Bb[f["k"]][2]; o = box[0]; axes = [box[4] - o, box[2] - o, box[1] - o]
    rest = [a for a in range(3) if a != f["ax"]]
    h = max(rest, key=lambda a: np.linalg.norm(axes[a]))
    u = axes[h] / np.linalg.norm(axes[h])
    centre = o + axes[f["ax"]] * f["side"] + 0.5 * sum(axes[a] for a in rest)
    return centre, u, hinge, float(np.linalg.norm(axes[h]))


def mechanism(mob, state, a_root, b_root, seconds=4.0, warm=1.0):
    """per tick: the outer piece's rotation relative to the inner piece (vs bind) split into TWIST about the join line (a
    hinge: harmless) and SWING (opens the join); the pivot's distance from the join line; the chain's scale anisotropy"""
    spec = SPECS[mob]; env_state, shorts = spec["states"][state]
    _, g = find_geo(spec["pack"], spec["gid"]); bones = g["bones"]
    aff0 = affines(bones, {})
    c0, u0, hinge0, L = join_line(spec, a_root, b_root, bones, aff0)
    # the inner piece's frame = the bone that carries its cubes nearest the join
    Bn = set(subtree(bones, b_root)); An = (set(subtree(bones, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    a_bone = min((b for b in bones if b["name"] in An and b.get("cubes")), key=lambda b: 0 if b["name"] == a_root else 1)["name"] \
        if any(b["name"] in An and b.get("cubes") for b in bones) else a_root
    b_bone = b_root
    RA0, RB0 = polar_rot(aff0[a_bone][0]), polar_rot(aff0[b_bone][0])
    Rrel0 = RA0.T @ RB0; u_loc = RA0.T @ u0
    piv_off = float(np.linalg.norm(np.cross(hinge0 - c0, u0)))
    rows = []
    for k in range(int(seconds / DT)):
        t = k * DT
        bones_t, aff, ch = pose_at(spec, env_state, shorts, t, warm)
        RA, RB = polar_rot(aff[a_bone][0]), polar_rot(aff[b_bone][0])
        dR = (RA.T @ RB) @ Rrel0.T
        tw, sw = swing_twist(dR, u_loc)
        sv = np.linalg.svd(aff[b_bone][0], compute_uv=False)
        rows.append((t, tw, sw, float(sv.max() / max(sv.min(), 1e-9))))
    return {"join_len": round(L, 2), "pivot_off_line": round(piv_off, 2),
            "twist_max": round(max(r[1] for r in rows), 1), "swing_max": round(max(r[2] for r in rows), 1),
            "swing_median": round(float(np.median([r[2] for r in rows])), 1), "anisotropy_max": round(max(r[3] for r in rows), 3),
            "inner_bone": a_bone}


# ------------------------------------------------------------------------------------------------------------ bridge cover
def bridge_cover(mob, state, a_root, b_root, depth, seconds=4.0, warm=1.0):
    """with an overlap bridge of `depth` px on the outer piece: per tick, does the strip from each root station (x thickness)
    reaching `depth` px outward (where the bridge lies) still touch the inner piece? edge = worst station (any thickness
    touching = covered), face = worst (station, thickness). depth 0 = the bare root line (the shipped joint)."""
    spec = SPECS[mob]; env_state, shorts = spec["states"][state]
    _, g = find_geo(spec["pack"], spec["gid"]); bones0 = g["bones"]
    aff0 = affines(bones0, {})
    Bn = set(subtree(bones0, b_root)); An = (set(subtree(bones0, a_root)) - Bn) if a_root not in ("body", "body2") else {a_root}
    Ab0, Bb0 = boxes(bones0, aff0, An), boxes(bones0, aff0, Bn)
    by = {x["name"]: x for x in bones0}; A_, t_ = aff0[b_root]
    hinge = A_ @ np.array(by[b_root].get("pivot", [0, 0, 0]), float) + t_
    frames = root_frames(Bb0, Ab0, hinge)
    samp = []
    for fr in frames:
        box = Bb0[fr["k"]][2]; o = box[0]
        L = [np.linalg.norm(box[4] - o), np.linalg.norm(box[2] - o), np.linalg.norm(box[1] - o)]
        ax, side = fr["ax"], fr["side"]; rest = [k for k in range(3) if k != ax]
        h = max(rest, key=lambda k: L[k]); w = [k for k in rest if k != h][0]
        outs = np.linspace(0, depth / max(L[ax], 1e-6), 7) if depth > 0 else np.array([0.0])
        for i, sv in enumerate(np.linspace(0, 1, 21)):
            for j, wv in enumerate(np.linspace(0, 1, 5)):
                P = []
                for e in outs:
                    p = [0.0, 0.0, 0.0]; p[ax] = (1.0 + e) if side == 1.0 else -e; p[h] = sv; p[w] = wv; P.append(p)
                samp.append((fr["k"], i, j, P))
    bind = {}
    for k, i, j, P in samp: bind[(k, i, j)] = float(dist_to(params_to_pts(Bb0[k][2], P), Ab0).min())
    tol = EPS if min(bind.values()) <= EPS else min(bind.values()) + EPS
    keep = {key for key, v in bind.items() if v <= tol}
    rows = []
    for n in range(int(seconds / DT)):
        t = n * DT
        bones_t, aff, ch = pose_at(spec, env_state, shorts, t, warm)
        Ab, Bb = boxes(bones_t, aff, An), boxes(bones_t, aff, Bn)
        per = {}
        for k, i, j, P in samp:
            if (k, i, j) in keep: per[(k, i, j)] = float(dist_to(params_to_pts(Bb[k][2], P), Ab).min())
        stations = {}
        for (k, i, j), v in per.items(): stations.setdefault((k, i), []).append(v)
        rows.append((t, max(min(v) for v in stations.values()) if stations else 0.0, max(per.values()) if per else 0.0))
    e = [r[1] for r in rows]; f = [r[2] for r in rows]
    return {"depth": depth, "edge_max": round(max(e), 3), "edge_median": round(float(np.median(e)), 3), "face_max": round(max(f), 3),
            "at_t": rows[int(np.argmax(e))][0], "bind_gap": None if min(bind.values()) <= EPS else round(min(bind.values()), 3)}

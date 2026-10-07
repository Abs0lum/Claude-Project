#!/usr/bin/env python3
"""std_famshare.py — p22 FAMILY layer (his 14:52 ask + 12:51 rule): a creature that lacks a motion its anatomy really has
(std_families: family + allowed kinds) is OFFERED the best clip of that kind from a family relative, retargeted, as an EXTRA
`fam_<kind>` (nothing replaces its own clips; he keeps or drops each in p22).

Runs on the ASSEMBLY (assemble_std.py), after the share layer; never touches the frozen base.
Per (target, kind) the family's own clips of that kind are tried richest first (max 3 sources); the first that passes is offered:
  COVER   >= 80 % of the clip's bones exist in the target's standard rig (names are the standard language).
  CARRY   the variables the clip reads come along (molang_carry, renamed per source); one nobody can set refuses the copy.
  SCALE   position channels x (target rig height / source rig height); rotations as they are.
  SAME    sampled at 6 moments, every animated bone shared by both rigs turns the same way in the WORLD on both (geodesic angle
          between the two world-frame rotation changes <= 20 deg) — a bone with a different rest orientation would turn a
          leg sideways; such a copy is refused, never guessed.
  GROUND  (not swim / fly) the target never sinks more than max(1 px, the source's own sink x scale + 0.5) below its rest
          ground; walk / run touch the ground (within 1 px) at least once; no part moves farther than the rig's diagonal.
  EVAL    every channel evaluates (molang_eval) — an unevaluable clip is refused (cannot be checked = not offered).
Movement-driven clips are evaluated on a treadmill (time = distance at a normal pace).
Writes _docs/standard/FAMILY-SHARING.json + FAMILY-PICKLIST.md."""
import copy
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import anim_sample as AS  # noqa: E402
import molang_carry as MC  # noqa: E402
import molang_eval as ME  # noqa: E402
import posed_preview as PP  # noqa: E402
import std_convert as S  # noqa: E402
import std_cube as CU  # noqa: E402
import std_families as F  # noqa: E402
import std_share as SH  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

N_SAMPLES = 6
MAX_SOURCES = 3
SAME_DEG = 20.0
MOVE = re.compile(r"(modified_distance_moved|walk_distance)", re.I)


NOT_SOURCE = re.compile(r"(baby|^un|_un|unsit|wake|stand_?up|get_?up|_start|_end|start_|end_|to_|_to|transition|intro|outro)", re.I)


class Rig:
    def __init__(self, mob, stage):
        self.mob = mob
        self.slug = S.slug_of(mob)
        self.ef = next(stage.glob(f"*/entity/std/{self.slug}.entity.json"))
        self.af = self.ef.parent.parent.parent / "animations/std" / f"{self.slug}.animation.json"
        self.gf = self.ef.parent.parent.parent / "models/entity/std" / f"{self.slug}.geo.json"
        self.ent = S.jload(self.ef)
        self.an = S.jload(self.af)
        geo = S.jload(self.gf)["minecraft:geometry"]
        desc = self.ent["minecraft:client_entity"]["description"]
        gid = (desc.get("geometry") or {}).get("default") or next(iter((desc.get("geometry") or {}).values()), None)
        g = next((x for x in geo if x["description"]["identifier"] == gid), geo[0])
        self.bones = g["bones"]
        self.names = {b["name"] for b in self.bones}
        self.desc = desc
        self.fmt = self.ent.get("format_version", "1.10.0")
        self.rest = self._world(self.bones)
        pts = np.array([p for _, ps in self.rest["corners"].items() for p in ps]) if self.rest["corners"] else np.zeros((1, 3))
        self.ground = float(pts[:, 1].min())
        self.height = max(1.0, float(pts[:, 1].max() - pts[:, 1].min()))
        self.diag = float(np.linalg.norm(pts.max(0) - pts.min(0))) or 1.0

    @staticmethod
    def _world(bones):
        aff = bone_affines(bones)
        corners = {}
        for b in bones:
            A, t = aff[b["name"]]
            ps = [A @ p + t for c in (b.get("cubes") or []) for p in CU.corners(c)]
            if ps:
                corners[b["name"]] = ps
        return {"aff": aff, "corners": corners}

    def own_clips(self):
        out = {}
        for short, aid in (self.desc.get("animations") or {}).items():
            if aid.startswith("controller.") or short.startswith(("shared_", "fam_", "parade_")) or aid not in self.an["animations"]:
                continue
            if NOT_SOURCE.search(short):
                continue   # 15:4x: a BABY clip is made for the baby model; a transition (unsit, wake, stand up) is not the pose
            k = SH.kind_of(short)
            if not k:
                continue
            a = self.an["animations"][aid]
            if all(all(v in ([0, 0, 0], 0) for v in ch.values()) for ch in (a.get("bones") or {}).values()):
                continue
            r = SH.richness(a)
            if k not in out or r > out[k][2]:
                out[k] = (short, aid, r)
        return out

    def has_kind(self, k):
        for short in (self.desc.get("animations") or {}):
            if SH.kind_of(short.replace("shared_", "").replace("fam_", "")) == k:
                return True
        return False

    def env(self, extra_pre=()):
        e = {"q.is_on_ground": 1.0, "q.is_alive": 1.0, "q.delta_time": 0.05, "q.modified_move_speed": 1.0, "q.ground_speed": 2.0,
             "q.is_moving": 1.0, "q.life_time": 0.0}
        sc = self.desc.get("scripts") or {}
        for s in list(sc.get("initialize") or []) + list(sc.get("pre_animation") or []) + list(extra_pre):
            try:
                ME.run(s, e)
            except Exception:  # noqa: BLE001 — a script we cannot evaluate leaves its variables unset (read as 0)
                pass
        return e


def sample_times(clip):
    L = AS.clip_length(clip)
    return [L * (i + 0.5) / N_SAMPLES for i in range(N_SAMPLES)]


def posed(rig, clip, t, env, pos_scale=1.0, exact=False):
    e = dict(env)
    moving = bool(MOVE.search(str(clip.get("anim_time_update", ""))))
    at = t * 2.0 if (moving and not exact) else t        # treadmill: anim time = distance at a normal pace (2 blocks / s);
    #                                                      exact=True: t IS the anim time (a baked key)
    e.update({"q.anim_time": at, "q.life_time": t, "q.modified_distance_moved": t * 2.0, "q.walk_distance": t * 2.0})
    s = AS.sample_clip(clip, at, e)
    ch = {}
    for b, c in s.items():
        if b not in rig.names:
            continue
        o = {}
        if "rotation" in c:
            o["rotation"] = c["rotation"]
        if "position" in c:
            o["position"] = [x * pos_scale for x in c["position"]]
        ch[b] = o
    bones = PP.posed_bones(rig.bones, ch, {})
    return Rig._world(bones), set(ch)


def rot_angle(A, B):
    R = A @ B.T
    c = max(-1.0, min(1.0, (np.trace(R) - 1.0) / 2.0))
    return math.degrees(math.acos(c))


def lowest(world):
    return min(p[1] for ps in world["corners"].values() for p in ps) if world["corners"] else 0.0


def max_move(rest, world):
    m = 0.0
    for b, ps in world["corners"].items():
        for p, q in zip(ps, rest["corners"].get(b, ps)):
            m = max(m, float(np.linalg.norm(p - q)))
    return m


CORE = re.compile(r"^(root|body(_\d+)?|neck\w*|head|skull|spine\w*|chest|torso|shoulder_[lr]|upper_arm_[lr]|elbow_[lr]|forearm_[lr]|"
                  r"wrist_[lr]|front_foot_[lr]|hip_[lr]|thigh_[lr]|knee_[lr]|shin_[lr]|hock_[lr]|hind_foot_[lr]|leg\w*|foot\w*|"
                  r"ankle\w*|arm\w*|tail(_\d+)?|segment\w*|fin\w*|flipper\w*|jaw\w*)$")
BAKE_N = 24
OPTIONAL = re.compile(r"^(neck\w*|spine\w*|chest|torso|body_\d+|tail_\d+|jaw\w*|hock_[lr]|skull|wrist_[lr]|knee_[lr]|elbow_[lr])$")


def order(bones):
    by = {b["name"]: b for b in bones}
    out, seen = [], set()

    def visit(n):
        if n in seen:
            return
        p = by[n].get("parent")
        if p in by:
            visit(p)
        seen.add(n)
        out.append(n)
    for b in bones:
        visit(b["name"])
    return out


def _pivot_world(by, aff, n):
    par = by[n].get("parent")
    A, t = aff[par] if par else (np.eye(3), np.zeros(3))
    return A @ np.array(by[n].get("pivot", [0, 0, 0]), float) + t


def bake(src, tgt, clip, mapped, scale, env_s):
    """the source clip, retargeted in the WORLD (17:1x redesign). At each sample:
    ROTATION  every bone both rigs share — animated by the clip OR moved only through its parents (the wild dog sits by
              turning root_2, which the wolf lacks: its body must still tilt) — gets the world-frame rotation change its
              source bone makes, solved parent first.
    POSITION  only the TRUNK (the target's main body; its source = the same-named bone, else the source's main body) and the
              whole-body bones: their pivot moves by the source's world pivot displacement x scale (closed form through the
              parent's posed frame). Limbs, head and tail get no copied positions: attach_follow() seats them on the trunk.
    Keyframes in the clip's own anim-time units; anim_time_update kept when it reads only queries."""
    from equine_compare import rot_matrix
    L = AS.clip_length(clip)
    times = [L * i / BAKE_N for i in range(BAKE_N + 1)]
    by_t = {b["name"]: b for b in tgt.bones}
    by_s = {b["name"]: b for b in src.bones}
    ordr = order(tgt.bones)
    shared = (tgt.names & src.names) | set(mapped)
    rot_k, pos_k = defaultdict(dict), defaultdict(dict)
    prev = {}
    tb, sb = main_body(tgt), main_body(src)
    pos_bones = [n for n in ordr if n in whole_body_bones(tgt) or n == tb]
    src_of = {n: (n if n in src.names else (sb if n == tb else None)) for n in pos_bones}
    for at in times:
        e = dict(env_s)
        e.update({"q.anim_time": at, "q.life_time": at, "q.modified_distance_moved": at, "q.walk_distance": at})
        smp = AS.sample_clip(clip, at, e)
        ch = {b: {k: v for k, v in c.items() if k in ("rotation", "position")} for b, c in smp.items() if b in src.names}
        sbones = PP.posed_bones(src.bones, ch, {})
        saff = bone_affines(sbones)
        sby = {b["name"]: b for b in sbones}
        ws = {"aff": saff}
        Wp = {}
        key = f"{at:.4f}"
        for n in ordr:
            b = by_t[n]
            par = b.get("parent")
            W_par = Wp[par] if par in Wp else np.eye(3)
            bind = list(b.get("rotation", [0, 0, 0]) or [0, 0, 0])
            if n in shared:
                dR = ws["aff"][n][0] @ src.rest["aff"][n][0].T
                W_des = dR @ tgt.rest["aff"][n][0]
                eul = CU.euler_of(W_par.T @ W_des)
                d = [eul[i] - bind[i] for i in range(3)]
                if n in prev:                                  # unwrap: the equivalent angle closest to the last sample
                    d = [x + 360.0 * round((prev[n][i] - x) / 360.0) for i, x in enumerate(d)]
                prev[n] = d
                rot_k[n][key] = [round(float(x), 3) for x in d]
                Wp[n] = W_par @ rot_matrix([bind[i] + d[i] for i in range(3)])
            else:
                Wp[n] = W_par @ rot_matrix(bind)
        # positions: trunk + whole-body bones, parent first, against the target posed with what is baked so far
        for n in pos_bones:
            sn = src_of[n]
            if not sn:
                continue
            disp = (_pivot_world(sby, saff, sn) - _pivot_world(by_s, src.rest["aff"], sn)) * scale
            tch = {}
            for bn, kk in rot_k.items():
                if key in kk:
                    tch.setdefault(bn, {})["rotation"] = kk[key]
            for bn, kk in pos_k.items():
                if key in kk:
                    tch.setdefault(bn, {})["position"] = kk[key]
            tbones = PP.posed_bones(tgt.bones, tch, {})
            taff = bone_affines(tbones)
            tby = {x["name"]: x for x in tbones}
            want = _pivot_world(by_t, tgt.rest["aff"], n) + disp
            now = _pivot_world(tby, taff, n)
            par = by_t[n].get("parent")
            Ap = taff[par][0] if par else np.eye(3)
            Ar = tgt.rest["aff"][par][0] if par else np.eye(3)
            dp = np.linalg.inv(Ap @ Ar) @ (want - now)
            old = pos_k[n].get(key, [0.0, 0.0, 0.0])
            pos_k[n][key] = [round(float(old[i] + dp[i]), 4) for i in range(3)]
    for n in list(rot_k):                                       # a shared bone that never turns needs no channel
        if all(max(abs(x) for x in v) < 0.01 for v in rot_k[n].values()):
            rot_k.pop(n)
    for n in list(pos_k):
        if all(max(abs(x) for x in v) < 0.01 for v in pos_k[n].values()):
            pos_k.pop(n)
    out = {k: v for k, v in clip.items() if k in ("loop", "animation_length", "anim_time_update", "blend_weight")}
    if "anim_time_update" in out and re.search(r"\b(v|variable)\.", str(out["anim_time_update"])):
        out.pop("anim_time_update")
    out["animation_length"] = round(L, 4)
    out["bones"] = {}
    for n in set(rot_k) | set(pos_k):
        o = {}
        if n in rot_k:
            o["rotation"] = rot_k[n]
        if n in pos_k:
            o["position"] = pos_k[n]
        out["bones"][n] = o
    return out


GROUNDED = {"walk", "run", "idle", "eat", "sit", "sleep", "call"}


def ground_lock(tgt, c2, env_t, both_ways):
    """keep the animal on its ground (what an animator does after a retarget between different proportions): at every baked
    key the whole body (every top-level bone) shifts up — and, for poses that stay grounded, down — so its lowest point is the
    rest ground. Jumps / pounces are only lifted out of the ground, never pulled down."""
    keys = sorted({k for ch in c2["bones"].values() for c in ch.values() for k in c})
    tops = [b["name"] for b in tgt.bones if not b.get("parent")]
    shifts = {}
    for k in keys:
        w, _ = posed(tgt, c2, float(k), env_t, exact=True)
        d = tgt.ground - lowest(w)
        shifts[k] = d if both_ways else max(0.0, d)
    if all(abs(v) < 0.05 for v in shifts.values()):
        return
    for n in tops:
        ch = c2["bones"].setdefault(n, {})
        pos = ch.get("position")
        if pos is None:
            pos = {k: [0.0, 0.0, 0.0] for k in keys}
        elif not isinstance(pos, dict):
            pos = {k: list(AS.sample_channel(pos, float(k), {})) for k in keys}
        for k in keys:
            v = list(pos.get(k) or AS.sample_channel(pos, float(k), {}))
            v[1] = round(v[1] + shifts[k], 4)
            pos[k] = v
        ch["position"] = pos


FIT = 0.10   # body height miss allowed, share of the animal's height (cat on the lion's lie: 0.32; gelada: 0.14)
LOW_POSES = {"sit", "sleep"}   # poses that LOWER the body: the trunk height follows the source, the limbs make room (17:1x)


def _trunk_min(rig, world):
    return float(np.array(world["corners"][main_body(rig)])[:, 1].min())


def _set_key(c2, n, chan, k, v, keys):
    ch = c2["bones"].setdefault(n, {})
    cur = ch.get(chan)
    if not isinstance(cur, dict):
        base = cur if isinstance(cur, list) else None
        cur = {kk: list(base or [0.0, 0.0, 0.0]) for kk in keys}
    cur[k] = [round(float(x), 4) for x in v]
    ch[chan] = cur


def low_pose_lock(src, tgt, clip, c2, env_s, env_t):
    """17:1x (FAM-PREVIEW-3: cat / deer / gelada floating on their own folded legs or tail). For a pose that lowers the body:
    1 TRUNK  the target's trunk keeps the source's trunk height RATIO (posed clearance / rest clearance, per key) — the lion lies
             with its belly 0.1 px off the ground, so the cat lies with its belly on the ground, not lifted by its longer legs;
    2 ROOM   every carried chain (leg, tail, head) that then reaches below the ground swings about the animal's side-to-side
             axis at its top joint by the smallest angle (2..90 deg, either way) that brings it out (what a real animal does:
             tucks the leg further / lifts the tail);
    3 LIFT   whatever still sinks lifts the whole animal (the old lock) — only up, never down."""
    from equine_compare import rot_matrix
    keys = sorted({k for ch in c2["bones"].values() for c in ch.values() if isinstance(c, dict) for k in c}, key=float)
    if not keys:
        return
    tops = [b["name"] for b in tgt.bones if not b.get("parent")]
    rest_by = {b["name"]: b for b in tgt.bones}
    sub = _subtree(tgt)
    chains = [j for j, _, _, _ in carriers(tgt)]
    src_rest_clear = _trunk_min(src, src.rest) - src.ground
    tgt_rest_clear = _trunk_min(tgt, tgt.rest) - tgt.ground
    for k in keys:
        at = float(k)
        ws, _ = posed(src, clip, at, env_s, exact=True)
        ratio = (_trunk_min(src, ws) - src.ground) / src_rest_clear if src_rest_clear > 0.5 else 1.0
        want = tgt.ground + max(0.0, ratio) * tgt_rest_clear
        wt, _ = posed(tgt, c2, at, env_t, exact=True)
        dy = want - _trunk_min(tgt, wt)
        for n in tops:
            pos = (c2["bones"].get(n) or {}).get("position")
            v = list(AS.sample_channel(pos, at, {})) if pos is not None else [0.0, 0.0, 0.0]
            v[1] += dy
            _set_key(c2, n, "position", k, v, keys)
        for j in chains:
            by, aff = _pose_full(tgt, c2, at, env_t)
            pts = []
            for n in sub[j]:
                for c in (by[n].get("cubes") or []):
                    A, t = aff[n]
                    pts += [A @ q + t for q in CU.corners(c)]
            if not pts:
                continue
            pts = np.array(pts)
            if pts[:, 1].min() >= tgt.ground - 0.3:
                continue
            P = _pivot_world(by, aff, j)
            best = None
            for mag in range(2, 92, 2):
                for sgn in (1, -1):
                    th = math.radians(sgn * mag)
                    Rx = np.array([[1, 0, 0], [0, math.cos(th), -math.sin(th)], [0, math.sin(th), math.cos(th)]])
                    lo = float(((pts - P) @ Rx.T + P)[:, 1].min())
                    if best is None or lo > best[0] + 1e-6:
                        best = (lo, sgn * mag, Rx)
                    if lo >= tgt.ground - 0.3:
                        best = (lo, sgn * mag, Rx)
                        break
                if best[0] >= tgt.ground - 0.3:
                    break
            if best is None or best[0] <= pts[:, 1].min() + 1e-6:
                continue
            Rx = best[2]
            par = rest_by[j].get("parent")
            Ap = aff[par][0] if par else np.eye(3)
            bind = list(rest_by[j].get("rotation", [0, 0, 0]) or [0, 0, 0])
            eul = CU.euler_of(Ap.T @ Rx @ aff[j][0])
            rot = (c2["bones"].get(j) or {}).get("rotation")
            old = list(AS.sample_channel(rot, at, {})) if rot is not None else [0.0, 0.0, 0.0]
            d = [eul[i] - bind[i] for i in range(3)]
            d = [x + 360.0 * round((old[i] - x) / 360.0) for i, x in enumerate(d)]
            _set_key(c2, j, "rotation", k, d, keys)
    ground_lock(tgt, c2, env_t, both_ways=False)


def whole_body_bones(rig):
    """bones whose subtree holds >= 90 % of the rig's cubes (root / root_2 / body …): moving them moves the whole animal."""
    kids = defaultdict(list)
    for b in rig.bones:
        kids[b.get("parent")].append(b["name"])
    n_cubes = {b["name"]: len(b.get("cubes") or []) for b in rig.bones}
    total = sum(n_cubes.values()) or 1

    def sub(n):
        return n_cubes[n] + sum(sub(k) for k in kids[n])
    return {b["name"] for b in rig.bones if sub(b["name"]) >= 0.9 * total}


def _vol(b):
    return sum(float(np.prod([max(0.01, x) for x in c.get("size", [0, 0, 0])])) for c in (b.get("cubes") or []))


def _subtree(rig):
    kids = defaultdict(list)
    for b in rig.bones:
        kids[b.get("parent")].append(b["name"])
    out = {}

    def sub(n):
        if n not in out:
            out[n] = {n}.union(*[sub(k) for k in kids[n]]) if kids[n] else {n}
        return out[n]
    for b in rig.bones:
        sub(b["name"])
    return out


def main_body(rig):
    """the cubed bone with the largest cube volume (the trunk)."""
    cub = [b for b in rig.bones if b.get("cubes")]
    return max(cub, key=_vol)["name"] if cub else None


def body_chain(rig):
    """the main body and its ancestors (moving them moves the trunk)."""
    by = {b["name"]: b for b in rig.bones}
    n, out = main_body(rig), set()
    while n:
        out.add(n)
        n = by[n].get("parent")
    return out


WING_PART = re.compile(r"^(wing|primary|secondary|tertial|feather|alula)", re.I)
TOUCH = 3.0   # 17:1x: the cat's upper arm stops 1.26 px under its body at rest, its thigh 2.05 px (Patrix legs end short of the
#               trunk; the fur overlap hides it) — "touching" for a carrier is within 3 px


def _ancestors(by, n):
    out = []
    while n:
        out.append(n)
        n = by[n].get("parent")
    return out


def _lca_depth(by, a, b):
    """depth (from the top bone) of the deepest joint both bones hang under."""
    pa = _ancestors(by, a)
    pb = set(_ancestors(by, b))
    for n in pa:
        if n in pb:
            return len(_ancestors(by, n))
    return 0


def carriers(rig):
    """17:1x (FAM-PREVIEW-2): the standard rig hangs limbs, head and tail off CUBELESS joints (root / root_2), so the hierarchy
    does not say what a part is attached to — the rest geometry does. For every cubed part with no cubed ancestor: its carrier =
    the largest part it touches at rest (gap <= TOUCH px) outside its own subtree and bigger than its whole subtree; its top joint =
    the highest ancestor-or-self whose subtree does not hold the carrier. Returns [(top joint, part, carrier, rest gap)],
    carriers-first order (a carrier that itself follows comes before the parts it carries)."""
    by = {b["name"]: b for b in rig.bones}
    sub = _subtree(rig)
    vol = {b["name"]: _vol(b) for b in rig.bones}
    out = []
    for b in rig.bones:
        if not b.get("cubes"):
            continue
        p = b.get("parent")
        while p and not by[p].get("cubes"):
            p = by[p].get("parent")
        if p:
            continue                                    # hierarchy already carries it
        x = b["name"]
        if WING_PART.match(x):
            continue        # 17:2x (audit): a folded wing touches the body at rest and opens away from it — that is flight, not a
            #                 loose part (the wing root's own contact is std_flight's G6)
        sv = sum(vol[n] for n in sub[x])
        cands = []
        for c in rig.rest["corners"]:
            if c in sub[x] or x in sub[c] or vol[c] <= sv:
                continue
            g = gap(rig.rest["corners"][x], rig.rest["corners"][c])
            if g <= TOUCH:
                # 17:2x (shared-clip audit: a horn paired with the neck came "loose" when the head turned): the part that shares
                # the DEEPEST joint with it first (horn + skull share `head`; horn + neck only share root), then the closest,
                # then the biggest
                cands.append((-_lca_depth(by, x, c), round(g * 2) / 2, -vol[c], c))
        if not cands:
            continue
        c = min(cands)[3]
        j = x
        while by[j].get("parent") and c not in sub[by[j]["parent"]]:
            j = by[j]["parent"]
        if any(r[0] == j for r in out):
            continue                                    # one carrier per joint
        out.append((j, x, c, gap(rig.rest["corners"][x], rig.rest["corners"][c])))
    followers = {j for j, _, _, _ in out}
    depth = {}

    def d(row):
        j, x, c, _ = row
        if j in depth:
            return depth[j]
        depth[j] = 0
        up = next((r for r in out if c in sub[r[0]] and r[0] != j), None)
        depth[j] = d(up) + 1 if up and up[0] in followers else 0
        return depth[j]
    return sorted(out, key=d)


def _pose_full(rig, c2, at, env):
    e = dict(env)
    e.update({"q.anim_time": at, "q.life_time": at, "q.modified_distance_moved": at, "q.walk_distance": at})
    smp = AS.sample_clip(c2, at, e)
    ch = {b: {k: v for k, v in c.items() if k in ("rotation", "position")} for b, c in smp.items() if b in rig.names}
    bones = PP.posed_bones(rig.bones, ch, {})
    return {b["name"]: b for b in bones}, bone_affines(bones)


def attach_follow(tgt, c2, env_t):
    """re-seat every carried part on its carrier at every baked key: the top joint's pivot goes where the carrier's rigid motion
    takes its rest pivot. Bedrock position = a shift in the parent's REST frame that then rides the parent's pose
    (posed_preview, D-C311), so the channel change is closed form: dp = (A_par_posed @ A_par_rest)^-1 @ (wanted - now)."""
    rows = carriers(tgt)
    if not rows:
        return 0
    keys = sorted({k for ch in c2["bones"].values() for c in ch.values() if isinstance(c, dict) for k in c}, key=float)
    if not keys:
        return 0
    rest_by = {b["name"]: b for b in tgt.bones}
    raff = tgt.rest["aff"]
    sub = _subtree(tgt)
    level, levels = {}, []
    for j, x, c, g0 in rows:                    # rows come carriers-first: a row whose carrier rides an earlier joint goes deeper
        lv = max([level[r] + 1 for r in level if c in sub[r]] or [0])
        level[j] = lv
        while len(levels) <= lv:
            levels.append([])
        levels[lv].append((j, x, c, g0))
    for k in keys:
        at = float(k)
        for group in levels:
            by, aff = _pose_full(tgt, c2, at, env_t)          # one pose per level (17:1x speed: was one per row)
            for j, x, c, g0 in group:
                par = rest_by[j].get("parent")
                Ap, tp = aff[par] if par else (np.eye(3), np.zeros(3))
                now = Ap @ np.array(by[j].get("pivot", [0, 0, 0]), float) + tp
                Ar, tr = raff[par] if par else (np.eye(3), np.zeros(3))
                q = Ar @ np.array(rest_by[j].get("pivot", [0, 0, 0]), float) + tr          # rest world pivot
                Ac0, tc0 = raff[c]
                Ac, tcw = aff[c]
                shift_c = np.array(by[c].get("pivot", [0, 0, 0]), float) - np.array(rest_by[c].get("pivot", [0, 0, 0]), float)
                want = Ac @ (Ac0.T @ (q - tc0) + shift_c) + tcw
                delta = want - now
                if float(np.linalg.norm(delta)) < 0.01:
                    continue
                dp = np.linalg.inv(Ap @ Ar) @ delta
                ch = c2["bones"].setdefault(j, {})
                pos = ch.get("position")
                if not isinstance(pos, dict):
                    base = pos if isinstance(pos, list) else None
                    pos = {kk: list(base or [0.0, 0.0, 0.0]) for kk in keys}
                v = list(pos.get(k) or AS.sample_channel(pos, at, {}))
                pos[k] = [round(float(v[i2] + dp[i2]), 4) for i2 in range(3)]
                ch["position"] = pos
    return len(rows)


def joined_pairs(rig):
    """(child, part it hangs on, rest gap px) for every bone with cubes: its nearest cubed ancestor, or — 17:1x — for a part hung
    off cubeless joints, the carrier it touches at rest (carriers())."""
    by = {b["name"]: b for b in rig.bones}
    out = []
    for b in rig.bones:
        if not b.get("cubes"):
            continue
        p = b.get("parent")
        while p and not by[p].get("cubes"):
            p = by[p].get("parent")
        if p and WING_PART.match(b["name"]) and not WING_PART.match(p):
            continue        # a wing piece hung (through cubeless wing joints) on the body: opening the wing is not coming loose
        if p:
            out.append((b["name"], p, gap(rig.rest["corners"][b["name"]], rig.rest["corners"][p])))
    out += [(x, c, g0) for _, x, c, g0 in carriers(rig)]
    return out


def gap(ps, qs):
    """distance between two parts' bounding boxes (0 when they touch / overlap)."""
    a, b = np.array(ps), np.array(qs)
    d = np.maximum(0.0, np.maximum(a.min(0) - b.max(0), b.min(0) - a.max(0)))
    return float(np.linalg.norm(d))


def src_parent(src, n):
    return next((b.get("parent") for b in src.bones if b["name"] == n), None)


def try_retarget(src, tgt, kind, short, aid):
    clip = src.an["animations"][aid]
    bones = set((clip.get("bones") or {}))
    if not bones:
        return None, "empty clip"
    core = {b for b in bones if CORE.match(b)}
    if not core:
        return None, "moves no body-carrying joint"
    # intermediate joints (an extra neck / spine / tail segment, the jaw, a hock, knee or elbow split) are OPTIONAL: the world
    # solve gives the next mapped joint its source world motion anyway (felid census 15:4x: neck 1170, tail_3 460, body_2 345 …)
    need = {b for b in core if not OPTIONAL.match(b)} or core
    cover = len(need & tgt.names & src.names) / len(need)
    if cover < 0.9:
        return None, f"body joints cover {cover:.2f}"
    mapped = bones & tgt.names & src.names
    scale = tgt.height / src.height
    env_s = src.env()
    try:
        c2 = bake(src, tgt, clip, mapped, scale, env_s)
    except Exception as e:  # noqa: BLE001
        return None, f"unevaluable ({type(e).__name__}: {str(e)[:40]})"
    if not c2["bones"]:
        return None, "nothing to move on this rig"
    env_t = tgt.env()
    attach_follow(tgt, c2, env_t)
    if kind not in ("swim", "fly"):
        if kind in LOW_POSES:
            low_pose_lock(src, tgt, clip, c2, env_s, env_t)
        else:
            ground_lock(tgt, c2, env_t, both_ways=kind in GROUNDED)
    worst_same, sink_t, sink_s, touch, explode = 0.0, 0.0, 0.0, False, 0.0
    pairs, detached = joined_pairs(tgt), []
    try:
        for t in sample_times(clip):
            ws, chs = posed(src, clip, t, env_s)
            wt, cht = posed(tgt, c2, t, env_t)
            for b in mapped & set(c2["bones"]):
                if "rotation" not in c2["bones"][b]:
                    continue
                Rs = ws["aff"][b][0] @ src.rest["aff"][b][0].T
                Rt = wt["aff"][b][0] @ tgt.rest["aff"][b][0].T
                worst_same = max(worst_same, rot_angle(Rs, Rt))
            lt, ls = lowest(wt), lowest(ws)
            sink_t = max(sink_t, tgt.ground - lt)
            sink_s = max(sink_s, src.ground - ls)
            touch = touch or (lt <= tgt.ground + 1.0)
            explode = max(explode, max_move(tgt.rest, wt) / tgt.diag)
            for child, par, g0 in pairs:
                g = gap(wt["corners"][child], wt["corners"][par])
                if g > g0 + 1.0:
                    detached.append((child, par, round(g - g0, 1)))
    except Exception as e:  # noqa: BLE001
        return None, f"unevaluable ({type(e).__name__}: {str(e)[:40]})"
    if kind in LOW_POSES:                       # 17:1x FIT: the body must reach the source's height (as a share of its rest
        src_rc = _trunk_min(src, src.rest) - src.ground          # clearance) — a cat whose legs are too long to fold under it
        tgt_rc = _trunk_min(tgt, tgt.rest) - tgt.ground          # floats on them; that copy is refused, not shown
        worst_fit = 0.0
        for t in sample_times(clip):
            ws, _ = posed(src, clip, t, env_s)
            wt, _ = posed(tgt, c2, t, env_t)
            if src_rc > 0.5 and tgt_rc > 0.5:     # off = how far the body sits from where the source's ratio puts it, as a
                want = tgt.ground + (_trunk_min(src, ws) - src.ground) / src_rc * tgt_rc   # share of the animal's HEIGHT
                worst_fit = max(worst_fit, abs(_trunk_min(tgt, wt) - want) / tgt.height)
        if worst_fit > FIT:
            return None, f"cannot get as low as the source (body {worst_fit * 100:.0f} % of its height off)"
    if detached:
        worst = max(detached, key=lambda x: x[2])
        return None, f"a part comes loose ({worst[0]} from {worst[1]}, {worst[2]} px)"
    if worst_same > SAME_DEG:
        return None, f"turns differently on this rig ({worst_same:.0f} deg)"
    if kind not in ("swim", "fly"):
        if sink_t > max(1.0, sink_s * scale + 0.5):
            return None, f"sinks {sink_t:.1f} px into the ground"
        if kind in ("walk", "run") and not touch:
            return None, "feet never touch the ground"
    if explode > 1.0:
        return None, f"a part moves {explode:.1f} x the body size"
    return (c2, [], [], {"cover": round(cover, 2), "same_deg": round(worst_same, 1), "scale": round(scale, 3),
                         "sink": round(sink_t, 2), "baked": True}), None


def _scale_channel(ch, s):
    def one(v):
        if isinstance(v, (int, float)):
            return round(v * s, 4)
        if isinstance(v, str):
            return f"({v}) * {s:.4f}"
        if isinstance(v, list):
            return [one(x) for x in v]
        if isinstance(v, dict):
            return {k: one(x) if k != "lerp_mode" else x for k, x in v.items()}
        return v
    if isinstance(ch, dict) and not ("pre" in ch or "post" in ch):
        return {k: one(v) for k, v in ch.items()}
    return one(ch)


def main(stage, write=True, only_family=None):
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    fam = defaultdict(list)
    for c in census:
        if c["body_plan"] == "object":
            continue
        f, kinds = F.family_of(c["id"])
        if f and (not only_family or f == only_family) and list(stage.glob(f"*/entity/std/{S.slug_of(c['id'])}.entity.json")):
            fam[f].append(c["id"])
    rows, changed = [], {}
    for f, mobs in sorted(fam.items()):
        kinds = F.FAMILY_TABLE[f][1]
        rigs = {m: changed.get(m) or Rig(m, stage) for m in mobs}
        own = {m: r.own_clips() for m, r in rigs.items()}
        for m, r in rigs.items():
            for k in kinds:
                if r.has_kind(k) or (k == "fly" and (r.desc.get("animations") or {}).get("std_flight")):
                    continue   # (birds fly with the standard flight — never a copied fly clip)
                srcs = sorted(((o[k][2], s) for s, o in own.items() if s != m and k in o), reverse=True)[:MAX_SOURCES]
                if not srcs:
                    rows.append({"family": f, "to": m, "kind": k, "offered": False, "why": "no relative has this motion"})
                    continue
                reasons = []
                for _, s in srcs:
                    short, aid, rich = own[s][k]
                    res, why = try_retarget(rigs[s], r, k, short, aid)
                    if res:
                        c2, init, pre, info = res
                        new_id = f"animation.std.{r.slug}.fam_{k}"
                        r.an["animations"][new_id] = c2
                        r.desc.setdefault("animations", {})[f"fam_{k}"] = new_id
                        MC.apply_to_entity(r.desc, init, pre, r.fmt)
                        changed[m] = r
                        rows.append({"family": f, "to": m, "kind": k, "offered": True, "from": s, "from_clip": short, **info})
                        break
                    reasons.append(f"{s}: {why}")
                else:
                    rows.append({"family": f, "to": m, "kind": k, "offered": False, "why": " | ".join(reasons)})
    if write:
        for r in changed.values():
            r.ef.write_text(json.dumps(r.ent, indent=1))
            r.af.write_text(json.dumps(r.an, indent=1))
    (ROOT / "_docs/standard/FAMILY-SHARING.json").write_text(json.dumps(rows, indent=1))
    lines = ["# FAMILY SHARING — p22 candidates (fam_<kind>)", "",
             "Offered only inside an anatomy family and only for motions that family really has (std_families.py). Each passed "
             "the cover / variables / same-turn / ground / size gates. Keep or drop each in p22.", "",
             "| family | creature | motion | offered | from (clip) | turn diff | size x | why not |", "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        lines.append(f"| {x['family']} | {x['to']} | {x['kind']} | {'yes' if x['offered'] else 'no'} | "
                     f"{(x.get('from', '') + ' `' + x.get('from_clip', '') + '`') if x['offered'] else ''} | {x.get('same_deg', '')} | "
                     f"{x.get('scale', '')} | {'' if x['offered'] else x['why'][:120]} |")
    (ROOT / "_docs/standard/FAMILY-PICKLIST.md").write_text("\n".join(lines) + "\n")
    off = [x for x in rows if x["offered"]]
    print(f"{len(rows)} gaps · {len(off)} offered · {len(rows) - len(off)} not offered")
    return rows


if __name__ == "__main__":
    st = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ROOT / "_staging/assembled"
    fam_only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--family=")), None)
    main(st, write="--dry" not in sys.argv, only_family=fam_only)

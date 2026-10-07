#!/usr/bin/env python3
"""jem_anim_port.py — D-C283: port a Patrix JEM's WHOLE animation (every part channel) to Bedrock, onto a Converter B geometry.

Why: the silverfish (his a17 "parts?") is FreshLX's own jointed model — head, 5-segment tail, 6 legs, antennae — animated
entirely by JEM expressions; the vanilla wiggle drives bones it does not have. spider_walk.py ported the walk TERMS only; this
ports every assignment, so the Bedrock mob moves exactly as the Java one (and serves the flying wave next).

Method (all conventions witnessed / established earlier in the project):
  * every JEM assignment runs, in file order, as a Molang statement in the entity's `scripts.pre_animation`:
      var.x / varb.x      -> v.<p>_x
      <part>.<ch>         -> v.<p>_<part>_<ch>   (a later expression reading a part channel reads this variable, as in OptiFine)
    render parameters: limb_swing -> q.modified_distance_moved · limb_speed -> q.modified_move_speed · age -> q.life_time*20 ·
    head_yaw -> q.target_y_rotation · head_pitch -> q.target_x_rotation · is_alive -> q.is_alive · is_hurt -> q.hurt_time>0 ·
    hurt_time -> q.hurt_time · swing_progress -> (v.attack_time ?? 0) · random(id) -> v.<p>_rid (math.random once per entity,
    scripts.initialize) · render.* dropped.  Trig / torad / if / pi via jem2molang (radians in, Molang degrees inside).
  * the animation `animation.<p>.jem` then drives every geometry bone that has a JEM channel, as the DIFFERENCE from the
    Converter B rest the geometry was baked with (convb.averaged_models — the same call bake() makes):
      rotation [deg] = deg(r - r_rest) on x, y, z (same sign: Bedrock rot = deg(JEM rot), jem2molang doc)
      position [px]  = (+d tx, -d ty, +d tz)   (Converter B: V_BB = (-tx, 24 - ty, tz); Blockbench exports position x negated)
      scale          = s (absolute; the geometry rest scale is 1)
  * channels listed in `drop` are not driven (e.g. a whole-model size the pack's size rule owns).
API: port(jname, geometry_bones, prefix, drop=(), scale_div=None) -> (initialize, pre_animation, animation dict, report)
     numeric_check(jname, prefix, pre, anim, cases) -> max |Molang - JEM| per channel kind"""
import json, math, re, sys
sys.path.insert(0, "/home/claude/tools")
from jem2molang import to_molang
from convb import split_this, seeds_for, averaged_models, AQUATIC, AVG_LIMB_SWING, TEMPLATE_KEY, CEM
from jem_convert import load_json

PARAMS = {"limb_swing": "q.modified_distance_moved", "limb_speed": "q.modified_move_speed", "age": "(q.life_time * 20)",
          "head_yaw": "q.target_y_rotation", "head_pitch": "q.target_x_rotation", "is_alive": "q.is_alive",
          "is_hurt": "(q.hurt_time > 0)", "hurt_time": "q.hurt_time", "swing_progress": "(v.attack_time ?? 0)",
          "is_on_ground": "q.is_on_ground", "is_in_water": "q.is_in_water"}
CH = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")


def assignments(jem):
    out = []
    for m in jem.get("models", []):
        for a in m.get("animations", []) or []:
            for k, v in a.items(): out.append((k, str(v)))
    return out


def _var(prefix, name):
    return f"v.{prefix}_{re.sub(r'[^a-z0-9_]', '_', name.lower())}"


def molang_of(expr, prefix, params_extra=None):
    e = re.sub(r"\brandom\s*\(\s*id\s*\)", "rid", expr)
    names = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?\b", e))
    vm = {"rid": f"v.{prefix}_rid"}
    params = {**PARAMS, **(params_extra or {})}
    for n in names:
        if n in params: vm[n] = params[n]
        elif n.startswith(("var.", "varb.")): vm[n] = _var(prefix, n.split(".", 1)[1])
        elif "." in n and (n.split(".")[1] in CH or n.split(".")[1] == "visible"): vm[n] = _var(prefix, n.replace(".", "_"))
    return to_molang(e, vm)


def rest_of(jname):
    tkey = TEMPLATE_KEY.get(jname, jname)
    jem = split_this(load_json(CEM / f"{jname}.jem"))
    rest, _ = averaged_models(jem, seeds_for(jem, jname, tkey), params=AQUATIC.get(jname), avg_limb_swing=jname in AVG_LIMB_SWING)
    return jem, rest


def port(jname, geometry_bones, prefix, drop=(), scale_div=None, only=None, rewrites=(), params_extra=None, seeds=None, extra_driven=None):
    """only: drive just these parts (every assignment still runs: the variables they read); rewrites: [(target, new JEM
    expression)] for assignments that read things Bedrock has no query for (documented at the call site)."""
    jem, rest = rest_of(jname)
    init = [f"v.{prefix}_rid = math.random(0.0, 1.0);"]
    pre, driven, skipped = [], {}, []
    # D-C299 (FA-1): SEEDS = the values the vanilla Java model writes into its parts each frame BEFORE the CEM animations run
    # (OptiFine semantics: a JEM expression that reads a vanilla part channel before assigning it sees THIS frame's vanilla
    # value, not last frame's). {part: {ch: molang}} -> statements at the top of pre_animation, in part order.
    for part, chs in (seeds or {}).items():
        for ch, expr in chs.items():
            pre.append(f"{_var(prefix, part + '_' + ch)} = {expr};")
    rw = dict(rewrites)
    for target, expr in assignments(jem):
        if target.startswith("render."): skipped.append(target); continue
        expr = rw.get(target, expr)
        pre.append(f"{_var(prefix, target.split('.', 1)[1] if target.startswith(('var.', 'varb.')) else target.replace('.', '_'))} = "
                   f"{molang_of(expr, prefix, params_extra)};")
        if not target.startswith(("var.", "varb.")):
            part, ch = target.split(".")
            if ch not in CH and ch != "visible": continue      # visible_boxes etc.: not portable
            driven.setdefault(part, set()).add(ch)
    for part, chs in (extra_driven or {}).items():
        driven.setdefault(part, set()).update(chs)
    # D-C317 (his R17 i01/i02, the golem's legs pivoting on the ground): a JEM expression may READ a part channel no
    # assignment ever WRITES (golem `head2.rz = -body_top.rz/2`). OptiFine then reads the part's current value = its rest
    # value; the port read a variable nothing sets, the game raised "unknown variable" and stopped the WHOLE pre_animation
    # at that line (30 unknown variables in his log). Such reads are now seeded with the rest value (cem_eval's model
    # default when the rest has none: t/r 0, s 1) at the top of pre_animation.
    written = {re.match(r"\s*(v\.[a-z0-9_]+)\s*=", st).group(1) for st in pre if re.match(r"\s*(v\.[a-z0-9_]+)\s*=", st)}
    never = []
    for target, expr in assignments(jem):
        for ref in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\.(tx|ty|tz|rx|ry|rz|sx|sy|sz)\b", str(rw.get(target, expr))):
            part, ch = ref
            if part in ("var", "varb", "render", "this"): continue
            vname = _var(prefix, f"{part}_{ch}")
            if vname in written or (part, ch) in never: continue
            never.append((part, ch))
    seeded = []
    for part, ch in never:
        val = rest.get(part, {}).get(ch, 1.0 if ch.startswith("s") else 0.0)
        pre.insert(len(seeded), f"{_var(prefix, part + '_' + ch)} = {float(val):.6f};")
        seeded.append(f"{part}.{ch}={float(val):.6f}")
    bones = {}
    have = set(geometry_bones)
    for part, chs in driven.items():
        if only is not None and part not in only: continue
        if part not in have: skipped.append(f"{part} (not a geometry bone)"); continue
        r = rest.get(part, {})
        b = {}
        def v(ch): return _var(prefix, f"{part}_{ch}")
        if {"rx", "ry", "rz"} & chs:
            rot = []
            for ch in ("rx", "ry", "rz"):
                rot.append(f"({v(ch)} - {r.get(ch, 0.0):.6f}) * 57.2957795" if ch in chs and (part, ch) not in drop else 0.0)
            if any(isinstance(x, str) for x in rot): b["rotation"] = rot
        if {"tx", "ty", "tz"} & chs:
            pos = []
            for ch, sg in (("tx", ""), ("ty", "-"), ("tz", "")):
                pos.append(f"{sg}({v(ch)} - {r.get(ch, 0.0):.6f})" if ch in chs and (part, ch) not in drop else 0.0)
            if any(isinstance(x, str) for x in pos): b["position"] = pos
        if {"sx", "sy", "sz", "visible"} & chs:
            # D-C299: JEM `visible` (Java ModelPart.visible hides the part AND its children) -> bone scale 0, which Bedrock
            # inherits down the subtree the same way
            vis = f"({v('visible')} ? 1.0 : 0.0)" if "visible" in chs else None
            sc = []
            for ch in ("sx", "sy", "sz"):
                if ch in chs and (part, ch) not in drop:
                    e = f"{v(ch)} / {scale_div[part]:.6f}" if scale_div and part in scale_div else v(ch)
                    sc.append(f"({e}) * {vis}" if vis else e)
                else: sc.append(vis if vis else 1.0)
            if any(isinstance(x, str) for x in sc): b["scale"] = sc
        if b: bones[part] = b
    anim = {"loop": True, "bones": bones}
    if only is not None:
        pre = _prune(pre, anim, prefix)
    # D-C286 (his R9 c03: the enderman jaw never bootstrapped): Bedrock drops a statement that reads a never-set variable when the
    # entity is strict (min_engine_version 1.21.0), so recurrences (v.x = f(v.x)) and reads before the first write need `?? 0`
    import molang_rbw_lint as RBW
    pre = RBW.guard_reads(pre, known=[f"{prefix}_rid"] if init else ())
    return init, pre, anim, {"driven": {k: sorted(v) for k, v in driven.items()}, "skipped": skipped, "rest": rest, "seeded_rest_reads": seeded}


def _prune(pre, anim, prefix):
    """keep only the statements the driven channels depend on (file order kept): an enderman runs the jaw's 11, not all 80."""
    tgt = [re.match(r"\s*(v\.[a-z0-9_]+)\s*=", st).group(1) for st in pre]
    reads = [set(re.findall(r"v\.%s_[a-z0-9_]+" % re.escape(prefix), st.split("=", 1)[1])) for st in pre]
    need = set(re.findall(r"v\.%s_[a-z0-9_]+" % re.escape(prefix), json.dumps(anim)))
    while True:
        more = set().union(*[reads[i] for i, t in enumerate(tgt) if t in need]) - need
        if not more: break
        need |= more
    return [st for st, t in zip(pre, tgt) if t in need]


def numeric_check(jname, prefix, init, pre, anim, cases, scale_div=None, seed_fn=None, env_fn=None):
    """Molang (molang_eval) vs the JEM (cem_eval) for the driven channels: returns the largest |difference| per kind."""
    import molang_eval as ME
    from cem_eval import CemContext, evaluate, assign
    jem, rest = rest_of(jname)
    worst = {"rotation": 0.0, "position": 0.0, "scale": 0.0}
    for c in cases:
        ctx = CemContext({k: v for k, v in c.items() if not k.startswith("_")})
        ctx.params["id"] = 1.0
        for target, expr in assignments(jem):                       # two passes: steady state of var recurrences / part refs
            pass
        for _ in range(2):
            for part, d in (seed_fn(c) if seed_fn else {}).items(): ctx.model(part).update(d)
            for target, expr in assignments(jem):
                if target.startswith("render."): continue
                try: assign(target, evaluate(expr, ctx), ctx)
                except Exception: pass
        env = {f"v.{prefix}_rid": 0.5, "q.modified_distance_moved": c.get("limb_swing", 0.0), "q.modified_move_speed": c.get("limb_speed", 0.0),
               "q.life_time": c.get("age", 0.0) / 20.0, "q.target_y_rotation": c.get("head_yaw", 0.0), "q.target_x_rotation": c.get("head_pitch", 0.0),
               "q.is_alive": 1.0 if c.get("is_alive", True) else 0.0, "q.hurt_time": c.get("hurt_time", 0.0),
               "v.attack_time": c.get("swing_progress", 0.0), "q.is_on_ground": 1.0 if c.get("is_on_ground", True) else 0.0,
               "q.is_in_water": 1.0 if c.get("is_in_water", False) else 0.0}
        if env_fn: env.update(env_fn(c))
        for _ in range(2):
            for s in pre: ME.run(s, env)
        for part, b in anim["bones"].items():
            m = ctx.model(part); r = rest.get(part, {})
            for kind, chans in (("rotation", ("rx", "ry", "rz")), ("position", ("tx", "ty", "tz")), ("scale", ("sx", "sy", "sz"))):
                if kind not in b: continue
                for i, ch in enumerate(chans):
                    e = b[kind][i]
                    if not isinstance(e, str): continue
                    got = ME.run(e, dict(env))
                    if kind == "rotation": want = math.degrees(m[ch] - r.get(ch, 0.0))
                    elif kind == "position": want = (m[ch] - r.get(ch, 0.0)) * (-1.0 if ch == "ty" else 1.0)
                    else:
                        want = (m[ch] if ch in m else 1.0) / (scale_div[part] if scale_div and part in scale_div else 1.0)   # the bake holds the rest scale
                        if f"v.{prefix}_{part}_visible" in env and not m.get("visible", True): want = 0.0
                    worst[kind] = max(worst[kind], abs(got - want))
    return worst

#!/usr/bin/env python3
"""cem_eval.py — evaluate OptiFine CEM animation expressions (cem_animation.txt grammar) in Python (research, D-C255).

Used to find the REST POSE of Fresh-Animations-style JEMs (Patrix): their animations assign tx/ty/tz/rx/ry/rz
every frame, so the static translate/rotate is NOT what the player sees.  We evaluate every expression with the
entity at rest (still, on the ground, day, adult) and iterate var.* recurrences to a fixed point.

Expression grammar (from cem_animation.txt): + - * / %, ! && ||, comparisons, ternary-like if(c,a,[c2,a2,...],else),
functions sin cos tan asin acos atan atan2 torad todeg min max clamp abs floor ceil exp frac log pow random round
signum sqrt fmod lerp between equals in ifb print printb; constants pi true false; variables <model>.<var>,
var.<name>, varb.<name>, render params (limb_swing, limb_speed, age, head_pitch, head_yaw, ...), entity params.
Rotations rx/ry/rz are RADIANS (Java ModelRenderer angles); translations tx/ty/tz are Java rotation-point coords.
"""
import math, re, random as _random


class CemContext:
    def __init__(self, params=None):
        self.params = {  # rest state
            "limb_swing": 0.0, "limb_speed": 0.0, "age": 0.0, "head_pitch": 0.0, "head_yaw": 0.0, "time": 0.0, "day_time": 6000.0,
            "day_count": 0.0, "frame_time": 0.05, "frame_counter": 0.0, "dimension": 0.0, "rule_index": 0.0, "health": 20.0, "hurt_time": 0.0,
            "death_time": 0.0, "anger_time": 0.0, "anger_time_start": 0.0, "max_health": 20.0, "pos_x": 0.0, "pos_y": 64.0, "pos_z": 0.0,
            "rot_x": 0.0, "rot_y": 0.0, "swing_progress": 0.0, "id": 1.0, "player_pos_x": 0.0, "player_pos_y": 64.0, "player_pos_z": 0.0,
            "player_rot_x": 0.0, "player_rot_y": 0.0,
        }
        bools = ["is_aggressive", "is_alive", "is_burning", "is_child", "is_glowing", "is_hurt", "is_in_hand", "is_in_item_frame", "is_in_ground", "is_in_gui",
                 "is_in_lava", "is_in_water", "is_invisible", "is_on_ground", "is_on_head", "is_on_shoulder", "is_ridden", "is_riding", "is_sitting",
                 "is_sneaking", "is_sprinting", "is_tamed", "is_wet"]
        for b in bools: self.params[b] = False
        self.params["is_alive"] = True; self.params["is_on_ground"] = True
        if params: self.params.update(params)
        self.vars = {}      # var.name / varb.name
        self.models = {}    # model name -> dict of tx,ty,tz,rx,ry,rz,sx,sy,sz,visible
        self.render = {}

    def model(self, name):
        return self.models.setdefault(name, {"tx": 0.0, "ty": 0.0, "tz": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "sx": 1.0, "sy": 1.0, "sz": 1.0, "visible": True, "visible_boxes": True})


def _if(*args):
    # if(cond, val, [cond2, val2, ...], val_else)
    args = list(args)
    while len(args) >= 3:
        c, v = args[0], args[1]
        if c: return v
        args = args[2:]
    return args[0] if args else 0.0


# D-C314: clamp is Java-exact (OptiFine Config.limit / Mth.clamp: x < lo ? lo : min(x, hi)) even when lo > hi
FUNCS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": lambda x: math.asin(max(-1.0, min(1.0, x))), "acos": lambda x: math.acos(max(-1.0, min(1.0, x))),
    "atan": math.atan, "atan2": math.atan2, "torad": math.radians, "todeg": math.degrees, "min": min, "max": max,
    "clamp": lambda x, a, b: a if x < a else min(x, b), "abs": abs, "floor": math.floor, "ceil": math.ceil, "exp": math.exp, "frac": lambda x: x - math.floor(x),
    "log": lambda x: math.log(x) if x > 0 else 0.0, "pow": math.pow, "random": lambda *a: 0.5, "round": round, "signum": lambda x: (x > 0) - (x < 0),
    "sqrt": lambda x: math.sqrt(max(0.0, x)), "fmod": math.fmod, "lerp": lambda k, x, y: x + (y - x) * k, "if": _if, "ifb": _if,
    "between": lambda x, a, b: a <= x <= b, "equals": lambda x, y, e: abs(x - y) <= e, "in": lambda x, *vals: any(x == v for v in vals),
    "print": lambda i, n, x: x, "printb": lambda i, n, x: x,
}

TOKEN = re.compile(r"\s*(?:(\d+\.\d*|\.\d+|\d+)|([A-Za-z_][A-Za-z_0-9]*(?:[.:][A-Za-z_0-9]+)*)|(&&|\|\||==|!=|>=|<=|[-+*/%!<>(),]))")


class Parser:
    """Recursive-descent parser producing a Python closure over a CemContext."""
    def __init__(self, text, ctx, self_model=None):
        self.ctx = ctx; self.self_model = self_model
        self.toks = []
        pos = 0; text = text.strip()
        while pos < len(text):
            m = TOKEN.match(text, pos)
            if not m or m.end() == pos: raise ValueError(f"bad token at {text[pos:pos+20]!r}")
            pos = m.end(); self.toks.append(m.group(1) or m.group(2) or m.group(3))
        self.i = 0

    def peek(self): return self.toks[self.i] if self.i < len(self.toks) else None
    def take(self, t=None):
        v = self.peek()
        if t is not None and v != t: raise ValueError(f"expected {t} got {v}")
        self.i += 1; return v

    def parse(self):
        v = self.expr()
        if self.peek() is not None: raise ValueError(f"trailing {self.peek()}")
        return v

    def expr(self): return self.p_or()
    def p_or(self):
        v = self.p_and()
        while self.peek() == "||": self.take(); r = self.p_and(); v = (lambda a, b: (lambda: bool(a()) or bool(b())))(v, r)
        return v
    def p_and(self):
        v = self.p_cmp()
        while self.peek() == "&&": self.take(); r = self.p_cmp(); v = (lambda a, b: (lambda: bool(a()) and bool(b())))(v, r)
        return v
    def p_cmp(self):
        v = self.p_add()
        while self.peek() in ("==", "!=", ">=", "<=", ">", "<"):
            op = self.take(); r = self.p_add()
            v = (lambda a, b, op: (lambda: {"==": a() == b(), "!=": a() != b(), ">=": a() >= b(), "<=": a() <= b(), ">": a() > b(), "<": a() < b()}[op]))(v, r, op)
        return v
    def p_add(self):
        v = self.p_mul()
        while self.peek() in ("+", "-"):
            op = self.take(); r = self.p_mul()
            v = (lambda a, b, op: (lambda: a() + b() if op == "+" else a() - b()))(v, r, op)
        return v
    def p_mul(self):
        v = self.p_un()
        while self.peek() in ("*", "/", "%"):
            op = self.take(); r = self.p_un()
            def mk(a, b, op):
                def f():
                    x, y = a(), b()
                    if op == "*": return x * y
                    if op == "/": return x / y if y != 0 else 0.0
                    return math.fmod(x, y) if y != 0 else 0.0
                return f
            v = mk(v, r, op)
        return v
    def p_un(self):
        t = self.peek()
        if t == "-": self.take(); r = self.p_un(); return lambda: -r()
        if t == "+": self.take(); return self.p_un()
        if t == "!": self.take(); r = self.p_un(); return lambda: not bool(r())
        return self.p_atom()
    def p_atom(self):
        t = self.take()
        if t is None: raise ValueError("unexpected end")
        if t == "(":
            v = self.expr(); self.take(")"); return v
        if re.match(r"^(\d+\.\d*|\.\d+|\d+)$", t):
            f = float(t); return lambda: f
        if t == "pi": return lambda: math.pi
        if t == "true": return lambda: True
        if t == "false": return lambda: False
        if self.peek() == "(":  # function
            self.take("("); args = []
            if self.peek() != ")":
                args.append(self.expr())
                while self.peek() == ",": self.take(); args.append(self.expr())
            self.take(")")
            fn = FUNCS.get(t)
            if fn is None: raise ValueError(f"unknown function {t}")
            return (lambda fn, args: (lambda: fn(*[a() for a in args])))(fn, args)
        # variable
        ctx, sm = self.ctx, self.self_model
        if t.startswith("var.") or t.startswith("varb."):
            return lambda: ctx.vars.get(t, 0.0 if t.startswith("var.") else False)
        if t.startswith("render."):
            return lambda: ctx.render.get(t[7:], 0.0)
        if "." in t:
            model, attr = t.rsplit(".", 1)
            if model == "this": model = sm
            if ":" in model: model = model.split(":")[-1]
            return (lambda model, attr: (lambda: ctx.model(model).get(attr, 0.0)))(model, attr)
        if t in ctx.params: return (lambda t: (lambda: ctx.params[t]))(t)
        raise ValueError(f"unknown variable {t}")


def evaluate(text, ctx, self_model=None):
    return Parser(str(text), ctx, self_model).parse()()


def assign(target, value, ctx, self_model=None):
    if target.startswith("var.") or target.startswith("varb."): ctx.vars[target] = value; return
    if target.startswith("render."): ctx.render[target[7:]] = value; return
    model, attr = target.rsplit(".", 1)
    if model == "this": model = self_model
    if ":" in model: model = model.split(":")[-1]
    ctx.model(model)[attr] = value


def rest_pose(jem, params=None, iterations=8, seeds=None):
    """Run every animation block of a JEM at rest; return {model_name: {tx,ty,tz,rx,ry,rz,...}} after convergence.
    seeds = {vanilla_part: {attr: value}} are re-applied at the START of every iteration = the values the vanilla
    model code writes each frame before the CEM animations run (e.g. the horse's neck ty 4 / tz -12 / rx 30 deg, body rx 0).
    Without them an expression that reads a vanilla part (Patrix equines read neck.ty to detect rearing/eating) sees 0."""
    ctx = CemContext(params)
    steps = []
    for part in jem.get("models", []):
        if not isinstance(part, dict): continue
        pname = part.get("part") or part.get("id")
        for block in part.get("animations", []) or []:
            for k, v in block.items(): steps.append((pname, k, v))
    errors = {}
    for _ in range(iterations):
        for m, d in (seeds or {}).items(): ctx.model(m).update(d)
        for pname, k, v in steps:
            try:
                val = evaluate(v, ctx, pname)
                assign(k, val, ctx, pname)
            except Exception as e:
                errors[k] = str(e)[:80]
    return ctx, errors


if __name__ == "__main__":
    import json, sys
    jem = json.loads(open(sys.argv[1], encoding="utf-8-sig").read())
    ctx, errors = rest_pose(jem)
    for m, d in sorted(ctx.models.items()):
        print(m, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items() if k in ("tx", "ty", "tz", "rx", "ry", "rz")})
    if errors: print("ERRORS", errors)

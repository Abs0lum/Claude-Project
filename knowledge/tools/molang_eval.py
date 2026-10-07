#!/usr/bin/env python3
"""molang_eval.py — a small, literal Molang evaluator for previewing SHIPPED particle JSON offline.

Why it exists (D-C242 retro-sweep): hand-porting particle expressions into Python hid the degrees trap twice.
This evaluates the expression strings exactly as written, with Molang's rules:
  * math.sin / math.cos take DEGREES; math.pi is 3.14159...
  * `cond ? a : b` ternary; `cond ? a` (no else) yields a or 0
  * assignments `v.x = expr` (also inside parentheses), statements separated by ';'
  * booleans are 1.0 / 0.0; unknown variables read as 0.0 (Molang behaviour)
Supported: numbers, v./variable./t./temp./q./query. names, math.* functions below, unary - and !, * / + -,
< <= > >= == !=, && ||, ?? (null-coalesce, treated as 'left if set else right'), ternary, (), {} blocks, return.
Not supported (raises): arrays, strings, loops, geometry queries.
"""
import math, random, re

FUNCS = {
    "sin": lambda x: math.sin(math.radians(x)), "cos": lambda x: math.cos(math.radians(x)),
    "abs": abs, "floor": math.floor, "ceil": math.ceil, "round": round, "trunc": math.trunc, "sqrt": math.sqrt,
    "exp": math.exp, "ln": math.log, "pow": math.pow, "min": min, "max": max,
    "clamp": lambda x, a, b: min(max(x, a), b), "mod": math.fmod, "lerp": lambda a, b, t: a + (b - a) * t,
    "atan": lambda x: math.degrees(math.atan(x)), "atan2": lambda y, x: math.degrees(math.atan2(y, x)),
    "asin": lambda x: math.degrees(math.asin(x)), "acos": lambda x: math.degrees(math.acos(x)),
}
TOKEN = re.compile(r"\s*(?:(\d+\.\d*|\.\d+|\d+)|([A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)|(\?\?|&&|\|\||==|!=|<=|>=|[-+*/()<>!?:;=,{}]))")
ALIAS = {"variable": "v", "temp": "t", "query": "q"}


def tokenize(src):
    pos, out = 0, []
    src = src.strip()
    while pos < len(src):
        m = TOKEN.match(src, pos)
        if not m or m.end() == pos:
            raise SyntaxError(f"molang: cannot read {src[pos:pos + 20]!r}")
        num, name, op = m.groups()
        if num is not None: out.append(("num", float(num)))
        elif name is not None:
            head, _, rest = name.partition(".")
            out.append(("name", (ALIAS.get(head, head) + ("." + rest if rest else "")).lower()))
        else: out.append(("op", op))
        pos = m.end()
    out.append(("end", None))
    return out


class Parser:
    """Pratt parser -> nested tuples; evaluated by `ev`."""
    def __init__(self, src): self.t = tokenize(src); self.i = 0
    def peek(self, k=0): return self.t[self.i + k]
    def take(self, kind=None, val=None):
        tok = self.t[self.i]
        if (kind and tok[0] != kind) or (val is not None and tok[1] != val):
            raise SyntaxError(f"molang: expected {val or kind}, got {tok}")
        self.i += 1; return tok
    def program(self):
        stmts = []
        while self.peek()[0] != "end" and self.peek() != ("op", "}"):
            if self.peek() == ("op", ";"): self.take(); continue
            stmts.append(self.statement())
            if self.peek() == ("op", ";"): self.take()
        return ("block", stmts)
    def statement(self):
        if self.peek() == ("name", "return"):
            self.take(); return ("return", self.expr(0))
        return self.expr(0)
    PREC = {"=": 1, "?": 2, "??": 3, "||": 4, "&&": 5, "==": 6, "!=": 6, "<": 7, "<=": 7, ">": 7, ">=": 7,
            "+": 8, "-": 8, "*": 9, "/": 9}
    def expr(self, minp):
        left = self.unary()
        while True:
            tok = self.peek()
            if tok[0] != "op" or tok[1] not in self.PREC: return left
            op = tok[1]; p = self.PREC[op]
            if p < minp: return left
            self.take()
            if op == "=":
                if left[0] != "var": raise SyntaxError("molang: assignment to a non-variable")
                left = ("assign", left[1], self.expr(p))            # right-associative
            elif op == "?":
                a = self.expr(p)
                if self.peek() == ("op", ":"):
                    self.take(); left = ("tern", left, a, self.expr(p))
                else:
                    left = ("tern", left, a, ("num", 0.0))
            else:
                left = ("bin", op, left, self.expr(p + 1))
    def unary(self):
        tok = self.peek()
        if tok == ("op", "-"): self.take(); return ("neg", self.unary())
        if tok == ("op", "!"): self.take(); return ("not", self.unary())
        return self.primary()
    def primary(self):
        kind, val = self.take()
        if kind == "num": return ("num", val)
        if kind == "op" and val == "(":
            e = self.expr(0); self.take("op", ")"); return e
        if kind == "op" and val == "{":
            b = self.program(); self.take("op", "}"); return b
        if kind == "name":
            if val == "math.pi": return ("num", math.pi)
            if val.startswith("math."):
                fn = val[5:]; self.take("op", "("); args = []
                if self.peek() != ("op", ")"):
                    args.append(self.expr(0))
                    while self.peek() == ("op", ","): self.take(); args.append(self.expr(0))
                self.take("op", ")"); return ("call", fn, args)
            if val.startswith(("q.", "query.")) and self.i < len(self.t) and self.peek() == ("op", "("):
                # D-C299: query calls with NUMERIC arguments (q.position(1), q.is_item_equipped(0)) read env["q.name(args)"]
                self.take("op", "("); args = []
                if self.peek() != ("op", ")"):
                    args.append(self.expr(0))
                    while self.peek() == ("op", ","): self.take(); args.append(self.expr(0))
                self.take("op", ")"); return ("qcall", "q." + val.split(".", 1)[1], args)
            return ("var", val)
        raise SyntaxError(f"molang: unexpected {kind} {val}")


STRICT = False          # D-C317: True in the gates (N2 / N3): an unguarded read of a never-set v.* raises


class UnknownVariable(NameError):
    pass


class strict:
    """with molang_eval.strict(): ... — evaluate with STRICT on (restored on exit)"""
    def __enter__(self):
        global STRICT
        self.old, STRICT = STRICT, True
        return self
    def __exit__(self, *a):
        global STRICT
        STRICT = self.old


class Return(Exception):
    def __init__(self, v): self.v = v


def ev(node, env, rng):
    k = node[0]
    if k == "num": return node[1]
    if k == "var":
        if STRICT and node[1] not in env and node[1].startswith("v."):
            # D-C317: the game treats a read of a never-set variable as an ERROR (strict entities stop the whole script);
            # the gates evaluate strictly so a port can no longer pass on the lenient 0.0
            raise UnknownVariable(node[1])
        return float(env.get(node[1], 0.0))
    if k == "assign": env[node[1]] = ev(node[2], env, rng); return env[node[1]]
    if k == "neg": return -ev(node[1], env, rng)
    if k == "not": return 0.0 if ev(node[1], env, rng) else 1.0
    if k == "tern": return ev(node[2], env, rng) if ev(node[1], env, rng) else ev(node[3], env, rng)
    if k == "block":
        last = 0.0
        for s in node[1]: last = ev(s, env, rng)
        return last
    if k == "return": raise Return(ev(node[1], env, rng))
    if k == "qcall":
        args = [ev(a, env, rng) for a in node[2]]
        return float(env.get(f"{node[1]}({','.join(repr(float(x)) for x in args)})", 0.0))
    if k == "call":
        args = [ev(a, env, rng) for a in node[2]]
        if node[1] == "random": return rng.uniform(args[0], args[1])
        if node[1] == "random_integer": return float(rng.randint(int(args[0]), int(args[1])))
        if node[1] == "die_roll": return sum(rng.uniform(args[1], args[2]) for _ in range(int(args[0])))
        if node[1] not in FUNCS: raise NameError(f"molang: math.{node[1]} not supported")
        return float(FUNCS[node[1]](*args))
    if k == "bin":
        op, a, b = node[1], node[2], node[3]
        if op == "&&": return 1.0 if (ev(a, env, rng) and ev(b, env, rng)) else 0.0
        if op == "||": return 1.0 if (ev(a, env, rng) or ev(b, env, rng)) else 0.0
        if op == "??":
            return ev(a, env, rng) if (a[0] != "var" or a[1] in env) else ev(b, env, rng)
        x, y = ev(a, env, rng), ev(b, env, rng)
        if op == "+": return x + y
        if op == "-": return x - y
        if op == "*": return x * y
        if op == "/": return x / y if y != 0 else 0.0
        return 1.0 if {"<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y, "==": x == y, "!=": x != y}[op] else 0.0
    raise ValueError(node)


_CACHE = {}
def run(src, env, rng=random):
    """Evaluate a Molang string (or a plain number) against `env` (a dict, mutated by assignments)."""
    if isinstance(src, (int, float)): return float(src)
    tree = _CACHE.get(src)
    if tree is None:
        tree = _CACHE[src] = Parser(src).program()
    try:
        return ev(tree, env, rng)
    except Return as r:
        return r.v


if __name__ == "__main__":      # self-test: the degrees rule and the vanilla firefly's own syntax
    e = {}
    assert abs(run("math.sin(90)", e) - 1) < 1e-12 and abs(run("math.sin(math.pi)", e) - math.sin(math.radians(math.pi))) < 1e-12
    run("v.a = 2; v.b = v.a > 1 ? 5 : 7;", e); assert e["v.b"] == 5
    run("v.c = 0; v.a > 1 ? (v.c = 3);", e); assert e["v.c"] == 3
    run("v.should_change = math.random( 0, 1 ) <= 0.05; v.should_change ? ( v.acceleration_x = math.random( -5, 5 ) );", e)
    assert run("variable.a + 1", e) == 3 and run("math.clamp(5, 0, 1)", e) == 1 and run("-v.a * 2", e) == -4
    assert run("v.z ?? 4", {}) == 4 and run("!0", e) == 1
    print("molang_eval self-test OK (sin(pi) in degrees =", round(run("math.sin(math.pi)", e), 5), ")")

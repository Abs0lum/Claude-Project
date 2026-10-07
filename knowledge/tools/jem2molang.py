#!/usr/bin/env python3
"""jem2molang.py — D-C278: translate OptiFine CEM (JEM) animation expressions to Bedrock Molang, and pull the walk terms.
JEM trig is in RADIANS, Molang trig in DEGREES; JEM rotations are radians, Bedrock animation rotations degrees with the SAME
sign on all three axes (file rot = [-bb_x, -bb_y, bb_z] and bb = [-deg(rx), -deg(ry), deg(rz)] -> file = deg(r*)).
API: walk_terms(expr, marker="var.ls") -> expr keeping only the top-level additive terms that mention the marker
     to_molang(expr, varmap) -> Molang string (value in the SAME units as the JEM value)
D-C280: unary `+` is dropped (Bedrock rejects it: "binary Add '+' operator at end of expression" — RP-06 1.4.13 spider)."""
import re

FUNCS = {"sin": "math.sin", "cos": "math.cos", "clamp": "math.clamp", "abs": "math.abs", "min": "math.min", "max": "math.max",
         "sqrt": "math.sqrt", "pow": "math.pow", "floor": "math.floor", "ceil": "math.ceil", "exp": "math.exp", "atan2": "math.atan2",
         "asin": "math.asin", "acos": "math.acos", "atan": "math.atan"}


def split_top(expr, seps="+-"):
    """top-level additive split -> [(sign, term)]"""
    out, depth, cur, sign = [], 0, "", "+"
    i = 0; s = expr.strip()
    while i < len(s):
        ch = s[i]
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if depth == 0 and ch in seps and cur.strip() and not re.search(r"[*/(,]\s*$", cur) and not re.search(r"[eE]$", cur.strip()):
            out.append((sign, cur.strip())); sign = ch; cur = ""
        elif depth == 0 and ch in seps and not cur.strip():
            sign = "-" if (sign == "-") != (ch == "-") else "+"
        else:
            cur += ch
        i += 1
    if cur.strip(): out.append((sign, cur.strip()))
    return out


def walk_terms(expr, marker="var.ls"):
    keep = [(sg, t) for sg, t in split_top(expr) if marker in t]
    s = " ".join(f"{sg} ({t})" for sg, t in keep).strip() or "0"
    return s[1:].strip() if s.startswith("+") else s


def _args(s, i):
    """s[i] == '(' -> (list of arg strings, index after ')')"""
    depth, cur, args = 0, "", []
    j = i
    while j < len(s):
        ch = s[j]
        if ch == "(":
            depth += 1
            if depth == 1: j += 1; continue
        elif ch == ")":
            depth -= 1
            if depth == 0: args.append(cur); return args, j + 1
        elif ch == "," and depth == 1:
            args.append(cur); cur = ""; j += 1; continue
        cur += ch; j += 1
    raise ValueError("unbalanced: " + s)


def to_molang(expr, varmap):
    s = expr; out = ""; i = 0
    while i < len(s):
        m = re.match(r"[A-Za-z_][A-Za-z0-9_\.]*", s[i:])
        if m:
            name = m.group(0); j = i + len(name)
            if j < len(s) and s[j] == "(":
                args, k = _args(s, j); a = [to_molang(x, varmap) for x in args]
                if name in ("sin", "cos"): out += f"{FUNCS[name]}(({a[0]}) * 57.2957795)"
                elif name in ("asin", "acos", "atan"): out += f"({FUNCS[name]}({a[0]}) * 0.0174532925)"
                elif name == "atan2": out += f"(math.atan2({a[0]}, {a[1]}) * 0.0174532925)"
                elif name == "torad": out += f"(({a[0]}) * 0.0174532925)"
                elif name == "todeg": out += f"(({a[0]}) * 57.2957795)"
                elif name == "if":
                    # if(c1, v1, c2, v2, ..., else)
                    expr_ = a[-1] if len(a) % 2 == 1 else "0"
                    for c, v in reversed(list(zip(a[0:-1:2], a[1::2]))): expr_ = f"(({c}) ? ({v}) : ({expr_}))"
                    out += expr_
                elif name == "clamp" and not all(re.fullmatch(r"\s*-?[0-9.]+\s*", x) for x in a[1:3]):
                    # D-C314: Java clamp = x < lo ? lo : min(x, hi) - differs from min(max(x, lo), hi) when lo > hi (the golem's var.bend);
                    # dynamic bounds get the exact form, literal bounds keep math.clamp
                    out += f"((({a[0]}) < ({a[1]})) ? ({a[1]}) : math.min(({a[0]}), ({a[2]})))"
                elif name == "between": out += f"((({a[0]}) >= ({a[1]})) && (({a[0]}) <= ({a[2]})))"
                elif name == "equals": out += f"(math.abs(({a[1]}) - ({a[0]})) <= ({a[2]}))"          # D-C314: OptiFine equals(x, y, epsilon)
                elif name == "in": out += "(" + " || ".join(f"(({a[0]}) == ({v}))" for v in a[1:]) + ")"   # D-C314: in(x, v1, v2, ...)
                elif name in FUNCS: out += f"{FUNCS[name]}({', '.join(a)})"
                else: raise ValueError("unknown function " + name)
                i = k; continue
            if name == "pi": out += "3.14159265"
            elif name in varmap: out += varmap[name]
            else: raise ValueError("unknown name " + name)
            i = j; continue
        if s[i] == "+" and (not out.strip() or out.rstrip()[-1] in "(,+-*/?:<>=!&|"):
            i += 1; continue          # D-C280: unary plus (JEM `clamp(+cos(...`) — Bedrock has none; `+x` == `x`
        out += s[i]; i += 1
    return out


if __name__ == "__main__":
    vm = {"var.ls": "v.pw_ls", "limb_speed": "q.modified_move_speed", "is_on_ground": "q.is_on_ground"}
    e = "torad(-60) - sin(var.b)/60 +clamp(-cos(torad(-90)+var.ls)/5*limb_speed, -pi, if(!is_on_ground, pi, 0)) +cos(var.ls*2)/4  /6*clamp(limb_speed*6, 0, 1)"
    w = walk_terms(e); print(w); print(to_molang(w, vm))
    import molang_lint
    for src in ("clamp(+cos(var.ls)/5*limb_speed, -pi, if(!is_on_ground, pi, 0))", "+cos(var.ls)", "sin(var.ls) - +cos(var.ls)",
                "2*+var.ls", "clamp(1, +2, +3)", "1 + 2"):
        m = to_molang(src, vm); err = molang_lint.check(m)
        assert err is None and "(+" not in m.replace(" ", "") and ",+" not in m.replace(" ", ""), (src, m, err)
    assert to_molang("1 + 2", vm) == "1 + 2"
    print("jem2molang self-test OK (unary + dropped, binary + kept, every output parses)")

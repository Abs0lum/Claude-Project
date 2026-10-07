#!/usr/bin/env python3
"""molang_lint.py — parse EVERY Molang string a pack ships, with Bedrock's grammar, before it ships (D-C280, D-C281).

Why (his 09:59 first-load log, RP-06 1.4.13): six spider-walk rotations failed in the game with
  "binary Add '+' operator at end of expression" — the JEM text `clamp(+cos(...` was carried over as `math.clamp(+math.cos(...`.
Bedrock has NO unary plus: `+` is always binary, so `(+x` is a `+` with nothing on its left. The 1.4.13 gate never parsed the
Molang it shipped (it evaluated the JEM source instead), so the error could only be found in the game.

Grammar: the molang_eval Pratt parser (unary `-` and `!` only; statements need `;`), extended for lint-only constructs
(strings 'x', calls on any name, [index], ->, {blocks}) and for three forms Bedrock accepts (calibrated on his stack):
`0.0f` float suffix (vanilla bow controller), `( stmt; stmt; expr )` groups, `//` and `/* */` comments in the JSON.

Where Molang lives (the collectors below):
  RP  animations · animation_controllers · entity (client) · attachables · render_controllers · particles (D-C281)
  BP  blocks (permutation conditions, bone_visibility) · items (conditions) · entities (scripts, numeric property defaults)
      animations + animation_controllers (Molang entries; slash commands and `@s event` lines are NOT Molang) ·
      features (scatter / conditional-list fields) · feature_rules (distribution)
Pack kind comes from the manifest modules ("resources" -> RP; "data" / "script" -> BP).

API:  lint_pack(src)  -> (n_checked, [(relpath, jsonpath, expr, error)])   src = a pack folder OR a .mcpack/.zip file
      check(expr)     -> None | error text
CLI:  molang_lint.py SRC [SRC ...]   (exit 1 when any error)"""
import io, json, re, sys, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_eval as M

TOKEN = re.compile(r"\s*(?:(\d+\.\d*f?|\.\d+f?|\d+f?)|('[^']*')|([A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)"
                   r"|(\?\?|&&|\|\||==|!=|<=|>=|->|[-+*/()<>!?:;=,{}\[\]]))")


def tokenize(src):
    pos, out = 0, []
    src = src.strip()
    while pos < len(src):
        m = TOKEN.match(src, pos)
        if not m or m.end() == pos:
            raise SyntaxError(f"cannot read {src[pos:pos + 20]!r}")
        num, st, name, op = m.groups()
        if num is not None: out.append(("num", float(num.rstrip("f"))))   # Bedrock accepts C-style 0.0f
        elif st is not None: out.append(("str", st))
        elif name is not None: out.append(("name", name.lower()))
        else: out.append(("op", op))
        pos = m.end()
    out.append(("end", None))
    return out


class LintParser(M.Parser):
    """molang_eval's grammar (so unary + stays an error, exactly as in Bedrock) + the constructs a lint must accept."""
    def __init__(self, src): self.t = tokenize(src); self.i = 0

    def program(self):
        """statements must be separated by ';' (molang_eval is lenient here; Bedrock is not)."""
        stmts = []
        while self.peek()[0] != "end" and self.peek() != ("op", "}"):
            if self.peek() == ("op", ";"): self.take(); continue
            stmts.append(self.statement())
            if self.peek() == ("op", ";"): self.take()
            elif self.peek()[0] != "end" and self.peek() != ("op", "}"):
                raise SyntaxError(f"expected ';' or end, got {self.peek()}")
        return ("block", stmts)

    def primary(self):
        kind, val = self.take()
        if kind in ("num", "str"): node = (kind, val)
        elif kind == "op" and val == "(":
            node = self.expr(0)
            if self.peek() == ("op", ";"):            # Bedrock accepts ( stmt; stmt; expr ) (seen in shipped third-party anims)
                rest = [node]
                while self.peek() == ("op", ";"):
                    self.take()
                    if self.peek() == ("op", ")"): break
                    rest.append(self.statement())
                node = ("block", rest)
            self.take("op", ")")
        elif kind == "op" and val == "{":
            node = self.program(); self.take("op", "}")
        elif kind == "name":
            if val in ("break", "continue", "this", "true", "false"): return ("kw", val)
            if self.peek() == ("op", "("):
                self.take(); args = []
                if self.peek() != ("op", ")"):
                    args.append(self.expr(0))
                    while self.peek() == ("op", ","): self.take(); args.append(self.expr(0))
                self.take("op", ")"); node = ("call", val, args)
            else:
                node = ("var", val)
        else:
            raise SyntaxError(f"unexpected {kind} {val!r} (Bedrock: an operator with nothing on its left)"
                              if kind == "op" and val in "+*/" else f"unexpected {kind} {val!r}")
        while True:                                   # postfix: [index]  ->  arrow
            if self.peek() == ("op", "["):
                self.take(); idx = self.expr(0); self.take("op", "]"); node = ("index", node, idx)
            elif self.peek() == ("op", "->"):
                self.take(); node = ("arrow", node, self.primary())
            else:
                return node


DIRECT_VAR = re.compile(r"^(v|variable|t|temp|c|context)\.[a-z_][a-z_0-9]*$")


def _coalesce_errors(node, out):
    """D-C285 (his R8 first-load log): Bedrock rejects `??` unless its LEFT side is a direct variable reference —
    `variable.squid.swim_rotation ?? 0.0` -> "found left-hand-side of ?? expression that isn't a direct-variable reference - this
    is unsupported at this time" and the WHOLE animation is dropped. `v.x ?? 0` is accepted (moose, silverfish in his stack)."""
    if isinstance(node, tuple):
        if len(node) == 4 and node[0] == "bin" and node[1] == "??":
            l = node[2]
            if not (isinstance(l, tuple) and l[0] == "var" and DIRECT_VAR.match(l[1])):
                out.append("left-hand side of ?? is not a direct variable (Bedrock: 'isn't a direct-variable reference')")
        for x in node[1:]:
            if isinstance(x, (tuple, list)): _coalesce_errors(x, out)
    elif isinstance(node, list):
        for x in node: _coalesce_errors(x, out)


def check(expr):
    """None when `expr` parses (and passes Bedrock's semantic rules we know of), else the error text."""
    if not isinstance(expr, str): return None
    s = expr.strip()
    if not s: return None
    try:
        p = LintParser(s); tree = p.program()
        if p.peek()[0] != "end": return f"trailing input at {p.peek()}"
    except (SyntaxError, IndexError) as e:
        return str(e)
    errs = []; _coalesce_errors(tree, errs)
    return errs[0] if errs else None


def is_command(s):
    """BP animation/controller entries that are commands or entity events, not Molang: '/say x', '@s pw:event'."""
    t = s.lstrip()
    return t.startswith("/") or t.startswith("@")


# ---------------------------------------------------------------- RP collectors
def _chan(v, path, out, skip_keys=("lerp_mode",)):
    if isinstance(v, str): out.append((path, v))
    elif isinstance(v, list):
        for i, x in enumerate(v): _chan(x, f"{path}[{i}]", out, skip_keys)
    elif isinstance(v, dict):
        for k, x in v.items():
            if k in skip_keys: continue
            _chan(x, f"{path}.{k}", out, skip_keys)


def from_animations(d, bp=False):
    out = []
    for an, a in (d.get("animations") or {}).items():
        if not isinstance(a, dict): continue
        for k in ("anim_time_update", "blend_weight", "start_delay", "loop_delay"):
            if isinstance(a.get(k), str): out.append((f"{an}.{k}", a[k]))
        for t, v in (a.get("timeline") or {}).items():
            items = []; _chan(v, f"{an}.timeline.{t}", items)
            out += [(p, s) for p, s in items if not (bp and is_command(s))]
        for bn, b in (a.get("bones") or {}).items():
            if not isinstance(b, dict): continue
            for ch in ("rotation", "position", "scale"):
                if ch in b: _chan(b[ch], f"{an}.bones.{bn}.{ch}", out)
        for fx in ("particle_effects", "sound_effects"):
            for t, v in (a.get(fx) or {}).items():
                for i, e in enumerate(v if isinstance(v, list) else [v]):
                    if isinstance(e, dict) and isinstance(e.get("pre_effect_script"), str):
                        out.append((f"{an}.{fx}.{t}[{i}].pre_effect_script", e["pre_effect_script"]))
    return out


def from_controllers(d, bp=False):
    out = []
    for cn, c in (d.get("animation_controllers") or {}).items():
        for sn, s in ((c or {}).get("states") or {}).items():
            p = f"{cn}.states.{sn}"
            for i, a in enumerate(s.get("animations", []) or []):
                if isinstance(a, dict):
                    for k, v in a.items(): out.append((f"{p}.animations[{i}].{k}", v))
            for i, t in enumerate(s.get("transitions", []) or []):
                for k, v in (t or {}).items(): out.append((f"{p}.transitions[{i}].{k}", v))
            for k in ("on_entry", "on_exit"):
                for i, v in enumerate(s.get(k, []) or []):
                    if isinstance(v, str) and bp and is_command(v): continue
                    out.append((f"{p}.{k}[{i}]", v))
            for vn, v in (s.get("variables") or {}).items():
                if isinstance(v, dict) and "input" in v: out.append((f"{p}.variables.{vn}.input", v["input"]))
            if isinstance(s.get("blend_transition"), str): out.append((f"{p}.blend_transition", s["blend_transition"]))
            for i, e in enumerate(s.get("particle_effects", []) or []):
                if isinstance(e, dict) and "pre_effect_script" in e:
                    out.append((f"{p}.particle_effects[{i}].pre_effect_script", e["pre_effect_script"]))
    return out


def _scripts(desc, out):
    sc = desc.get("scripts") or {}
    for k in ("initialize", "pre_animation"):
        # Bedrock runs the list as ONE script (vanilla 1.26 splits a `? { ... };` block across entries), so lint it joined
        lines = [v for v in (sc.get(k, []) or []) if isinstance(v, str)]
        if lines: out.append((f"scripts.{k}[0..{len(lines) - 1}]", "\n".join(lines)))
    for i, a in enumerate(sc.get("animate", []) or []):
        if isinstance(a, dict):
            for k, v in a.items(): out.append((f"scripts.animate[{i}].{k}", v))
    for k in ("scale", "scalex", "scaley", "scalez", "scaleX", "scaleY", "scaleZ", "should_update_bones_and_effects_offscreen",
              "should_update_effects_offscreen"):
        if isinstance(sc.get(k), str): out.append((f"scripts.{k}", sc[k]))


def from_client_entity(d):
    out = []
    desc = (d.get("minecraft:client_entity") or d.get("minecraft:attachable") or {}).get("description", {}) or {}
    _scripts(desc, out)
    for i, r in enumerate(desc.get("render_controllers", []) or []):
        if isinstance(r, dict):
            for k, v in r.items(): out.append((f"render_controllers[{i}].{k}", v))
    return out


def from_render_controllers(d):
    out = []
    for rn, r in (d.get("render_controllers") or {}).items():
        if not isinstance(r, dict): continue
        if isinstance(r.get("geometry"), str): out.append((f"{rn}.geometry", r["geometry"]))
        for i, m in enumerate(r.get("materials", []) or []):
            for k, v in (m or {}).items(): out.append((f"{rn}.materials[{i}].{k}", v))
        for i, t in enumerate(r.get("textures", []) or []): out.append((f"{rn}.textures[{i}]", t))
        for i, pv in enumerate(r.get("part_visibility", []) or []):
            for k, v in (pv or {}).items():
                if isinstance(v, str): out.append((f"{rn}.part_visibility[{i}].{k}", v))
        for k in ("color", "overlay_color", "on_fire_color", "is_hurt_color"):
            for ch, v in (r.get(k) or {}).items():
                if isinstance(v, str): out.append((f"{rn}.{k}.{ch}", v))
        for k in ("light_color_multiplier",):
            if isinstance(r.get(k), str): out.append((f"{rn}.{k}", r[k]))
        for k, v in (r.get("uv_anim") or {}).items(): _chan(v, f"{rn}.uv_anim.{k}", out)
    return out


# particle fields that hold names, ids, paths or text rather than Molang
PARTICLE_SKIP_KEYS = ("identifier", "material", "texture", "effect", "event_name", "event", "log", "lerp_mode")
PARTICLE_SKIP_COMPONENTS = ("minecraft:emitter_lifetime_events", "minecraft:particle_lifetime_events",
                            "minecraft:particle_expire_if_in_blocks", "minecraft:particle_expire_if_not_in_blocks")   # block ids


def from_particles(d):
    out = []
    pe = d.get("particle_effect") or {}
    for cname, comp in (pe.get("components") or {}).items():
        if cname in PARTICLE_SKIP_COMPONENTS: continue
        _chan(comp, f"components.{cname}", out, PARTICLE_SKIP_KEYS)
    for cname, curve in (pe.get("curves") or {}).items():
        _chan(curve, f"curves.{cname}", out, PARTICLE_SKIP_KEYS + ("type",))
    for ename, ev in (pe.get("events") or {}).items():
        _chan(ev, f"events.{ename}", out, PARTICLE_SKIP_KEYS + ("type",))
    return [(p, s) for p, s in out if not s.lstrip().startswith("#")]      # "#RRGGBBAA" colours


# ---------------------------------------------------------------- BP collectors
def _conditions(v, path, out):
    """every string under a key named 'condition' (block permutations, legacy item/block events, conditional lists)."""
    if isinstance(v, dict):
        for k, x in v.items():
            if k == "condition" and isinstance(x, str): out.append((f"{path}.{k}", x))
            else: _conditions(x, f"{path}.{k}", out)
    elif isinstance(v, list):
        for i, x in enumerate(v): _conditions(x, f"{path}[{i}]", out)


def _bone_visibility(v, path, out):
    if isinstance(v, dict):
        for k, x in v.items():
            if k == "bone_visibility" and isinstance(x, dict):
                for b, e in x.items():
                    if isinstance(e, str): out.append((f"{path}.bone_visibility.{b}", e))
            else: _bone_visibility(x, f"{path}.{k}", out)
    elif isinstance(v, list):
        for i, x in enumerate(v): _bone_visibility(x, f"{path}[{i}]", out)


def from_bp_blocks(d):
    out = []; b = d.get("minecraft:block") or {}
    _conditions(b, "block", out); _bone_visibility(b, "block", out)
    return out


def from_bp_items(d):
    out = []; _conditions(d.get("minecraft:item") or {}, "item", out)
    return out


def from_bp_entities(d):
    out = []
    desc = (d.get("minecraft:entity") or {}).get("description", {}) or {}
    _scripts(desc, out)
    for pn, pr in (desc.get("properties") or {}).items():
        if isinstance(pr, dict) and pr.get("type") in ("int", "float") and isinstance(pr.get("default"), str):
            out.append((f"properties.{pn}.default", pr["default"]))
    _set_property((d.get("minecraft:entity") or {}).get("events") or {}, "events", out)
    return out


def _set_property(v, path, out):
    """entity event `set_property` values are Molang ("warm" for an enum is a plain name, which parses)."""
    if isinstance(v, dict):
        for k, x in v.items():
            if k == "set_property" and isinstance(x, dict):
                for pn, e in x.items():
                    if isinstance(e, str): out.append((f"{path}.set_property.{pn}", e))
            else: _set_property(x, f"{path}.{k}", out)
    elif isinstance(v, list):
        for i, x in enumerate(v): _set_property(x, f"{path}[{i}]", out)


def _distribution(v, path, out):
    for k in ("iterations", "scatter_chance", "x", "y", "z"):
        x = v.get(k)
        if isinstance(x, str): out.append((f"{path}.{k}", x))
        elif isinstance(x, dict):
            for i, e in enumerate(x.get("extent", []) or []):
                if isinstance(e, str): out.append((f"{path}.{k}.extent[{i}]", e))
            for kk in ("numerator", "denominator"):
                if isinstance(x.get(kk), str): out.append((f"{path}.{k}.{kk}", x[kk]))


def from_bp_features(d):
    out = []
    for fk, f in d.items():
        if not isinstance(f, dict): continue
        if fk == "minecraft:scatter_feature": _distribution(f, fk, out)
        _conditions(f, fk, out)
    return out


def from_bp_feature_rules(d):
    out = []; r = d.get("minecraft:feature_rules") or {}
    if isinstance(r.get("distribution"), dict): _distribution(r["distribution"], "distribution", out)
    return out


RP_KINDS = (("animations", from_animations), ("animation_controllers", from_controllers), ("entity", from_client_entity),
            ("attachables", from_client_entity), ("render_controllers", from_render_controllers), ("particles", from_particles))
BP_KINDS = (("blocks", from_bp_blocks), ("items", from_bp_items), ("entities", from_bp_entities),
            ("animations", lambda d: from_animations(d, bp=True)), ("animation_controllers", lambda d: from_controllers(d, bp=True)),
            ("features", from_bp_features), ("feature_rules", from_bp_feature_rules))


# ---------------------------------------------------------------- pack sources
def strip_json_comments(txt):
    """Remove // line and /* block */ comments outside strings (Bedrock's JSON reader tolerates both, also after a value)."""
    out = []; i = 0; n = len(txt); in_str = False
    while i < n:
        c = txt[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n: out.append(txt[i + 1]); i += 2; continue
            if c == '"': in_str = False
            i += 1
        elif c == '"': in_str = True; out.append(c); i += 1
        elif txt.startswith("//", i):
            j = txt.find("\n", i); i = n if j < 0 else j
        elif txt.startswith("/*", i):
            j = txt.find("*/", i + 2); i = n if j < 0 else j + 2
        else: out.append(c); i += 1
    return "".join(out)


def _parse_json(txt):
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return json.loads(strip_json_comments(txt))


def pack_files(src):
    """{relpath: text} for every .json of the pack rooted at its manifest (a folder or a .mcpack/.zip)."""
    src = Path(src); files = {}
    if src.is_dir():
        for p in src.rglob("*.json"): files[p.relative_to(src).as_posix()] = p.read_bytes()
    else:
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.endswith(".json"): files[n] = z.read(n)
    mans = sorted((k for k in files if k.split("/")[-1] == "manifest.json"), key=lambda k: k.count("/"))
    prefix = mans[0][: -len("manifest.json")] if mans else ""
    return {k[len(prefix):]: v.decode("utf-8-sig", "replace") for k, v in files.items() if k.startswith(prefix)}


def pack_kinds(files):
    try:
        mods = [m.get("type") for m in _parse_json(files["manifest.json"]).get("modules", [])]
    except Exception:
        mods = []
    kinds = []
    if "resources" in mods: kinds.append(("RP", RP_KINDS))
    if any(t in ("data", "script", "javascript") for t in mods): kinds.append(("BP", BP_KINDS))
    return kinds


def lint_pack(src):
    files = pack_files(src); n = 0; errs = []
    for _, table in pack_kinds(files):
        for folder, fn in table:
            for rel in sorted(k for k in files if k.startswith(folder + "/")):
                try:
                    d = _parse_json(files[rel])
                except Exception as e:
                    errs.append((rel, "<file>", "", f"JSON: {e}")); continue
                if not isinstance(d, dict): continue
                for path, expr in fn(d):
                    if not isinstance(expr, str): continue
                    n += 1
                    e = check(expr)
                    if e: errs.append((rel, path, expr, e))
    return n, errs


def _selftest():
    """Bedrock's own verdicts (his 09:59 log + vanilla files), then the collectors on tiny fixtures."""
    assert check("math.clamp(+math.cos(90), 0, 1)") and check("+1") and check("1 + (+2)") and check("a, +b") is not None
    assert check("math.clamp(math.cos(90), 0, 1)") is None and check("-q.x + 1") is None and check("!q.is_on_ground ? 1 : 0") is None
    assert check("q.property('minecraft:climate_variant') == 'cold'") is None and check("array.skins[q.variant]") is None
    assert check("v.a = 1; v.b = v.a > 0 ? 2 : 3; return v.b;") is None and check("1 +") is not None and check("(1") is not None
    assert check("q.is_item_name_any('slot.weapon.mainhand', 0, 'minecraft:bow')") is None and check("1e+5") is not None
    assert check("query.main_hand_item_use_duration > 0.0f && !query.is_using_item") is None
    assert check("-( v.freq = 1.5; v.mag = -3; math.sin(q.anim_time * v.freq) * v.mag )") is None and check("( v.a = 1; +v.a )") is not None
    # D-C285: the ?? left side (his R8 log: rejected; moose / silverfish forms accepted in his stack)
    assert check("variable.squid.swim_rotation ?? 0.0") is not None and check("q.x ?? 1") is not None
    assert check("v.smoothed_move_speed ?? 0") is None and check("math.sin(3.14 * (v.attack_time ?? 0))") is None
    assert check("Math.lerp(v.a ?? 0, q.modified_move_speed, 0.15)") is None and check("variable.a.b ?? 1") is not None
    p = {"particle_effect": {"description": {"identifier": "pw:x"}, "components": {
        "minecraft:emitter_rate_steady": {"spawn_rate": "+2", "max_particles": 10},
        "minecraft:emitter_lifetime_events": {"creation_event": "pw:burst"},
        "minecraft:particle_appearance_tinting": {"color": {"gradient": {"0.0": "#FFAABBCC"}, "interpolant": "v.particle_age"}},
        "minecraft:particle_motion_collision": {"events": [{"event": "pw:hit", "min_speed": 1}]}},
        "events": {"e": {"particle_effect": {"effect": "pw:y", "type": "emitter", "pre_effect_script": "v.a = 1;"}, "log": "hi: there"}}}}
    got = from_particles(p)
    assert [s for _, s in got] == ["+2", "v.particle_age", "v.a = 1;"], got
    blk = {"minecraft:block": {"permutations": [{"condition": "q.block_state('pw:a') == 1", "components": {
        "minecraft:geometry": {"identifier": "geometry.x", "bone_visibility": {"b": "q.block_state('pw:b') == +1", "c": True}}}}]}}
    assert [s for _, s in from_bp_blocks(blk)] == ["q.block_state('pw:a') == 1", "q.block_state('pw:b') == +1"]
    ctl = {"animation_controllers": {"c": {"states": {"s": {"on_entry": ["/say hi", "@s pw:ev", "v.x = 1;"],
                                                               "transitions": [{"t": "q.is_sneaking"}]}}}}}
    assert [s for _, s in from_controllers(ctl, bp=True)] == ["q.is_sneaking", "v.x = 1;"]
    ft = {"minecraft:scatter_feature": {"places_feature": "pw:f", "iterations": "math.random_integer(1, 3)",
                                        "x": {"distribution": "uniform", "extent": [0, "+15"]}, "scatter_chance": {"numerator": 1, "denominator": 4}}}
    assert [s for _, s in from_bp_features(ft)] == ["math.random_integer(1, 3)", "+15"]
    j = _parse_json('{"a": "x // not a comment", /* c */ "b": true // trailing\n, "c": "q.x /* kept */"}')
    assert j == {"a": "x // not a comment", "b": True, "c": "q.x /* kept */"}, j
    assert from_particles({"particle_effect": {"components": {"minecraft:particle_expire_if_not_in_blocks": ["minecraft:water"]}}}) == []
    split = {"description": {"scripts": {"pre_animation": ["v.a = 1;", "(v.a) ? {", "v.b = 2;", "};"]}}}
    assert [check(e) for _, e in from_client_entity({"minecraft:client_entity": split})] == [None]
    print("molang_lint self-test OK")


if __name__ == "__main__":
    _selftest()
    bad = 0
    for d in sys.argv[1:]:
        n, errs = lint_pack(d)
        print(f"{Path(d).name}: {n} Molang strings, {len(errs)} errors")
        for f, path, expr, e in errs:
            print(f"  {f} | {path} | {e} | {expr[:140]}")
        bad += len(errs)
    sys.exit(1 if bad else 0)

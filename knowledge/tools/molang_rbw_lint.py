#!/usr/bin/env python3
"""molang_rbw_lint.py — RBW standing gate (D-C286): a client entity's pre_animation must not READ a variable BEFORE its first WRITE.

Why (his R9 p6 c03 "I don't see a bottom jaw" + 10 content-log errors "unhandled request for unknown variable 'variable.pw_em_…'"):
the ported Patrix jaw keeps state across frames (aggro ramps: v.pw_em_aggroa = f(v.pw_em_aggroa, …), and a frame guard
v.pw_em_frame_counter_prev read before the line that sets it). Since 1.4.22 the enderman declares min_engine_version 1.21.0, and
the game then treats a read of a never-set variable as an ERROR, so the statement is dropped — a self-referencing recurrence can
never bootstrap, every variable downstream stays unknown, and every jaw channel is skipped (head + jaw stay at rest, overlapping).
Bedrock's fix is the null-coalescing read `(v.x ?? 0)` (legal: a direct variable on the left, L-QQ-DIRECT).

Rule: walk scripts.initialize (1.10.0+ files) then scripts.pre_animation in order; a `v.`/`variable.` name READ in a statement
before any earlier statement (or initialize) WROTE it, while some statement of the same list writes it (so it is ours, not an
engine-provided variable), is a finding — unless that read sits on the left of `??`.
API: lint_pack(pack) -> (n_entities, [(entity file, statement index, variable, statement)])"""
import re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

VAR = re.compile(r"\b(?:v|variable)\.([a-z_][a-z_0-9]*)\b(?!\s*\.)", re.I)
ASSIGN = re.compile(r"\b(?:v|variable)\.([a-z_][a-z_0-9]*)\s*=(?!=)", re.I)
GUARDED = re.compile(r"\b(?:v|variable)\.([a-z_][a-z_0-9]*)\s*\?\?", re.I)


def statements(lines):
    out = []
    for s in lines or []:
        if not isinstance(s, str): continue
        for part in s.split(";"):
            if part.strip(): out.append(part.strip())
    return out


def check_scripts(sc):
    init = statements(sc.get("initialize"))
    pre = statements(sc.get("pre_animation"))
    written = set()
    for st in init:
        m = ASSIGN.match(st)
        if m: written.add(m.group(1).lower())
    ours = {m.group(1).lower() for st in pre for m in [ASSIGN.match(st)] if m}
    finds = []
    for i, st in enumerate(pre):
        m = ASSIGN.match(st)
        target = m.group(1).lower() if m else None
        rhs = st[m.end():] if m else st
        guarded = {g.lower() for g in GUARDED.findall(rhs)}
        for name in {x.lower() for x in VAR.findall(rhs)}:
            if name in ours and name not in written and name not in guarded:
                finds.append((i, name, st[:140]))
        if target: written.add(target)
    return finds


def guard_reads(pre, known=(), always=()):
    """D-C286: rewrite a pre_animation list so every read of one of ITS OWN variables before that variable's first write
    (self-references included) becomes `(v.x ?? 0)`; `known` = names already set (initialize), `always` = names to guard
    wherever they are read (set elsewhere, e.g. an animation controller's on_entry). Statements are kept one per string."""
    out = []; written = {k.lower() for k in known}; alw = {a.lower() for a in always}
    ours = {m.group(1).lower() for s in statements(pre) for m in [ASSIGN.match(s)] if m}
    for s in pre:
        if not isinstance(s, str): out.append(s); continue
        parts = []
        for st in [x for x in s.split(";") if x.strip()]:
            st = st.strip(); m = ASSIGN.match(st)
            head, rhs = (st[:m.end()], st[m.end():]) if m else ("", st)
            guarded = {g.lower() for g in GUARDED.findall(rhs)}
            def rep(mm):
                n = mm.group(1).lower()
                if n in guarded: return mm.group(0)
                if (n in ours and n not in written) or n in alw: return f"({mm.group(0)} ?? 0)"
                return mm.group(0)
            parts.append(head + VAR.sub(rep, rhs))
            if m: written.add(m.group(1).lower())
        out.append("; ".join(parts) + ";")
    return out


def lint_pack(pack):
    n = 0; out = []
    root = Path(pack) / "entity"
    for p in sorted(root.rglob("*.json")) if root.exists() else []:
        try: d = ML._parse_json(p.read_text(encoding="utf-8-sig"))
        except Exception: continue
        if not isinstance(d, dict) or "minecraft:client_entity" not in d: continue
        n += 1
        sc = (d["minecraft:client_entity"].get("description") or {}).get("scripts") or {}
        for i, name, st in check_scripts(sc):
            out.append((p.relative_to(pack).as_posix(), i, name, st))
    return n, out


def _selftest():
    bad = {"pre_animation": ["v.a = math.clamp(v.a + 1, 0, 5);", "v.b = v.c;", "v.c = 1;"]}
    assert [f[1] for f in check_scripts(bad)] == ["a", "c"], check_scripts(bad)
    ok = {"initialize": ["v.a = 0;"], "pre_animation": ["v.a = v.a + 1;", "v.b = (v.c ?? 0);", "v.c = q.life_time;", "v.d = v.gliding_speed_value;"]}
    assert check_scripts(ok) == [], check_scripts(ok)
    g = guard_reads(["v.a = math.clamp(v.a + 1, 0, 5);", "v.b = v.c * v.r;", "v.c = 1;"], always=("r",))
    assert g == ["v.a = math.clamp((v.a ?? 0) + 1, 0, 5);", "v.b = (v.c ?? 0) * (v.r ?? 0);", "v.c = 1;"], g
    assert check_scripts({"pre_animation": g}) == []
    print("molang_rbw_lint self-test OK")


if __name__ == "__main__":
    _selftest()
    bad = 0
    for a in sys.argv[1:]:
        n, f = lint_pack(a)
        print(f"{Path(a).name}: {n} client entities; {len(f)} read-before-write findings")
        for x in f: print("  ", x)
        bad += len(f)
    sys.exit(1 if bad else 0)

#!/usr/bin/env python3
"""molang_carry.py — copy a clip to another creature WITH the variables it reads (10-01, the p21 shared_ defect: 103 reads of
variables only the SOURCE creature's scripts set — per-entity NWR, tools/nwr_entity_lint.py).

carry(clip, src_desc, tgt_desc, prefix) -> (clip2, init_stmts, pre_stmts, missing)
  * needed = every variable the clip reads that is not engine-provided and not guarded with `??`;
  * every needed variable the SOURCE writes in its scripts (initialize / pre_animation) is carried: the source statements
    that write it are copied, and the closure is taken (a carried statement's own variable reads are carried too);
  * every carried variable is RENAMED `<prefix><name>` in the clip and in the carried statements, so it can never collide
    with (or silently re-define) a variable of the target;
  * missing = needed variables the source does not write in its scripts (written by a controller / timeline / nowhere):
    the caller must refuse the copy unless the TARGET itself writes them.
Statements are split on top-level `;` (not inside () or {})."""
import copy
import json
import re
import sys

sys.path.insert(0, "/home/claude/tools")
import molang_nwr_lint as NW  # noqa: E402

READ, WRITE, GUARD = NW.READ, NW.WRITE, NW.GUARD


def split_statements(s):
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "({":
            depth += 1
        elif ch in ")}":
            depth -= 1
        if ch == ";" and depth == 0:
            if "".join(cur).strip():
                out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


def script_statements(desc, key):
    out = []
    for s in ((desc.get("scripts") or {}).get(key) or []):
        if isinstance(s, str):
            out += split_statements(s)
    return out


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def reads_of_text(texts):
    r = set()
    for s in texts:
        guarded = {g.lower() for g in GUARD.findall(s)}
        r |= {x.lower() for x in READ.findall(s)} - guarded
    return r


def writes_of_desc(desc):
    w = set()
    for s in strings(desc.get("scripts") or {}):
        w |= {m.lower() for m in WRITE.findall(s)}
    return w


def rename(text, names, prefix):
    if not names:
        return text
    rx = re.compile(r"\b(v|variable)\.(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b", re.I)
    return rx.sub(lambda m: f"{m.group(1)}.{prefix}{m.group(2).lower()}", text)


def rename_json(x, names, prefix):
    if isinstance(x, str):
        return rename(x, names, prefix)
    if isinstance(x, dict):
        return {k: rename_json(v, names, prefix) for k, v in x.items()}
    if isinstance(x, list):
        return [rename_json(v, names, prefix) for v in x]
    return x


def carry(clip, src_desc, tgt_desc, prefix):
    src_stmts = {k: script_statements(src_desc, k) for k in ("initialize", "pre_animation")}
    writers = {}
    for k, sts in src_stmts.items():
        for i, st in enumerate(sts):
            for w in WRITE.findall(st):
                writers.setdefault(w.lower(), []).append((k, i))
    need = reads_of_text(strings(clip)) - NW.ENGINE
    carried, missing, picked = set(), set(), set()
    todo = list(need)
    while todo:
        v = todo.pop()
        if v in carried or v in missing:
            continue
        if v not in writers:
            missing.add(v)
            continue
        carried.add(v)
        for k, i in writers[v]:
            if (k, i) in picked:
                continue
            picked.add((k, i))
            st = src_stmts[k][i]
            for r in reads_of_text([st]) - NW.ENGINE:
                if r not in carried:
                    todo.append(r)
            for w in WRITE.findall(st):            # a statement writing two variables carries both
                if w.lower() not in carried:
                    todo.append(w.lower())
    clip2 = rename_json(copy.deepcopy(clip), carried, prefix)
    init = [rename(src_stmts["initialize"][i], carried, prefix) + ";" for k, i in sorted(picked) if k == "initialize"]
    pre = [rename(src_stmts["pre_animation"][i], carried, prefix) + ";" for k, i in sorted(picked) if k == "pre_animation"]
    # a variable the source never writes but the TARGET does is fine (same engine meaning is not guaranteed; the caller's gate
    # decides); report only what nobody writes
    missing -= writes_of_desc(tgt_desc)
    return clip2, init, pre, sorted(missing)


def _ver(s):
    try:
        return tuple(int(x) for x in str(s).split("."))
    except ValueError:
        return (0,)


def apply_to_entity(desc, init, pre, format_version="1.10.0"):
    """append carried statements (as one string per list, idempotent by content) to the target entity's scripts.
    A format < 1.10.0 entity has no `initialize` (L-FMT-SCRIPTS; his content log 1): its carried initialize statements become
    `v.x = v.x ?? (value);` at the FRONT of pre_animation (set once, then kept)."""
    sc = desc.setdefault("scripts", {})
    if _ver(format_version) < (1, 10, 0) and init:
        once = []
        for st in init:
            for one in split_statements(st):
                lhs, rhs = one.split("=", 1)
                once.append(f"{lhs.strip()} = {lhs.strip()} ?? ({rhs.strip()});")
        block = " ".join(once)
        cur = sc.setdefault("pre_animation", [])
        if block not in cur:
            cur.insert(0, block)
        init = []
    for key, sts in (("initialize", init), ("pre_animation", pre)):
        if not sts:
            continue
        cur = sc.setdefault(key, [])
        block = " ".join(sts)
        if block not in cur:
            cur.append(block)


if __name__ == "__main__":
    print(json.dumps(split_statements("v.a = 1; v.b = (v.a > 0 ? {v.c = 2; v.c} : 0); v.d = 3"), indent=0))

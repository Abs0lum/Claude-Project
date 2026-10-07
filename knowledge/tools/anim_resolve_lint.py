#!/usr/bin/env python3
"""anim_resolve_lint.py — D-C283 standing gate (his 12:46 "Yes"): every animation an entity is told to play must exist.

Why: RP-06 1.4.12 ravager (`anim_nose`) and 1.4.14 pillager (`anim_fall`, `anim_landing`) logged
"[Animation][error]-Error: can't find animation <name>" when they spawned: they use a SHARED villager controller whose states play
short names the entity's own `animations` map does not define. Static, so it can be caught before shipping.

Checks per client entity (RP `entity/*.json`, attachables too):
  1. every controller the entity lists resolves to a definition (this pack > the rest of the stack > vanilla samples);
  2. every short name a state of those controllers plays (string entries and {name: condition} keys) is a key of the entity's
     `animations` map;
  3. every short name in `scripts.animate` is a key of the `animations` map;
  4. every animation id the `animations` map points at exists (pack > stack > vanilla), unless it is itself a controller id.
API:  lint_pack(root, stack=()) -> (n_entities, [(entity file, identifier, problem)])
CLI:  anim_resolve_lint.py PACK_DIR [--stack DIR ...]"""
import glob, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

VANILLA = Path("/home/claude/_intake/bedrock-samples/resource_pack")


def _load(p):
    try:
        return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def definitions(roots):
    """{controller id: def}, {animation id: def} — first root wins (pass the pack first, vanilla last)."""
    ctl, anim = {}, {}
    for root in roots:
        for f in glob.glob(str(Path(root) / "animation_controllers/**/*.json"), recursive=True):
            d = _load(f) or {}
            for k, v in (d.get("animation_controllers") or {}).items(): ctl.setdefault(k, v)
        for f in glob.glob(str(Path(root) / "animations/**/*.json"), recursive=True):
            d = _load(f) or {}
            for k, v in (d.get("animations") or {}).items(): anim.setdefault(k, v)
    return ctl, anim


def _names(entries):
    out = []
    for e in entries or []:
        if isinstance(e, str): out.append(e)
        elif isinstance(e, dict): out += list(e.keys())
    return out


def lint_pack(root, stack=()):
    root = Path(root)
    ctl, anim = definitions([root, *stack, VANILLA])
    problems, n = [], 0
    for f in sorted(glob.glob(str(root / "entity/*.json")) + glob.glob(str(root / "attachables/*.json"))):
        d = _load(f)
        if not d: continue
        desc = (d.get("minecraft:client_entity") or d.get("minecraft:attachable") or {}).get("description") or {}
        ident = desc.get("identifier")
        if not ident: continue
        n += 1; rel = Path(f).relative_to(root).as_posix()
        amap = desc.get("animations") or {}
        for short, aid in amap.items():
            if isinstance(aid, str) and aid not in anim and aid not in ctl:
                problems.append((rel, ident, f"animations.{short} -> {aid} is defined nowhere (pack, stack, vanilla)"))
        ctl_ids = [aid for aid in amap.values() if isinstance(aid, str) and aid in ctl]
        for e in desc.get("animation_controllers") or []:             # legacy list form
            ctl_ids += [v for v in (e.values() if isinstance(e, dict) else [e]) if isinstance(v, str)]
        for cid in dict.fromkeys(ctl_ids):
            c = ctl.get(cid)
            if c is None:
                problems.append((rel, ident, f"controller {cid} is defined nowhere")); continue
            for sn, st in (c.get("states") or {}).items():
                for name in _names(st.get("animations")):
                    if name not in amap:
                        problems.append((rel, ident, f"controller {cid} state '{sn}' plays '{name}' — not in the entity's animations"))
        for name in _names((desc.get("scripts") or {}).get("animate")):
            if name not in amap:
                problems.append((rel, ident, f"scripts.animate plays '{name}' — not in the entity's animations"))
    return n, list(dict.fromkeys(problems))


if __name__ == "__main__":
    args = sys.argv[1:]; stack = []
    if "--stack" in args:
        i = args.index("--stack"); stack = [Path(a) for a in args[i + 1:]]; args = args[:i]
    bad = 0
    for a in args:
        n, probs = lint_pack(a, [s for s in stack if Path(s) != Path(a)])
        print(f"{a}: {n} entities, {len(probs)} problems")
        for rel, ident, msg in probs: print(f"  {rel} | {ident} | {msg}")
        bad += len(probs)
    sys.exit(1 if bad else 0)

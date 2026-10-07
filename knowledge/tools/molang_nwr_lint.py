#!/usr/bin/env python3
"""molang_nwr_lint.py — NWR standing gate (D-C317): no client entity may READ a variable that nothing in the pack ever WRITES,
unless the read is guarded with `??` or the variable is one the engine provides.

Why (his R17 p13 i01 / i02, "legs are pivoting from the ground instead of from hips"): the golem port read
v.pw_ig_body_top_rz, which no statement sets. In game that read is an error: the entity's whole pre_animation stopped at that
line, 30 variables stayed unknown (his content log names all 30) and the legs lost their slide. The older RBW lint
(molang_rbw_lint) only audits variables the script writes SOMEWHERE (read before the first write); a variable written nowhere
was the unaudited space (P11). The offline evaluator read it as 0, so N2 / N3 passed too (they now run molang_eval strict).

What counts as a write: `v.x =` / `variable.x =` in any client entity script (initialize / pre_animation / animate conditions),
any animation file (timeline / variables) and any animation controller (on_entry / on_exit / variables) of the SAME pack.
Engine-provided variables (read by Mojang's own files and written nowhere in them): ENGINE below.
API: lint_pack(pack) -> (entities scanned, [(entity file, variable, first statement)])."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

WRITE = re.compile(r"\b(?:v|variable)\.([a-z0-9_]+)\s*=(?!=)", re.I)
READ = re.compile(r"\b(?:v|variable)\.([a-z0-9_]+)", re.I)
GUARD = re.compile(r"\b(?:v|variable)\.([a-z0-9_]+)\s*\?\?", re.I)
# ENGINE = read by Mojang's own bedrock-samples resource pack and written nowhere in it = provided by the engine (D-C317 census:
# 168 names, e.g. gliding_speed_value, attack_time, liedownamount, raise_arms, TropicalFish.* ). Derived from the files, not typed.
SAMPLES = Path("/home/claude/_intake/bedrock-samples/resource_pack")


def engine_vars():
    w, r = set(), set()
    for f in SAMPLES.rglob("*.json"):
        t = f.read_text(encoding="utf-8-sig", errors="ignore")
        w |= {x.lower() for x in WRITE.findall(t)}; r |= {x.lower() for x in READ.findall(t)}
    if not r: raise FileNotFoundError(f"Mojang samples not found at {SAMPLES} (the engine list is derived from them)")
    return r - w


ENGINE = engine_vars()


def pack_writes(pack):
    w = set()
    for sub in ("animations", "animation_controllers", "entity"):
        for f in Path(pack, sub).rglob("*.json") if Path(pack, sub).exists() else []:
            try: w |= {m.lower() for m in WRITE.findall(f.read_text(encoding="utf-8-sig", errors="ignore"))}
            except Exception: pass
    return w


def lint_pack(pack):
    pack = Path(pack); writes = pack_writes(pack); n = 0; out = []
    for f in sorted((pack / "entity").rglob("*.json")) if (pack / "entity").exists() else []:
        try: d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
        except Exception: continue
        if not isinstance(d, dict) or "minecraft:client_entity" not in d: continue
        n += 1
        sc = (d["minecraft:client_entity"].get("description") or {}).get("scripts") or {}
        stmts = []
        for key in ("initialize", "pre_animation"):
            for s in sc.get(key, []) or []:
                if isinstance(s, str): stmts += [x.strip() for x in s.split(";") if x.strip()]
        for a in sc.get("animate", []) or []:
            if isinstance(a, dict): stmts += [str(v) for v in a.values()]
        seen = set()
        for st in stmts:
            m = WRITE.match(st)
            rhs = st[m.end():] if m else st
            guarded = {g.lower() for g in GUARD.findall(rhs)}
            for r in READ.findall(rhs):
                r = r.lower()
                if r in writes or r in guarded or r in ENGINE or r in seen: continue
                seen.add(r); out.append((f.relative_to(pack).as_posix(), r, st[:160]))
    return n, out


def _selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        e = Path(t, "entity"); e.mkdir()
        (e / "a.entity.json").write_text(json.dumps({"format_version": "1.10.0", "minecraft:client_entity": {"description": {
            "identifier": "x:a", "scripts": {"pre_animation": ["v.b = v.never / 2;", "v.c = (v.guarded ?? 0) + v.b;", "v.d = v.gliding_speed_value;"]}}}}))
        n, out = lint_pack(t)
        assert n == 1 and [o[1] for o in out] == ["never"], out
    print("molang_nwr_lint selftest ok")


if __name__ == "__main__":
    if len(sys.argv) == 1: _selftest()
    for p in sys.argv[1:]:
        n, out = lint_pack(p)
        print(f"{p}: {n} client entities, {len(out)} never-written reads")
        for o in out: print("   ", o)

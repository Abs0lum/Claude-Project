#!/usr/bin/env python3
"""verify_rp06_1411.py — gate for RP-06 v1.4.11 (D-C270).
  A  diff vs 1.4.10 = creeper.entity.json + manifest changed, render_controllers/pw_creeper_armor.render.json added, nothing else
  B  creeper.entity.json: format 1.8.0, render_controllers are all STRINGS, both controllers resolve (ours in this pack, vanilla's
     controller.render.creeper in the vanilla RP); everything else in the file unchanged
  C  pw_creeper_armor == vanilla creeper_armor verbatim + part_visibility [{"*": "query.is_powered"}]; RC file format 1.8.0
  D  the stack: no client entity / attachable in any local pack puts an object in render_controllers under format < 1.10.0
  E  manifest 1.4.11, uuid kept; every changed/added file is strict JSON
Exit 1 on any FAIL."""
import filecmp, glob, json, re, sys
from pathlib import Path
ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp06-1410", ROOT / "_build/rp06-1411"
VAN = ROOT / "_intake/bedrock-samples/resource_pack"
results = []


def check(tag, ok, msg):
    results.append((tag, bool(ok), msg)); print(f"{'PASS' if ok else 'FAIL'} {tag}: {msg}")


def load(f):
    t = re.sub(r"^\s*//.*$", "", open(f, encoding="utf-8-sig", errors="replace").read(), flags=re.M)
    try: return json.loads(t)
    except Exception:
        try: return json.loads(re.sub(r",(\s*[}\]])", r"\1", t))
        except Exception: return None


def files(r):
    return {str(p.relative_to(r)) for p in r.rglob("*") if p.is_file()}


def ver(v):
    try: return tuple(int(x) for x in str(v).split("."))
    except Exception: return (0,)


def main():
    fo, fn = files(OLD), files(NEW)
    ch = {f for f in fo & fn if not filecmp.cmp(OLD / f, NEW / f, shallow=False)}
    check("A", fn - fo == {"render_controllers/pw_creeper_armor.render.json"} and not (fo - fn) and ch == {"entity/creeper.entity.json", "manifest.json"},
          f"added {sorted(fn - fo)} changed {sorted(ch)}")
    eo, en = load(OLD / "entity/creeper.entity.json"), load(NEW / "entity/creeper.entity.json")
    rcs = en["minecraft:client_entity"]["description"]["render_controllers"]
    rc_ids = set()
    for f in glob.glob(str(NEW / "render_controllers/*.json")) + glob.glob(str(VAN / "render_controllers/*.json")):
        d = load(f)
        if d: rc_ids |= set(d.get("render_controllers", {}))
    do = json.loads(json.dumps(eo)); dn = json.loads(json.dumps(en))
    do["minecraft:client_entity"]["description"].pop("render_controllers"); dn["minecraft:client_entity"]["description"].pop("render_controllers")
    check("B", en["format_version"] == "1.8.0" and all(isinstance(x, str) for x in rcs) and all(x in rc_ids for x in rcs) and do == dn,
          f"format {en['format_version']}; render_controllers {rcs} (all strings, all resolve); rest of the file unchanged: {do == dn}")
    ours = load(NEW / "render_controllers/pw_creeper_armor.render.json")
    van = load(VAN / "render_controllers/creeper_armor.render_controllers.json")["render_controllers"]["controller.render.creeper_armor"]
    mine = dict(ours["render_controllers"]["controller.render.pw_creeper_armor"]); pv = mine.pop("part_visibility", None)
    check("C", ours["format_version"] == "1.8.0" and mine == van and pv == [{"*": "query.is_powered"}], f"vanilla shell verbatim: {mine == van}; part_visibility {pv}")
    bad = []; n = 0
    for r in ["_build/rp06-1411", "_build/rp07-1415", "_build/rp08-147", "_build/rp10-142", "_build/rp05-51", "_build/rp04-142", "_build/rp03-60",
              "_build/rp02-205", "_build/rp01-104", "_build/testrunner-rp-0.3.0", "_build/markers-0.2.1"]:
        for f in glob.glob(str(ROOT / r / "entity/**/*.json"), recursive=True) + glob.glob(str(ROOT / r / "attachables/**/*.json"), recursive=True):
            d = load(f)
            if not d: continue
            for key in ("minecraft:client_entity", "minecraft:attachable"):
                if key in d:
                    n += 1
                    if any(isinstance(x, dict) for x in d[key].get("description", {}).get("render_controllers", [])) and ver(d.get("format_version")) < (1, 10, 0):
                        bad.append(f.replace(str(ROOT) + "/", ""))
    check("D", not bad, f"{n} entity/attachable files: object-form render controllers under format < 1.10.0: {bad}")
    mo, mn = load(OLD / "manifest.json"), load(NEW / "manifest.json")
    strict = []
    for f in ch | (fn - fo):
        try: json.loads((NEW / f).read_text(encoding="utf-8-sig"))
        except Exception as e: strict.append((f, str(e)[:50]))
    check("E", mn["header"]["version"] == [1, 4, 11] and mn["header"]["uuid"] == mo["header"]["uuid"] and not strict, f"manifest {mn['header']['version']} uuid kept; strict-JSON failures {strict}")
    fails = [r for r in results if not r[1]]
    print(f"GATE {'OPEN' if not fails else 'CLOSED'} {len(results) - len(fails)}/{len(results)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

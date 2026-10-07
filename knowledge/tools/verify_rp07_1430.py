#!/usr/bin/env python3
"""verify_rp07_1430.py — gate for RP-07 1.4.30 (build_rp07_1430.py). Static checks only rule OUT (P1).
  A  diff vs 1.4.29 = manifest + the fox animation + the fox entity + the fox geometry file, nothing else
  B  manifest 1.4.30, uuids kept; strict JSON on the changed files
  C  fox geometry: pw_render at the origin, parent of every former top-level bone; every cube's world corners == 1.4.29 (rest pose)
  D  fox entity: only initialize / pre_animation changed; the pounce latch runs first; pw_jem still the only animation
  N2 / N3 on the shipped fox (Molang == JEM; posed geometry == the JEM at the pose)
  S  standing lints on the new pack: Molang grammar, read-before-write (baseline), animation resolution (baseline)"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import r16b
import build_r16b as BR
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp07-1429", ROOT / "_build/rp07-1430"
res = []
def check(tag, ok, msg=""):
    res.append((tag, bool(ok))); print(("PASS " if ok else "FAIL ") + tag + (f" — {msg}" if msg else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
fo = {str(p.relative_to(OLD)): p for p in OLD.rglob("*") if p.is_file()}; fn = {str(p.relative_to(NEW)): p for p in NEW.rglob("*") if p.is_file()}
changed = sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k]))
pg, _ = R.geo_file(NEW, "geometry.pw_fox"); geo_rel = str(pg.relative_to(NEW))
want = sorted(["manifest.json", "animations/pw_fox_jem.animation.json", "entity/fox.entity.json", geo_rel])
check("A diff = manifest + fox animation / entity / geometry", changed == want and set(fo) == set(fn), f"changed {changed}")
mo, mn = R.jl(OLD / "manifest.json"), R.jl(NEW / "manifest.json")
check("B manifest 1.4.30, uuids kept", mn["header"]["version"] == [1, 4, 30] and all(m["version"] == [1, 4, 30] for m in mn["modules"])
      and mn["header"]["uuid"] == mo["header"]["uuid"] and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]])
bad = []
for k in changed:
    try: json.loads(fn[k].read_text(encoding="utf-8"))
    except Exception as e: bad.append(f"{k}: {e}")
check("B strict JSON", not bad, str(bad))
_, go = R.geo_file(OLD, "geometry.pw_fox"); _, gn = R.geo_file(NEW, "geometry.pw_fox")
byn = {b["name"]: b for b in gn["bones"]}
tops_old = [b["name"] for b in go["bones"] if not b.get("parent")]
Wo = {(x[0], x[1]): np.array(x[2]) for x in world_boxes(go["bones"])}; Wn = {(x[0], x[1]): np.array(x[2]) for x in world_boxes(gn["bones"])}
err = max(float(np.abs(Wo[k] - Wn[k]).max()) for k in Wo) if set(Wo) == set(Wn) else 99.0
check("C geometry: pw_render at the origin over every former top-level bone; rest cubes unchanged", byn.get("pw_render", {}).get("pivot") == [0.0, 0.0, 0.0]
      and all(byn[t].get("parent") == "pw_render" for t in tops_old) and err < 1e-6 and gn["description"] == go["description"], f"max corner move {err:.2e} px")
eo = ML._parse_json((OLD / "entity/fox.entity.json").read_text())["minecraft:client_entity"]["description"]
en = ML._parse_json((NEW / "entity/fox.entity.json").read_text())["minecraft:client_entity"]["description"]
same = {k: en[k] == eo[k] for k in eo if k != "scripts"}
sc_ok = en["scripts"]["animate"] == eo["scripts"]["animate"] == ["pw_jem"] and en["scripts"].get("scale") == eo["scripts"].get("scale")
check("D entity: only initialize / pre_animation changed; the pounce latch first; pw_jem only", all(same.values()) and sc_ok
      and en["scripts"]["pre_animation"][0].startswith("v.pw_fx_pounce_on = ") and len(en["scripts"]["pre_animation"]) == len(eo["scripts"]["pre_animation"]) + 1,
      f"{sum(same.values())}/{len(same)} other keys identical")
anim = R.jl(NEW / "animations/pw_fox_jem.animation.json")["animations"][BR.anim_id("fox")]
r16b.bake("fox")
w2 = r16b.n2("fox", en["scripts"]["initialize"], en["scripts"]["pre_animation"], anim)
check("N2 fox Molang == JEM", w2["rotation"] <= 0.01 and w2["position"] <= 1e-3 and w2["scale"] <= 1e-3, str({k: round(v, 5) for k, v in w2.items()}))
w3, per = r16b.n3("fox", gn["bones"], en["scripts"]["initialize"], en["scripts"]["pre_animation"], anim)
check("N3 fox posed shipped geometry == the JEM at the pose", w3 <= 0.01, f"worst {w3:.4f} px over {len(per)} cases")
# the pitch itself (renderer move): pounce leap up = nose up (negative), drop = nose down, on the ground 0, stuck 60
import molang_eval as ME
rot = anim["bones"]["pw_render"]["rotation"][0]
def pitch(env):
    e = {"q.is_on_ground": 1.0, "q.is_interested": 0.0, "q.is_stalking": 0.0, "q.is_stunned": 0.0, "q.vertical_speed": 0.0, **env}
    for s in en["scripts"]["pre_animation"][:1]: ME.run(s, e)
    return ME.run(rot, e)
cases = {"on the ground": pitch({"q.vertical_speed": 3.0}), "leap up after wiggle": pitch({"q.is_on_ground": 0.0, "q.is_interested": 1.0, "q.vertical_speed": 4.0}),
         "falling in a pounce": pitch({"q.is_on_ground": 0.0, "v.pw_fx_pounce_on": 1.0, "q.vertical_speed": -5.0}),
         "a plain jump (no stalk / wiggle)": pitch({"q.is_on_ground": 0.0, "q.vertical_speed": 4.0}), "stuck in snow": pitch({"q.is_stunned": 1.0})}
check("P pounce pitch: 0 on the ground and on a plain jump, nose up on the leap, nose down on the drop, 60 stuck",
      cases["on the ground"] == 0 and cases["a plain jump (no stalk / wiggle)"] == 0 and cases["leap up after wiggle"] < 0 < cases["falling in a pounce"]
      and cases["stuck in snow"] == 60.0, str({k: round(v, 2) for k, v in cases.items()}))
n_ml, e_ml = ML.lint_pack(NEW)
check("S Molang grammar (standing)", not e_ml, f"{n_ml} strings, {len(e_ml)} errors")
import molang_rbw_lint, anim_resolve_lint
n_rb, f_rb = molang_rbw_lint.lint_pack(NEW)
base = set(json.load(open(ROOT / "_docs/convb/rbw_baseline.json")).get("RP-07", []))
new_rb = sorted({f"{x[0]} | {x[2]}" for x in f_rb} - base)
check("S read-before-write (standing, baseline)", not new_rb, f"NEW {new_rb[:3]}")
n_ar, e_ar = anim_resolve_lint.lint_pack(NEW, stack=(ROOT / "_build/rp06-1423",))
ars_base = set(json.load(open(R.ARS_BASELINE)).get("RP-07", [])) if R.ARS_BASELINE.exists() else set()
new_ar = sorted({f"{e[0]} | {e[2]}" for e in e_ar} - ars_base)
check("S every animation an entity plays exists (standing, baseline)", not new_ar, f"NEW {new_ar[:3]}")
print(f"\n{'GATE OPEN' if all(r[1] for r in res) else 'GATE SHUT'} {sum(r[1] for r in res)}/{len(res)}")
sys.exit(0 if all(r[1] for r in res) else 1)

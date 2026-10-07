#!/usr/bin/env python3
"""verify_rp06_1424.py — gate for RP-06 1.4.24 (build_rp06_1424.py, the vex held-item probe). Static checks only rule OUT (P1).
  A   diff vs 1.4.23 = manifest + vex entity + pw_vex animation; added = the two probe geometries + the probe render controller
  B   manifest 1.4.24, uuids kept; strict JSON
  V1  probe A = geometry.pw_vex with ONLY right_arm / left_arm renamed rightArm / leftArm (every cube, pivot, rotation identical)
  V2  probe B = geometry.pw_vex with ONLY rightItem / leftItem moved under body; their rest world pivot + orientation unchanged
  V3  animation: rightArm / leftArm channels == right_arm / left_arm channels; every other channel untouched
  V4  probe A posed == pw_vex posed (4 poses: the hand points + arm cubes move identically), so the only difference is the NAME
  V5  render controller: geometry index = v.pw_vx_probe (0 = sword / empty -> A, 1 = amethyst shard -> B); every Geometry.* /
      Texture.* it names exists on the entity; the entity sets v.pw_vx_probe first in pre_animation
  S   standing lints: NWR, Molang grammar, read-before-write (baseline), animation resolution (baseline), attachables"""
import copy, hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import molang_eval as ME
import wing_contact as WC

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp06-1423", ROOT / "_build/rp06-1424"
res = []
def check(tag, ok, msg=""):
    res.append((tag, bool(ok))); print(("PASS " if ok else "FAIL ") + tag + (f" — {msg}" if msg else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
fo = {str(p.relative_to(OLD)): p for p in OLD.rglob("*") if p.is_file()}; fn = {str(p.relative_to(NEW)): p for p in NEW.rglob("*") if p.is_file()}
changed = sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])); added = sorted(set(fn) - set(fo))
check("A diff = manifest + vex entity + pw_vex animation; added = 2 probe geometries + probe render controller",
      changed == sorted(["manifest.json", "entity/vex.entity.json", "animations/pw_vex.animation.json"]) and not (set(fo) - set(fn))
      and added == sorted(["models/entity/pw_vex_probe_a.geo.json", "models/entity/pw_vex_probe_b.geo.json", "render_controllers/pw_vex_probe.render.json"]),
      f"changed {changed}; added {added}")
mo, mn = R.jl(OLD / "manifest.json"), R.jl(NEW / "manifest.json")
check("B manifest 1.4.24, uuids kept", mn["header"]["version"] == [1, 4, 24] and all(m["version"] == [1, 4, 24] for m in mn["modules"])
      and mn["header"]["uuid"] == mo["header"]["uuid"] and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]])
bad = []
for k in changed + added:
    try: json.loads(fn[k].read_text(encoding="utf-8"))
    except Exception as e: bad.append(f"{k}: {e}")
check("B strict JSON", not bad, str(bad))
_, g0 = R.geo_file(NEW, "geometry.pw_vex"); _, ga = R.geo_file(NEW, "geometry.pw_vex_probe_a"); _, gb = R.geo_file(NEW, "geometry.pw_vex_probe_b")
RN = {"right_arm": "rightArm", "left_arm": "leftArm"}
exp_a = copy.deepcopy(g0["bones"])
for b in exp_a:
    b["name"] = RN.get(b["name"], b["name"])
    if b.get("parent") in RN: b["parent"] = RN[b["parent"]]
check("V1 probe A = pw_vex with only the two arm names changed", ga["bones"] == exp_a and ga["description"]["texture_width"] == g0["description"]["texture_width"],
      f"{len(ga['bones'])} bones")
by0 = {b["name"]: b for b in g0["bones"]}; byb = {b["name"]: b for b in gb["bones"]}
others_same = all(byb[n] == by0[n] for n in by0 if n not in ("rightItem", "leftItem"))
a0, ab = WC.affines(g0["bones"], {}), WC.affines(gb["bones"], {})
dev = 0.0
for it in ("rightItem", "leftItem"):
    w0 = a0[it][0] @ np.array(by0[it]["pivot"]) + a0[it][1]; wb = ab[it][0] @ np.array(byb[it]["pivot"]) + ab[it][1]
    dev = max(dev, float(np.abs(w0 - wb).max()), float(np.abs(a0[it][0] - ab[it][0]).max()))
check("V2 probe B = pw_vex with only the hand bones under body; their rest pivot + orientation unchanged",
      others_same and byb["rightItem"]["parent"] == "body" and byb["leftItem"]["parent"] == "body" and dev < 1e-3, f"max deviation {dev:.1e}")
ao = R.jl(OLD / "animations/pw_vex.animation.json")["animations"]["animation.pw_vex.jem"]["bones"]
an = R.jl(NEW / "animations/pw_vex.animation.json")["animations"]["animation.pw_vex.jem"]["bones"]
check("V3 animation: rightArm / leftArm == right_arm / left_arm; every other channel untouched",
      an["rightArm"] == an["right_arm"] and an["leftArm"] == an["left_arm"] and {k: v for k, v in an.items() if k not in ("rightArm", "leftArm")} == ao)
ent = ML._parse_json((NEW / "entity/vex.entity.json").read_text())["minecraft:client_entity"]["description"]
pre = ent["scripts"]["pre_animation"]
worst = 0.0
for lt, ch_, eq0 in ((1.0, 0.0, 1.0), (7.3, 1.0, 1.0), (12.0, 0.0, 0.0), (20.5, 1.0, 0.0)):
    env = {"q.life_time": lt, "q.delta_time": 0.05, "q.is_charging": ch_, "q.is_item_equipped(0.0)": eq0, "q.is_item_equipped(1.0)": 0.0,
           "q.modified_distance_moved": 2.0, "q.modified_move_speed": 0.3, "q.is_alive": 1.0, "q.is_on_ground": 0.0}
    for s in ent["scripts"]["initialize"]: ME.run(s, env)
    for _ in range(24):
        for s in pre[1:]: ME.run(s, env)          # statement 0 = the probe selector (a string query molang_eval does not evaluate)
    chans = {}
    for b, c in an.items():
        chans[b] = {k: [ME.run(x, dict(env)) if isinstance(x, str) else float(x) for x in c[k]] for k in ("rotation", "position", "scale") if k in c}
    A0, AA = WC.affines(g0["bones"], chans), WC.affines(ga["bones"], chans)
    for n0 in ("rightItem", "leftItem", "right_arm", "left_arm"):
        na = RN.get(n0, n0)
        p0 = A0[n0][0] @ np.array(by0[n0]["pivot"]) + A0[n0][1]
        pa = AA[na][0] @ np.array(next(b for b in ga["bones"] if b["name"] == na)["pivot"]) + AA[na][1]
        worst = max(worst, float(np.abs(p0 - pa).max()), float(np.abs(A0[n0][0] - AA[na][0]).max()))
check("V4 probe A posed == pw_vex posed (4 poses: calm / charging, holding / empty)", worst < 1e-6, f"max deviation {worst:.1e}")
rc = R.jl(NEW / "render_controllers/pw_vex_probe.render.json")["render_controllers"]["controller.render.pw_vex_probe"]
geos = rc["arrays"]["geometries"]["Array.geos"]; texs = rc["arrays"]["textures"]["Array.textures"]
ok = (geos == ["Geometry.probe_a", "Geometry.probe_b"] and all(g.split(".", 1)[1] in ent["geometry"] for g in geos)
      and all(t.split(".", 1)[1] in ent["textures"] for t in texs) and rc["geometry"] == "Array.geos[v.pw_vx_probe ?? 0.0]"
      and ent["render_controllers"] == ["controller.render.pw_vex_probe"]
      and pre[0] == "v.pw_vx_probe = q.is_item_name_any('slot.weapon.mainhand', 'minecraft:amethyst_shard') ? 1.0 : 0.0;")
check("V5 render controller: index v.pw_vx_probe (0 sword / empty -> A, 1 shard -> B); every Geometry / Texture it names exists; selector first", ok,
      f"geos {geos}; entity geometry {sorted(ent['geometry'])}")
import molang_nwr_lint, molang_rbw_lint, anim_resolve_lint, attachables_lint
n_nw, f_nw = molang_nwr_lint.lint_pack(NEW)
check("S NWR (standing)", not f_nw, f"{n_nw} entities; {[(x[0], x[1]) for x in f_nw][:4]}")
n_ml, e_ml = ML.lint_pack(NEW)
check("S Molang grammar (standing)", not e_ml, f"{n_ml} strings, {len(e_ml)} errors {e_ml[:2]}")
n_rb, f_rb = molang_rbw_lint.lint_pack(NEW)
base = set(json.load(open(ROOT / "_docs/convb/rbw_baseline.json")).get("RP-06", []))
new_rb = sorted({f"{x[0]} | {x[2]}" for x in f_rb} - base)
check("S read-before-write (standing, baseline)", not new_rb, f"NEW {new_rb[:3]}")
n_ar, e_ar = anim_resolve_lint.lint_pack(NEW, stack=(ROOT / "_build/rp07-1431",))
ars_base = set(json.load(open(R.ARS_BASELINE)).get("RP-06", [])) if R.ARS_BASELINE.exists() else set()
new_ar = sorted({f"{e[0]} | {e[2]}" for e in e_ar} - ars_base)
check("S every animation an entity plays exists (standing, baseline)", not new_ar, f"NEW {new_ar[:3]}")
n_at, f_at = attachables_lint.lint_pack(NEW)
check("S attachables on where vanilla has them (standing)", not f_at, f"{n_at} entities; {f_at[:4]}")
print(f"\n{'GATE OPEN' if all(r[1] for r in res) else 'GATE SHUT'} {sum(r[1] for r in res)}/{len(res)}")
sys.exit(0 if all(r[1] for r in res) else 1)

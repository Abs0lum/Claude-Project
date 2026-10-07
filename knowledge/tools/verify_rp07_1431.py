#!/usr/bin/env python3
"""verify_rp07_1431.py — gate for RP-07 1.4.31 (build_rp07_1431.py). Static checks only rule OUT (P1); his p14 rules IN.
  A   diff vs 1.4.30 = manifest + golem entity + fox entity / geometry, nothing else (both animation files byte-identical)
  B   manifest 1.4.31, uuids kept; strict JSON on the changed files
  G1  golem: the never-assigned read is seeded (v.pw_ig_body_top_rz = 0 BEFORE its first read); strict run of the whole script
      raises nothing (the shipped 1.4.30 script raises at statement 70 = his 30 logged unknown variables)
  G2  golem N2 (strict) + N3 on the shipped geometry
  F1  fox held_item: parent snout, world point = snout lower-front corner + Mojang's (0, -0.7, -1), level at rest; every other
      cube of geometry.pw_fox unchanged
  F2  fox N2 (strict) + N3 (sit settled = FreshLX exactly)
  F3  sit settle: sit_amt 0 -> 1 in 0.25 s (5 frames of 0.05 s); a mid-blend body pose lies between standing and sitting
  F4  pounce pitch unchanged from 1.4.30 (0 on the ground / plain jump, nose up on the leap, down on the drop, 60 stuck)
  S   standing lints on the whole pack: NWR (new), Molang grammar, read-before-write (baseline), animation resolution (baseline)"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import molang_eval as ME
import r16b
import build_r16b as BR
import wing_contact as WC
from verify_rp07_1415_rp06_1410 import world_boxes

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp07-1430", ROOT / "_build/rp07-1431"
res = []
def check(tag, ok, msg=""):
    res.append((tag, bool(ok))); print(("PASS " if ok else "FAIL ") + tag + (f" — {msg}" if msg else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
fo = {str(p.relative_to(OLD)): p for p in OLD.rglob("*") if p.is_file()}; fn = {str(p.relative_to(NEW)): p for p in NEW.rglob("*") if p.is_file()}
changed = sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k]))
pg, _ = R.geo_file(NEW, "geometry.pw_fox"); geo_rel = str(pg.relative_to(NEW))
# the two animation files come out byte-identical: the fixes live in the entity scripts (golem seed, fox sit ramp + blended
# branches); the animation channels read the same variables as before
want = sorted(["manifest.json", "entity/fox.entity.json", geo_rel, "entity/iron_golem.entity.json"])
same_anims = all(md5(OLD / a) == md5(NEW / a) for a in ("animations/pw_fox_jem.animation.json", "animations/pw_iron_golem_jem.animation.json"))
check("A diff = manifest + golem entity + fox entity / geometry (both animation files identical)", changed == want and set(fo) == set(fn) and same_anims,
      f"changed {changed}; animations identical {same_anims}")
mo, mn = R.jl(OLD / "manifest.json"), R.jl(NEW / "manifest.json")
check("B manifest 1.4.31, uuids kept", mn["header"]["version"] == [1, 4, 31] and all(m["version"] == [1, 4, 31] for m in mn["modules"])
      and mn["header"]["uuid"] == mo["header"]["uuid"] and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]])
bad = []
for k in changed:
    try: json.loads(fn[k].read_text(encoding="utf-8"))
    except Exception as e: bad.append(f"{k}: {e}")
check("B strict JSON", not bad, str(bad))


def ent(pack, stem): return ML._parse_json((pack / f"entity/{stem}.entity.json").read_text())["minecraft:client_entity"]["description"]


def strict_run(desc, env_extra):
    env = {"q.life_time": 3.0, "q.delta_time": 0.05, "q.is_on_ground": 1.0, "q.is_alive": 1.0, "q.modified_distance_moved": 4.0,
           "q.modified_move_speed": 0.5, "q.health": 100.0, "q.max_health": 100.0, **env_extra}
    try:
        with ME.strict():
            for s in desc["scripts"].get("initialize", []): ME.run(s, env)
            for _ in range(3):
                for i, s in enumerate(desc["scripts"]["pre_animation"]): ME.run(s, env)
        return None
    except ME.UnknownVariable as e:
        return f"statement {i + 1}: {e}"


# ---------------------------------------------------------------- golem
gn, go = ent(NEW, "iron_golem"), ent(OLD, "iron_golem")
pre = gn["scripts"]["pre_animation"]
first_w = next(i for i, s in enumerate(pre) if s.lstrip().startswith("v.pw_ig_body_top_rz ="))
first_r = next(i for i, s in enumerate(pre) if "v.pw_ig_body_top_rz" in s.split("=", 1)[1])
err_new, err_old = strict_run(gn, {}), strict_run(go, {})
check("G1 golem: body_top.rz seeded before its first read; the whole script runs strict (1.4.30 stops at statement 70)",
      first_w < first_r and err_new is None and err_old is not None and err_old.startswith("statement 70"), f"write {first_w} read {first_r}; new {err_new}; old {err_old}")
anim_g = R.jl(NEW / "animations/pw_iron_golem_jem.animation.json")["animations"][BR.anim_id("iron_golem")]
_, geo_g = R.geo_file(NEW, "geometry.pw_iron_golem")
r16b.bake("iron_golem")
w2 = r16b.n2("iron_golem", gn["scripts"]["initialize"], pre, anim_g)
w3, per = r16b.n3("iron_golem", geo_g["bones"], gn["scripts"]["initialize"], pre, anim_g)
check("G2 golem N2 strict (Molang == JEM) + N3 (posed shipped geometry == JEM at the pose)",
      w2["rotation"] <= 0.01 and w2["position"] <= 1e-3 and w2["scale"] <= 1e-3 and w3 <= 0.01, f"N2 {({k: round(v, 5) for k, v in w2.items()})} N3 {w3:.4f} px / {len(per)} cases")

# ---------------------------------------------------------------- fox
_, gfo = R.geo_file(OLD, "geometry.pw_fox"); _, gfn = R.geo_file(NEW, "geometry.pw_fox")
by = {b["name"]: b for b in gfn["bones"]}; hb = by.get("held_item")
aff = WC.affines(gfn["bones"], {})
sn = np.array([p for _, _, P in WC.boxes(gfn["bones"], aff, {"snout"}) for p in P])
target = sn.min(0) + np.array([0.0, -0.7, -1.0])
A, t = aff["held_item"] if hb else (np.eye(3), np.zeros(3))
world = A @ np.array(hb["pivot"]) + t if hb else None
Wo = {(x[0], x[1]): np.array(x[2]) for x in world_boxes(gfo["bones"])}; Wn = {(x[0], x[1]): np.array(x[2]) for x in world_boxes(gfn["bones"])}
err = max(float(np.abs(Wo[k] - Wn[k]).max()) for k in Wo) if set(Wo) == set(Wn) else 99.0
check("F1 fox held_item under snout at Mojang's offset, level at rest; every other cube unchanged",
      hb is not None and hb.get("parent") == "snout" and not hb.get("cubes") and float(np.abs(world - target).max()) < 1e-3
      and float(np.abs(A - np.eye(3)).max()) < 1e-4 and err < 1e-6 and len(gfn["bones"]) == len(gfo["bones"]) + 1,
      f"world {np.round(world, 3).tolist() if world is not None else None} target {np.round(target, 3).tolist()}; other cubes max move {err:.1e}")
fx = ent(NEW, "fox"); anim_f = R.jl(NEW / "animations/pw_fox_jem.animation.json")["animations"][BR.anim_id("fox")]
r16b.bake("fox")
w2 = r16b.n2("fox", fx["scripts"]["initialize"], fx["scripts"]["pre_animation"], anim_f)
w3, per = r16b.n3("fox", gfn["bones"], fx["scripts"]["initialize"], fx["scripts"]["pre_animation"], anim_f)
check("F2 fox N2 strict + N3 (settled sit == FreshLX exactly)", w2["rotation"] <= 0.01 and w2["position"] <= 1e-3 and w2["scale"] <= 1e-3 and w3 <= 0.01,
      f"N2 {({k: round(v, 5) for k, v in w2.items()})} N3 {w3:.4f} px / {len(per)} cases")
# F3: the ramp and a mid-blend pose
env = {"q.is_sitting": 1.0, "q.is_stalking": 0.0, "q.is_sleeping": 0.0, "q.delta_time": 0.05, "q.is_on_ground": 1.0, "q.life_time": 2.0}
amts = []
for _ in range(6):
    ME.run(fx["scripts"]["pre_animation"][0], env); amts.append(round(env["v.pw_fx_sit_amt"], 3))
def body_rx(amt):
    e = {"q.is_sitting": 1.0, "q.is_stalking": 0.0, "q.is_sleeping": 0.0, "v.pw_fx_sit_amt": amt, "q.delta_time": 0.0}
    st = next(s for s in fx["scripts"]["pre_animation"] if s.startswith("v.pw_fx_body_rx ="))
    return ME.run(st, e)
r0, r5, r1 = body_rx(0.0), body_rx(0.5), body_rx(1.0)
check("F3 sit settle: 0 -> 1 in 5 frames (0.25 s); a half-way body pose lies between standing and sitting",
      amts[4] == 1.0 and amts[3] < 1.0 and min(r0, r1) < r5 < max(r0, r1), f"ramp {amts}; body rx stand {r0:.3f} half {r5:.3f} sat {r1:.3f}")
rot = anim_f["bones"]["pw_render"]["rotation"][0]
def pitch(e):
    e = {"q.is_on_ground": 1.0, "q.is_interested": 0.0, "q.is_stalking": 0.0, "q.is_stunned": 0.0, "q.vertical_speed": 0.0, **e}
    ME.run(next(s for s in fx["scripts"]["pre_animation"] if s.startswith("v.pw_fx_pounce_on =")), e)
    return ME.run(rot, e)
cs = {"ground": pitch({"q.vertical_speed": 3.0}), "leap": pitch({"q.is_on_ground": 0.0, "q.is_interested": 1.0, "q.vertical_speed": 4.0}),
      "drop": pitch({"q.is_on_ground": 0.0, "v.pw_fx_pounce_on": 1.0, "q.vertical_speed": -5.0}), "plain jump": pitch({"q.is_on_ground": 0.0, "q.vertical_speed": 4.0}),
      "stuck": pitch({"q.is_stunned": 1.0})}
check("F4 pounce pitch unchanged (0 ground / plain jump, nose up leap, down drop, 60 stuck)",
      cs["ground"] == 0 and cs["plain jump"] == 0 and cs["leap"] < 0 < cs["drop"] and cs["stuck"] == 60.0, str({k: round(v, 2) for k, v in cs.items()}))

# ---------------------------------------------------------------- standing lints
import molang_nwr_lint, molang_rbw_lint, anim_resolve_lint
n_nw, f_nw = molang_nwr_lint.lint_pack(NEW)
check("S NWR no read of a variable nothing in the pack writes (standing, new)", not f_nw, f"{n_nw} entities; {[(x[0], x[1]) for x in f_nw][:4]}")
n_ml, e_ml = ML.lint_pack(NEW)
check("S Molang grammar (standing)", not e_ml, f"{n_ml} strings, {len(e_ml)} errors")
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

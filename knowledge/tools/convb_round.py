#!/usr/bin/env python3
"""convb_round.py — one Converter B round as a reusable build + gate (generalised from build/verify_rp07_1416.py, D-C274).

CONFIG (dict):
  src, dst       build dirs (dst is rebuilt from src)
  version        "1.4.17" — manifest header + modules; uuids kept
  name, desc     manifest header name / description
  pre            [hook(dst)] run after the copy, before the jobs (D-C283: a mob converted for the first time needs its entity /
                 a placeholder geometry in the pack first)
  jobs           [(label, stem, gkey, jname, tkey)] — the geometry each entity binds is rebuilt from the Patrix JEM
                 (convb_build.build_mob: bake + vanilla-part pivots + bind + split + Java parents + legs + frame bones)
  look           {stem: old look animation id} — replaced by animation.pw_convb.look (additive head look)
  look_file      animation file to write when missing (the look animation), or None when the pack already has it
  unbound_ok     {label: {bone names allowed to be missing}}
  placement      {label: ("ground",) | ("centre", y, z)} — gate C
Gate lines: A diff · J strict JSON · K manifest · B cubes == bake (legs: sizes/UVs) · L texture size / paths · C placement ·
D joints (0-thickness cards count as touching) · E binds · F part_visibility owns cubes · G frames · H look axis · I look binding."""
import hashlib, json, math, re, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
from convb_build import build_mob, _angle
from convb_preview import library, bind_info
from convb import bake, CEM
from jem_convert import load_json
from verify_rp07_1415_rp06_1410 import world_boxes, inside_frac
from equine_compare import bone_affines

ROOT = Path("/home/claude")
LOOK_ID = "animation.pw_convb.look"
LOOK_DOC = {"format_version": "1.8.0", "animations": {LOOK_ID: {"loop": True, "bones": {
    "head": {"rotation": ["query.target_x_rotation", "query.target_y_rotation", 0.0]}}}}}


def jl(p):
    t = re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", t))


ARS_BASELINE = Path("/home/claude/_docs/convb/ars_baseline.json")   # {pack tag: ["entity file | message", ...]}


def wj(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(d, indent=1), encoding="utf-8")


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD {m}\n")


def geo_file(dst, ident):
    for p in sorted((dst / "models/entity").glob("*.json")):
        d = jl(p)
        ids = [g["description"]["identifier"] for g in d.get("minecraft:geometry", [])]
        if ident in ids:
            assert ids == [ident], (p.name, ids)
            return p, d["minecraft:geometry"][0]
    raise FileNotFoundError(ident)


def moving_bones(desc, anims):
    out = set()
    for short, aid in (desc.get("animations") or {}).items():
        a = anims.get(aid)
        if not isinstance(a, dict): continue
        for bn, bv in (a.get("bones") or {}).items():
            if isinstance(bv, dict) and ({"rotation", "position"} & set(bv)): out.add(bn)
    return out - {"placeholder_bone"}


VB_KEYS = ("visible_bounds_width", "visible_bounds_height", "visible_bounds_offset")
VAN_RP = ROOT / "_intake/bedrock-samples/resource_pack"
VB_MARGIN = 0.5                     # blocks added on every side of the rest extent (limbs / wings / rods move)


def van_box(stem, gkey):
    """L-VISBOUNDS (D-C301): Mojang's own culling box for <stem>.entity.json's geometry[gkey] as (lo_y, hi_y, width) in blocks, or
    None (no vanilla entity / geometry, or Mojang set no offset). Mojang's box already covers Mojang's animation range."""
    pe = VAN_RP / f"entity/{stem}.entity.json"
    if not pe.exists(): return None
    try: geo = jl(pe)["minecraft:client_entity"]["description"].get("geometry") or {}
    except Exception: return None
    gid = geo.get(gkey) or geo.get("default")
    if not isinstance(gid, str): return None
    for q in (VAN_RP / "models/entity").rglob("*.json"):
        t = q.read_text(encoding="utf-8-sig")
        if gid not in t: continue
        d = jl(q)
        cands = [g["description"] for g in d.get("minecraft:geometry", []) or [] if g.get("description", {}).get("identifier") == gid]
        cands += [g for k, g in d.items() if isinstance(g, dict) and k.split(":")[0] == gid]
        for c in cands:
            w, h, o = c.get("visible_bounds_width"), c.get("visible_bounds_height"), c.get("visible_bounds_offset")
            if w and h and o is not None: return (float(o[1]) - float(h) / 2.0, float(o[1]) + float(h) / 2.0, float(w))
    return None


def bounds(desc, bones, van=None):
    """L-VISBOUNDS (D-C301): Bedrock's culling box is CENTRED on visible_bounds_offset (width in x and z, height in y). Converter B
    used to write width / height with NO offset (box centred at the feet: the upper half of a tall mob could be culled when its
    feet leave the screen). Now: the rest extent of the model + VB_MARGIN on every side, united with Mojang's own box for the mob
    (van = (lo, hi, width) from van_box), offset at the centre. Any old bounds in desc are dropped (they were the broken kind)."""
    P = np.array([p for x in world_boxes(bones) for p in x[2]]) / 16.0
    lo, hi = float(P[:, 1].min()) - VB_MARGIN, float(P[:, 1].max()) + VB_MARGIN
    w = 2.0 * (float(max(np.abs(P[:, 0]).max(), np.abs(P[:, 2]).max())) + VB_MARGIN)
    if van: lo, hi, w = min(lo, van[0]), max(hi, van[1]), max(w, van[2])
    d = {k: v for k, v in desc.items() if k != "identifier" and k not in VB_KEYS}
    off = round((lo + hi) / 2.0, 2)                                  # rounded OUTWARD: the box never shrinks below the need (D-C303)
    d["visible_bounds_width"] = math.ceil(w * 100.0 - 1e-9) / 100.0
    d["visible_bounds_height"] = math.ceil(2.0 * max(hi - off, off - lo) * 100.0 - 1e-9) / 100.0
    d["visible_bounds_offset"] = [0.0, off, 0.0]
    return d


def rebound(dst, done):
    """after the post hooks (which may move or add bones: blaze MODEL_OFFSET, creaking upperBody, sniffer pivot): recompute every
    job geometry's culling box from its FINAL bones (+ Mojang's box). done = [(label, stem, gkey, ident)]"""
    out = {}
    for label, stem, gkey, ident in done:
        p, g = geo_file(dst, ident); d = jl(p)
        van = van_box(stem, gkey)
        for gg in d["minecraft:geometry"]:
            if gg["description"]["identifier"] == ident:
                gg["description"] = {"identifier": ident, **bounds(gg["description"], gg["bones"], van)}
                out[label] = {k: gg["description"][k] for k in VB_KEYS} | {"mojang_box": van}
        wj(p, d)
    return out


def build_one(jname, stem, bind_names, moving, old_bones, look):
    import convb_build as cb
    orig = cb.align_frames
    cb.align_frames = lambda bones, animated, look=(): orig(bones, set(moving), look=look)
    try:
        return cb.build_mob(jname, stem, bind_names, old_bones, look_bones=look)
    finally:
        cb.align_frames = orig


def build(cfg):
    src, dst = cfg["src"], cfg["dst"]
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for hook in cfg.get("pre", []):                               # D-C283: set-up before the jobs (new entity / placeholder geometry)
        log(f"{dst.name}: pre {hook.__name__}: {hook(dst)}")
    report = {}; done = []
    for label, stem, gkey, jname, tkey in cfg["jobs"]:
        epack = cfg.get("entity_src", {}).get(stem, dst)          # the entity may live in another pack (ravager: RP-06)
        anims, rcs = library(epack)
        ent = jl(epack / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        ident = ent["geometry"][gkey]; p, g = geo_file(dst, ident)
        names, rel, _ = bind_info(ent, anims, rcs)
        look = ["head"] if stem in cfg["look"] else []
        moving = (moving_bones(ent, anims) | set(look)) - set(cfg.get("frame_exempt", {}).get(label, ()))
        bones, tw, th, info = build_one(jname, stem, names, moving, g["bones"], look)
        desc = {"identifier": ident, **bounds(g["description"], bones, van_box(stem, gkey)), "texture_width": tw, "texture_height": th}
        done.append((label, stem, gkey, ident))
        wj(p, {"format_version": "1.16.0", "minecraft:geometry": [{"description": desc, "bones": bones}]})
        report[label] = {"identifier": ident, "file": p.name, "stem": stem, "bones": len(bones), "cubes": sum(len(b.get("cubes", [])) for b in bones),
                         "mapping": {k: v for k, v in info["mapping"].items() if k != v}, "unbound": info["missing"], "frames": info["frames"],
                         "frame_err": info["frame_err"], "reparent_err": info.get("reparent_err", 0.0), "pivot_shift": info["pivot_shift"], "texture": [tw, th]}
        log(f"{dst.name}: {ident} <- Patrix {jname}.jem (Converter B; {len(bones)} bones, {report[label]['cubes']} cubes; pivot shift {info['pivot_shift']}; "
            f"frames {sorted(info['frames'])}; unbound {info['missing']})")
    for hook in cfg.get("post", []):                              # extra file work (e.g. trader llama decor), logged by the hook
        log(f"{dst.name}: post {hook.__name__}: {hook(dst)}")
    vb = rebound(dst, done)                                        # D-C301: culling boxes from the final bones
    for label, v in vb.items(): report.setdefault(label, {})["visible_bounds"] = v
    log(f"{dst.name}: visible bounds (centred offset, final bones + Mojang's box): " + "; ".join(f"{k} h {v['visible_bounds_height']} @ y {v['visible_bounds_offset'][1]}" for k, v in vb.items()))
    if cfg["look"]:
        lf = dst / "animations/pw_convb_look.animation.json"
        if not lf.exists(): wj(lf, LOOK_DOC)
        for stem, old_id in cfg["look"].items():
            pe = dst / f"entity/{stem}.entity.json"; d = jl(pe); desc = d["minecraft:client_entity"]["description"]
            assert desc["animations"].get("look_at_target") == old_id, (stem, desc["animations"].get("look_at_target"))
            desc["animations"]["look_at_target"] = LOOK_ID; wj(pe, d)
        log(f"{dst.name}: look_at_target -> {LOOK_ID} on {sorted(cfg['look'])}")
    mp = dst / "manifest.json"; m = jl(mp); v = [int(x) for x in cfg["version"].split(".")]
    m["header"]["version"] = v
    for mod in m.get("modules", []): mod["version"] = v
    m["header"]["name"] = cfg["name"]; m["header"]["description"] = cfg["desc"]
    wj(mp, m)
    json.dump(report, open(cfg["report"], "w"), indent=1)
    log(f"{dst.name}: manifest {cfg['version']}; report {cfg['report']}")
    return report


# ---------------------------------------------------------------------------------------------------------------- gate
def _touch(a, b):
    """contact test that also works for 0-thickness cards (inflate the degenerate axis by 0.05 px for the test)."""
    def fat(pts):
        P = np.array(pts); o = P[0]; ax = [P[4] - o, P[2] - o, P[1] - o]
        out = [o.copy()]
        for i, v in enumerate(ax):
            if np.linalg.norm(v) < 1e-6:
                n = np.cross(ax[(i + 1) % 3], ax[(i + 2) % 3]); n = n / (np.linalg.norm(n) or 1) * 0.05
                o = o - n; ax[i] = 2 * n
        o0 = o
        return [o0 + ax[0] * i + ax[1] * j + ax[2] * k for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    A, B = fat(a), fat(b)
    return inside_frac(A, B) or inside_frac(B, A)


def verify(cfg):
    fails = []; n = [0]
    def check(tag, ok, msg):
        n[0] += 1; print(("PASS " if ok else "FAIL ") + tag + " — " + msg)
        if not ok: fails.append(tag)
    md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
    OLD, NEW = cfg["src"], cfg["dst"]; rep = json.load(open(cfg["report"]))
    fo = {str(p.relative_to(OLD)): p for p in OLD.rglob("*") if p.is_file()}; fn = {str(p.relative_to(NEW)): p for p in NEW.rglob("*") if p.is_file()}
    changed = sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])); added = sorted(set(fn) - set(fo)); removed = sorted(set(fo) - set(fn))
    # D-C284: a geometry file NEW this round is in the added set, not the changed one; a look entity that already ran the look
    # animation before this round is not rewritten
    look_changed = {f"entity/{s}.entity.json" for s in cfg["look"]
                    if not (OLD / f"entity/{s}.entity.json").exists()
                    or jl(OLD / f"entity/{s}.entity.json")["minecraft:client_entity"]["description"]["animations"].get("look_at_target") != LOOK_ID}
    expected = (({f"models/entity/{r['file']}" for r in rep.values()} | look_changed | {"manifest.json"}
                 | set(cfg.get("extra_changed", []))) - set(added))
    exp_added = [] if (OLD / "animations/pw_convb_look.animation.json").exists() or not cfg["look"] else ["animations/pw_convb_look.animation.json"]
    exp_added = sorted(exp_added + list(cfg.get("extra_added", [])))
    check("A1 changed set", set(changed) == expected, f"{len(changed)} changed; unexpected {sorted(set(changed) - expected)}; missing {sorted(expected - set(changed))}")
    exp_removed = sorted(cfg.get("extra_removed", []))
    check("A2 added / removed", added == exp_added and removed == exp_removed, f"added {added} removed {removed} (expected removed {exp_removed})")
    bad = []; js = [k for k in changed + added if k.endswith(".json")]
    for k in js:
        try: json.loads(fn[k].read_text(encoding="utf-8"), parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
        except Exception as e: bad.append(f"{k}: {e}")
    check("J strict JSON", not bad, f"{len(js)} json files; {bad[:3]}")
    pngs = [k for k in changed if k.endswith(".png") and k not in set(cfg.get("png_checked_elsewhere", ()))]   # D-C299: whole-sheet swaps have their own pixel gates
    if pngs:   # changed textures: same size/mode; changed pixels only inside the allowed texel boxes
        from PIL import Image
        out = []
        for k in pngs:
            a, b = Image.open(fo[k]), Image.open(fn[k])
            A = np.asarray(a.convert("RGBA")).astype(int); Bn = np.asarray(b.convert("RGBA")).astype(int)
            ok = a.size == b.size
            diff = np.abs(A - Bn).sum(-1) > 0 if ok else None
            if ok:
                s_ = a.size[0] // cfg.get("png_texels", (128, 64))[0]; allow = np.zeros_like(diff)
                for u0, v0, u1, v1 in cfg.get("png_allowed", []): allow[v0 * s_:v1 * s_, u0 * s_:u1 * s_] = True
                ok = not (diff & ~allow).any()
            out.append(f"{k.split('/')[-1]} {int(diff.sum()) if diff is not None else '?'} px")
            if not ok: bad.append(k)
        check("T textures", not bad, f"{len(pngs)} changed; {out}; outside allowed boxes: {bad}")
    mo, mn = jl(OLD / "manifest.json"), jl(NEW / "manifest.json"); v = [int(x) for x in cfg["version"].split(".")]
    check("K manifest", mn["header"]["version"] == v and all(m["version"] == v for m in mn["modules"]) and mn["header"]["uuid"] == mo["header"]["uuid"]
          and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]], f"version {mn['header']['version']} uuid kept {mn['header']['uuid'] == mo['header']['uuid']}")
    for label, stem, gkey, jname, tkey in cfg["jobs"]:
        epack = cfg.get("entity_src", {}).get(stem)
        anims, rcs = library(epack or NEW)
        en = jl((epack or NEW) / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        eo_path = (epack or OLD) / f"entity/{stem}.entity.json"          # D-C284: an entity NEW in this round has no old file
        eo = jl(eo_path)["minecraft:client_entity"]["description"] if eo_path.exists() else en
        ident = en["geometry"][gkey]; _, g = geo_file(NEW, ident); bones = g["bones"]; by = {b["name"]: b for b in bones}
        tag = label.replace(" ", "_")
        # VB (D-C301, L-VISBOUNDS standing gate): the culling box has an offset, is centred on the model and holds its whole rest
        # extent (+ margin) and Mojang's own box for the mob
        d_ = g["description"]; P_ = np.array([q for x in world_boxes(bones) for q in x[2]]) / 16.0; vbx = van_box(stem, gkey)
        o_ = d_.get("visible_bounds_offset"); h_ = float(d_.get("visible_bounds_height", 0)); w_ = float(d_.get("visible_bounds_width", 0))
        lo_, hi_ = (o_[1] - h_ / 2, o_[1] + h_ / 2) if o_ else (-h_ / 2, h_ / 2)
        ok_ = (o_ is not None and lo_ <= P_[:, 1].min() - 0.49 and hi_ >= P_[:, 1].max() + 0.49
               and w_ / 2 >= max(np.abs(P_[:, 0]).max(), np.abs(P_[:, 2]).max()) + 0.49
               and (not vbx or (lo_ <= vbx[0] + 1e-6 and hi_ >= vbx[1] - 1e-6 and w_ >= vbx[2] - 1e-6)))
        check(f"VB {tag} culling box: offset set, holds the model (y {P_[:, 1].min():.2f}..{P_[:, 1].max():.2f}) + 0.5 and Mojang's box", ok_,
              f"box y {lo_:.2f}..{hi_:.2f} w {w_:.2f} offset {o_}; Mojang {vbx}")
        # B — every non-leg cube equals the bake (after the documented whole-model offset)
        import convb_build as cb
        bk, tw, th, _ = bake(jname)
        off = np.array(cb.MODEL_OFFSET.get(stem, [0, 0, 0]), float)
        legs = {b["name"] for b in bones if re.fullmatch(r"leg\d(_pose)?", b["name"])}
        legsub = set()
        for L in legs: legsub |= set(cb._subtree(bones, L))
        A = {}; Bk = {}
        for x in world_boxes(bones):
            if x[0] not in legsub: A.setdefault((tuple(x[3]), x[5]), []).append(np.array(x[2]))
        for x in world_boxes(bk): Bk.setdefault((tuple(x[3]), x[5]), []).append(np.array(x[2]) + off)
        errs, miss = [], []
        for k, lst in A.items():
            if k not in Bk: miss.append(k); continue
            for arr in lst: errs.append(min(float(np.abs(arr - q).max()) for q in Bk[k]))
        nb = sum(len(v) for v in Bk.values()); nn = sum(len(b.get("cubes", [])) for b in bones)
        check(f"B {tag} cubes == bake", not miss and (max(errs) if errs else 0) < 0.02 and nb == nn,
              f"{nn} cubes (bake {nb}); max corner error {max(errs) if errs else 0:.4f} px; unmatched {len(miss)}; leg-subtree cubes excluded {sum(len(by[b].get('cubes', [])) for b in legsub)}")
        jem = load_json(CEM / f"{jname}.jem"); ts = jem.get("textureSize") or [64, 32]
        tex_ok = en["textures"] == eo["textures"] or cfg.get("textures_changed", {}).get(stem) == en["textures"]
        check(f"L {tag} texture", [g["description"]["texture_width"], g["description"]["texture_height"]] == list(ts) and tex_ok,
              f"geometry {g['description']['texture_width']}x{g['description']['texture_height']} JEM {ts[0]}x{ts[1]}; entity textures "
              f"{'unchanged' if en['textures'] == eo['textures'] else 'changed as planned' if tex_ok else 'CHANGED UNPLANNED'}")
        P = np.array([q for x in world_boxes(bones) for q in x[2]]); lo, hi = P.min(0), P.max(0); c = (lo + hi) / 2
        pl = cfg["placement"][label]
        if pl[0] == "old":   # D-C277: reference = the shipped (OLD) geometry's box centre, within 6 px
            _, og = geo_file(OLD, ident); Po = np.array([q for x in world_boxes(og["bones"]) for q in x[2]]); co = (Po.min(0) + Po.max(0)) / 2
            check(f"C {tag} placement vs shipped", abs(c[1] - co[1]) <= 6 and abs(c[2] - co[2]) <= 6 and abs(c[0] - co[0]) <= 3,
                  f"centre {np.round(c, 1).tolist()} vs shipped {np.round(co, 1).tolist()} (y {lo[1]:.1f}..{hi[1]:.1f})")
        elif pl[0] == "ground":
            gb = cfg.get("ground_bones", {}).get(label)       # D-C299: the parts that stand (feet), when a tail / wing tip droops lower by design
            glo = np.array([q for x in world_boxes(bones) if x[0] in gb for q in x[2]]).min(0) if gb else lo
            gt = cfg.get("ground_tol", {}).get(label, (-1.0, None))       # D-C314: a documented design sink (FreshLX's hoglin idle toe), reason recorded
            check(f"C {tag} on the ground", gt[0] <= glo[1] <= 0.5, f"min y {glo[1]:.2f}" + (f" of {gb}" if gb else "") + f" (y {lo[1]:.1f}..{hi[1]:.1f}, z {lo[2]:.1f}..{hi[2]:.1f})"
                  + (f" — allowed to {gt[0]}: {gt[1]}" if gt[1] else ""))
        else: check(f"C {tag} placement", abs(c[1] - pl[1]) <= 6 and abs(c[2] - pl[2]) <= 6, f"centre y {c[1]:.1f} z {c[2]:.1f} vs reference y {pl[1]} z {pl[2]}")
        W = {}
        for x in world_boxes(bones): W.setdefault(x[0], []).append(x[2])
        floating = [nm for nm, bx in W.items() if not any(_touch(a, q) for a in bx for m2, bs in W.items() if m2 != nm for q in bs)]
        jok = cfg.get("joints_ok", {}).get(label)          # D-C299: parts that float free BY DESIGN (blaze rods), reason recorded
        check(f"D {tag} joints", not floating or len(W) == 1 or bool(jok), f"{len(W)} bones with boxes; floating {floating}" + (f" — by design: {jok}" if jok and floating else ""))
        names, rel, _ = bind_info(en, anims, rcs)
        low = {k.lower() for k in by}
        missing = sorted(nm for nm in names - {"placeholder_bone"} if nm.lower() not in low)   # Bedrock bone names: case-insensitive
        ok_missing = cfg["unbound_ok"].get(label, set())
        check(f"E {tag} binds", set(missing) <= ok_missing, f"{len(names)} names; missing {missing} (allowed {sorted(ok_missing)})")
        pv = set()
        for rc in en.get("render_controllers", []):
            k = rc if isinstance(rc, str) else list(rc)[0]
            for pp in (rcs.get(k, {}).get("part_visibility") or []): pv |= {x for x in pp if x != "*"}
        empty = sorted(x for x in pv if x in by and not by[x].get("cubes"))
        check(f"F {tag} part_visibility owns cubes", not empty, f"pv bones {sorted(pv)}; empty {empty}")
        # frame_exempt: bones whose animation is DESIGNED in their rotated parent's frame (guardian spike slide along its own axis;
        # proven by that round's own gate line) — the entity-frame rule does not apply to them
        aff = bone_affines(bones); moving = moving_bones(en, anims) - set(cfg.get("frame_exempt", {}).get(label, ()))
        worst = max([(_angle(aff[by[nm]["parent"]][0]), nm) for nm in moving if nm in by and by[nm].get("parent")], default=(0.0, "-"))
        lookp = _angle(aff[by["head"]["parent"]][0]) if stem in cfg["look"] and by.get("head", {}).get("parent") else 0.0
        check(f"G {tag} frames", worst[0] <= 45.0 and lookp <= 5.0, f"worst moved-bone parent frame {worst[0]:.1f} deg ({worst[1]}); look parent {lookp:.1f} deg")
        if stem in cfg["look"]:
            a0 = bone_affines(bones)["head"][0]; a1 = bone_affines(bones, add_rot={"head": [0, 30, 0]})["head"][0]
            Rw = a1 @ a0.T; w, vv = np.linalg.eig(Rw); ax = np.real(vv[:, np.argmin(np.abs(w - 1))]); tilt = math.degrees(math.acos(min(1, abs(ax[1]) / np.linalg.norm(ax))))
            check(f"H {tag} look axis", tilt <= 5.0 and abs(_angle(Rw) - 30) < 1.0, f"yaw axis {tilt:.2f} deg from vertical, turn {_angle(Rw):.1f} deg")
            la = en["animations"].get("look_at_target"); relb = [b for b, vv2 in (anims.get(la, {}).get("bones") or {}).items() if isinstance(vv2, dict) and vv2.get("relative_to")]
            check(f"I {tag} look", la == LOOK_ID and not relb and "head" in (anims.get(la, {}).get("bones") or {}), f"look_at_target -> {la}; relative_to bones {relb}")
    for hook in cfg.get("verify_hooks", []): hook(cfg, check)
    import molang_lint                                   # D-C281 standing gate (his 10:31 "ABSOLUTELY"): every build parses its Molang
    n_ml, e_ml = molang_lint.lint_pack(NEW)
    check("MLS every Molang string parses with Bedrock's grammar (standing gate)", not e_ml,
          f"{n_ml} strings, {len(e_ml)} errors {[(e[0], e[1], e[3]) for e in e_ml[:3]]}")
    # D-C284 standing gate (his 12:46 "Yes"): every animation / controller an entity names must resolve (pack > stack > vanilla).
    # cfg["ars_stack"] = the other mob packs that load with this one; known pre-existing findings live in ARS_BASELINE (a NEW
    # finding fails the gate; a baseline entry that disappears is reported so the baseline can shrink).
    import anim_resolve_lint
    n_ar, e_ar = anim_resolve_lint.lint_pack(NEW, stack=tuple(cfg.get("ars_stack", ())))
    base = set(json.load(open(ARS_BASELINE)).get(cfg.get("ars_tag", NEW.name), [])) if ARS_BASELINE.exists() else set()
    found = {f"{e[0]} | {e[2]}" for e in e_ar}
    new_f = sorted(found - base); gone = sorted(base - found)
    check("ARS every animation an entity plays exists (standing gate)", not new_f,
          f"{n_ar} entities, {len(found)} findings ({len(found & base)} known baseline); NEW {new_f[:3]}; fixed since baseline {len(gone)}")
    # D-C285 standing gates (his R8 log + shots): a render controller must not hide every cube of the geometry it draws (the
    # silverfish: vanilla default-hide RC over the Patrix bones), and no client-entity section its format_version does not allow
    # (the enderman: scripts.animate / initialize in a 1.8.0 file). Stack for RC resolution = cfg["ars_stack"], then vanilla.
    import rc_visibility_lint, entity_schema_lint
    n_rc, f_rc = rc_visibility_lint.lint_pack(NEW, tuple(cfg.get("ars_stack", ())))
    check("RCV every render controller leaves the geometry it draws visible (standing gate)", not f_rc,
          f"{n_rc} entities; all-hidden {[(x[0], x[2]) for x in f_rc][:3]}")
    n_fm, e_fm, i_fm = entity_schema_lint.lint_pack(NEW)
    check("FMT no client-entity section its format_version rejects (standing gate)", not e_fm,
          f"{n_fm} entities; errors {e_fm[:3]}; info {len(i_fm)}")
    # D-C286 standing gate (his R9 c03 + 10 'unknown variable' errors): no pre_animation read before its first write unless ??-guarded;
    # known benign findings (a read only inside an already-written lazy branch) live in _docs/convb/rbw_baseline.json
    import molang_rbw_lint
    n_rb, f_rb = molang_rbw_lint.lint_pack(NEW)
    rb_base = set(json.load(open(ROOT / "_docs/convb/rbw_baseline.json")).get(cfg.get("ars_tag", NEW.name), []))
    rb_new = sorted({f"{x[0]} | {x[2]}" for x in f_rb} - rb_base)
    check("RBW no pre_animation variable read before its first write (standing gate)", not rb_new,
          f"{n_rb} entities; {len(f_rb)} findings ({len({f'{x[0]} | {x[2]}' for x in f_rb} & rb_base)} baseline); NEW {rb_new[:4]}")
    # D-C317 standing gate (his R17 i01/i02, golem legs pivoting on the ground): no unguarded read of a variable NOTHING in the
    # pack writes (engine variables = Mojang's own read-but-never-written list); the game stops the whole script at such a read
    import molang_nwr_lint
    n_nw, f_nw = molang_nwr_lint.lint_pack(NEW)
    check("NWR no read of a variable nothing in the pack writes (standing gate)", not f_nw,
          f"{n_nw} entities; {[(x[0], x[1]) for x in f_nw][:4]}")
    # D-C288 standing gate (his R10 d02 'the bogged has no bow'): every client entity whose vanilla counterpart enables attachables
    # must enable them too, or bows / crossbows / wolf armor are silently never drawn
    import attachables_lint
    n_at, f_at = attachables_lint.lint_pack(NEW)
    check("ATT every entity whose vanilla counterpart enables attachables enables them too (standing gate)", not f_at,
          f"{n_at} entities; missing {f_at[:6]}")
    if cfg.get("prec_order"):                            # D-C284 standing gate: our client entities must WIN in his stack order
        import entity_precedence
        rows = entity_precedence.census(cfg["prec_order"])
        lose = [f"{r['id']} -> {r['winner']}" for r in rows if r["ours_lose"]]
        check("PREC every client entity of ours wins against the packs above it (min_engine_version, then pack order)", not lose,
              f"{len(rows)} shared identifiers; ours lose: {lose[:4]}")
    total = n[0]
    print(f"\n{'GATE OPEN' if not fails else 'GATE CLOSED'} {total - len(fails)}/{total}" + (f"  FAILS: {fails}" if fails else ""))
    return 0 if not fails else 1

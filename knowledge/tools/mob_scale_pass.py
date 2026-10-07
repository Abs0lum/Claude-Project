#!/usr/bin/env python3
"""mob_scale_pass.py — phase G (his 22:50 ruling D-C543): the scale and damage pass over BP-02's entity files.

Rules (ASSUMPTIONS for witness, shown to him as the before/after table before anything ships):
  G1 GIANTS: every pw:giant_* becomes 2.5 x its base mob's effective height (collision box height x scale; the scale
     ratio alone when a box height is 0). Every scale value in the giant's file is multiplied by the same factor, so
     baby/adult variants keep their proportions; shells and everything in the model scale with it (one model).
     Base lookup: pw:<rest>, then sf_nba:<rest without _nba>, then pw:<rest without the pack suffix>; unmapped giants are
     listed and left alone. Giant damage = the base's damage + 2.
  G2 SMALL HOSTILES: a hostile mob (family monster, or a nearest-attackable-target goal) SMALLER THAN THE PLAYER — its
     effective collision volume (width^2 x height x scale^3) below the player's 0.6 x 0.6 x 1.8 = 0.648 — hits for at most
     2 and attacks half as often (melee / delayed / box attack cooldown doubled; the engine's default cooldown is 1 s).
  Mobs the player's size or larger are not touched. Only files of this pack change (vanilla mobs it does not override
  keep vanilla values).
Usage: mob_scale_pass.py ENTITIES_DIR REPORT.json [REPORT.md]"""
import json
import sys
from pathlib import Path

PLAYER_VOL = 0.6 * 0.6 * 1.8
GIANT_X = 2.5


def walk(o, fn, path=()):
    if isinstance(o, dict):
        fn(o, path)
        for k, v in o.items():
            walk(v, fn, path + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, fn, path + (i,))


def info(d):
    e = d.get("minecraft:entity")
    if not e:
        return None
    comps = e.get("components", {})
    fam = comps.get("minecraft:type_family", {}).get("family", [])
    scales, attacks, nat = [], [], False
    def fn(o, path):
        nonlocal nat
        s = o.get("minecraft:scale")
        if isinstance(s, dict) and isinstance(s.get("value"), (int, float)):
            scales.append(s["value"])
        a = o.get("minecraft:attack")
        if isinstance(a, dict) and "damage" in a:
            attacks.append(a["damage"])
        if "minecraft:behavior.nearest_attackable_target" in o:
            nat = True
    walk(e, fn)
    cb = comps.get("minecraft:collision_box", {}) or {}
    w, h = cb.get("width") or 0, cb.get("height") or 0
    s = max(scales) if scales else 1.0
    return {"id": e["description"]["identifier"], "fam": fam, "hostile": "monster" in fam or nat, "scale": s, "w": w, "h": h,
            "eff_h": h * s if h else None, "vol": (w * w * h * s ** 3) if (w and h) else None, "attacks": attacks}


def dmax(dm):
    if isinstance(dm, dict):
        return dm.get("range_max", dm.get("range_min", 0))
    if isinstance(dm, list):
        return max(dm) if dm else 0
    return dm or 0


def set_damage(e, fn_new):
    def fn(o, path):
        a = o.get("minecraft:attack")
        if isinstance(a, dict) and "damage" in a:
            a["damage"] = fn_new(a["damage"])
    walk(e, fn)


def cap_damage(dm, cap):
    if isinstance(dm, dict):
        out = dict(dm)
        if "range_max" in out:
            out["range_max"] = min(out["range_max"], cap)
        if "range_min" in out:
            out["range_min"] = min(out["range_min"], out.get("range_max", cap))
        return out
    if isinstance(dm, list):
        return [min(x, cap) for x in dm]
    return min(dm, cap)


def double_cooldowns(e):
    changed = []
    def fn(o, path):
        for k in ("minecraft:behavior.melee_attack", "minecraft:behavior.delayed_attack", "minecraft:behavior.melee_box_attack"):
            g = o.get(k)
            if isinstance(g, dict):
                before = g.get("cooldown_time", 1)
                g["cooldown_time"] = round(before * 2, 3)
                changed.append([k.split(".")[-1], before, g["cooldown_time"]])
    walk(e, fn)
    return changed


def scale_all(e, factor):
    def fn(o, path):
        s = o.get("minecraft:scale")
        if isinstance(s, dict) and isinstance(s.get("value"), (int, float)):
            s["value"] = round(s["value"] * factor, 4)
    walk(e, fn)


def main():
    root, rep_json = Path(sys.argv[1]), Path(sys.argv[2])
    rep_md = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    files = {}
    for p in sorted(root.rglob("*.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        i = info(d)
        if i:
            files[i["id"]] = (p, d, i)
    rows, unmapped = [], []
    # G1 giants
    for gid, (p, d, gi) in list(files.items()):
        if not gid.startswith("pw:giant_"):
            continue
        rest = gid[len("pw:giant_"):]
        cands = [f"pw:{rest}"]
        for suf in ("_nba", "_anf", "_wa", "_wwa", "_ysav", "_ytri", "_ifs", "_ws"):
            if rest.endswith(suf):
                cands += [f"sf_nba:{rest[:-len(suf)]}", f"pw:{rest[:-len(suf)]}"]
        base = next((files[c] for c in cands if c in files), None)
        if not base:
            unmapped.append(gid)
            continue
        bi = base[2]
        if gi["h"] and bi["h"]:
            target = GIANT_X * bi["h"] * bi["scale"] / gi["h"]
        else:
            target = GIANT_X * bi["scale"]
        factor = target / gi["scale"] if gi["scale"] else 1
        e = d["minecraft:entity"]
        scale_all(e, factor)
        bd = max([dmax(x) for x in bi["attacks"]] or [1])
        newd = bd + 2
        before_d = max([dmax(x) for x in gi["attacks"]] or [0])
        if gi["attacks"]:
            set_damage(e, lambda dm, nd=newd: ({**dm, "range_min": min(dm.get("range_min", nd), nd), "range_max": nd} if isinstance(dm, dict) else nd))
        p.write_text(json.dumps(d, indent=1))
        rows.append({"id": gid, "rule": "G1 giant", "base": bi["id"], "scale": [round(gi["scale"], 3), round(target, 3)],
                     "eff_h": [round(gi["eff_h"], 2) if gi["eff_h"] else None, round(target * gi["h"], 2) if gi["h"] else None],
                     "base_eff_h": round(bi["eff_h"], 2) if bi["eff_h"] else None, "damage": [before_d, newd if gi["attacks"] else before_d]})
    # G2 small hostiles (re-read the giants' new sizes: a giant can become small)
    for mid, (p, d, _) in files.items():
        i = info(d)
        if not i["hostile"] or i["vol"] is None or i["vol"] >= PLAYER_VOL:
            continue
        e = d["minecraft:entity"]
        before = max([dmax(x) for x in i["attacks"]] or [0])
        set_damage(e, lambda dm: cap_damage(dm, 2))
        cds = double_cooldowns(e)
        if not i["attacks"] and not cds:
            continue
        p.write_text(json.dumps(d, indent=1))
        row = next((r for r in rows if r["id"] == mid), None)
        entry = {"rule": "G2 small hostile", "vol": round(i["vol"], 3), "damage2": [before, min(before, 2)], "cooldowns": cds[:3]}
        if row:
            row.update(entry); row["rule"] = "G1 giant + G2 small"
        else:
            rows.append({"id": mid, **entry, "eff_h": [round(i["eff_h"], 2) if i["eff_h"] else None] * 2})
    out = {"player_volume": PLAYER_VOL, "giant_x": GIANT_X, "rows": rows, "unmapped_giants": unmapped,
           "counts": {"giants": sum(1 for r in rows if "G1" in r["rule"]), "small": sum(1 for r in rows if "G2" in r["rule"]), "unmapped": len(unmapped)}}
    rep_json.write_text(json.dumps(out, indent=1))
    if rep_md:
        lines = ["# Mob pass G (D-C543) — before / after", "", f"Player volume {PLAYER_VOL:.3f} m³; giants = {GIANT_X} × base height.", "",
                 "| mob | rule | base | scale | height | damage | cooldown |", "|---|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: (r["rule"], r["id"])):
            sc = f'{r["scale"][0]} → {r["scale"][1]}' if "scale" in r else ""
            eh = r.get("eff_h") or [None, None]
            ht = f'{eh[0]} → {eh[1]}' if eh[0] is not None else ""
            dm = r.get("damage") or r.get("damage2") or ["", ""]
            if "damage" in r and "damage2" in r:
                dm = [r["damage"][0], r["damage2"][1]]
            cd = "; ".join(f"{c[0]} {c[1]}→{c[2]} s" for c in r.get("cooldowns", []))
            lines.append(f'| {r["id"]} | {r["rule"]} | {r.get("base", "")} | {sc} | {ht} | {dm[0]} → {dm[1]} | {cd} |')
        if unmapped:
            lines += ["", "Giants without a base (unchanged): " + ", ".join(unmapped)]
        rep_md.write_text("\n".join(lines) + "\n")
    print(json.dumps(out["counts"]), "unmapped:", unmapped)


if __name__ == "__main__":
    main()

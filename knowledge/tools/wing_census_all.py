#!/usr/bin/env python3
"""wing_census_all.py — his 01:42 "Not ALL wings need correction, but check them all": every entity in RP-06 / RP-07 whose
geometry has a wing bone gets an automatic spec (flap animation = 'fly' / 'flying' / 'pw_jem' / first animation touching a
wing) and every join is measured with wing_contact: wing root <-> the bone it hangs from, and wing piece <-> wing piece.
Output: _docs/wings/WING-CENSUS-ALL.json + .md table."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import wing_contact as W

WING = re.compile(r"wing", re.I)
SKIP = {"minecraft:silverfish"}                                # 'wing1-3' are body segments, not wings


def auto_specs():
    specs = {}
    for pack in (W.RP06, W.RP07):
        lib = W.anim_library(pack)
        for f in sorted((pack / "entity").glob("*.json")):
            try: d = W.jl(f)["minecraft:client_entity"]["description"]
            except Exception: continue
            if d["identifier"] in SKIP: continue
            gid = (d.get("geometry") or {}).get("default") or next(iter((d.get("geometry") or {}).values()), None)
            if not gid: continue
            try: _, g = W.find_geo(pack, gid)
            except Exception: continue
            bones = g["bones"]; by = {b["name"]: b for b in bones}
            wings = [b["name"] for b in bones if WING.search(b["name"]) and any(x.get("cubes") for x in bones if x["name"] in W.subtree(bones, b["name"]))]
            if not wings: continue
            anims = d.get("animations", {})
            touch = [s for s, aid in anims.items() if isinstance(lib.get(aid), dict) and any(bn in wings for bn in lib[aid].get("bones", {}))]
            pick = [s for s in ("fly", "flying", "pw_jem") if s in touch] or touch[:1]
            if not pick: continue
            hinges = []
            for w in wings:
                if not by[w].get("cubes"): continue                      # group bones: their pieces are measured themselves
                anc = by[w].get("parent")
                while anc and not by[anc].get("cubes"): anc = by[anc].get("parent")   # nearest ancestor that draws something
                if not anc: continue
                if WING.search(anc): hinges.append((f"{anc} | {w}", anc, w))     # wing piece <-> wing piece (shared edge)
                else: hinges.append((f"{w} | on {anc}", anc, w))                 # wing root <-> the body part it hangs from
            if not hinges: continue
            key = f"{d['identifier'].split(':')[-1]}@{pack.name}"
            specs[key] = dict(pack=pack, stem=f.name.replace(".entity.json", ""), gid=gid,
                              states={"flap": ({"q.modified_move_speed": 0.4, "q.is_on_ground": 0.0}, pick)}, hinges=hinges)
    return specs


if __name__ == "__main__":
    specs = auto_specs()
    for manual in ("parrot", "phantom"):                           # cubes sit in unnamed sub-bones: the hand-made spec is right
        for k in [k for k in specs if k.split("@")[0] == manual]: specs.pop(k)
        specs[manual] = W.SPECS[manual]
    W.SPECS.update(specs)
    print(len(specs), "winged entities:", ", ".join(specs))
    res = W.census(list(specs))
    out = Path("/home/claude/_docs/wings"); out.mkdir(parents=True, exist_ok=True)
    json.dump({k: v for k, v in res.items()}, open(out / "WING-CENSUS-ALL.json", "w"), indent=1)
    lines = ["| mob | animation | join | result | worst edge px | median | bind-pose gap |", "|---|---|---|---|---|---|---|"]
    for mob, sts in res.items():
        for st, joins in sts.items():
            for lab, s in joins.items():
                if not s.get("shown"): lines.append(f"| {mob} | {specs[mob]['states'][st][1]} | {lab} | hidden / no join | | | |"); continue
                lines.append(f"| {mob} | {specs[mob]['states'][st][1]} | {lab} | {'CLOSED' if s['edge_max'] <= W.PASS_PX else 'OPENS'} | {s['edge_max']} | {s['edge_median']} | {s['rest_gap'] or ''} |")
    (out / "WING-CENSUS-ALL.md").write_text("# Wing-contact census — every winged mob (RP-06 1.4.21 + RP-07 1.4.27)\n\n" + "\n".join(lines) + "\n")

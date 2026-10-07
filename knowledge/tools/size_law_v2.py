#!/usr/bin/env python3
"""size_law_v2.py — L-SIZE-REAL v2 (his 01:51 + Z1 = A at 01:57 CT 10-01). SUPERSEDES the D-C291 curve (true scale from 0.60 m).
CURVE: K = 1.875 / 1.778 blocks per metre (his 5'10" character = 1.875 blocks)
    real >= 0.30 m : blocks = K x real                               (true size)
    real <  0.30 m : blocks = K x 0.30 x (real / 0.30) ** (1/3)       (termite 0.6 cm -> 0.086, ant 1.2 cm -> 0.108, frog 10 cm -> 0.219)
The curve is applied to the animal's LARGEST real dimension D; the magnification k = curve(D) / (K x D) is applied to every
dimension, so a small animal keeps its proportions.
SPECIES NORMALIZATION (his 'same species within a very close range and ratio of height and length'): every version of one species
is fitted to the SAME real (H, L): one uniform scale per version = sqrt((Ht / h) x (Lt / l)) (least squares in log space on height
and length). Long / flat animals (L > 6 H: snakes, eels, rays, lizards) are fitted on length only. Models posed with spread wings
(width > 1.3 x length and a wingspan known) are fitted on wingspan. Residuals over 15 % are listed for him (one-axis stretch only on
his say-so). Our own creatures (sf_nba) and vanilla mobs use the same species figure when a ported species matches (his earlier
calibrations — predators at the top of the adult-male range — win: the species is rescaled to our figure, H : L kept); else their
single-dimension size_law row (mode hb / max / h) on the new curve.
DEADBAND 5 % (nothing within 5 % of its target is touched). Output: _docs/sizes/size_law_v2_plan.json"""
import json, math, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import size_law as SL

ROOT = Path("/home/claude")
K = SL.K
R0, P, DEADBAND, FLAG = 0.30, 1 / 3, 0.05, 0.15


def curve(real):
    return K * real if real >= R0 else K * R0 * (real / R0) ** P


def predator_overrides():
    """his D-C298 predator figures (top of the adult-male range) from build_size_round2.PREDATOR"""
    src = (ROOT / "tools/build_size_round2.py").read_text()
    body = src[src.index("PREDATOR = {"): src.index("}", src.index("PREDATOR = {")) + 1]
    out = {}
    for k, v in re.findall(r'"([a-z_]+)":\s*\(([0-9.]+|None)', body):
        if v != "None": out[k] = float(v)
    return out


# ported species -> our own size_law key (same real animal); the species is rescaled to our figure
OURS = {"lion": "lion", "lion_female": "female_lion", "tiger_bengal": "tiger", "bear_american_black": "black_bear", "bear_grizzly": "grizzly_bear",
        "hyena_spotted": "hyena", "coyote": "coyote", "alligator_american": "alligator", "komodo_dragon": "komodo_dragon", "orca": "orca",
        "walrus": "walrus", "beaver": "beaver", "raccoon": "raccoon", "red_panda": "red_panda", "platypus": "platypus", "kakapo": "kakapo",
        "hamster_syrian": "hamster", "skunk_striped": "skunk", "gorilla": "gorilla", "giraffe_reticulated": "giraffe", "zebra_plains": "zebra",
        "rhino_white": "rhino", "elephant_african_bush": "elephant", "ostrich": "ostrich", "wild_boar": "boar", "deer_whitetailed": "deer",
        "toucan_toco": "toucan", "iguana_green": "iguana", "mole_european": "mole", "blue_jay": "bluejay", "shark_great_white": "great_white_shark",
        "scalloped_hammerhead": "hammer_head_shark", "whale_humpback": "whale", "octopus_common": "octopus", "moon_jellyfish": "jellyfish",
        "raven_common": "raven", "wild_turkey": "turkey", "flamingo_american": "flamingo", "carpenter_ant": "ant", "termite_worker": "termite",
        "moose_alaskan": "moose", "seal_harbor": "seal", "kangaroo": "kangaroo", "otter_neotropical": "otter", "hedgehog_european": "hedgehog",
        "snail_garden": "snail", "rattlesnake_eastern_diamondback": "rattlesnake"}


def hb_length(c):
    """model head-body length (tail bones left out, size_rule.TAIL) — the measure the earlier size rounds used for 'hb' rows"""
    import roster_size_census as RC, size_rule as SR
    from pathlib import Path as _P
    try:
        stack = [_P(x) for x in ("/home/claude/_build/rp07-1437", "/home/claude/_build/rp06-1424", "/home/claude/_build/rp08-148")
                 if _P(x).name != c["rp"]] + [ROOT / "_intake/bedrock-samples/resource_pack"]
        rp = ROOT / "_build" / c["rp"] if (ROOT / "_build" / c["rp"]).exists() else ROOT / "_intake/bedrock-samples/resource_pack"
        m = RC.measure_file(c["client_file"], rp, stack, exclude=SR.TAIL)
        return m["l"] if m else None
    except Exception: return None


def plan(census, species_rows):
    sp = {r["id"]: r for r in species_rows}
    pred = predator_overrides()
    by_species = {}
    for r in species_rows: by_species.setdefault(r["species"], r)
    ours_species = {v: k for k, v in OURS.items()}                       # our key -> ported species key
    rows = []
    for c in census:
        i = c["id"]; key = i.split(":")[1]
        if "h" not in c: rows.append({"id": i, "action": "skip", "why": c.get("measure_error", "not measured")}); continue
        mh, ml, mw = c["model_h"], c["model_l"], c["model_w"]
        row = {"id": i, "current_scale": c["adult_scale"], "model": [mh, ml, mw], "drawn": [c["h"], c["l"], c["w"]], "bp_pack": c.get("bp_pack")}
        H = L = WS = None; basis = ""; species = None; mode = None; real1 = None
        if i in sp and not sp[i].get("fantasy"):
            s = sp[i]; species = s["species"]; H, L, WS = s["H"], s["L"], s.get("WS"); basis = s["basis"]
            if species in OURS:                                            # his calibration for this animal wins
                ok = OURS[species]; fig = pred.get(ok, SL.REAL.get(ok, (None,))[0])
                if fig and SL.REAL.get(ok, (0, "max"))[1] == "max":
                    f = fig / max(L, H); H, L = H * f, L * f; WS = WS * f if WS else None; basis += f" | rescaled to our {ok} {fig} m (his calibration)"
        elif key in ours_species and ours_species[key] in by_species and i.startswith("sf_nba:"):
            s = by_species[ours_species[key]]; species = s["species"]; H, L, WS = s["H"], s["L"], s.get("WS")
            fig = pred.get(key, SL.REAL.get(key, (None,))[0])
            if fig and SL.REAL.get(key, (0, "max"))[1] == "max":
                f = fig / max(L, H); H, L = H * f, L * f; WS = WS * f if WS else None
            basis = f"species {species} (shared with the ported versions), our figure {fig} m"
        elif key in SL.REAL and (i.startswith("sf_nba:") or i.startswith("minecraft:")):
            real1, mode, basis = SL.REAL[key]; real1 = pred.get(key, real1)
        else:
            rows.append(dict(row, action="skip", why="no real-life size (fantasy or not an animal)")); continue
        if H is not None:
            wings = bool(WS) and mw > 1.3 * ml
            Lr = WS if wings else L; ml_use = mw if wings else ml
            D = max(H, Lr); k = curve(D) / (K * D)
            Ht, Lt = K * H * k, K * Lr * k
            if Lr > 6 * H or mh <= 0: s_new = Lt / ml_use; fit = "length only"
            else: s_new = math.sqrt((Ht / mh) * (Lt / ml_use)); fit = "height + " + ("wingspan" if wings else "length")
            res_h = mh * s_new / Ht - 1; res_l = ml_use * s_new / Lt - 1
            row.update({"species": species, "real": {"H": H, "L": L, "WS": WS}, "fit": fit, "target": [round(Ht, 3), round(Lt, 3)],
                        "new_scale": round(s_new, 4), "residual_h": round(res_h, 3), "residual_l": round(res_l, 3), "basis": basis,
                        "flag": abs(res_h) > FLAG or abs(res_l) > FLAG})
        else:
            if real1 >= 0.60:                                            # the law did not change above 0.60 m: every such mob already
                rows.append(dict(row, species=key, real={mode: real1}, fit=f"single ({mode})", target=[round(curve(real1), 3)],   # passed his
                                 new_scale=c["adult_scale"], basis=basis, flag=False, note="law unchanged above 0.60 m (witnessed)")); continue   # size rounds
            if mode == "hb":                                             # head-body: the tail is left out, as the size rounds measured it
                ml = hb_length(c) or ml
            dim = {"hb": ml, "max": max(mh, ml, mw), "h": mh}[mode]
            t = curve(real1); s_new = t / dim
            row.update({"species": key, "real": {mode: real1}, "fit": f"single ({mode})", "target": [round(t, 3)], "new_scale": round(s_new, 4), "basis": basis, "flag": False})
        rows.append(row)
    anchor(rows)
    for row in rows:
        if "new_scale" not in row: continue
        f = row["new_scale"] / row["current_scale"] if row["current_scale"] else 1
        row["factor"] = round(f, 4); row["action"] = "keep" if abs(f - 1) < DEADBAND else ("grow" if f > 1 else "shrink")
    return rows


def anchor(rows):
    """Versions of one species are balanced against EACH OTHER by the height + length fit; the species as a whole is then anchored
    so its median version hits the law on the animal's LARGEST real dimension (length for a lion, height for a giraffe, wingspan
    for a spread-wing butterfly) — the dimension the size law was always judged on (his witnessed calibrations stay)."""
    import statistics
    groups = {}
    for r in rows:
        if r.get("species") and "real" in r and "H" in r["real"]: groups.setdefault(r["species"], []).append(r)
    for sp, rs in groups.items():
        ratios = []
        for r in rs:
            H, L, WS = r["real"]["H"], r["real"]["L"], r["real"]["WS"]
            mh, ml, mw = r["model"]; wings = r["fit"].endswith("wingspan")
            Lr, mlu = (WS, mw) if wings else (L, ml)
            D, dim = (H, mh) if H >= Lr else (Lr, mlu)
            r["anchor_dim"] = "height" if H >= Lr else ("wingspan" if wings else "length")
            ratios.append(curve(D) / (dim * r["new_scale"]))
        A = statistics.median(ratios)
        ours = [r for r in rs if r["id"].startswith(("sf_nba:", "minecraft:"))]
        if ours and max(ours[0]["real"]["H"], ours[0]["real"]["L"]) >= 0.60:   # our witnessed size wins (law unchanged >= 0.60 m):
            A = ours[0]["current_scale"] / ours[0]["new_scale"]                 # the ported versions are matched to OUR version
        for r in rs:
            r["new_scale"] = round(r["new_scale"] * A, 4); r["species_anchor"] = round(A, 4)
            Ht, Lt = r["target"]; mh, ml, mw = r["model"]; mlu = mw if r["fit"].endswith("wingspan") else ml
            r["drawn_new"] = [round(mh * r["new_scale"], 3), round(mlu * r["new_scale"], 3)]
            r["residual_h"] = round(r["drawn_new"][0] / Ht - 1, 3); r["residual_l"] = round(r["drawn_new"][1] / Lt - 1, 3)
        hs = [r["drawn_new"][0] for r in rs]; ls = [r["drawn_new"][1] for r in rs]
        spread = max(max(hs) / min(hs), max(ls) / min(ls)) - 1 if len(rs) > 1 else 0
        for r in rs:
            r["species_versions"] = len(rs); r["species_spread"] = round(spread, 3)
            r["flag"] = len(rs) > 1 and spread > FLAG


if __name__ == "__main__":
    census = json.loads((ROOT / "_docs/sizes/all_mob_census.json").read_text())
    species = json.loads((ROOT / "_docs/sizes/menagerie_real_sizes.json").read_text())
    rows = plan(census, species)
    (ROOT / "_docs/sizes/size_law_v2_plan.json").write_text(json.dumps(rows, indent=1))
    from collections import Counter
    print(Counter(r["action"] for r in rows), "flagged:", sum(1 for r in rows if r.get("flag")))

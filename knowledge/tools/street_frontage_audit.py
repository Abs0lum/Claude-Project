#!/usr/bin/env python3
"""street_frontage_audit.py — how much house frontage each kit street of a civtest run really offers.
Reads the run's final heightmap ([CIVHEIGHT]) and the last evo record's streets; walks each street's corridor (frame t),
takes the sidewalk height per t (the median over w 1..11), splits it into level runs, and reports per street: length,
level runs, how many runs are long enough for each house size (frontage + 1-cell gaps), and the total frontage a row of
the commonest houses could use. Usage: street_frontage_audit.py LOG [--plateau]
--plateau (1.3.230 PL): also packs each street (back to back, 1-cell gaps, from its start) under three FRONTAGE laws — a
level run (rise 0, the columns above), the current law (rise <= 1, KIT.FRONT_RISE) and the plateau law (rise <= 2, the
door — the frontage's middle cell — within one step of the floor; PLAN.PLATEAU.frontRise / doorStep). It measures the
frontage rule only: built plots, the land behind (cut / fill / walls) and the sewer link are NOT modelled here (the node
suite tests/test_plateau.mjs covers those)."""
import json
import statistics
import sys
sys.path.insert(0, "/home/claude/tools")
import civ_height_render as R  # noqa: E402

NEEDS = {"cottage_s": 7 + 2, "cottage_m": 9 + 2, "bakery/smithy": 9 + 2, "cottage_l": 12 + 2}


def main():
    text = open(sys.argv[1], errors="ignore").read()
    head, G = R.parse_height(text)
    recs = R.records(text)
    evo = [r for r in recs if r.get("step") == "evo" and isinstance(r.get("streets"), list)]
    streets = evo[-1]["streets"]
    tot = {k: 0 for k in NEEDS}
    tot_len = tot_runs = 0
    for s in streets:
        f = s["f"]
        hs = []
        for t in range(s["tmin"], s["tmin"] + s["n"]):
            vals = []
            for w in range(1, 12):
                x, z = f["ox"] + t * f["ux"] + w * f["vx"], f["oz"] + t * f["uz"] + w * f["vz"]
                zi, xi = z - head["z0"], x - head["x0"]
                if 0 <= zi < len(G) and 0 <= xi < len(G[0]) and isinstance(G[zi][xi], int):
                    vals.append(G[zi][xi])
            hs.append(int(statistics.median(vals)) if vals else None)
        runs = []
        cur, n = None, 0
        for h in hs:
            if h == cur and h is not None:
                n += 1
            else:
                if n:
                    runs.append((cur, n))
                cur, n = h, 1
        runs.append((cur, n))
        lens = sorted((n for h, n in runs if h is not None), reverse=True)
        fits = {k: sum(n // v for n in lens) for k, v in NEEDS.items()}      # houses per side if packed back to back
        for k in NEEDS:
            tot[k] += fits[k]
        tot_len += s["n"]
        tot_runs += len(runs)
        print(f"street {s['id']:>2} {s['role']:<9}{' bench' if s.get('bench') else '      '} len {s['n']:>3} ramps {s['ramps']:>2}  runs {len(runs):>2}  "
              f"longest {lens[:6]}  fit/side cs {fits['cottage_s']:>2} cm {fits['cottage_m']:>2} cl {fits['cottage_l']:>2}")
    print(f"TOTAL street length {tot_len}, level runs {tot_runs}; houses per side if every level run were used: {tot}")
    if "--plateau" in sys.argv:
        plateau_report(head, G, streets)


FRONTS = {"cottage_s": 7, "cottage_m": 9, "cottage_l": 12, "park": 15}


def pack(hs, fz, rise_max, door_step=None):
    """houses of frontage fz packed back to back (1-cell gaps) from the street's start: a window fits when its sidewalk
    heights rise <= rise_max and (plateau law) the door (middle cell) stands within door_step of the floor (the highest)"""
    n, at = 0, 0
    while at + fz <= len(hs):
        w = hs[at:at + fz]
        ok = None not in w and max(w) - min(w) <= rise_max
        if ok and door_step is not None and max(w) - min(w) > 1:
            ok = max(w) - w[fz // 2] <= door_step
        if ok:
            n += 1
            at += fz + 1
        else:
            at += 1
    return n


def plateau_report(head, G, streets):
    print("\nFRONTAGE LAWS (per side; rise0 = level, rise1 = the current law, plateau = rise <= 2 with the door within 1):")
    tot = {k: [0, 0, 0] for k in FRONTS}
    for s in streets:
        f = s["f"]
        hs = []
        for t in range(s["tmin"], s["tmin"] + s["n"]):
            vals = []
            for w in range(1, 12):
                x, z = f["ox"] + t * f["ux"] + w * f["vx"], f["oz"] + t * f["uz"] + w * f["vz"]
                zi, xi = z - head["z0"], x - head["x0"]
                if 0 <= zi < len(G) and 0 <= xi < len(G[0]) and isinstance(G[zi][xi], int):
                    vals.append(G[zi][xi])
            hs.append(int(statistics.median(vals)) if vals else None)
        row = []
        for k, fz in FRONTS.items():
            a, b, c = pack(hs, fz, 0), pack(hs, fz, 1), pack(hs, fz, 2, 1)
            tot[k][0] += a
            tot[k][1] += b
            tot[k][2] += c
            row.append(f"{k} {a:>2}/{b:>2}/{c:>2}")
        print(f"street {s['id']:>2} {s['role']:<9} len {s['n']:>3}  " + "  ".join(row))
    for k, (a, b, c) in tot.items():
        gain = f"+{c - b} ({(c - b) / b * 100:.0f} %)" if b else f"+{c - b}"
        print(f"TOTAL {k:<9} per side: rise0 {a:>3}  rise1 {b:>3}  plateau {c:>3}  plateau vs current law {gain}; both sides x2")


if __name__ == "__main__":
    main()

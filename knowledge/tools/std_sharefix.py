#!/usr/bin/env python3
"""std_sharefix.py — p22 layer after `share` (RETRO-SWEEP hit L-ATTACH, 10-01). The share layer copies a same-species clip
from another creator's rig AS IS; the attach audit (shared_attach_audit.py) found 46 of 242 such copies in p21 pull a part
loose (> 1 px; 20 > 3 px; 6 of the 8 worst confirmed by renders: lemur jump, gorilla eat, lion sit, skunk idle, meerkat sit,
swan attack). For every applied share row (SHARING.json), on the ASSEMBLY:
  OK        the raw copy keeps every part joined (hierarchy + carrier pairs, std_famshare.joined_pairs) -> kept as it is
  REBAKED   loose -> retargeted like a family copy (std_famshare.try_retarget: world solve, trunk displacement, attach-follow,
            ground lock, every family gate) -> the shared_<kind> clip is REPLACED by the rebaked one
  DROPPED   loose and the retarget refuses -> the shared_<kind> entry is removed from the creature (the clip definition
            stays in the file, unused; never deleted)
Writes _docs/standard/SHARE-FIX.json."""
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_famshare as FS  # noqa: E402


def loose(rig, clip):
    pairs, env = FS.joined_pairs(rig), rig.env()
    worst = (0.0, None)
    for t in FS.sample_times(clip):
        w, _ = FS.posed(rig, clip, t, env)
        for c, p, g0 in pairs:
            g = FS.gap(w["corners"][c], w["corners"][p]) - g0
            if g > worst[0]:
                worst = (g, (c, p))
    return worst


def main(stage, write=True):
    stage = Path(stage)
    rows = [r for r in json.loads((ROOT / "_docs/standard/SHARING.json").read_text()) if r.get("applied")]
    rigs, report = {}, []

    def rig(m):
        if m not in rigs:
            rigs[m] = FS.Rig(m, stage)
        return rigs[m]
    for r in rows:
        k, tgt_id, src_id = r["kind"], r["to"], r["from"]
        out = {"to": tgt_id, "kind": k, "from": src_id, "from_clip": r["from_clip"]}
        try:
            t = rig(tgt_id)
            aid = t.desc["animations"].get(f"shared_{k}")
            clip = t.an["animations"].get(aid) if aid else None
            if clip is None:
                out["result"] = "absent"
                report.append(out)
                continue
            g, pair = loose(t, clip)
            out["loose_px"] = round(g, 1)
            if g <= 1.0:
                out["result"] = "OK"
                report.append(out)
                continue
            out["loose_part"] = pair
            s = rig(src_id)
            s_aid = s.desc["animations"][r["from_clip"]]
            res, why = FS.try_retarget(s, t, k, r["from_clip"], s_aid)
            if res:
                t.an["animations"][aid] = res[0]
                out["result"] = "REBAKED"
                out["gates"] = res[3]
            else:
                t.desc["animations"].pop(f"shared_{k}", None)
                out["result"] = "DROPPED"
                out["why"] = why
        except Exception as e:  # noqa: BLE001
            out["result"] = "ERROR"
            out["why"] = f"{type(e).__name__}: {str(e)[:80]}"
        report.append(out)
    if write:
        for m, r_ in rigs.items():
            r_.ef.write_text(json.dumps(r_.ent, indent=1))
            r_.af.write_text(json.dumps(r_.an, indent=1))
        (ROOT / "_docs/standard/SHARE-FIX.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
    from collections import Counter
    print("sharefix:", dict(Counter(x["result"] for x in report)))
    return report


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_staging/assembled", write="--dry" not in sys.argv)

#!/usr/bin/env python3
"""shared_attach_audit.py — RETRO-SWEEP hit (10-01, L-ATTACH): the p21 share layer (std_share: same species, other creator)
copies clips between rigs with no attachment check. This audit poses every shared_<kind> clip on its target rig at 6 moments
and reports parts that come loose: hierarchy pairs + carrier pairs (std_famshare.carriers: the part a limb / head / tail
touches at rest, ranked by deepest shared joint). Loose = gap grows > 1 px beyond its rest gap.
Usage: shared_attach_audit.py [STAGE]   -> _docs/standard/SHARED-ATTACH-AUDIT.json (+ printed list)"""
import json
import sys
import time
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_famshare as FS  # noqa: E402


def audit(stage, prefix="shared_"):
    stage = Path(stage)
    out, n = [], 0
    for ef in sorted(stage.glob("*/entity/std/*.entity.json")):
        d = S.jload(ef)["minecraft:client_entity"]["description"]
        sh = [(s, a) for s, a in (d.get("animations") or {}).items() if s.startswith(prefix)]
        if not sh:
            continue
        try:
            r = FS.Rig(d["identifier"], stage)
        except Exception as e:  # noqa: BLE001
            out.append({"id": d["identifier"], "clip": "*", "why": f"rig unreadable {str(e)[:40]}"})
            continue
        pairs, env = FS.joined_pairs(r), r.env()
        for s, a in sh:
            clip = r.an["animations"].get(a)
            if clip is None:
                continue
            n += 1
            worst = (0.0, None, None)
            try:
                for t in FS.sample_times(clip):
                    w, _ = FS.posed(r, clip, t, env)
                    for c, p, g0 in pairs:
                        g = FS.gap(w["corners"][c], w["corners"][p]) - g0
                        if g > worst[0]:
                            worst = (g, (c, p), round(t, 3))
            except Exception as e:  # noqa: BLE001
                out.append({"id": d["identifier"], "clip": s, "why": f"unevaluable {str(e)[:40]}"})
                continue
            if worst[0] > 1.0:
                out.append({"id": d["identifier"], "clip": s, "loose_px": round(worst[0], 1), "part": worst[1][0],
                            "from": worst[1][1], "at_s": worst[2]})
    return n, out


if __name__ == "__main__":
    t0 = time.time()
    n, out = audit(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_staging/assembled")
    (ROOT / "_docs/standard/SHARED-ATTACH-AUDIT.json").write_text(json.dumps(out, indent=1) + "\n")
    big = [x for x in out if x.get("loose_px", 0) > 3]
    print(f"shared clips audited {n} in {time.time() - t0:.0f}s · loose > 1 px: {len(out)} · > 3 px: {len(big)}")
    for x in sorted(out, key=lambda x: -x.get("loose_px", 0)):
        print(" ", x)

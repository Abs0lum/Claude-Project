#!/usr/bin/env python3
"""std_parade.py — p22 PARADE layer (backlog from p21: "FROZEN HERE … = skip"). In the witness pens a creature stands still,
so every clip driven by movement (anim_time_update reads the distance moved, or a channel scales with the move speed) shows
nothing. A PARADE copy of such a clip runs on a treadmill: same keys and channels, but
  anim_time_update   distance queries  ->  q.anim_time + q.delta_time * PACE   (the anim clock advances as if walking)
  in every Molang string:
    q.modified_distance_moved / q.walk_distance / q.limb_swing   ->  (q.life_time * PACE)
    q.modified_move_speed / q.limb_swing_amount                  ->  1.0
    q.ground_speed / q.horizontal_speed                          ->  PACE
    q.is_moving                                                  ->  1.0
PACE = 1.5 blocks / s for walk-like clips, 3.5 for run / gallop / sprint / charge.
The copy is a NEW animation id `animation.std.<slug>.parade_<short>` in the creature's std animation file; it is NOT added to
the entity's animate list (nothing plays it in a world) — only the test runner plays it in the pen (/playanimation). The
original clip is untouched. Runs on the ASSEMBLY (assemble_std.py), after share + fam. Writes _docs/standard/PARADE.json."""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

MOVE = re.compile(r"\b(q|query)\.(modified_distance_moved|walk_distance|limb_swing|modified_move_speed|limb_swing_amount|"
                  r"ground_speed|horizontal_speed|is_moving)\b", re.I)
FAST = re.compile(r"(run|gallop|sprint|charge|dash|flee)", re.I)


def pace_of(short):
    return 3.5 if FAST.search(short) else 1.5


def treadmill_str(s, pace):
    def sub(m):
        q = m.group(2).lower()
        if q in ("modified_distance_moved", "walk_distance", "limb_swing"):
            return f"(q.life_time * {pace})"
        if q in ("modified_move_speed", "limb_swing_amount", "is_moving"):
            return "1.0"
        return f"{pace}"
    return MOVE.sub(sub, s)


def treadmill(x, pace):
    if isinstance(x, str):
        return treadmill_str(x, pace)
    if isinstance(x, list):
        return [treadmill(v, pace) for v in x]
    if isinstance(x, dict):
        return {k: treadmill(v, pace) for k, v in x.items()}
    return x


def is_moving(clip):
    return bool(MOVE.search(json.dumps(clip)))


def parade_of(clip, short):
    pace = pace_of(short)
    out = {k: treadmill(v, pace) for k, v in clip.items() if k != "anim_time_update"}
    atu = str(clip.get("anim_time_update", ""))
    if atu and MOVE.search(atu):
        out["anim_time_update"] = f"q.anim_time + q.delta_time * {pace}"
    elif atu:
        out["anim_time_update"] = treadmill_str(atu, pace)
    out.setdefault("loop", True)
    return out


def main(stage, write=True):
    stage = Path(stage)
    packs, report = {}, []
    for ef in sorted(stage.glob("*/entity/std/*.entity.json")):
        rp = ef.parent.parent.parent.name
        af = ef.parent.parent.parent / "animations/std" / ef.name.replace(".entity.json", ".animation.json")
        if not af.exists():
            continue
        ent = S.jload(ef)
        desc = ent["minecraft:client_entity"]["description"]
        an = S.jload(af)
        own = an.setdefault("animations", {})
        if rp not in packs:
            packs[rp] = S.Pack(ROOT / "_build" / rp)
        lib = packs[rp].anims
        slug = ef.name.replace(".entity.json", "")
        made = []
        for short, aid in (desc.get("animations") or {}).items():
            if aid.startswith("controller.") or short.startswith("parade_"):
                continue
            clip = own.get(aid) or lib.get(aid)
            if not isinstance(clip, dict) or not is_moving(clip):
                continue
            pid = f"animation.std.{slug}.parade_{short}"
            own[pid] = parade_of(clip, short)
            made.append({"short": short, "from": aid, "parade": pid, "pace": pace_of(short)})
        if made:
            report.append({"id": desc.get("identifier"), "rp": rp, "parade": made})
            if write:
                af.write_text(json.dumps(an, indent=1) + "\n")
    if write:
        (ROOT / "_docs/standard/PARADE.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"parade: {sum(len(r['parade']) for r in report)} clips on {len(report)} creatures")
    return report


def _test():
    c = {"loop": True, "anim_time_update": "query.modified_distance_moved",
         "bones": {"leg": {"rotation": ["math.cos(q.anim_time * 38) * 40 * q.modified_move_speed", 0, 0]}}}
    p = parade_of(c, "walk")
    assert p["anim_time_update"] == "q.anim_time + q.delta_time * 1.5", p
    assert p["bones"]["leg"]["rotation"][0] == "math.cos(q.anim_time * 38) * 40 * 1.0", p
    assert c["anim_time_update"] == "query.modified_distance_moved"          # original untouched
    r = parade_of({"bones": {"b": {"position": [0, "Math.sin(Query.Walk_Distance*10)", 0]}}}, "run")
    assert r["bones"]["b"]["position"][1] == "Math.sin((q.life_time * 3.5)*10)", r
    assert not is_moving({"bones": {"b": {"rotation": ["q.life_time * 20", 0, 0]}}})
    print("std_parade tests OK")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_staging/assembled", write="--dry" not in sys.argv)

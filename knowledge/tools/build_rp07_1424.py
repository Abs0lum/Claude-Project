#!/usr/bin/env python3
"""build_rp07_1424.py — D-C286 (R9 witness: his p6 c03 FAIL "I don't see a bottom jaw, but I thought I did last time" + 10 content-log
errors "unhandled request for unknown variable 'variable.pw_em_…'"; Round 12 GO 17:0x CT 09-29). RP-07 v1.4.24 from v1.4.23.

THE JAW NEVER BOOTSTRAPPED. Since 1.4.22 the enderman declares min_engine_version 1.21.0, and the game then drops any statement that
reads a variable nobody has set yet. The ported Patrix jaw keeps state from frame to frame — v.pw_em_aggroa / aggroc read
THEMSELVES and v.pw_em_frame_counter_prev (written three statements later), and v.pw_em_r reads v.pw_em_rid (set by the
controller's on_entry, which runs after pre_animation) — so the first statement fails, everything that depends on it fails, and
every jaw channel is skipped: head2 and the jaw cube stay at rest, exactly on top of each other (no visible jaw). A strict-rule
simulation of 400 frames drops 4,001 statements and never sets a jaw variable; the fix — `(v.x ?? 0)` on those first reads
(molang_rbw_lint.guard_reads; also built into jem_anim_port.port from now on) — drops 0 and sets all of them from frame 0.
Nothing else changes (gate: only entity/enderman.entity.json + manifest; the jaw port still equals the JEM frame by frame).
verify: python3 tools/verify_rp07_1424.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
CHANGED, ADDED, REMOVED = [], [], []
RP06 = ROOT / "_build/rp06-1417"
FIRST_READS = {"pw_em_rid", "pw_em_frame_counter_prev", "pw_em_aggroa", "pw_em_aggroc"}


def enderman_guards(dst):
    import molang_rbw_lint as RBW
    pe = dst / "entity/enderman.entity.json"; d = R.jl(pe); sc = d["minecraft:client_entity"]["description"]["scripts"]
    before = list(sc["pre_animation"])
    assert {f[1] for f in RBW.check_scripts(sc)} == FIRST_READS - {"pw_em_rid"}, RBW.check_scripts(sc)
    sc["pre_animation"] = RBW.guard_reads(before, always=("pw_em_rid",))
    changed = [(a, b) for a, b in zip(before, sc["pre_animation"]) if a.strip() != b.strip()]
    assert len(changed) == 3 and not RBW.check_scripts(sc), (len(changed), RBW.check_scripts(sc))
    R.wj(pe, d); CHANGED.append("entity/enderman.entity.json")
    return f"enderman pre_animation: {len(changed)} statements guarded ({sorted(FIRST_READS)} read with ?? 0)"


def strict_sim(pre, frames=400, dt=0.05):
    """the game's strict rule, emulated: a statement that reads one of our v.* variables before anything set it (and not through
    `??`) is DROPPED. Returns (dropped statements, the frame each jaw variable is first set, aggro b at 99/299/399)."""
    import re, molang_eval as ME, molang_rbw_lint as RBW
    env = {"v.gliding_speed_value": 1.0}; setv = {"gliding_speed_value"}; drops = 0; first = {}; seen = []
    for i in range(frames):
        angry = 100 <= i < 300
        env.update({"q.life_time": i * dt, "q.delta_time": dt, "q.is_angry": 1.0 if angry else 0.0, "q.is_alive": 1.0, "q.hurt_time": 0.0,
                    "q.modified_distance_moved": 0.0, "q.modified_move_speed": 0.0, "q.target_y_rotation": 0.0, "q.target_x_rotation": 0.0})
        if i == 1: env["v.pw_em_rid"] = 0.37; setv.add("pw_em_rid")          # the controller's on_entry, after frame 0's pre_animation
        for st in RBW.statements(pre):
            m = RBW.ASSIGN.match(st); rhs = st[m.end():] if m else st
            reads = {x.lower() for x in RBW.VAR.findall(rhs)} - {g.lower() for g in RBW.GUARDED.findall(rhs)}
            if any(r not in setv for r in reads if r.startswith("pw_em_")): drops += 1; continue
            ME.run(st.replace("this", "0") + ";", env)
            if m: setv.add(m.group(1).lower())
        for k in ("pw_em_jaw_sx", "pw_em_jaw_ty", "pw_em_head2_ty", "pw_em_aggrob"):
            if k in setv and k not in first: first[k] = i
        if i in (99, 299, 399): seen.append(round(env.get("v.pw_em_aggrob", -1), 3))
    return drops, first, seen


def verify_extra(cfg, check):
    OLD, NEW = cfg["src"], cfg["dst"]
    po = R.jl(OLD / "entity/enderman.entity.json")["minecraft:client_entity"]["description"]
    pn = R.jl(NEW / "entity/enderman.entity.json")["minecraft:client_entity"]["description"]
    a = dict(po); b = dict(pn); sa = dict(a.pop("scripts")); sb = dict(b.pop("scripts"))
    check("EN3 enderman: only scripts.pre_animation changed (controllers, animations, geometry, min_engine_version identical)",
          a == b and {k: v for k, v in sa.items() if k != "pre_animation"} == {k: v for k, v in sb.items() if k != "pre_animation"}, "")
    d0, f0, s0 = strict_sim(sa["pre_animation"]); d1, f1, s1 = strict_sim(sb["pre_animation"])
    check("EN4 strict-rule simulation: 1.4.23 never sets a jaw variable (the witnessed FAIL); 1.4.24 drops 0 and sets all by frame 0",
          d0 > 3000 and not f0 and d1 == 0 and f1 and max(f1.values()) == 0 and s1[0] < 0.05 and s1[1] > 0.95 and s1[2] < 0.05,
          f"1.4.23 drops {d0}, set {f0}; 1.4.24 drops {d1}, first set {f1}, aggro b at 99/299/399 {s1}")
    import build_rp07_1421 as B21
    worst, seen = B21.jaw_frames_check()
    check("EN5 the (guarded) jaw port still equals the JEM frame by frame", worst < 1e-3 and seen[0] < 0.05 and seen[1] > 0.95, f"worst {worst:.2e}; {seen}")


CFG = {
    "src": ROOT / "_build/rp07-1423", "dst": ROOT / "_build/rp07-1424", "version": "1.4.24",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.24",
    "desc": ("v1.4.24 (2026-09-29) R9 FIX (D-C286): the Patrix enderman jaw now actually opens when angry (its frame-to-frame values "
             "were read before they were set, which the game refuses). Includes all of 1.4.23: tadpole upright, pufferfish spikes rooted, "
             "squid tilt, wolf / sheep sizes."),
    "pre": [], "jobs": [], "look": {}, "unbound_ok": {}, "placement": {},
    "post": [enderman_guards],
    "extra_changed": CHANGED, "extra_added": ADDED, "extra_removed": REMOVED,
    "ars_tag": "RP-07", "ars_stack": [RP06],
    "prec_order": [("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                   ("RP-07", ROOT / "_build/rp07-1424"), ("RP-06", RP06)],
    "verify_hooks": [verify_extra], "report": ROOT / "_docs/convb/build_rp07_1424_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
    json.dump({"changed": sorted(set(CHANGED)), "added": sorted(set(ADDED)), "removed": REMOVED},
              open(ROOT / "_docs/convb/build_rp07_1424_files.json", "w"), indent=1)

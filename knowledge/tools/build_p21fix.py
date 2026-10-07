#!/usr/bin/env python3
"""build_p21fix.py — RP-07 1.4.41 + RP-06 1.4.27 (his content log 1, 10-01): the assembled standard (base groups + share layer
with carried variables) on top of 1.4.40 / 1.4.26, through every gate incl. the game-log gates. BP-02 unchanged (1.3.200)."""
import json, sys
from pathlib import Path
ROOT = Path("/home/claude"); sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S
S.STAGE = ROOT / "_staging/assembled"
import build_std_round as B
B.S.STAGE = S.STAGE
B.RP = {"rp07-1439": ("rp07-1440", "rp07-1441", [1, 4, 41]), "rp06-1425": ("rp06-1426", "rp06-1427", [1, 4, 27])}
B.STACK = ["rp06-1427", "rp07-1441", "rp08-149"]
B.NOTE = ("CONTENT-LOG FIX (his log 1, 10-01): 48 empty-bone clips made valid; 8 old-format birds play the standard flight / "
          "flutter through a controller; armor_offset.default_neck defined identically in every model of 51 entities; shared "
          "clips carry the variables they read.")
LOC = "armor_offset.default_neck"


def fix_sniffer():
    """the sniffer (not in the standard round) pairs our geometry.pw_sniffer with Mojang's vanilla geometry.sniffer.baby, heads at
    different places -> the same locator mismatch. Our own copy of the vanilla baby model (geometry.pw_sniffer_baby) carries the
    locator, identical to the adult's; the entity's baby slot points at it. Mojang vanilla files are used inside our packs (§9)."""
    D = ROOT / "_build/rp07-1441"
    P = S.Pack(D); V = S.Pack(S.VANILLA)
    f, desc = P.entities["minecraft:sniffer"]
    ent = S.jload(f)
    d = ent["minecraft:client_entity"]["description"]
    adult_id = d["geometry"]["default"]
    gf = next(p for p in (D / "models").rglob("*.json") if adult_id in p.read_text(errors="ignore"))
    G = S.jload(gf)
    geos = G["minecraft:geometry"] if "minecraft:geometry" in G else None
    adult = next(g for g in geos if g["description"]["identifier"] == adult_id)
    head = next(b for b in adult["bones"] if b["name"].lower() == "head")
    off = [float(x) for x in head.get("pivot", [0, 0, 0])]
    baby = json.loads(json.dumps(V.geos["geometry.sniffer.baby"]))
    baby["description"]["identifier"] = "geometry.pw_sniffer_baby"
    common = {b["name"] for b in adult["bones"]} & {b["name"] for b in baby["bones"]}
    bone = "body" if "body" in common else ("root" if "root" in common else "head")
    for g in (adult, baby):
        next(b for b in g["bones"] if b["name"] == bone).setdefault("locators", {})[LOC] = off
    gf.write_text(json.dumps(G, indent=1))
    (D / "models/entity/pw_sniffer_baby.geo.json").write_text(json.dumps({"format_version": "1.12.0", "minecraft:geometry": [baby]}, indent=1))
    d["geometry"]["baby"] = "geometry.pw_sniffer_baby"
    Path(f).write_text(json.dumps(ent, indent=1))
    return {"sniffer": {"bone": bone, "offset": off, "adult_file": str(gf.relative_to(D))}}


def fix_nbump():
    """the Runner's bump-test mob pw:nbump shows four animals' models (warden / dolphin / turtle / parrot) in one entity; their
    heads differ by nature -> the same locator, IDENTICAL, on the `body` bone all four share (harmless to the real warden /
    dolphin / turtle / parrot that use these models alone)."""
    R = S.Pack(ROOT / "_build/testrunner-rp-0.7.0")
    gids = list(R.entities["pw:nbump"][1]["geometry"].values())
    off = None
    done = []
    for pk in ("rp06-1427", "rp07-1441"):
        D = ROOT / "_build" / pk
        for f in (D / "models").rglob("*.json"):
            t = f.read_text(errors="ignore")
            if not any(g in t for g in gids):
                continue
            G = S.jload(f)
            changed = False
            for g in G.get("minecraft:geometry", []):
                if g["description"]["identifier"] in gids:
                    if off is None:
                        off = [0.0, 24.0, 0.0]
                    next(b for b in g["bones"] if b["name"] == "body").setdefault("locators", {})[LOC] = off
                    changed = True
                    done.append(g["description"]["identifier"])
            if changed:
                f.write_text(json.dumps(G, indent=1))
    assert sorted(done) == sorted(gids), (done, gids)
    return {"nbump": done}


_orig_gate = B.gate
def _gate(report, stack=None):
    if not report.get("gate_only"):
        report.update(fix_sniffer())
        report.update(fix_nbump())
    return _orig_gate(report, stack)
B.gate = _gate
rep, (ok, checks) = B.run(gate_only="--gate-only" in sys.argv, with_bp02=False)
out = {"report": rep, "gate_ok": ok, "checks": checks}
(ROOT / "_docs/standard/BUILD-P21FIX.json").write_text(json.dumps(out, indent=1))
gl = next(c["game_log_gates"] for c in checks if "game_log_gates" in c)
print("gate_ok", ok, {k: v for k, v in gl.items() if k.startswith("n_")})
print("locator left:", gl["locator_clashes"])
print([ (c.get("pack"), c.get("n_json_errors"), c.get("n_unresolved"), c.get("duplicate_ids")) for c in checks if "pack" in c], [c.get("n") for c in checks if "staged_vs_built_mismatch" in c])

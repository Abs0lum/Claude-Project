#!/usr/bin/env python3
"""build_p21fix2.py — RP-07 1.4.42 + RP-06 1.4.28 (his content log 2, 10-01): 12 RP-06 SF creatures + the spider reconverted with
the packs above in view (their clips live in RP-07); explicit armor_offset locators removed; extra models' head bones back to their
original names (head channels duplicated). Built from 1.4.40 / 1.4.26 (1.4.41's post-steps — explicit locators on the sniffer and
the bump-test models — are NOT carried over). Gates: all, incl. the log-2 gates."""
import json, sys
from pathlib import Path
ROOT = Path("/home/claude"); sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S
S.STAGE = ROOT / "_staging/assembled"
import build_std_round as B
B.S.STAGE = S.STAGE
B.RP = {"rp07-1439": ("rp07-1440", "rp07-1442", [1, 4, 42]), "rp06-1425": ("rp06-1426", "rp06-1428", [1, 4, 28])}
B.STACK = ["rp06-1428", "rp07-1442", "rp08-149"]
B.EXTRA_ENTITY_PACKS = [ROOT / "_build/testrunner-rp-0.7.1"]
B.NOTE = ("CONTENT-LOG FIX 2 (his log 2, 10-01): 12 hostile SF creatures + spider animate again (their clips converted with the "
          "standard rig); armor_offset locator clashes removed (explicit locators gone, extra models' head names restored); "
          "everything of 1.4.41 (empty-bone clips valid, 8 old-format birds fly, shared clips carry their settings).")
rep, (ok, checks) = B.run(gate_only="--gate-only" in sys.argv, with_bp02=False)
(ROOT / "_docs/standard/BUILD-P21FIX2.json").write_text(json.dumps({"report": rep, "gate_ok": ok, "checks": checks}, indent=1))
gl = next(c["game_log_gates"] for c in checks if "game_log_gates" in c)
print("gate_ok", ok, {k: v for k, v in gl.items() if k.startswith("n_")})
print("locator:", gl["locator_clashes"][:10], "unconverted:", gl["unconverted"][:5], "empty files:", gl["empty_anim_files"][:5])
print([(c.get("pack"), c.get("n_json_errors"), c.get("n_unresolved"), c.get("duplicate_ids")) for c in checks if "pack" in c], [c.get("n") for c in checks if "staged_vs_built_mismatch" in c])

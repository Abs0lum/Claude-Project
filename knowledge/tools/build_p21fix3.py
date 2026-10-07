#!/usr/bin/env python3
"""build_p21fix3.py — his log 3 + his 16:31 catch (R1 = a): RP-07 1.4.43 (the blobfish `lead` locator on one bone name in both
models) + RP-04 1.3.144 (its in-game NAME carries the real version; nothing else changes). RP-06 stays 1.4.28."""
import json, shutil, sys
from pathlib import Path
ROOT = Path("/home/claude"); sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S
S.STAGE = ROOT / "_staging/assembled"
import build_std_round as B
B.S.STAGE = S.STAGE
B.RP = {"rp07-1439": ("rp07-1442", "rp07-1443", [1, 4, 43])}
B.STACK = ["rp06-1428", "rp07-1443", "rp08-149"]
B.EXTRA_ENTITY_PACKS = [ROOT / "_build/testrunner-rp-0.7.1", ROOT / "_build/rp04-144"]
B.NOTE = ("CONTENT-LOG FIX 3 (his log 3, 10-01): the blobfish leash point on one bone in both its models. Includes all of the "
          "1.4.41 / 1.4.42 fixes.")


def build_rp04():
    src, dst = ROOT / "_build/rp04-143", ROOT / "_build/rp04-144"
    assert not dst.exists(), "never rebuild a build dir"
    shutil.copytree(src, dst)
    B.bump_manifest(dst, [1, 3, 144], "NAME FIX (his 16:31 catch: the title said v1.3.142): the pack's name now carries its real "
                                      "version. Nothing else changed.")
    m = json.loads((dst / "manifest.json").read_text(encoding="utf-8-sig"))
    return m["header"]["name"]


if "--gate-only" not in sys.argv:
    print("RP-04:", build_rp04())
rep, (ok, checks) = B.run(gate_only="--gate-only" in sys.argv, with_bp02=False)
(ROOT / "_docs/standard/BUILD-P21FIX3.json").write_text(json.dumps({"report": rep, "gate_ok": ok, "checks": checks}, indent=1))
gl = next(c["game_log_gates"] for c in checks if "game_log_gates" in c)
print("gate_ok", ok, {k: v for k, v in gl.items() if k.startswith("n_")})
print([(c.get("pack"), c.get("n_json_errors"), c.get("n_unresolved"), c.get("duplicate_ids")) for c in checks if "pack" in c], [c.get("n") for c in checks if "staged_vs_built_mismatch" in c])

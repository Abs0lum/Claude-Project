#!/usr/bin/env python3
"""build_size_v2.py — D-C363 size law v2 for OUR creatures + vanilla mobs (the ported ones are sized in the port pipeline,
menagerie_p3_adjust.sizes). Run AFTER build_menagerie_r3.py 1.3.12 (it edits that build in place, text-level, scale values only):
  * PW-StripMine BP 1.3.12: every sf_nba creature the plan grows / shrinks (x new / current on every minecraft:scale; base inserted
    when none) — our witnessed sizes above 0.60 m are kept by the plan.
  * BP-02 1.3.198 -> 1.3.199: vanilla mobs the plan changes (the curve below 0.60 m: bee, frog, tadpole, axolotl, rabbit, chicken,
    armadillo, bat, pufferfish, tropical fish): BP-02's own copy edited, or Mojang's 1.26.50 behaviour file copied in with only
    its scale changed (the round-1 method).
Report: _docs/sizes/size_v2_ours_report.json"""
import json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from build_size_round import rescale_text

ROOT = Path("/home/claude"); SM = ROOT / "_build/stripmine-bp-1312"; B0, B1 = ROOT / "_build/bp02-198", ROOT / "_build/bp02-199"
VAN_BP = ROOT / "_intake/bedrock-samples/behavior_pack/entities"
PLAN = {r["id"]: r for r in json.loads((ROOT / "_docs/sizes/size_law_v2_plan.json").read_text())}


def ident_of(raw):
    m = re.search(r'"identifier"\s*:\s*"([a-z_]+:[a-z0-9_]+)"', raw); return m.group(1) if m else None


def main():
    rep = {"stripmine": [], "bp02": []}
    todo = {i: r for i, r in PLAN.items() if r.get("action") in ("grow", "shrink")}
    for p in sorted((SM / "entities").glob("*.json")):                         # sf_nba (not pw_menagerie)
        raw = p.read_text(encoding="utf-8-sig"); i = ident_of(raw)
        if i not in todo or not i.startswith("sf_nba:"): continue
        f = todo[i]["new_scale"] / todo[i]["current_scale"]
        out, n, ins = rescale_text(raw, f); p.write_text(out, encoding="utf-8")
        rep["stripmine"].append({"id": i, "file": p.name, "factor": round(f, 4), "scales": n, "inserted": ins})
    if B1.exists(): shutil.rmtree(B1)
    shutil.copytree(B0, B1)
    for i, r in todo.items():
        if not i.startswith("minecraft:"): continue
        f = r["new_scale"] / r["current_scale"]; name = i.split(":")[1]
        own = [p for p in (B1 / "entities").glob("*.json") if ident_of(p.read_text(encoding="utf-8-sig")) == i]
        if own: p = own[0]; raw = p.read_text(encoding="utf-8-sig"); how = "BP-02 copy"
        else:
            src = [p for p in VAN_BP.glob("*.json") if ident_of(p.read_text(encoding="utf-8-sig")) == i]
            assert src, f"no Mojang behaviour file for {i}"
            raw = src[0].read_text(encoding="utf-8-sig"); p = B1 / "entities" / src[0].name; how = "Mojang 1.26.50 copy"
        out, n, ins = rescale_text(raw, f); p.write_text(out, encoding="utf-8")
        rep["bp02"].append({"id": i, "file": p.name, "how": how, "factor": round(f, 4), "scales": n, "inserted": ins,
                            "target_blocks": r.get("target")})
    m = json.loads((B1 / "manifest.json").read_text(encoding="utf-8-sig")); v = [1, 3, 199]
    m["header"]["version"] = v; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.199"
    for mod in m["modules"]: mod["version"] = v
    m["header"]["description"] = ("v1.3.199 (2026-10-01) SIZE LAW v2 (his 01:51 + Z1): true size from 30 cm, a gentle ramp below - "
        + ", ".join(f"{x['id'].split(':')[1]} x{x['factor']}" for x in rep["bp02"]) + ". Each changed file = the scale values only. Includes all of v1.3.198.")
    (B1 / "manifest.json").write_text(json.dumps(m, indent=1))
    sm = json.loads((SM / "manifest.json").read_text(encoding="utf-8-sig"))
    sm["header"]["description"] = ("v1.3.12 (2026-10-01) SIZE LAW v2 (his 01:51 + Z1 = A): every creature at like-life size - true size from 30 cm, "
        f"a gentle ramp below (ant 0.10 block); versions of one species normalized to each other ({len([x for x in PLAN.values() if x.get('species_versions', 1) > 1])} "
        f"rows in shared species); {len(rep['stripmine'])} of our own creatures + the ported ones resized; plus every behaviour fix of v1.3.11. "
        "Pairs with RP-07 v1.4.38 and BP-02 v1.3.199.")
    (SM / "manifest.json").write_text(json.dumps(sm, indent=1))
    (ROOT / "_docs/sizes/size_v2_ours_report.json").write_text(json.dumps(rep, indent=1))
    line = f"BUILD size v2: StripMine 1.3.12 +{len(rep['stripmine'])} sf_nba resized; BP-02 1.3.199 {len(rep['bp02'])} vanilla mobs resized"
    print(line)
    with open(ROOT / "_logs/phase_log.md", "a") as fh: fh.write(f"[{time.strftime('%H:%M')} CT 10-01] {line}\n")


if __name__ == "__main__":
    main()

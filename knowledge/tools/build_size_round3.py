#!/usr/bin/env python3
"""build_size_round3.py — SIZE ROUND 3 (R14 fix round; D-C307 his re-rulings after my corrected numbers). Text-level edits on
the shipped files, the same method as rounds 1-2 (only minecraft:scale values change; verify_size_round3.py proves it):
  * BP-02 v1.3.193 from v1.3.192:
      - dolphin 3.81 m -> 3.12 m (his f15 "typical male": ADW adult males 2.44-3.81 m, midpoint 3.12);
      - polar bear stays 2.5 m head-body on the NEW Patrix model (RP-07 1.4.27): x (old model length / new model length);
      - NEW Mojang copy: endermite x 0.75 (his f12 "20-30 % smaller ... I defer": 25 %; fantasy creature, not on the curve).
  * PW-StripMine BP v1.3.6 from v1.3.5 (Realm-only):
      grizzly 2.4 -> 2.8 m (big coastal brown-bear male) · alligator 4.8 -> 5.5 m and komodo 3.0 -> 3.45 m (+15 %, "imposing",
      beyond real life by his ruling like the sharks) · rat snake 2.07 -> 1.43 m (average adult male).
Factors are taken against what the shipped files draw today (size_round2_report.json to_blocks; the polar bear re-measured).
Usage: build_size_round3.py -> _build/bp02-193, _build/stripmine-bp-136 + _docs/sizes/size_round3_report.json"""
import json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import size_law as S
import build_size_round as R1
import visible_size as V

ROOT = Path("/home/claude")
DATE = "2026-09-30"
R2 = {r["id"]: r for r in json.load(open(ROOT / "_docs/sizes/size_round2_report.json"))["rows"]}
NEW_M = {"minecraft:dolphin": (3.12, "typical adult male (ADW adult males 2.44-3.81 m, midpoint) - his f15 ruling"),
         "sf_nba:grizzly_bear": (2.8, "big coastal brown-bear male - his re-ruling (grizzly reads bigger than the lion)"),
         "sf_nba:alligator": (5.5, "4.8 m top of range + 15 % - his 'imposing reptiles' ruling"),
         "sf_nba:komodo_dragon": (3.45, "3.0 m top of range + 15 % - his 'imposing reptiles' ruling"),
         "sf_nba:snake": (1.43, "average adult male (SVL mean 1.182 m + 17.5 % tail, Virginia Herpetological Society) - his ruling")}
ENDERMITE_FACTOR = 0.75


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD size-round-3: {m}\n")


def rows():
    out = []
    for ident, (m, why) in NEW_M.items():
        r = R2[ident]; base = r["to_blocks"]; tgt = S.target(m)
        out.append({"id": ident, "real_m_old": r["real_m"], "real_m": m, "mode": r["mode"], "why": why,
                    "from_blocks": round(base, 3), "to_blocks": round(tgt, 3), "factor": round(tgt / base, 4)})
    old = V.measure(ROOT / "_build/rp07-1426", "polar_bear", [ROOT / "_build/rp06-1420"], everyday=True)
    new = V.measure(ROOT / "_build/rp07-1427", "polar_bear", [ROOT / "_build/rp06-1421"], everyday=True)
    f = old["l"] / new["l"]
    out.append({"id": "minecraft:polar_bear", "real_m_old": 2.5, "real_m": 2.5, "mode": "hb", "model_l_old": old["l"], "model_l_new": new["l"],
                "model_h_old": old["h"], "model_h_new": new["h"], "why": "2.5 m head-body kept; the model changed (April -> Patrix, RP-07 1.4.27)",
                "from_blocks": R2["minecraft:polar_bear"]["to_blocks"], "to_blocks": R2["minecraft:polar_bear"]["to_blocks"], "factor": round(f, 4)})
    return out


def build_bp02(rs):
    src, dst = ROOT / "_build/bp02-192", ROOT / "_build/bp02-193"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    done = []
    for r in rs:
        if not r["id"].startswith("minecraft:"): continue
        fn = {"minecraft:polar_bear": "polar_bear.json", "minecraft:dolphin": "dolphin.json"}[r["id"]]
        p = dst / "entities" / fn; assert p.exists(), p
        out, n, ins = R1.rescale_text(p.read_text(encoding="utf-8"), r["factor"]); assert n >= 1 and not ins, (fn, n, ins)
        p.write_text(out, encoding="utf-8"); done.append({**r, "file": f"entities/{fn}", "scales_changed": n})
    raw = (R1.VAN_BP / "endermite.json").read_text(encoding="utf-8")
    out, n, ins = R1.rescale_text(raw, ENDERMITE_FACTOR); assert ins, (n, ins)
    (dst / "entities/endermite.json").write_text(out, encoding="utf-8")
    done.append({"id": "minecraft:endermite", "file": "entities/endermite.json", "new_file": True, "factor": ENDERMITE_FACTOR, "scales_changed": n,
                 "base_inserted": ins, "why": "his f12: 20-30 % smaller, 'I defer' -> 25 %"})
    mp = dst / "manifest.json"; m = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 3, 193]
    m["header"]["version"] = v; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.193"
    for mod in m["modules"]: mod["version"] = v
    m["header"]["description"] = (f"v1.3.193 ({DATE}) SIZE ROUND 3 (R14 fixes): the dolphin at a typical adult male (3.1 m, was 3.8), the "
        "endermite 25 % smaller, the polar bear kept at 2.5 m on its new Patrix model (RP-07 1.4.27) - model AND hitbox. Each file = the "
        "shipped behaviour file (the endermite: Mojang's 1.26.50 file) with only its scale values changed. Everything else byte-identical to v1.3.192.")
    mp.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log(f"bp02-193: {len(done)} behaviour entities resized; manifest 1.3.193")
    return done


def build_stripmine(rs):
    src, dst = ROOT / "_build/stripmine-bp-135", ROOT / "_build/stripmine-bp-136"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    targets = {r["id"]: r for r in rs if r["id"].startswith("sf_nba:")}
    done, found = [], set()
    for p in sorted((dst / "entities").rglob("*.json")):
        raw = p.read_text(encoding="utf-8-sig")
        m = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', raw)
        if not m or m.group(1) not in targets: continue
        r = targets[m.group(1)]
        out, n, ins = R1.rescale_text(raw, r["factor"]); assert n >= 1 and not ins, (p.name, n, ins)
        p.write_text(out, encoding="utf-8"); found.add(r["id"])
        done.append({**r, "file": str(p.relative_to(dst)), "scales_changed": n})
    missing = sorted(set(targets) - found); assert not missing, missing
    mp = dst / "manifest.json"; mf = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 3, 6]
    mf["header"]["version"] = v; mf["header"]["name"] = "PW StripMine BP v1.3.6"
    for mod in mf["modules"]: mod["version"] = v
    mf["header"]["description"] = (f"v1.3.6 ({DATE}) SIZE ROUND 3 (R14 fixes, his rulings): grizzly 2.8 m (bigger than the lion), alligator "
        "5.5 m and komodo dragon 3.45 m (imposing: 15 % past the real top of range), rat snake 1.43 m (average adult male). Realm-only pack. "
        "Everything else byte-identical to v1.3.5.")
    mp.write_text(json.dumps(mf, indent=1), encoding="utf-8")
    log(f"stripmine-bp-136: {len(found)} creatures rescaled")
    return done


if __name__ == "__main__":
    rs = rows()
    rep = {"rows": rs, "bp02": build_bp02(rs), "stripmine": build_stripmine(rs)}
    json.dump(rep, open(ROOT / "_docs/sizes/size_round3_report.json", "w"), indent=1)
    for r in rs: print(f"{r['id']:24s} {r['from_blocks']} -> {r['to_blocks']} x{r['factor']}  {r.get('model_l_old', '')} {r.get('model_l_new', '')}")

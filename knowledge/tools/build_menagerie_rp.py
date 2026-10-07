#!/usr/bin/env python3
"""build_menagerie_rp.py — D-C359: RP-07 1.4.34 -> 1.4.35, resource-side fixes from his 00:29 FULL content log (BDS cannot see these).
  - ported client entities: animation entries their own pack never shipped removed (+ their animate lines) — 'can't find animation baby_transform'
  - YTri olhar.json loop "true" -> true; YTri canario controller query.is_flying (no such query) -> (!query.is_on_ground)
  - sounds.json: the ported creatures' entries re-merged without the events the game rejects (ask, sniff, spit)
Asserts the staged BP equals the delivered StripMine BP 1.3.11 (behaviour side unchanged). Usage: build_menagerie_rp.py 1.4.35"""
import hashlib, json, shutil, sys, time
from pathlib import Path

ROOT = Path("/home/claude"); STAGE = ROOT / "_build/menagerie-stage"
VER = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1.4.35").split(".")]
R0, R1 = ROOT / "_build" / f"rp07-1{VER[1]}{VER[2] - 1}", ROOT / "_build" / f"rp07-1{VER[1]}{VER[2]}"
BP = ROOT / "_build/stripmine-bp-1312"


def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()


def main():
    bp_diff = [str(p.relative_to(STAGE / "BP")) for p in (STAGE / "BP").rglob("*") if p.is_file()
               and (not (BP / p.relative_to(STAGE / "BP")).exists() or md5(p) != md5(BP / p.relative_to(STAGE / "BP")))]
    assert not bp_diff, f"BP would change: {bp_diff[:5]}"
    if R1.exists(): shutil.rmtree(R1)
    shutil.copytree(R0, R1)
    improved, added = [], []
    for p in (STAGE / "RP").rglob("*"):
        if not p.is_file() or "_fragments" in p.parts: continue
        rel = p.relative_to(STAGE / "RP"); o = R1 / rel
        assert "pw_menagerie" in rel.parts, f"outside pw_menagerie: {rel}"
        if o.exists() and md5(o) == md5(p): continue
        (improved if o.exists() else added).append(str(rel))
        o.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, o)
    ours_fixed = []                                              # his D1 (c): our own controllers with the same start-state typo
    for f in sorted((R1 / "animation_controllers").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8-sig")); hit = False
        for cid, c in (d.get("animation_controllers") or {}).items():
            st = c.get("states") or {}
            if st and c.get("initial_state", "default") not in st: c["initial_state"] = next(iter(st)); hit = True; ours_fixed.append(cid)
        if hit: f.write_text(json.dumps(d, indent=2))
    sj = json.loads((R1 / "sounds.json").read_text(encoding="utf-8-sig")); ents = sj["entity_sounds"]["entities"]
    fr = json.loads((STAGE / "RP/_fragments/sounds.json").read_text())["entity_sounds"]["entities"]
    resound = [k for k, v in fr.items() if ents.get(k) != v]
    for k in resound: ents[k] = fr[k]
    (R1 / "sounds.json").write_text(json.dumps(sj, indent=1))
    V = ".".join(map(str, VER)); PV = ".".join(map(str, VER[:2] + [VER[2] - 1]))
    m = json.loads((R1 / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = VER; m["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{V}"
    m["header"]["description"] = (f"v{V} (2026-10-01) MENAGERIE resource fixes from his full content log: animation entries the add-ons never "
                                  "shipped removed (baby_transform ...), a looping flag written as text, the canary's flying test, sound events "
                                  "the game rejects (ask / sniff / spit); the old-style controller lines now point at ported controllers (WA attacks, "
                                  f"bird walk / fly, toucan, crab, deer baby, celebrate), dead ones dropped (WA eggs, IFS boar, WA hyena). Pairs with PW-StripMine BP v1.3.12. Includes all of v{PV}.")
    for mod in m["modules"]: mod["version"] = VER
    (R1 / "manifest.json").write_text(json.dumps(m, indent=1))
    (ROOT / f"_logs/menagerie_rp{V}_improved.json").write_text(json.dumps({"improved": improved, "added": added, "resound": resound}, indent=1))
    line = f"BUILD RP-07 {V}: {len(improved)} ported files improved, {len(added)} added (controllers), {len(resound)} sounds.json entries re-merged; BP unchanged (== 1.3.11)"
    print(line)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 10-01] {line}\n")


if __name__ == "__main__":
    main()

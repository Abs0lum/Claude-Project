#!/usr/bin/env python3
"""verify_menagerie_rp.py — gate for an RP-07 menagerie fix round (D-C359). Static checks only rule OUT; his device rules in."""
import hashlib, json, re, sys, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import addon_port_scan as S

ROOT = Path("/home/claude"); VER = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1.4.35").split(".")]
R0, R1 = ROOT / "_build" / f"rp07-1{VER[1]}{VER[2] - 1}", ROOT / "_build" / f"rp07-1{VER[1]}{VER[2]}"
res = []
OURS_D1 = {"animation_controllers/pillager.animation_controllers.json", "animation_controllers/villager.animation_controllers.json",
           "animation_controllers/iron_golem.animation_controllers.json"}   # his D1 (c): our own start-state typos
def check(n, ok, d=""): res.append(ok); print(f"{'PASS' if ok else 'FAIL'}  {n}" + (f" — {d}" if d else ""))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def jl(p): return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))

m0, m1 = jl(R0 / "manifest.json"), jl(R1 / "manifest.json")
check(f"A manifest {VER}; uuids, capabilities (pbr) unchanged", m1["header"]["version"] == VER and m1["header"]["uuid"] == m0["header"]["uuid"]
      and [x["uuid"] for x in m1["modules"]] == [x["uuid"] for x in m0["modules"]] and m1.get("capabilities") == m0.get("capabilities"))
f0 = {str(p.relative_to(R0)): p for p in R0.rglob("*") if p.is_file()}; f1 = {str(p.relative_to(R1)): p for p in R1.rglob("*") if p.is_file()}
ch = [k for k in f0 if k in f1 and md5(f0[k]) != md5(f1[k])]
check("B nothing removed; additions and changes only in ported files (pw_menagerie), sounds.json and the manifest",
      set(f0) <= set(f1) and all("pw_menagerie" in k for k in set(f1) - set(f0)) and all(k in ("manifest.json", "sounds.json") or "pw_menagerie" in k or k in OURS_D1 for k in ch), f"{len(ch)} changed")
sj0, sj1 = jl(R0 / "sounds.json"), jl(R1 / "sounds.json")
e0, e1 = sj0["entity_sounds"]["entities"], sj1["entity_sounds"]["entities"]
check("B sounds.json: only ported creatures' entries changed, nothing outside entity_sounds.entities",
      {k: v for k, v in sj0.items() if k != "entity_sounds"} == {k: v for k, v in sj1.items() if k != "entity_sounds"} and set(e0) == set(e1)
      and all(k.startswith("pw:") and re.search(r"_(anf|wa|ws|wwa|ysav|ytri|ifs)$", k) for k in e0 if e0[k] != e1[k]))
bad_ev = [(k, ev) for k, v in e1.items() for ev in (v.get("events") or {}) if ev in ("ask", "sniff", "spit")]
check("C (his 00:29 log) no sound event the game rejects (ask, sniff, spit)", not bad_ev, str(bad_ev[:3]))
errs = []
for p in R1.rglob("*.json"):
    try: jl(p)
    except Exception: errs.append(str(p.relative_to(R1)))
check("C every JSON parses", not errs, str(errs[:3]))
z = Path(tempfile.mkdtemp()) / "rp.mcpack"
with zipfile.ZipFile(z, "w") as zf:
    for p in R1.rglob("*.json"): zf.write(p, str(p.relative_to(R1)))
n, e = ML.lint_pack(z); check("C Molang lint", not e, f"{n} strings, {len(e)} errors")
txt = [p for p in R1.rglob("*.json") if "pw_menagerie" in str(p) and (re.search(r'"loop":\s*"(true|false)"', p.read_text(errors="ignore")) or re.search(r"\b(query|q)\.is_flying\b", p.read_text(errors="ignore")))]
check("D (his 00:29 log) no looping flag written as text, no query.is_flying", not txt, str(txt[:2]))
anims = set()
for p in R1.rglob("animations/**/*.json"):
    try: anims |= set((jl(p).get("animations") or {}))
    except Exception: pass
for p in R1.rglob("animation_controllers/**/*.json"):
    try: anims |= set((jl(p).get("animation_controllers") or {}))
    except Exception: pass
VAN = S.vanilla_refs()
dead, orphan = [], []
for p in R1.glob("entity/pw_menagerie/**/*.json"):
    d = jl(p)["minecraft:client_entity"]["description"]; amap = d.get("animations") or {}
    dead += [(d["identifier"], v) for v in amap.values() if v not in anims and v not in VAN and not v.startswith(("animation.common", "animation.humanoid", "controller.animation.humanoid"))]
    for x in (d.get("scripts") or {}).get("animate", []) or []:
        k = x if isinstance(x, str) else next(iter(x))
        if k not in amap: orphan.append((d["identifier"], k))
check("D (his 00:29 'can't find animation baby_transform') every animation a ported creature names exists (ours or vanilla)", not dead, f"{len(dead)} e.g. {dead[:3]}")
check("D every scripts.animate line plays an animation the creature defines", not orphan, str(orphan[:3]))
# his 00:40 log: an emptied map / animate list is refused; a vanilla animation must never be removed
empty, lost = [], []
for k in f1:
    if not (k.startswith("entity/pw_menagerie/") and k in f0): continue
    d1 = jl(f1[k])["minecraft:client_entity"]["description"]; d0 = jl(f0[k])["minecraft:client_entity"]["description"]
    if d1.get("animations") == {} or (d1.get("scripts") or {}).get("animate") == [] or d1.get("scripts") == {}: empty.append(k)
    lost += [(d1["identifier"], v) for v in (d0.get("animations") or {}).values() if v not in (d1.get("animations") or {}).values() and (v in VAN or v in anims)]
check("D (his 00:40 log) no empty animations map / animate list / scripts", not empty, str(empty[:3]))
check("D no animation that resolves (ours or vanilla) was removed from any creature (his 00:40: coyote lost the fox controller)", not lost, f"{len(lost)} e.g. {lost[:3]}")
BASE = ROOT / "_build/rp07-1434"                                  # the last version before any animation clean-up
lost34 = []
for p in BASE.glob("entity/pw_menagerie/**/*.json"):
    q = R1 / p.relative_to(BASE)
    if not q.exists(): continue
    a0 = (jl(p)["minecraft:client_entity"]["description"].get("animations") or {}).values()
    a1 = set((jl(q)["minecraft:client_entity"]["description"].get("animations") or {}).values())
    lost34 += [(p.name, v) for v in a0 if v not in a1 and (v in VAN or v in anims)]
check("D since 1.4.34: no animation that resolves (vanilla or RP-07's own, e.g. animation.fox.baby_transform) was removed", not lost34, str(lost34[:3]))
leg_bad = []
for p in R1.glob("entity/pw_menagerie/**/*.json"):
    d = jl(p)["minecraft:client_entity"]["description"]
    if "animation_controllers" in d and not d.get("animations"): leg_bad.append((d["identifier"], "no animations map"))
    leg_bad += [(d["identifier"], v) for x in d.get("animation_controllers") or [] for v in (x.values() if isinstance(x, dict) else [x]) if v not in anims and v not in VAN]
check("D (his 00:51 log + L1/L2) every old-style controller line names a controller that exists, and only where there are animations to drive", not leg_bad, f"{len(leg_bad)} e.g. {leg_bad[:3]}")
init_bad = []
for p in R1.rglob("animation_controllers/**/*.json"):
    try: d = jl(p)
    except Exception: continue
    for cid, c in (d.get("animation_controllers") or {}).items():
        st = c.get("states") or {}
        if st and c.get("initial_state", "default") not in st: init_bad.append(cid)
check("D (his 01:05 log + D1 c) every animation controller starts in a state it has", not init_bad, str(init_bad[:4]))
mods_out = [k for k in f1 if k.startswith("models/") and not k.startswith(("models/entity/", "models/blocks/")) and k != "models/mobs.json"]
check("L every model is under models/entity or models/blocks (his 23:30 law)", not mods_out, str(mods_out[:2]))
print(("GATE OPEN" if all(res) else "GATE CLOSED") + f" — {sum(res)}/{len(res)}")

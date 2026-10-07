#!/usr/bin/env python3
"""verify_bp02_191.py — gate for BP-02 v1.3.191 (D-C293). Packages on GATE OPEN.
  A manifest 1.3.191, uuids + dependencies unchanged from 1.3.190
  B every JSON parses; node --check on every script
  C diff vs 1.3.190 = manifest.json + scripts/main.js changed, entities/zombie.json removed, nothing else
  D main.js diff = exactly the PW_VARIANTS block removed + the PW_BUILD line; no reference to VARIANT_SPECIES / onEntitySpawn /
    'ZOMBIE-PROOF' left; the BLOCK variant system (pw:randomize_variant, pw:variant_dump) intact
  E sheep.json untouched and still = Mojang 1.26.20 sheep + the pw:grass_block grazing pair
  F nothing in his stack reads the removed zombie property: no RP-06 / RP-07 / RP-08 entity, render controller or animation mentions
    pw:variant; no other BP script sets it on an entity
  P package -> /mnt/user-data/outputs/BP-02-AbsolutRealism-Tectonic-BP-v1_3_191.mcpack (archive == build dir)"""
import difflib, hashlib, json, re, subprocess, sys, zipfile
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
OLD, NEW, VER = ROOT / "_build/bp02-190", ROOT / "_build/bp02-191", "1.3.191"
OUT = Path("/mnt/user-data/outputs/BP-02-AbsolutRealism-Tectonic-BP-v1_3_191.mcpack")
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()

mo = json.loads((OLD / "manifest.json").read_text()); mn = json.loads((NEW / "manifest.json").read_text())
check("A manifest 1.3.191, uuids + dependencies unchanged", mn["header"]["version"] == [1, 3, 191] and all(x["version"] == [1, 3, 191] for x in mn["modules"])
      and mn["header"]["uuid"] == mo["header"]["uuid"] and [x["uuid"] for x in mn["modules"]] == [x["uuid"] for x in mo["modules"]]
      and mn["dependencies"] == mo["dependencies"] and mn["header"]["name"].endswith(VER))
bad = []
for p in NEW.rglob("*.json"):
    try: ML._parse_json(p.read_text(encoding="utf-8-sig"))
    except Exception as e: bad.append(f"{p.name}: {e}")
check("B every JSON parses", not bad, "; ".join(bad[:3]))
nc = [subprocess.run(["node", "--check", str(p)], capture_output=True).returncode for p in (NEW / "scripts").glob("*.js")]
check("B node --check on every script", nc and all(c == 0 for c in nc), f"{len(nc)} scripts")
tree = lambda d: {str(p.relative_to(d)): md5(p) for p in d.rglob("*") if p.is_file()}
to, tn = tree(OLD), tree(NEW)
changed = sorted(k for k in set(to) & set(tn) if to[k] != tn[k]); removed = sorted(set(to) - set(tn)); added = sorted(set(tn) - set(to))
check("C diff vs 1.3.190: manifest + main.js changed, zombie.json removed, nothing else", changed == ["manifest.json", "scripts/main.js"] and removed == ["entities/zombie.json"] and not added,
      f"changed {changed} removed {removed} added {added}")
a = (OLD / "scripts/main.js").read_text(encoding="utf-8").splitlines(); b = (NEW / "scripts/main.js").read_text(encoding="utf-8").splitlines()
d = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
plus = [l for l in d if l.startswith("+")]; minus = [l for l in d if l.startswith("-")]
blk = (ROOT / "_docs/bp02_191_removed_block.js").read_text(encoding="utf-8").splitlines()
nt = "\n".join(b)
check("D main.js diff = the PW_VARIANTS block + the PW_BUILD line only",
      plus == ['+const PW_BUILD = "1.3.191";'] and '-const PW_BUILD = "1.3.189";' in minus and len(minus) == len(blk) + 2 + 1,
      f"+{len(plus)} -{len(minus)} (block {len(blk)} lines + 2 blank + PW_BUILD)")
check("D no zombie-variant code left; the block variant system intact",
      not any(s in nt for s in ("VARIANT_SPECIES", "onEntitySpawn", "ZOMBIE-PROOF", "zombie variant system")) and "pw:randomize_variant" in nt and "pw:variant_dump" in nt)
sheep_o, sheep_n = OLD / "entities/sheep.json", NEW / "entities/sheep.json"
van = ML._parse_json((ROOT / "_intake/bedrock-samples/behavior_pack/entities/sheep.json").read_text(encoding="utf-8"))
ours = ML._parse_json(sheep_n.read_text(encoding="utf-8-sig"))
pairs = ours["minecraft:entity"]["components"]["minecraft:behavior.eat_block"]["eat_and_replace_block_pairs"]
vp = van["minecraft:entity"]["components"]["minecraft:behavior.eat_block"]["eat_and_replace_block_pairs"]
ours["minecraft:entity"]["components"]["minecraft:behavior.eat_block"]["eat_and_replace_block_pairs"] = [p for p in pairs if p.get("eat_block") != "pw:grass_block"]
check("E sheep.json untouched; = Mojang 1.26.20 sheep + the pw:grass_block grazing pair", md5(sheep_o) == md5(sheep_n) and ours == van
      and {"eat_block": "pw:grass_block", "replace_block": "dirt"} in pairs and len(pairs) == len(vp) + 1)
hits = []
for pack in ("rp06-1419", "rp07-1425", "rp08-148"):
    for sub in ("entity", "render_controllers", "animations", "animation_controllers"):
        for p in (ROOT / "_build" / pack / sub).rglob("*.json") if (ROOT / "_build" / pack / sub).exists() else []:
            if "pw:variant" in p.read_text(encoding="utf-8", errors="ignore"): hits.append(f"{pack}/{p.relative_to(ROOT / '_build' / pack)}")
for bp in ("bp01-135", "bp03-134", "stripmine-bp-134"):
    for p in (ROOT / "_build" / bp).rglob("*.js"):
        if re.search(r"setProperty\(\s*['\"]pw:variant", p.read_text(encoding="utf-8", errors="ignore")): hits.append(f"{bp}/{p.name}")
if re.search(r"setProperty\(\s*['\"]pw:variant", nt): hits.append("bp02-191/main.js")
check("F nothing in the stack reads or sets the removed zombie property pw:variant", not hits, str(hits[:5]))

ok = all(o for _, o in res)
if ok:
    tmp = OUT.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(NEW.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(NEW)).replace("\\", "/"))
    with zipfile.ZipFile(tmp) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    assert zh == {k: v for k, v in tree(NEW).items()}, "archive != build dir"
    if OUT.exists() and md5(OUT) != md5(tmp): tmp.unlink(); raise SystemExit("REFUSED: name exists with different bytes")
    tmp.replace(OUT)
    print(f"\nGATE OPEN {len(res)}/{len(res)}  PACKAGED {OUT.name} {OUT.stat().st_size:,} B md5 {md5(OUT)} ({len(zh)} files, archive == build dir)")
else:
    print(f"\nGATE CLOSED {sum(o for _, o in res)}/{len(res)}"); sys.exit(1)

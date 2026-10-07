#!/usr/bin/env python3
"""verify_bp02_195.py — gate for BP-02 v1.3.195 (build_bp02_195.py, the leaf full cut). Static checks only rule OUT (P1).
  A  manifest 1.3.195, uuids + dependencies unchanged          B  every JSON parses; node --check on every script
  C  diff vs 1.3.194 = manifest + main.js + the 9 leaf blocks, nothing added or removed
  D  main.js diff = exactly the 4 side-flag writes out + PW_BUILD 1.3.195
  E  each leaf block = the old block minus the 4 states, and v1-v6 geometry = the same identifier without bone_visibility; v0
     permutation byte-for-byte identical (the far cube untouched); 168 permutations each
  F  nothing anywhere reads or writes the removed states (BP-02 + every other BP in his stack + the TestRunner + our tools)
  G  api_audit: the same 3 pre-existing flags as 1.3.194         H  the mob-light mock still 14/14
  I  custom permutations after the cut (census) — about 19,500"""
import difflib, hashlib, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import block_state_census as BC

ROOT = Path("/home/claude")
OLD, NEW = ROOT / "_build/bp02-194", ROOT / "_build/bp02-195"
DROP = ("pw:open_n", "pw:open_e", "pw:open_s", "pw:open_w")
WOODS = ("acacia", "birch", "cherry", "dark_oak", "jungle", "mangrove", "oak", "pale_oak", "spruce")
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()

mo = json.loads((OLD / "manifest.json").read_text(encoding="utf-8-sig")); mn = json.loads((NEW / "manifest.json").read_text(encoding="utf-8-sig"))
check("A manifest 1.3.195, uuids + dependencies unchanged", mn["header"]["version"] == [1, 3, 195] and all(x["version"] == [1, 3, 195] for x in mn["modules"])
      and mn["header"]["uuid"] == mo["header"]["uuid"] and [x["uuid"] for x in mn["modules"]] == [x["uuid"] for x in mo["modules"]]
      and mn["dependencies"] == mo["dependencies"])
bad = []
for p in NEW.rglob("*.json"):
    try: ML._parse_json(p.read_text(encoding="utf-8-sig"))
    except Exception as e: bad.append(f"{p.name}: {e}")
check("B every JSON parses", not bad, "; ".join(bad[:3]))
nc = {p.name: subprocess.run(["node", "--check", str(p)], capture_output=True).returncode for p in (NEW / "scripts").glob("*.js")}
check("B node --check on every script", nc and all(c == 0 for c in nc.values()), f"{len(nc)} scripts")
tree = lambda d: {str(p.relative_to(d)): md5(p) for p in d.rglob("*") if p.is_file()}
to, tn = tree(OLD), tree(NEW)
changed = sorted(k for k in set(to) & set(tn) if to[k] != tn[k]); removed = sorted(set(to) - set(tn)); added = sorted(set(tn) - set(to))
want = sorted(["manifest.json", "scripts/main.js"] + [f"blocks/{w}_leaves.json" for w in WOODS])
check("C diff = manifest + main.js + 9 leaf blocks", changed == want and not added and not removed, f"changed {len(changed)} added {added} removed {removed}")
a = (OLD / "scripts/main.js").read_text(encoding="utf-8").split("\n"); b = (NEW / "scripts/main.js").read_text(encoding="utf-8").split("\n")
dl = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---"))]
minus = [l for l in dl if l.startswith("-")]; plus = [l for l in dl if l.startswith("+")]
ok = (len(minus) == 5 and sum('.withState("pw:open_' in l for l in minus) == 4 and any('PW_BUILD = "1.3.194"' in l for l in minus)
      and len(plus) == 1 and 'PW_BUILD = "1.3.195"' in plus[0])
check("D main.js diff = the 4 side-flag writes out + PW_BUILD 1.3.195", ok, f"-{len(minus)} +{len(plus)}")
okE, perms, v0same = True, {}, True
for w in WOODS:
    do = ML._parse_json((OLD / f"blocks/{w}_leaves.json").read_text(encoding="utf-8-sig")); dn = ML._parse_json((NEW / f"blocks/{w}_leaves.json").read_text(encoding="utf-8-sig"))
    v0o = next(p for p in do["minecraft:block"]["permutations"] if p["condition"] == "q.block_state('pw:variant') == 0")
    v0n = next(p for p in dn["minecraft:block"]["permutations"] if p["condition"] == "q.block_state('pw:variant') == 0")
    v0same &= v0o == v0n
    for k in DROP: do["minecraft:block"]["description"]["states"].pop(k)
    for perm in do["minecraft:block"]["permutations"]:
        g = perm["components"].get("minecraft:geometry")
        if isinstance(g, dict): perm["components"]["minecraft:geometry"] = g["identifier"]
    okE &= do == dn
    perms[w] = BC.block_perms(dn["minecraft:block"]["description"])[0]
check("E leaf blocks = old minus the 4 states + bone_visibility; v0 untouched; 168 permutations each", okE and v0same and set(perms.values()) == {168}, str(perms))
hits = []
scan = [NEW, ROOT / "_build/bp01-135", ROOT / "_build/bp03-134", ROOT / "_build/stripmine-bp-136", ROOT / "_build/markers-0.2.1",
        ROOT / "tools/testrunner_src"] + [d for d in Path("/tmp/claude-0/bps").iterdir() if d.is_dir()]
for d in scan:
    for p in d.rglob("*"):
        if p.suffix in (".js", ".json", ".mjs") and p.is_file() and p.name != "manifest.json":
            t = p.read_text(encoding="utf-8", errors="ignore")
            if any(k in t for k in DROP): hits.append(str(p))
check("F nothing reads or writes the removed states (every BP in his stack, the runner, our tools)", not hits, str(hits[:4]))
au = subprocess.run([sys.executable, str(ROOT / "tools/api_audit.py"), str(NEW)], capture_output=True, text=True, timeout=600).stdout
flags = [l for l in au.split("\n") if l.strip().startswith("scripts/")]
au_old = subprocess.run([sys.executable, str(ROOT / "tools/api_audit.py"), str(OLD)], capture_output=True, text=True, timeout=600).stdout
flags_old = [l for l in au_old.split("\n") if l.strip().startswith("scripts/")]
check("G api_audit: the same pre-existing flags as 1.3.194", flags == flags_old and len(flags) == 3, "\n".join(flags))
mk = subprocess.run(["node", str(ROOT / "tools/bp02_src/test_mob_light.mjs")], capture_output=True, text=True, cwd=str(ROOT / "tools/bp02_src"))
check("H mob-light mock run", mk.returncode == 0 and "14/14" in mk.stdout, (mk.stdout + mk.stderr).strip()[-200:])
BC.PACKS = {"BP-02 1.3.194": OLD, "StripMine BP 1.3.6": ROOT / "_build/stripmine-bp-136"}
before = sum(r["perms"] for r in BC.census() if "perms" in r)
BC.PACKS = {"BP-02 1.3.195": NEW, "StripMine BP 1.3.6": ROOT / "_build/stripmine-bp-136"}
tot = sum(r["perms"] for r in BC.census() if "perms" in r)
VANILLA = 66346 - 64728          # the 1c census: the game's total minus ours = everything that is not ours
check(f"I custom permutations after the full cut: {tot:,} = {before:,} - 9 x (2,688 - 168); world about {tot + VANILLA:,} (was {before + VANILLA:,})",
      tot == before - 9 * (2688 - 168), "")
print(f"\n{'GATE OPEN' if all(r[1] for r in res) else 'GATE SHUT'} {sum(r[1] for r in res)}/{len(res)}")
sys.exit(0 if all(r[1] for r in res) else 1)

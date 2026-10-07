#!/usr/bin/env python3
"""verify_phase1.py — GATE for the phase-1 name-audit builds (RP-03 .57, RP-01 .103, RP-05 .47, RP-04 .133). Packages only if every check passes."""
import json, os, re, sys, hashlib, zipfile, subprocess, importlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import block_census as BC
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); VAN = ROOT / "_intake/bedrock-samples/resource_pack"
results = []
def check(n, ok, d=""):
    results.append((n, bool(ok), d)); print(("PASS " if ok else "FAIL ") + n + (f" — {d}" if d else "")); return bool(ok)
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(root): return {str(p.relative_to(root)).replace(os.sep, "/"): p for p in root.rglob("*") if p.is_file()}
van_files = set(subprocess.run(["git", "-C", str(ROOT / "_intake/bedrock-samples"), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split("\n"))
van_stems = {p[len("resource_pack/"):].rsplit(".", 1)[0] for p in van_files if p.startswith("resource_pack/textures/")}
added = load(ROOT / "_logs/phase1_added.json")
PACKS = {"RP-03": (ROOT / "_build/src/RP-03-v1_3_56", ROOT / "_build/rp03-57", [1, 3, 57], "RP-03-AbsolutRealism-PBR-RP-v1_3_57.mcpack"),
         "RP-01": (ROOT / "_build/src/RP-01-v1_3_102", ROOT / "_build/rp01-103", [1, 3, 103], "RP-01-AbsolutRealism-Tectonic-RP-v1_3_103.mcpack"),
         "RP-05": (ROOT / "_build/src/RP-05-v1_3_46", ROOT / "_build/rp05-47", [1, 3, 47], "RP-05-AbsolutRealism-Flora-RP-v1_3_47.mcpack"),
         "RP-04": (ROOT / "_build/rp04-132", ROOT / "_build/rp04-133", [1, 3, 133], "RP-04-AbsolutRealism-Basic-RP-v1_3_133.mcpack")}
COMP = re.compile(r"(_mer|_n|_normal|_heightmap)$")
for tag, (src, dst, ver, outname) in PACKS.items():
    a, b = files(src), files(dst)
    diff = {n for n in set(a) | set(b) if n not in a or n not in b or a[n].read_bytes() != b[n].read_bytes()}
    expect = set(added[tag]) | {"manifest.json"} | ({"PW-DEPENDENCIES.md"} if tag == "RP-04" else set())
    check(f"{tag} I change set = added files + manifest{' + ledger' if tag == 'RP-04' else ''}", diff == expect, sorted(diff ^ expect)[:10])
    check(f"{tag} I nothing replaced (every added path is new to the pack)", all(n not in a for n in added[tag]))
    # every added COLOUR path (not a companion / texture set) is a vanilla path: the name oracle
    colours = [n for n in added[tag] if n.endswith(".png") and not COMP.search(n[:-4])]
    bad = [n for n in colours if n[:-4] not in van_stems]
    check(f"{tag} N every added colour path exists in vanilla 1.26.50 ({len(colours)} paths)", not bad, bad)
    # texture sets: strict json, references resolve
    tsets = [n for n in added[tag] if n.endswith(".texture_set.json")]
    ok = True; why = []
    for n in tsets:
        try: d = json.loads((dst / n).read_text(encoding="utf-8"))["minecraft:texture_set"]
        except Exception as e: ok = False; why.append(f"{n}: {e}"); continue
        folder = (dst / n).parent
        for k, v in d.items():
            if isinstance(v, str) and not (folder / f"{v}.png").exists() and not (folder / f"{v}.tga").exists(): ok = False; why.append(f"{n}: {k} -> {v} missing")
    check(f"{tag} T {len(tsets)} texture sets parse and resolve", ok, why[:6])
    m = load(dst / "manifest.json"); v = ".".join(map(str, ver))
    check(f"{tag} V manifest v{v} stamped (version, modules, name, description-stamp law)", m["header"]["version"] == ver and all(x["version"] == ver for x in m["modules"]) and f"v{v}" in m["header"]["name"] and m["header"]["description"].startswith(f"v{v} ("))
# entity layout sanity: each added entity texture vs vanilla alpha layout
def mask(im, grid):
    a = np.array(im.convert("RGBA"))[..., 3]; s = a.shape[0] // grid[1]; t = a.shape[1] // grid[0]
    return a.reshape(grid[1], s, grid[0], t).max(axis=(1, 3)) > 0
worst = []
for n in added["RP-04"]:
    v = VAN / n
    if not v.exists(): continue
    vi = Image.open(v); pi = Image.open(PACKS["RP-04"][1] / n)
    if pi.width % vi.width or pi.height % vi.height or pi.width // vi.width != pi.height // vi.height: worst.append((n, "size ratio")); continue
    mv, mp = mask(vi, vi.size), mask(pi, vi.size); iou = (mv & mp).sum() / max(1, (mv | mp).sum())
    if iou < 0.9: worst.append((n, round(float(iou), 3)))
check(f"RP-04 E every added entity texture keeps vanilla's layout (alpha IoU >= 0.9 on the vanilla grid, {len(added['RP-04'])} files)", not worst, worst)
# block census on the new trees: the mapped stems must now resolve to ours; MIXED must drop; no BROKEN
before = load(ROOT / "_logs/block_census_2026-09-22.json")["blocks"]
rep = BC.main(str(ROOT / "_packs/STACK-LIST-2026-09-21.txt"), str(ROOT / "_logs/block_census_phase1.json"), str(ROOT / "_docs/BLOCK-CENSUS-2026-09-22-phase1.md"),
              overrides={"RP-03": str(PACKS["RP-03"][1]), "RP-01": str(PACKS["RP-01"][1]), "RP-05": str(PACKS["RP-05"][1]), "RP-04": str(PACKS["RP-04"][1])})
mapped = {n[:-4] for t in ("RP-03", "RP-01", "RP-05") for n in added[t] if n.endswith(".png") and not COMP.search(n[:-4])}
still_van = sorted({s["path"] for v in rep.values() for s in v["slots"] if s["provider"] == "VANILLA" and s["path"] in mapped})
check(f"C none of the {len(mapped)} mapped block paths resolves to vanilla any more", not still_van, still_van[:8])
mixed_before = sum(1 for v in before.values() if v["class"] == "MIXED"); mixed_after = sum(1 for v in rep.values() if v["class"] == "MIXED")
fixed_blocks = sorted(b for b, v in before.items() if v["class"] == "MIXED" and rep.get(b, {}).get("class") == "ALL-OURS")
check(f"C MIXED blocks {mixed_before} -> {mixed_after}; {len(fixed_blocks)} blocks now ALL-OURS", mixed_after < mixed_before, ", ".join(fixed_blocks))
check("C no BROKEN block introduced", not [b for b, v in rep.items() if v["class"] == "BROKEN" and before.get(b, {}).get("class") != "BROKEN"])
for key in ("furnace", "blast_furnace", "smoker", "dispenser", "dropper", "powered_repeater", "unpowered_comparator", "observer", "iron_door", "stone_slab", "double_stone_slab3", "fletching_table", "end_portal_frame", "lit_pumpkin"):
    check(f"C {key} ALL-OURS", rep.get(key, {}).get("class") == "ALL-OURS", rep.get(key, {}).get("class"))
failed = [n for n, ok, _ in results if not ok]
if failed: print(f"\nGATE CLOSED — {failed}"); sys.exit(1)
# package
outs = []
for tag, (src, dst, ver, outname) in PACKS.items():
    out = OUT / outname
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(dst.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(dst)).replace(os.sep, "/"))
    with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    check(f"{tag} Z1 from-zip identity", zh == {n: md5(p) for n, p in files(dst).items()})
    r = subprocess.run(["python3", str(ROOT / "tools/verify_pack_versions.py"), str(out)], capture_output=True, text=True); print(r.stdout.strip())
    check(f"{tag} Z2 version-spot gate", r.returncode == 0, r.stderr[:200])
    outs.append(out)
failed = [n for n, ok, _ in results if not ok]
if failed:
    for o in outs: o.unlink(missing_ok=True)
    print(f"\nGATE CLOSED at packaging — {failed}"); sys.exit(1)
print(f"\nGATE OPEN — {len(results)} checks")
for o in outs: print(f"  {o.name} {o.stat().st_size:,} B md5 {md5(o)}")

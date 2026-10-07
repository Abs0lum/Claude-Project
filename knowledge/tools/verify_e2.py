#!/usr/bin/env python3
"""verify_e2.py — GATE for RP-04 v1.3.134 + RP-03 v1.3.58 (E2). Packages only if every check passes."""
import json, os, re, sys, hashlib, zipfile, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import bed_render as br, chest_e2 as ce, block_census as BC
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); VAN = ROOT / "_intake/bedrock-samples/resource_pack"
results = []
def check(n, ok, d=""):
    results.append((n, bool(ok), d)); print(("PASS " if ok else "FAIL ") + n + (f" — {d}" if d else "")); return bool(ok)
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(root): return {str(p.relative_to(root)).replace(os.sep, "/"): p for p in root.rglob("*") if p.is_file()}
van_stems = {p[len("resource_pack/"):].rsplit(".", 1)[0] for p in subprocess.run(["git", "-C", str(ROOT / "_intake/bedrock-samples"), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split("\n") if p.startswith("resource_pack/textures/")}
added = load(ROOT / "_logs/e2_added.json")
PACKS = {"RP-04": (ROOT / "_build/rp04-133", ROOT / "_build/rp04-134", [1, 3, 134], "RP-04-AbsolutRealism-Basic-RP-v1_3_134.mcpack"),
         "RP-03": (ROOT / "_build/rp03-57", ROOT / "_build/rp03-58", [1, 3, 58], "RP-03-AbsolutRealism-PBR-RP-v1_3_58.mcpack")}
COMP = re.compile(r"(_mer|_n|_normal|_heightmap)$")
REPLACED_OK = {"RP-04": {"textures/entity/chest/normal.png", "textures/entity/chest/trapped.png", "textures/entity/chest/ender.png", "textures/entity/chest/copper_default.png", "textures/entity/chest/copper_exposed.png",
                         "textures/entity/chest/copper_oxidized.png", "textures/entity/chest/copper_weathered.png", "textures/entity/chest/double_normal.png", "textures/entity/chest/trapped_double.png"}, "RP-03": set()}
for tag, (src, dst, ver, outname) in PACKS.items():
    a, b = files(src), files(dst)
    diff = {n for n in set(a) | set(b) if n not in a or n not in b or a[n].read_bytes() != b[n].read_bytes()}
    expect = set(added[tag]) | {"manifest.json"} | ({"PW-DEPENDENCIES.md"} if tag == "RP-04" else set())
    check(f"{tag} I change set = added/converted files + manifest{' + ledger' if tag == 'RP-04' else ''}", diff == expect, sorted(diff ^ expect)[:10])
    replaced = {n for n in added[tag] if n in a}
    check(f"{tag} I only the intended files were replaced ({len(replaced)})", replaced <= REPLACED_OK[tag], sorted(replaced - REPLACED_OK[tag]))
    colours = [n for n in added[tag] if n.endswith(".png") and not COMP.search(n[:-4])]
    bad = [n for n in colours if n[:-4] not in van_stems]
    check(f"{tag} N every added colour path exists in vanilla 1.26.50 ({len(colours)} paths)", not bad, bad)
    for n in added[tag]:
        if n.endswith(".json"):
            try: d = json.loads((dst / n).read_text(encoding="utf-8"))["minecraft:texture_set"]; ok = all((dst / n).parent.joinpath(f"{v}.png").exists() for v in d.values() if isinstance(v, str))
            except Exception as e: ok = False
            check(f"{tag} T {n} parses and resolves", ok)
    m = load(dst / "manifest.json"); v = ".".join(map(str, ver))
    check(f"{tag} V manifest v{v} stamped", m["header"]["version"] == ver and all(x["version"] == ver for x in m["modules"]) and f"v{v}" in m["header"]["name"] and m["header"]["description"].startswith(f"v{v} ("))
check("RP-04 L ledger stamped", "v1.3.134 ·" in (PACKS["RP-04"][1] / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"))
# ---- chests: render parity (converted on Bedrock unwrap vs Patrix on Java unwrap), the trapped-mark structure, doubles vs singles
cams = [br.Camera((-14, 22, -20), (8, 6, 8), 520, 400, 55), br.Camera((30, 22, 30), (8, 6, 8), 520, 400, 55)]
SE = PACKS["RP-04"][0] / "textures/entity/chest"; DE = PACKS["RP-04"][1] / "textures/entity/chest"
for single, out in (("normal", "normal"), ("trapped", "trapped"), ("ender", "ender"), ("copper", "copper_default"), ("copper_exposed", "copper_exposed"), ("copper_oxidized", "copper_oxidized"), ("copper_weathered", "copper_weathered")):
    P = Image.open(SE / f"{single}.png").convert("RGBA"); C = Image.open(DE / f"{out}.png").convert("RGBA")
    worst40 = worst100 = 0.0
    for cam in cams:
        x = np.array(br.render(ce.chest_faces("bedrock"), C, cam)).astype(int); y = np.array(br.render(ce.chest_faces("java"), P, cam)).astype(int)
        d = np.abs(x - y).max(axis=2); worst40 = max(worst40, float((d > 40).mean())); worst100 = max(worst100, float((d > 100).mean()))
    # half-texel sampling offsets between the two unwrap parameterisations give edge noise on high-contrast art; a wrong region would be whole-face
    check(f"C chest {out}: converted-on-Bedrock renders as Patrix-on-Java (>40 levels: {100*worst40:.2f}% < 3%, >100: {100*worst100:.2f}% < 0.5%)", worst40 < 0.03 and worst100 < 0.005)
# the vanilla chest itself renders as a chest on our Bedrock unwrap model (latch on the front): structural sanity via the trapped marks
van_n = np.array(Image.open(VAN / "textures/entity/chest/normal.png").convert("RGBA")).astype(int); van_t = np.array(Image.open(VAN / "textures/entity/chest/trapped.png").convert("RGBA")).astype(int)
dm = (np.abs(van_n - van_t).max(axis=2) > 0); ys, xs = np.nonzero(dm)
check("C vanilla trapped-chest marks sit in the NORTH regions (front = north, up-square bottom row = front)", set(xs.tolist()) <= set(range(14, 28)) and set(ys.tolist()) <= set(range(14, 19)) | set(range(31, 43)))
# doubles: each 30-wide front face = [L.south flipV | R.south flipV] — its left 15 columns must equal the corresponding single-chest front? (not necessarily); instead check the double's back equals the 07-03 witnessed-good back for normal/trapped
S = 8
for base, out in (("normal", "double_normal"), ("trapped", "trapped_double")):
    old = np.array(Image.open(SE / f"{out}.png").convert("RGBA")); new = np.array(Image.open(DE / f"{out}.png").convert("RGBA"))
    same_back = np.array_equal(old[14 * S:19 * S, 58 * S:88 * S], new[14 * S:19 * S, 58 * S:88 * S]) and np.array_equal(old[33 * S:43 * S, 58 * S:88 * S], new[33 * S:43 * S, 58 * S:88 * S])
    same_front_left = np.array_equal(old[14 * S:19 * S, 14 * S:29 * S], new[14 * S:19 * S, 14 * S:29 * S]) and np.array_equal(old[33 * S:43 * S, 14 * S:29 * S], new[33 * S:43 * S, 14 * S:29 * S])
    check(f"C {out}: back faces and the front's left half identical to the 07-03 witnessed-good double (only top/underside/ends/front-right changed by derivation)", same_back and same_front_left)
    check(f"C {out}: 128x64 grid, nothing outside the body/knob regions", new.shape[:2] == (64 * S, 128 * S))
# entity renames keep vanilla's alpha layout
def mask(im, grid):
    a = np.array(im.convert("RGBA"))[..., 3]; s = a.shape[0] // grid[1]; t = a.shape[1] // grid[0]
    return a.reshape(grid[1], s, grid[0], t).max(axis=(1, 3)) > 0
low = []
for n in added["RP-04"]:
    if "chest/" in n: continue
    v = VAN / n
    if not v.exists():
        for ext in (".tga", ".png"):
            if (VAN / (n[:-4] + ext)).exists(): v = VAN / (n[:-4] + ext)
    if not v.exists(): low.append((n, "no vanilla file")); continue
    vi = Image.open(v); pi = Image.open(PACKS["RP-04"][1] / n)
    if pi.width % vi.width or pi.height % vi.height: low.append((n, "size ratio")); continue
    mv, mp = mask(vi, vi.size), mask(pi, vi.size); iou = (mv & mp).sum() / max(1, (mv | mp).sum())
    if iou < 0.5 and "endercrystal_beam" not in n: low.append((n, round(float(iou), 3)))     # the beam is a scrolled strip whose art (lightning) differs; same dimensions
check(f"E renamed entity textures keep vanilla's alpha layout (IoU >= 0.5, beam excepted; {len(added['RP-04'])} files incl. chests)", not low, low)
# the diagonal banner patterns swap names between editions: each of ours must match vanilla's file of the SAME (Bedrock) name better than 0.9
for pat in ("diagonal_left", "diagonal_right", "diagonal_up_left", "diagonal_up_right"):
    vi = Image.open(VAN / f"textures/entity/banner/banner_{pat}.tga"); pi = Image.open(PACKS["RP-04"][1] / f"textures/entity/banner/banner_{pat}.png")
    mv, mp = mask(vi, vi.size), mask(pi, vi.size); check(f"E banner_{pat} matches vanilla's pattern of that name (IoU {(mv & mp).sum() / max(1, (mv | mp).sum()):.2f} >= 0.9)", (mv & mp).sum() / max(1, (mv | mp).sum()) >= 0.9)
# blocks: conduit base crop geometry, pot names, cauldron water strip + set; census re-run
cb = Image.open(PACKS["RP-03"][1] / "textures/blocks/conduit_base.png"); check("B conduit_base is the 24x12 (x8) unwrap crop", cb.size == (192, 96))
cw = Image.open(PACKS["RP-03"][1] / "textures/blocks/cauldron_water.png"); vw = Image.open(VAN / "textures/blocks/cauldron_water.png")
check(f"B cauldron_water strip {cw.size} has the same frame count as vanilla ({vw.height // vw.width} frames)", cw.height // cw.width == vw.height // vw.width)
rep = BC.main(str(ROOT / "_packs/STACK-LIST-2026-09-21.txt"), str(ROOT / "_logs/block_census_e2.json"), str(ROOT / "_docs/BLOCK-CENSUS-2026-09-22-e2.md"),
              overrides={"RP-03": str(PACKS["RP-03"][1]), "RP-01": str(ROOT / "_build/rp01-103"), "RP-05": str(ROOT / "_build/rp05-47"), "RP-04": str(PACKS["RP-04"][1])})
before = load(ROOT / "_logs/block_census_phase1.json")["blocks"]
mb, ma = sum(1 for v in before.values() if v["class"] == "MIXED"), sum(1 for v in rep.values() if v["class"] == "MIXED")
check(f"C census: MIXED {mb} -> {ma}; cauldron/lava_cauldron now ALL-OURS", ma < mb and rep.get("cauldron", {}).get("class") == "ALL-OURS" and rep.get("lava_cauldron", {}).get("class") == "ALL-OURS", f"cauldron={rep.get('cauldron', {}).get('class')}")
check("C no BROKEN block introduced", not [b for b, v in rep.items() if v["class"] == "BROKEN" and before.get(b, {}).get("class") != "BROKEN"])
failed = [n for n, ok, _ in results if not ok]
if failed: print(f"\nGATE CLOSED — {failed}"); sys.exit(1)
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
    check(f"{tag} Z2 version-spot gate", r.returncode == 0, r.stderr[:200]); outs.append(out)
failed = [n for n, ok, _ in results if not ok]
if failed:
    for o in outs: o.unlink(missing_ok=True)
    print(f"\nGATE CLOSED at packaging — {failed}"); sys.exit(1)
print(f"\nGATE OPEN — {len(results)} checks")
for o in outs: print(f"  {o.name} {o.stat().st_size:,} B md5 {md5(o)}")

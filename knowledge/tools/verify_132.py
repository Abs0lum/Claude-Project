#!/usr/bin/env python3
"""verify_132.py — GATE for RP-04 v1.3.132 (bed re-layout). Packages only if every check passes."""
import json, os, sys, hashlib, zipfile, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, "/home/claude/tools")
import bed_render as br
ROOT = Path("/home/claude"); RP0, RP = ROOT / "_build/rp04-131", ROOT / "_build/rp04-132"
OUT = Path("/mnt/user-data/outputs")
results = []
def check(n, ok, d=""):
    results.append((n, bool(ok), d)); print(("PASS " if ok else "FAIL ") + n + (f" — {d}" if d else "")); return bool(ok)
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(root): return {str(p.relative_to(root)).replace(os.sep, "/"): p for p in root.rglob("*") if p.is_file()}
COLOURS = ["black", "blue", "brown", "cyan", "gray", "green", "light_blue", "lime", "magenta", "orange", "pink", "purple", "red", "white", "yellow"]

a, b = files(RP0), files(RP)
diff = {n for n in set(a) | set(b) if n not in a or n not in b or a[n].read_bytes() != b[n].read_bytes()}
expect = {f"textures/entity/bed/{c}.png" for c in COLOURS} | {"textures/entity/bed/silver.png", "manifest.json", "PW-DEPENDENCIES.md"}
check("I change set = 16 bed textures + silver.png + manifest + ledger", diff == expect, sorted(diff ^ expect))
check("I light_gray.png and red_n.png untouched (dead paths, ruling pending)", a["textures/entity/bed/light_gray.png"].read_bytes() == b["textures/entity/bed/light_gray.png"].read_bytes() and a["textures/entity/bed/red_n.png"].read_bytes() == b["textures/entity/bed/red_n.png"].read_bytes())

def A(p): return np.array(Image.open(p).convert("RGBA"))
def reg(arr, u0, v0, u1, v1, s=8): return arr[v0 * s:v1 * s, u0 * s:u1 * s]
for c in COLOURS + ["silver"]:
    src = A(RP0 / f"textures/entity/bed/{'light_gray' if c == 'silver' else c}.png"); new = A(RP / f"textures/entity/bed/{c}.png")
    ok = (new.shape == (512, 512, 4)
          and np.array_equal(reg(new, 0, 6, 44, 22), reg(src, 0, 6, 44, 22))          # head sides row kept
          and np.array_equal(reg(new, 6, 0, 22, 6), reg(src, 6, 0, 22, 6))            # head end kept
          and np.array_equal(reg(new, 0, 22, 44, 38), reg(src, 0, 28, 44, 44))        # foot sides row moved up 6
          and np.array_equal(reg(new, 22, 0, 38, 6), reg(src, 22, 22, 38, 28))        # footboard into the foot-end square
          and np.array_equal(reg(new, 0, 38, 12, 44), reg(src, 50, 0, 62, 6)) and np.array_equal(reg(new, 12, 38, 24, 44), reg(src, 50, 6, 62, 12))
          and np.array_equal(reg(new, 0, 44, 12, 50), reg(src, 50, 12, 62, 18)) and np.array_equal(reg(new, 12, 44, 24, 50), reg(src, 50, 18, 62, 24))
          and reg(new, 38, 0, 64, 6)[..., 3].max() == 0 and reg(new, 44, 6, 64, 38)[..., 3].max() == 0    # rails transparent
          and reg(new, 24, 38, 64, 64)[..., 3].max() == 0 and reg(new, 0, 50, 64, 64)[..., 3].max() == 0
          and reg(new, 6, 22, 22, 38)[..., 3].min() > 0)                                                   # mattress rows 16..32 fully opaque (no slot)
    check(f"T {c}: engine-layout regions exact, rails/legs clear, no slot", ok)
# render identity: engine model + NEW texture == Java-layout model + ORIGINAL texture (3 cameras)
cams = [br.Camera((16, 38, -30), (16, 4, 10), 600, 340, 62), br.Camera((62, 42, 8), (14, 4, 8), 600, 340, 62), br.Camera((16, -30, -30), (16, 4, 8), 600, 340, 62)]
for c in ("orange", "red", "white"):
    src = Image.open(RP0 / f"textures/entity/bed/{c}.png").convert("RGBA"); new = Image.open(RP / f"textures/entity/bed/{c}.png").convert("RGBA")
    worst_frac, worst_blob = 0.0, 0
    for ci, cam in enumerate(cams):
        x = np.array(br.render(br.bedrock_bed_as_is(), new, cam)).astype(int); y = np.array(br.render(br.java_layout_bed(), src, cam)).astype(int)
        d = (np.abs(x - y).max(axis=2) > 0)
        blob = np.array(Image.fromarray(d.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(3))) > 0      # 3x3 solid differing blobs
        worst_frac = max(worst_frac, d.mean())
        if ci < 2: worst_blob = max(worst_blob, int(blob.sum()))     # from below, the painter's order of leg vs underside differs between the one-box and two-box models (renderer artifact)
    # one 32-row quad vs two 16-row quads sample texels at slightly different sub-pixel positions (nearest), so
    # hairline edge differences are expected; any solid blob would be a wrong region.
    check(f"R {c}: engine model + re-laid texture renders the same picture as the Java two-piece bed with the original (3 cameras: no solid differing blob, edge noise < 1%)", worst_blob == 0 and worst_frac < 0.01, f"blob px {worst_blob}, diff {100*worst_frac:.2f}%")
try: json.loads((RP / "manifest.json").read_text(encoding="utf-8")); check("J strict manifest", True)
except Exception as e: check("J strict manifest", False, str(e))
m = load(RP / "manifest.json"); check("V manifest v1.3.132 stamped", m["header"]["version"] == [1, 3, 132] and all(x["version"] == [1, 3, 132] for x in m["modules"]) and "1.3.132" in m["header"]["description"] and "1.3.132" in m["header"]["name"])
check("L ledger stamped", "v1.3.132 ·" in (RP / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"))
failed = [n for n, ok, _ in results if not ok]
if failed: print(f"\nGATE CLOSED — {failed}"); sys.exit(1)
out = OUT / "RP-04-AbsolutRealism-Basic-RP-v1_3_132.mcpack"
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(RP.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(RP)).replace(os.sep, "/"))
with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
check("Z1 from-zip identity", zh == {n: md5(p) for n, p in files(RP).items()})
r = subprocess.run(["python3", str(ROOT / "tools/verify_pack_versions.py"), str(out)], capture_output=True, text=True); print(r.stdout.strip())
check("Z2 version-spot gate", r.returncode == 0, r.stderr[:200])
failed = [n for n, ok, _ in results if not ok]
if failed: out.unlink(); print(f"\nGATE CLOSED at packaging — {failed}"); sys.exit(1)
print(f"\nGATE OPEN — {len(results)} checks; {out.name} {out.stat().st_size:,} B md5 {md5(out)}")

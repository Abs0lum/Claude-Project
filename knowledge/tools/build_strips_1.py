#!/usr/bin/env python3
"""build_strips_1.py — CAPPED-STRIP REPAIR round 1 (D-C262, Abs0lum 22:42 "look for similar issues and fix them as well").

Finding (stack census 09-27): at some point a 'long side <= 256' resize pass ran over RP-04, RP-10 and RP-05.  Every tall
flipbook strip it touched became a sliver (lava_flow 128x6144 -> 5x256, torch 128x2304 -> 14x256, lantern 128x384 -> 85x256,
fire 128x3840 -> 8x256, kelp_top 128x2560 -> 13x256 ...) and those slivers sit ABOVE RP-03's intact 128x strips in his pack
order, so the game draws the sliver.  This build:
  RP-04 v1.3.140  deletes every capped textures/blocks file that has an intact RP-03 twin (rule-selected, listed in the report);
                  restores the NETHER PORTAL from the Patrix 1.21.11 128x source (colour 128x4096, normal converted LabPBR->Bedrock,
                  MERS by lesson #156 tiled to the strip); replaces fire_0/fire_1/soul_fire_0/soul_fire_1 with the Patrix
                  30-frame strips and sets their flipbook frame order from the Patrix .mcmeta.
  RP-10 v1.3.41   deletes torch/soul_torch/copper_torch (RP-03 twins); rebuilds the FIRE family — fire_0/fire_1 + the four
                  per-instance variants a/b/c/d (the old a-d were 8x256 slivers of unknown recipe; the new ones are the Patrix strip
                  started at four different frames so neighbouring fires burn out of phase) + soul_fire_0/1; flipbook lists -> 30.
  RP-05 v1.3.50   deletes kelp_top.png, seagrass.png, kelp.png, nether_wart_stage2.png (RP-03 twins; vanilla kelp top + nether wart
                  stage 2 draw the intact strips again).
Everything else in the three packs is byte-identical (the gate asserts the diff).  Sources: _build/rp0X-*, RP-03 1.3.60,
_intake/patrix128/pull1b + pull2 (range-read from Patrix_1.21.11_128x_basic.zip, Drive 1NCU1Co22xCPTG3Zn5uU6ZnC7abdswSpD)."""
import json, os, re, shutil, sys, time
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
DATE = "2026-09-27"
RP3 = ROOT / "_build/rp03-60"
PAT1, PAT2 = ROOT / "_intake/patrix128/pull1b/assets/minecraft/textures/block", ROOT / "_intake/patrix128/pull2"
PACKS = {
    "RP-04": {"src": ROOT / "_build/rp04-139", "dst": ROOT / "_build/rp04-140", "ver": [1, 3, 140], "name": "AbsolutRealism Basic RP v1.3.140"},
    "RP-10": {"src": ROOT / "_build/rp10-140", "dst": ROOT / "_build/rp10-141", "ver": [1, 3, 41], "name": "AbsolutRealism Terrain RP v1.3.41"},
    "RP-05": {"src": ROOT / "_build/rp05-49", "dst": ROOT / "_build/rp05-50", "ver": [1, 3, 50], "name": "AbsolutRealism Flora RP v1.3.50"},
}
FIRE_ORDER = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # Patrix fire_0.png.mcmeta
FIRE_OFFSETS = {"a": 0, "b": 8, "c": 15, "d": 23}
REPORT = {}

def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD {m}\n")

def jl(p): return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
def jsave(p, o): Path(p).write_text(json.dumps(o, indent=1), encoding="utf-8")
def size(p):
    try: return Image.open(p).size
    except Exception: return None
def rgba(p): return np.asarray(Image.open(p).convert("RGBA")).astype(np.uint8)
def save(a, p): Image.fromarray(a.astype(np.uint8), "RGBA").save(p)

def mers_156(spec):
    """Lesson #156 (CONFIRMED v1.2.32) — LabPBR _s -> Bedrock MERS: M = 255 if G >= 230 else 0 · E = A if A < 255 else 0 ·
    R = 255 - R_lab · S = (B - 64) * 255 / 191 if B >= 65 else 0."""
    R, G, B, A = (spec[..., i].astype(int) for i in range(4))
    out = np.zeros_like(spec)
    out[..., 0] = np.where(G >= 230, 255, 0)
    out[..., 1] = np.where(A < 255, A, 0)
    out[..., 2] = 255 - R
    out[..., 3] = np.where(B >= 65, np.round((B - 64) * 255 / 191), 0)
    return out

def normal_156(n):
    """LabPBR _n (R = X, G = Y, B = AO, A = height) -> Bedrock tangent normal (R = X, G = Y, B = reconstructed Z, A = 255)."""
    x = n[..., 0].astype(float) / 255 * 2 - 1
    y = n[..., 1].astype(float) / 255 * 2 - 1
    z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    out = np.zeros_like(n)
    out[..., 0] = n[..., 0]; out[..., 1] = n[..., 1]
    out[..., 2] = np.round(z * 255); out[..., 3] = 255
    return out

def rotate_frames(strip, k):
    """Move the strip's frame sequence so frame k comes first (frames are square, stacked top to bottom)."""
    fw = strip.shape[1]; n = strip.shape[0] // fw
    frames = [strip[i * fw:(i + 1) * fw] for i in range(n)]
    return np.concatenate(frames[k:] + frames[:k], axis=0)

def set_frames(fb_list, tex_path, frames, tpf=None):
    hit = 0
    for e in fb_list:
        if e.get("flipbook_texture") == tex_path:
            e["frames"] = list(frames); hit += 1
            if tpf is not None: e["ticks_per_frame"] = tpf
    return hit

def stamp(pk, desc):
    cfg = PACKS[pk]; man = jl(cfg["dst"] / "manifest.json")
    man["header"]["name"] = cfg["name"]; man["header"]["version"] = cfg["ver"]
    for m in man["modules"]: m["version"] = cfg["ver"]
    man["header"]["description"] = desc
    jsave(cfg["dst"] / "manifest.json", man)

for pk, cfg in PACKS.items():
    if cfg["dst"].exists(): shutil.rmtree(cfg["dst"])
    shutil.copytree(cfg["src"], cfg["dst"])
    REPORT[pk] = {"deleted": [], "restored": [], "flipbook": []}

# ---------------------------------------------------------------- RP-04
d4 = PACKS["RP-04"]["dst"]; blocks4 = d4 / "textures/blocks"
for p in sorted(blocks4.glob("*.png")):
    twin = RP3 / "textures/blocks" / p.name
    if not twin.exists() or p.read_bytes() == twin.read_bytes(): continue
    s4, s3 = size(p), size(twin)
    if s4 and s3 and max(s4) == 256 and min(s4) < 128 and max(s3) > 256:
        p.unlink(); REPORT["RP-04"]["deleted"].append(f"{p.name} {s4[0]}x{s4[1]} -> RP-03 {s3[0]}x{s3[1]}")
# nether portal from the Patrix 128x source
save(rgba(PAT2 / "nether_portal.png"), blocks4 / "nether_portal.png")
save(normal_156(rgba(PAT2 / "nether_portal_n.png")), blocks4 / "nether_portal_n.png")
mer1 = mers_156(rgba(PAT2 / "nether_portal_s.png"))                         # 128x128 constant specular -> tile to the 32-frame strip
save(np.tile(mer1, (32, 1, 1)), blocks4 / "nether_portal_mer.png")
REPORT["RP-04"]["restored"] += ["nether_portal.png 128x4096 (Patrix)", "nether_portal_n.png 128x4096 (LabPBR->Bedrock)", "nether_portal_mer.png 128x4096 (#156, tiled)"]
# fire in RP-04 (shadowed by RP-10 in his order, still made right)
for fn, src in [("fire_0.png", PAT2 / "fire_0.png"), ("fire_1.png", PAT2 / "fire_1.png"), ("soul_fire_0.png", PAT1 / "soul_fire_0.png"), ("soul_fire_1.png", PAT2 / "soul_fire_1.png")]:
    save(rgba(src), blocks4 / fn); REPORT["RP-04"]["restored"].append(f"{fn} 128x3840 (Patrix, 30 frames)")
fb4 = jl(d4 / "textures/flipbook_textures.json")
for t in ["fire_0", "fire_1", "soul_fire_0", "soul_fire_1"]:
    n = set_frames(fb4, f"textures/blocks/{t}", FIRE_ORDER); REPORT["RP-04"]["flipbook"].append(f"{t}: {n} entr{'y' if n == 1 else 'ies'} -> Patrix 30-frame order")
jsave(d4 / "textures/flipbook_textures.json", fb4)
stamp("RP-04", f"v1.3.140 ({DATE}) CAPPED-STRIP REPAIR (D-C262): {len(REPORT['RP-04']['deleted'])} animated-strip textures that a 'long side 256' resize had "
      "reduced to slivers (lava flow, torches, lanterns, furnace fronts, stonecutter saw, respawn anchor top, sculk sensor tendrils, shrieker top) are removed so "
      "RP-03's intact 128x strips draw; the nether portal is restored from the Patrix 128x source (colour + normal + MERS, 32 frames); fire and soul fire carry the "
      "Patrix 30-frame strips with the Patrix frame order. Everything else byte-identical to v1.3.139.")
log(f"RP-04 v1.3.140: {len(REPORT['RP-04']['deleted'])} capped copies deleted, portal + fire restored")

# ---------------------------------------------------------------- RP-10
d10 = PACKS["RP-10"]["dst"]; blocks10 = d10 / "textures/blocks"
for fn in ["torch.png", "soul_torch.png", "copper_torch.png"]:
    p = blocks10 / fn; s = size(p); p.unlink(); REPORT["RP-10"]["deleted"].append(f"{fn} {s[0]}x{s[1]} -> RP-03 {size(RP3 / 'textures/blocks' / fn)[0]}x{size(RP3 / 'textures/blocks' / fn)[1]}")
fire0, fire1 = rgba(PAT2 / "fire_0.png"), rgba(PAT2 / "fire_1.png")
save(fire0, blocks10 / "fire_0.png"); save(fire1, blocks10 / "fire_1.png")
save(rgba(PAT1 / "soul_fire_0.png"), blocks10 / "soul_fire_0.png"); save(rgba(PAT2 / "soul_fire_1.png"), blocks10 / "soul_fire_1.png")
REPORT["RP-10"]["restored"] += ["fire_0.png / fire_1.png / soul_fire_0.png / soul_fire_1.png 128x3840 (Patrix, 30 frames)"]
# the strip in the Patrix play order, then each variant starts that order at a different frame (baked into the image)
def ordered(strip): fw = strip.shape[1]; return np.concatenate([strip[i * fw:(i + 1) * fw] for i in FIRE_ORDER], axis=0)
o0, o1 = ordered(fire0), ordered(fire1)
for v, k in FIRE_OFFSETS.items():
    save(rotate_frames(o0, k), blocks10 / f"fire_0_{v}.png"); save(rotate_frames(o1, k), blocks10 / f"fire_1_{v}.png")
    REPORT["RP-10"]["restored"].append(f"fire_0_{v}.png / fire_1_{v}.png = Patrix order started at frame {k}")
fb10 = jl(d10 / "textures/flipbook_textures.json")
seq = list(range(30))
for t in ["fire_0", "fire_1", "soul_fire_0", "soul_fire_1"]:
    n = set_frames(fb10, f"textures/blocks/{t}", FIRE_ORDER); REPORT["RP-10"]["flipbook"].append(f"{t}: {n} -> Patrix order (30)")
for base in ["fire_0", "fire_1"]:
    for v in FIRE_OFFSETS:
        n = set_frames(fb10, f"textures/blocks/{base}_{v}", seq); REPORT["RP-10"]["flipbook"].append(f"{base}_{v}: {n} -> 0..29 (offset baked)")
jsave(d10 / "textures/flipbook_textures.json", fb10)
stamp("RP-10", f"v1.3.41 ({DATE}) CAPPED-STRIP REPAIR (D-C262): torch / soul torch / copper torch slivers (14x256) removed so RP-03's 128x 18-frame strips draw; "
      "the FIRE family rebuilt from the Patrix 128x 30-frame strips — fire_0/fire_1 + the four per-instance variants (same strip, four start frames, so "
      "neighbouring fires burn out of phase) + soul fire; flipbook frame lists set to 30. Everything else byte-identical to v1.3.40.")
log("RP-10 v1.3.41: torches deleted, fire family rebuilt (base + a/b/c/d + soul), flipbooks -> 30 frames")

# ---------------------------------------------------------------- RP-05
d5 = PACKS["RP-05"]["dst"]; blocks5 = d5 / "textures/blocks"
for fn in ["kelp_top.png", "seagrass.png", "kelp.png", "nether_wart_stage2.png"]:
    p = blocks5 / fn; s = size(p); t = size(RP3 / "textures/blocks" / fn); p.unlink(); REPORT["RP-05"]["deleted"].append(f"{fn} {s[0]}x{s[1]} -> RP-03 {t[0]}x{t[1]}")
stamp("RP-05", f"v1.3.50 ({DATE}) CAPPED-STRIP REPAIR (D-C262): kelp top, seagrass, kelp and nether wart stage 2 slivers (13-64 px wide) removed so RP-03's "
      "intact 128x strips draw (kelp top 20 frames, seagrass 18, nether wart 4). Everything else byte-identical to v1.3.49.")
log("RP-05 v1.3.50: 4 capped copies deleted")

json.dump(REPORT, open(ROOT / "_logs/strips_1_build_report.json", "w"), indent=1)
print(json.dumps(REPORT, indent=1))

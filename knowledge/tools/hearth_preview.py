#!/usr/bin/env python3
"""hearth_preview.py — HEARTH v2 preview sheet (D-C208): Patrix fire + authored burning-log stages, NOTHING shipped.

Sources (all permitted): Patrix Java source 128x (oak_log, oak_log_top, magma, fire_0 30-frame strip, CTM fire tiles
1/3/5, big_smoke) pulled by HTTP range into _intake/patrix128; our own pw_hearth_soot / pw_hearth_ash / pw_hearth_embers
(RP-04 v1.3.129).  The hearth geometry is the shipped one (tools/homestead_build.py: texture 16x16 declared, log side
faces sample uv [0,0]+[12,3] = texels 0..96 x 0..24, log ends uv [6,6]+[3,3] = texels 48..72 square).

Outputs:
  _design/hearth-v2-textures.png   — the stage textures (side strip + end square) at 4x
  _design/hearth-v2-phases.png     — front view of the hearth per phase, 24 screen px per block px
  _design/hearth-log-stages/*.png  — the authored 128x textures (candidates; ship copies are made by the build)
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = "/home/claude/_intake/patrix128/assets/minecraft/textures/block"
RP = "/home/claude/_build/rp04-129/textures/blocks"
OUTD = "/home/claude/_design/hearth-log-stages"; os.makedirs(OUTD, exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
rng = np.random.default_rng(20260922)

def load(p): return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255.0
def save(a, p): Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA").save(p)

def noise(shape, scale, seed):
    r = np.random.default_rng(seed).random((shape[0] // scale + 2, shape[1] // scale + 2)).astype(np.float32)
    im = Image.fromarray((r * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255.0

def fbm(shape, seed):
    return 0.5 * noise(shape, 32, seed) + 0.3 * noise(shape, 12, seed + 1) + 0.2 * noise(shape, 4, seed + 2)

def cracks(shape, seed, width=0.06):
    """alligator-char crack network: ridges of a cell noise -> thin bright lines."""
    n = fbm(shape, seed)
    gy, gx = np.gradient(n)
    ridge = np.abs(n - 0.5)
    c = np.clip(1.0 - ridge / width, 0, 1)
    return c ** 1.5

def ember_ramp(heat):
    """heat 0..1 -> RGB ember colour (dull red -> orange -> yellow-white)."""
    h = np.clip(heat, 0, 1)[..., None]
    c0 = np.array([0.22, 0.02, 0.0]); c1 = np.array([1.0, 0.42, 0.05]); c2 = np.array([1.0, 0.92, 0.62])
    lo = c0 * (1 - h * 2) + c1 * (h * 2)
    hi = c1 * (1 - (h - 0.5) * 2) + c2 * ((h - 0.5) * 2)
    return np.where(h < 0.5, lo, hi)

def grain_along(base):
    """Patrix bark grain runs along the texture's y axis; our log side strip runs along x -> rotate 90 degrees so the
    grain follows the log's length.  (The shipped hearth logs show the grain ACROSS the log — same fix for 'fueled'.)"""
    return np.rot90(base, k=1)

def stage_side(base, stage):
    """base: Patrix oak log side, already grain-along.  Char is strongest across the middle of the log's length and
    on the strip's lower edge (the fire side); the wood detail is kept by multiplying, not by blending to flat black."""
    h, w = base.shape[:2]
    xs = np.linspace(-1, 1, w)[None, :]; ys = np.linspace(0, 1, h)[:, None]
    center = np.exp(-(xs / 0.6) ** 2) * (0.75 + 0.25 * ys)
    n = fbm((h, w), 7)
    lum = base[..., :3].mean(-1, keepdims=True)
    fiss = cracks((h, w), 11, 0.05)                           # crack network (thin lines)
    if stage == "lit":
        char = np.clip(0.15 + 0.85 * center + 0.3 * (n - 0.5), 0, 1); heat_k, ash_k, dark = 1.0, 0.0, 0.16
    elif stage == "embers":
        char = np.clip(0.6 + 0.4 * center + 0.25 * (n - 0.5), 0, 1); heat_k, ash_k, dark = 0.5, 0.35, 0.08
    else:
        char = np.clip(0.9 + 0.1 * center + 0.15 * (n - 0.5), 0, 1); heat_k, ash_k, dark = 0.0, 0.6, 0.06
    charred = base[..., :3] * (dark + 0.25 * lum)             # wood detail kept, crushed toward charcoal
    charred = charred * (1 - 0.6 * fiss[..., None] * char[..., None])   # fissures read darker
    out = base[..., :3] * (1 - char[..., None]) + charred * char[..., None]
    heat = np.clip((fiss * 1.3 + 0.15 * n) * np.clip((char - 0.3) / 0.6, 0, 1), 0, 1) * heat_k
    heat = heat * (0.6 + 0.4 * fbm((h, w), 31))               # uneven glow
    out = out * (1 - heat[..., None]) + ember_ramp(heat * 0.9 + 0.1 * (heat > 0)) * heat[..., None]
    dust = np.clip(0.55 * noise((h, w), 6, 41) + 0.45 * noise((h, w), 3, 42) - 0.35, 0, 1) * 1.6   # fine ash dusting
    ash = np.clip((char - 0.55) / 0.45, 0, 1) * np.clip(dust * (0.4 + 0.6 * fbm((h, w), 44)), 0, 1) * ash_k
    out = out * (1 - ash[..., None]) + np.array([0.76, 0.74, 0.70])[None, None] * (0.75 + 0.25 * n)[..., None] * ash[..., None]
    return np.concatenate([out, np.ones((h, w, 1), np.float32)], -1)

def stage_end(base_top, stage):
    """log end (rings): a radial ember core; the outer rings char; only the centre 24x24 texels are sampled."""
    h, w = base_top.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]; r = np.hypot(xx - w / 2, yy - h / 2) / (w / 2)
    n = fbm((h, w), 21); lum = base_top[..., :3].mean(-1, keepdims=True)
    fiss = cracks((h, w), 23, 0.07)
    if stage == "lit":
        core = np.clip(1 - r / 0.42, 0, 1) ** 0.9; char = np.clip(0.35 + 0.65 * np.clip(r / 0.5, 0, 1) + 0.25 * (n - 0.5), 0, 1); heat_k, ash_k, dark = 1.0, 0.0, 0.16
    elif stage == "embers":
        core = np.clip(1 - r / 0.3, 0, 1) ** 1.3; char = np.clip(0.7 + 0.3 * np.clip(r / 0.5, 0, 1) + 0.2 * (n - 0.5), 0, 1); heat_k, ash_k, dark = 0.5, 0.35, 0.12
    else:
        core = np.zeros_like(r); char = np.clip(0.9 + 0.1 * (n - 0.5), 0, 1); heat_k, ash_k, dark = 0.0, 0.55, 0.10
    charred = base_top[..., :3] * (dark + 0.3 * lum) * (1 - 0.5 * fiss[..., None])
    out = base_top[..., :3] * (1 - char[..., None]) + charred * char[..., None]
    heat = np.clip(core * (0.75 + 0.25 * n) + fiss * 0.5 * np.clip((char - 0.4) / 0.5, 0, 1), 0, 1) * heat_k
    out = out * (1 - heat[..., None]) + ember_ramp(heat) * heat[..., None]
    dust = np.clip(0.55 * noise((h, w), 6, 45) + 0.45 * noise((h, w), 3, 46) - 0.35, 0, 1) * 1.6
    ash = np.clip((char - 0.6) / 0.4, 0, 1) * np.clip(dust, 0, 1) * ash_k
    out = out * (1 - ash[..., None]) + np.array([0.74, 0.72, 0.68])[None, None] * ash[..., None]
    return np.concatenate([out, np.ones((h, w, 1), np.float32)], -1)

def fire_frame(strip, i):
    return strip[i * 128:(i + 1) * 128]

def front_view(phase, textures, scale=24, fire_tile=None, fire_frame_idx=0):
    """Orthographic front view (camera at -z looking +z), painter's order far -> near.  Block px -> screen."""
    W = H = 16 * scale
    img = Image.new("RGBA", (W, H), (30, 30, 34, 255))
    def rect(x0, x1, y0, y1): return (int((x0 + 8) * scale), int((16 - y1) * scale), int((x1 + 8) * scale), int((16 - y0) * scale))
    def paste_tex(tex, box, uv):            # uv = (u0, v0, w, h) in texels of a 128 texture (declared 16 -> x8)
        u0, v0, uw, vh = uv
        t = Image.fromarray((np.clip(tex, 0, 1) * 255).astype(np.uint8), "RGBA").crop((u0, v0, u0 + uw, v0 + vh))
        t = t.resize((box[2] - box[0], box[3] - box[1]), Image.NEAREST)
        img.alpha_composite(t, (box[0], box[1]))
    # back wall skin north face (soot): x -8..8, y 0..16
    paste_tex(textures["soot"], rect(-8, 8, 0, 16), (0, 0, 128, 128))
    # floor north face y 0..1 (soot) and bed north face y 1..2
    paste_tex(textures["soot"], rect(-8, 8, 0, 1), (0, 0, 128, 8))
    paste_tex(textures["bed"], rect(-6, 6, 1, 2), (0, 0, 96, 8))
    if phase in ("fueled", "lit", "embers"):
        side = textures["log_side"]; end = textures["log_end"]
        # lower pair along x: the front one (z=-4.5) hides the back one; north face 12x3 -> texels 0..96 x 0..24
        paste_tex(side, rect(-6, 6, 2, 5), (0, 0, 96, 24))
        # upper pair along z: north END faces at z=-7, 3x3 -> texels 48..72
        for x0 in (-4.5, -0.5):
            paste_tex(end, rect(x0, x0 + 3, 5, 8), (48, 48, 24, 24))
    if fire_tile is not None:
        fr = fire_frame(fire_tile, fire_frame_idx)
        w = 12 * math.cos(math.radians(45))            # a 45°-rotated 12-wide quad projects 8.49 wide
        paste_tex(fr, rect(-w / 2, w / 2, 4, 14), (0, 0, 128, 128))
    return img

def main():
    oak = load(f"{P}/oak_log.png"); oak_top = load(f"{P}/oak_log_top.png"); magma = load(f"{P}/magma.png")
    soot = load(f"{RP}/pw_hearth_soot.png"); ash = load(f"{RP}/pw_hearth_ash.png"); embers = load(f"{RP}/pw_hearth_embers.png")
    fire_tall = load(f"{P}/fire_0.png"); fire_mid = load("/home/claude/_intake/patrix128/assets/minecraft/optifine/ctm/patrix/fire/3.png")
    fire_low = load("/home/claude/_intake/patrix128/assets/minecraft/optifine/ctm/patrix/fire/5.png")
    oak = grain_along(oak)                                   # grain along the log (fix for the shipped 'fueled' look too)
    save(oak, f"{OUTD}/pw_hearth_log_fueled.png")
    stages = {}
    for st in ("lit", "embers", "cold"):
        stages[st] = (stage_side(oak, st), stage_end(oak_top, st))
        save(stages[st][0], f"{OUTD}/pw_hearth_log_{st}.png"); save(stages[st][1], f"{OUTD}/pw_hearth_log_end_{st}.png")
    # --- sheet 1: textures --------------------------------------------------------------------------------------
    cols = [("fueled (Patrix oak log, grain turned along the log)", oak, oak_top)] + [(f"{st}", *stages[st]) for st in ("lit", "embers", "cold")]
    sheet = Image.new("RGB", (4 * 300 + 40, 720), (18, 18, 22)); d = ImageDraw.Draw(sheet)
    d.text((20, 10), "HEARTH v2 — burning-log stage textures (authored from Patrix oak log + Patrix magma glow + our soot/ash) — 128x, shown 2x", fill=(255, 255, 255), font=FB)
    d.text((20, 32), "row 1: full side texture · row 2: the 96x24 strip the log SIDE faces actually sample (4x) · row 3: the 24x24 END-grain core the log ends sample (6x)", fill=(200, 200, 200), font=F)
    for i, (name, side, end) in enumerate(cols):
        x = 20 + i * 300
        d.text((x, 60), name, fill=(255, 230, 180), font=FB)
        s = Image.fromarray((np.clip(side, 0, 1) * 255).astype(np.uint8), "RGBA").resize((256, 256), Image.NEAREST); sheet.paste(s, (x, 84))
        strip = Image.fromarray((np.clip(side, 0, 1) * 255).astype(np.uint8), "RGBA").crop((0, 0, 96, 24)).resize((288, 72), Image.NEAREST); sheet.paste(strip, (x, 356))
        core = Image.fromarray((np.clip(end, 0, 1) * 255).astype(np.uint8), "RGBA").crop((48, 48, 72, 72)).resize((144, 144), Image.NEAREST); sheet.paste(core, (x, 444))
        full = Image.fromarray((np.clip(end, 0, 1) * 255).astype(np.uint8), "RGBA").resize((128, 128), Image.NEAREST); sheet.paste(full, (x + 160, 444))
        d.text((x, 596), "side strip 0..96 x 0..24", fill=(160, 160, 160), font=F); d.text((x, 614), "end core 48..72 (6x) · full end (1x)", fill=(160, 160, 160), font=F)
    d.text((20, 660), "Glow = an ember colour ramp in the crack network (Patrix magma kept for the inward log faces, à la Patrix campfire). Under Vibrant Visuals the glow can also go into a MER emissive channel (RP-03).", fill=(200, 200, 200), font=F)
    d.text((20, 680), "Orientation fix: the shipped logs sample Patrix bark with the grain ACROSS the 12-px log (F10 shows ring-like bands); every stage here has the grain turned along the log.", fill=(255, 200, 120), font=F)
    sheet.save("/home/claude/_design/hearth-v2-textures.png")
    # --- sheet 2: phases, front view -----------------------------------------------------------------------------
    T = {"soot": soot}
    views = []
    views.append(("cold (empty)", front_view("cold", dict(T, bed=ash))))
    views.append(("fueled (logs, unlit)", front_view("fueled", dict(T, bed=ash, log_side=oak, log_end=oak_top))))
    views.append(("lit — Patrix fire tile 1 (tall), 30 frames", front_view("lit", dict(T, bed=embers, log_side=stages["lit"][0], log_end=stages["lit"][1]), fire_tile=fire_tall, fire_frame_idx=15)))
    views.append(("lit — frame 22", front_view("lit", dict(T, bed=embers, log_side=stages["lit"][0], log_end=stages["lit"][1]), fire_tile=fire_tall, fire_frame_idx=22)))
    views.append(("embers — CTM tile 5 (low licks) over glowing coals", front_view("embers", dict(T, bed=embers, log_side=stages["embers"][0], log_end=stages["embers"][1]), fire_tile=fire_low, fire_frame_idx=4)))
    views.append(("cold — burnt out (charcoal + ash, no flame)", front_view("embers", dict(T, bed=ash, log_side=stages["cold"][0], log_end=stages["cold"][1]))))
    sheet2 = Image.new("RGB", (6 * 400 + 40, 500), (18, 18, 22)); d = ImageDraw.Draw(sheet2)
    d.text((20, 10), "HEARTH v2 — front view per phase (shipped geometry, 24 screen px per block px, camera at the open front) — proposal, not shipped", fill=(255, 255, 255), font=FB)
    for i, (name, im) in enumerate(views):
        x = 20 + i * 400
        d.text((x, 40), name, fill=(255, 230, 180), font=F)
        sheet2.paste(im.convert("RGB"), (x, 62))
    d.text((20, 456), "Cold-with-logs is a NEW look: today the cold phase draws no logs; leaving charcoal in the pit after burn-out is a design choice for Abs0lum (yes/no).", fill=(200, 200, 200), font=F)
    d.text((20, 474), "Flame quads are the shipped 12x10 crossed quads; the Patrix tile is the whole 128x128 frame (tall flames reach the quad top). Embers use CTM tile 5.", fill=(200, 200, 200), font=F)
    sheet2.save("/home/claude/_design/hearth-v2-phases.png")
    print("ok")

if __name__ == "__main__":
    main()

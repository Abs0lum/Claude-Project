#!/usr/bin/env python3
"""firefly_compare.py — visual comparison set for the FIREFLY v2 decision (Abs0lum 23:25: "provide images of the
different aspects of each so I can choose by how they look visually").

Outputs (_design/):
  firefly-A-bushes-night.gif    the 4 Patrix 256 bush variants at night, each glow layer animating at its own speed
  firefly-B-flyers.gif          7 panels, 10 s loop: how the flying fireflies of each approach look and move
  firefly-C-rhythm.png          small multiples: one firefly's brightness over 12 s for each approach
  firefly-D-colours.png         the glow colours on a night background
  firefly-E-creature.png        StripMine's Naturalist creature firefly (textures + glow frames)
  firefly-F-closeup.png         one firefly of each approach, close up, at full brightness (shape only)
  firefly-H-v2-size.png / .gif   his pick (OURS v2) at 80% size (23:47 ruling) vs VFXCore and v2 as first shown
  firefly-G-ours-two-readings.png  OUR current bush fireflies two ways: the fade as Molang computes it (degrees) vs
                                   full brightness -- for Abs0lum to say which one matches his screen

The flyer simulation re-implements each pack's published parameters (particle JSON / decompiled constants / source)
in 2-D, side view, 60 px per block. Molang trig is in DEGREES (as the engine evaluates it). Bedrock billboard `size`
is a half-extent. Vibrant Visuals bloom is NOT simulated (it widens bright emissive sprites in game)."""
import math, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/claude"); OUT = ROOT / "_design"; OUT.mkdir(exist_ok=True)
P256 = ROOT / "_intake/patrix256-firefly/assets/minecraft/textures"
STUDY = ROOT / "_intake/firefly-study"
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
FONT_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
PPB = 60                     # pixels per block
PW, PH = 320, 230            # panel size (5.3 x 3.8 blocks)
FPS = 10; SECONDS = 10; DT = 1 / FPS; SUB = 2   # physics sub-steps per frame (20 Hz like the game tick)


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255.0


# ---------------------------------------------------------------- night background with grass and two bushes
def background(seed=7):
    rng = random.Random(seed)
    h, w = PH, PW
    y = np.linspace(0, 1, h)[:, None]
    sky = np.zeros((h, w, 3), np.float32)
    sky[..., 0] = 0.020 + 0.020 * y; sky[..., 1] = 0.030 + 0.030 * y; sky[..., 2] = 0.070 + 0.030 * y
    img = Image.fromarray((sky * 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    ground_y = h - 26
    d.rectangle([0, ground_y, w, h], fill=(14, 20, 14, 255))
    for _ in range(170):                                     # grass blades
        x = rng.uniform(0, w); hh = rng.uniform(8, 26); lean = rng.uniform(-5, 5)
        d.line([(x, ground_y + 2), (x + lean, ground_y - hh)], fill=(18 + rng.randint(0, 10), 30 + rng.randint(0, 14), 18, 255), width=1)
    bush = Image.open(P256 / "block/firefly_bush.png").convert("RGBA").resize((96, 96), Image.LANCZOS)
    arr = np.asarray(bush).astype(np.float32); arr[..., :3] *= 0.16                     # night: dark silhouette
    bush = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    for bx in (40, 205):
        img.alpha_composite(bush, (bx, ground_y - 90))
    return np.asarray(img).astype(np.float32)[..., :3] / 255.0, ground_y


def to_px(x, y, ground_y):
    return x * PPB, ground_y - y * PPB


# ---------------------------------------------------------------- sprite drawing (blend or additive)
_CACHE = {}
def draw(canvas, tex, cx, cy, half_blocks, color, alpha, additive):
    size = max(1, int(round(2 * half_blocks * PPB)))
    if alpha <= 0.003:
        return
    key = (id(tex), size)
    t = _CACHE.get(key)
    if t is None:
        t = Image.fromarray((tex * 255).astype(np.uint8), "RGBA").resize((size, size), Image.LANCZOS if tex.shape[0] > size else Image.NEAREST)
        t = _CACHE[key] = np.asarray(t).astype(np.float32) / 255.0
    x0 = int(round(cx - size / 2)); y0 = int(round(cy - size / 2))
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(PW, x0 + size), min(PH, y0 + size)
    if xa >= xb or ya >= yb:
        return
    sub = t[ya - y0:yb - y0, xa - x0:xb - x0]
    rgb = sub[..., :3] * np.asarray(color, np.float32)[None, None, :3]
    a = sub[..., 3:4] * alpha
    region = canvas[ya:yb, xa:xb]
    if additive:
        region += rgb * a
    else:
        region[:] = region * (1 - a) + rgb * a
    np.clip(region, 0, 1, out=region)


def soft_disc(n=32, core=0.0, falloff=2.2):
    yy, xx = np.mgrid[0:n, 0:n]; r = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / (n / 2)
    a = np.clip(1 - r, 0, 1) ** falloff
    if core:
        a = np.maximum(a, (r < core).astype(np.float32))
    t = np.ones((n, n, 4), np.float32); t[..., 3] = a
    return t


PIXEL = np.ones((1, 1, 4), np.float32)
TEX = {
    "ours_disc": rgba(ROOT / "_build/rp05-48/textures/particle/firefly.png"),
    "vfx": rgba(STUDY / "U1/VFXCore [RP]_x/textures/vfxcore/biomes/firefly.png"),
    "pure": rgba(STUDY / "U2/RP_x/textures/PUREVFX/firefly_glow.png"),
    "part": rgba(STUDY / "U8/particular-1.1.1_x/assets/particular/textures/particle/firefly.png"),
}
ill = rgba(STUDY / "U5/Illuminations-main/src/main/resources/assets/illuminations/textures/particle/firefly.png")
TEX["ill_halo"], TEX["ill_core"] = ill[:16], ill[16:]
for k in ("ill_halo", "ill_core"):                     # LA texture: luminance -> rgb white, alpha kept
    TEX[k][..., :3] = 1.0
TEX["prop_halo"] = soft_disc(32, falloff=2.6); TEX["prop_core"] = soft_disc(16, core=0.35, falloff=1.2)


def hsv_shift(rgb, deg):
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*rgb); return colorsys.hsv_to_rgb((h + deg / 360) % 1, s, v)


def catmull(nodes, t):
    """Molang catmull_rom curve with the given nodes over t in [0,1] (first/last node are control points)."""
    n = len(nodes) - 3
    u = min(max(t, 0), 0.9999) * n; i = int(u); f = u - i
    p0, p1, p2, p3 = nodes[i], nodes[i + 1], nodes[i + 2], nodes[i + 3]
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def grad(stops, t):
    ks = sorted(stops)
    if t <= ks[0]: return stops[ks[0]]
    for a, b in zip(ks, ks[1:]):
        if t <= b:
            f = (t - a) / (b - a); return tuple(x + (y - x) * f for x, y in zip(stops[a], stops[b]))
    return stops[ks[-1]]


def hexa(h):   # "#AARRGGBB" -> (r,g,b,a)
    h = h.lstrip("#"); a = int(h[0:2], 16) / 255; return (int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, int(h[6:8], 16) / 255, a)


# ---------------------------------------------------------------- the seven approaches
class Fly:
    def __init__(s, **k): s.__dict__.update(k)


def model_vanilla(rng):
    def spawn(t):
        bx = rng.choice((1.47, 4.2)); return Fly(x=bx + rng.uniform(-0.5, 0.5), y=rng.uniform(0.3, 1.2), vx=rng.uniform(-0.5, 0.5), vy=rng.uniform(-0.2, 0.5),
                                                 ax=rng.uniform(-5, 5), ay=rng.uniform(-5, 5), age=0, life=rng.uniform(10, 15))
    def step(f, dt):
        if rng.random() <= 0.05: f.ax, f.ay = rng.uniform(-5, 5), rng.uniform(-5, 5)
        f.vx += (f.ax - 3 * f.vx) * dt; f.vy += (f.ay - 3 * f.vy) * dt
    def look(f):
        a = grad({0: (0,), 0.3: (1,), 0.5: (1,), 1: (0,)}, f.age / f.life)[0]
        return [(PIXEL, 0.0375, (1, 1, 0.92), a, False)]
    return dict(name="1  Vanilla (game default)", spawn=spawn, step=step, look=look, every=1.6, burst=1)


def model_ours_now(rng, fade="degrees"):
    """fade="degrees": RP-10's alpha line exactly as Molang evaluates it (math.sin takes DEGREES, so
    sin(math.pi * age/life) is sin of at most 3.14 deg -> peak alpha 0.099, rising all life, gone at its brightest).
    fade="ignored": the same fireflies at full brightness, in case the engine did not apply the alpha."""
    def spawn(t):
        bx = rng.choice((1.47, 4.2)); cx, cy = bx + rng.uniform(-0.5, 0.5), rng.uniform(0.4, 1.2)
        return [Fly(x=cx + rng.uniform(-0.3, 0.3), y=cy + rng.uniform(-0.3, 0.3), vx=0, vy=0.04, age=0, life=rng.uniform(8, 14),
                    r1=rng.random(), r2=rng.random(), r3=rng.random(), r4=rng.random()) for _ in range(5)]
    def step(f, dt):   # accelerations in DEGREES, as Molang evaluates them
        ax = math.sin(math.radians(f.age * 2.5 + f.r1 * 6.28)) * 0.3; ay = math.cos(math.radians(f.age * 1.5 + f.r2 * 6.28)) * 0.15
        f.vx += (ax - 0.6 * f.vx) * dt; f.vy += (ay - 0.6 * f.vy) * dt
    def look(f):
        a = min(max(math.sin(math.radians(math.pi * f.age / f.life)) * 1.8, 0), 1) if fade == "degrees" else 1.0
        col = (1.0, 0.92, 0.55) if f.r4 < 0.5 else (0.85, 1.0, 0.65)
        return [(TEX["ours_disc"], 0.08, col, a, True)]
    return dict(name="2  OURS NOW (RP-10 + RP-05)", spawn=spawn, step=step, look=look, every=1.6, burst=5)


def model_vfx(rng):
    def one(cx, cy):
        ang = rng.uniform(0, math.pi); sp = rng.uniform(0.3, 0.9)
        return Fly(x=cx, y=cy, vx=math.cos(ang) * sp, vy=math.sin(ang) * sp, age=0, life=rng.uniform(8, 13), r2=rng.uniform(-1, 1), r3=rng.random(), r4=rng.random())
    def spawn(t):
        cx, cy = rng.uniform(0.4, 4.9), rng.uniform(0.5, 1.5)
        if rng.random() < 0.4: return [one(cx + rng.uniform(-1.5, 1.5), cy + rng.uniform(-0.4, 0.4)) for _ in range(6)]
        return [one(cx, cy)]
    def step(f, dt):
        ax = f.r2 / 2; ay = f.r2 / 5 * ((math.cos(math.radians(f.age * 360)) * 5 * f.r3) + 0.5)
        f.vx += (ax - 5 * f.vx) * dt; f.vy += (ay - 5 * f.vy) * dt
    stops = {0: hexa("#00FFFFFF"), .1: hexa("#FFFFFFFF"), .24: hexa("#A6F0D254"), .41: hexa("#FFFFFFFF"), .5: hexa("#A6F0D254"),
             .65: hexa("#FFFFFFFF"), .81: hexa("#A6F0D254"), .92: hexa("#FFFFFFFF"), 1: hexa("#00FFFFFF")}
    def look(f):
        c = grad(stops, f.age / f.life); return [(TEX["vfx"], 0.08 + 0.05 * f.r4, c[:3], c[3], False)]
    return dict(name="3  VFXCore", spawn=spawn, step=step, look=look, every=3.0, burst=1)


def model_pure(rng):
    nodes = [0, 0.9, 0.15, 1, 0.1, 0.85, 0, 0.95, 0.2, 0]
    def spawn(t):
        ax, ay = rng.uniform(0.4, 4.9), rng.uniform(0.2, 0.8)
        return [Fly(x=ax + rng.uniform(-0.75, 0.75), y=ay + rng.uniform(0, 0.6), vx=rng.uniform(-0.3, 0.3), vy=rng.uniform(0, 0.3), age=0,
                    life=rng.uniform(9, 15), r1=rng.random(), r2=rng.random(), r3=rng.random()) for _ in range(1 + rng.randrange(3))]
    def step(f, dt):
        ax = math.cos(math.radians(f.age * 0.8 + f.r3 * 360)) * 0.35; ay = math.sin(math.radians(f.age * 1.1 + f.r2 * 360)) * 0.18 + 0.03
        f.vx += (ax - 1.6 * f.vx) * dt; f.vy += (ay - 1.6 * f.vy) * dt
    def look(f):
        b = min(max(catmull(nodes, f.age / f.life), 0), 1); a = 0x14 / 255 + (1 - 0x14 / 255) * b
        return [(TEX["pure"], 0.08 + f.r1 * 0.03, (200 / 255, 1.0, 120 / 255), a, True)]
    return dict(name="4  PUREVFX", spawn=spawn, step=step, look=look, every=3.0 / 0.35 / 2, burst=1)


def model_ill(rng):
    base = (0xBF / 255, 1.0, 0.0)
    def spawn(t):
        return Fly(x=rng.uniform(0.3, 5.0), y=rng.uniform(0.3, 2.5), vx=0, vy=0, age=0, life=rng.uniform(20, 60), a=0.0, goal=rng.random(),
                   tx=None, ty=None, cool=0, col=hsv_shift(base, (rng.random() - 0.5) * 30), sc=0.1 * (rng.random() * 0.5 + 0.5) * 2 * (0.25 + rng.random() * 0.5))
    def step(f, dt):
        if abs(f.a - f.goal) < 0.05: f.goal = rng.random()
        f.a = min(1, f.a + 0.05) if f.goal > f.a else max(0, f.a - 0.05)
        f.cool -= 1                                    # Java: targets sigma 10 blocks; scaled to sigma 2.2 so they stay in view
        if f.tx is None or (f.tx - f.x) ** 2 + (f.ty - f.y) ** 2 < 0.36 or f.cool <= 0:
            f.tx = min(max(f.x + rng.gauss(0, 1.0) * 2.2, 0.6), 4.7); f.ty = min(max(f.y + rng.gauss(0, 1) * 0.8, 0.2), 3.0); f.cool = rng.randrange(20, 100)
        dx, dy = f.tx - f.x, f.ty - f.y; L = math.hypot(dx, dy) or 1
        f.vx = 0.9 * f.vx + 0.1 * dx / L * 2.0; f.vy = 0.9 * f.vy + 0.1 * dy / L * 2.0   # 0.1 block/tick cap = 2 blocks/s
    def look(f):
        if f.life - f.age < 1.0: f.a = max(0, f.a - 0.05)
        return [(TEX["ill_halo"], f.sc, f.col, f.a, False), (TEX["ill_core"], f.sc, (1, 1, 1), f.a, False)]
    return dict(name="5  Illuminations / Effective", spawn=spawn, step=step, look=look, every=4.5, burst=1, tick_based=True)


def model_part(rng):
    pal = [(0.7333, 1.0, 0.4196), (0.4196, 0.9804, 1.0), (1.0, 0.4863, 0.4196)]
    def spawn(t):
        return Fly(x=rng.uniform(0.3, 5.0), y=rng.uniform(0.25, 1.3), vx=0, vy=0, age=0, life=10.0, a=0.0, on=False, sw=rng.randrange(0, 60),
                   col=pal[0] if rng.random() < 0.8 else rng.choice(pal[1:]), ph=rng.uniform(0, 100))
    def step(f, dt):
        f.sw -= 1
        if f.sw <= 0:
            f.on = not f.on; f.sw = rng.randrange(10, 21) if f.on else rng.randrange(40, 81)
        f.a = min(1, f.a + 0.33) if f.on else max(0, f.a - 0.33)
        t = f.age + f.ph
        f.vx = 0.18 * math.sin(t * 0.7) * math.cos(t * 0.31); f.vy = 0.10 * math.sin(t * 0.53 + 1.3)
    def look(f):
        return [(TEX["part"], 0.25, f.col, f.a, False)]
    return dict(name="6  Particular", spawn=spawn, step=step, look=look, every=2.0, burst=1, tick_based=True)


V2_SCALE = 0.8   # Abs0lum 23:47: "I want it shrunk in size by 20%" (linear; halo 0.11 -> 0.088, core 0.03 -> 0.024 half-extent)


def model_prop(rng, scale=1.0, name="7  PROPOSED (ours v2)"):
    """PROPOSED ours v2: real-firefly rhythm (dark 2-4 s, flash 0.5-1 s) with soft breathing ramps, halo + small core,
    normal blending, warm yellow-green, near the ground, slow drift, 1 per emit. `scale` multiplies both sprite sizes."""
    warm = (0.86, 1.0, 0.45)
    def spawn(t):
        return Fly(x=rng.uniform(0.3, 5.0), y=rng.uniform(0.3, 1.6), vx=0, vy=0, age=0, life=rng.uniform(14, 24), a=0.0, on=False,
                   sw=rng.randrange(0, 60), ph=rng.uniform(0, 100))
    def step(f, dt):
        f.sw -= 1
        if f.sw <= 0:
            f.on = not f.on; f.sw = rng.randrange(10, 21) if f.on else rng.randrange(40, 81)
        f.a = min(1, f.a + 0.2) if f.on else max(0, f.a - 0.1)           # ~0.25 s rise, ~0.5 s fade
        t = f.age + f.ph
        f.vx = 0.22 * math.sin(t * 0.45) * math.cos(t * 0.21); f.vy = 0.08 * math.sin(t * 0.37 + 0.7)
    def look(f):
        fade = min(1, f.age / 1.0, (f.life - f.age) / 1.5)
        return [(TEX["prop_halo"], 0.11 * scale, warm, 0.7 * f.a * fade, False), (TEX["prop_core"], 0.03 * scale, (1, 1, 0.85), f.a * fade, False)]
    return dict(name=name, spawn=spawn, step=step, look=look, every=1.4, burst=1, tick_based=True)


MODELS = [model_vanilla, model_ours_now, model_vfx, model_pure, model_ill, model_part, model_prop]


def simulate(model_fn, seed):
    rng = random.Random(seed); m = model_fn(rng)
    bg, gy = background()
    flies = []; frames = []; next_spawn = 0.0; t = -15.0                                  # 15 s warm-up
    total = int((SECONDS + 15) * FPS)
    for fi in range(total):
        for _ in range(SUB):
            dt = DT / SUB
            while t >= next_spawn:
                got = m["spawn"](t); flies += got if isinstance(got, list) else [got]
                next_spawn += rng.expovariate(1 / m["every"])
            for f in flies:
                m["step"](f, dt)
                f.x += f.vx * dt * (1 if not m.get("tick_based") else 1); f.y += f.vy * dt; f.age += dt
                # the panel stands for a slice of a 3-D cloud: bounce off its edges instead of vanishing
                if f.x < 0.15 or f.x > 5.15: f.vx = -f.vx; f.x = min(max(f.x, 0.15), 5.15)
                if f.y < 0.08 or f.y > 3.4: f.vy = -f.vy; f.y = min(max(f.y, 0.08), 3.4)
                if hasattr(f, "ax") and (f.x in (0.15, 5.15)): f.ax = -f.ax
                if hasattr(f, "ay") and (f.y in (0.08, 3.4)): f.ay = -f.ay
            flies = [f for f in flies if f.age < f.life]
            t += dt
        if t >= 0:
            canvas = bg.copy()
            for f in flies:
                cx, cy = to_px(f.x, f.y, gy)
                for tex, half, col, a, add in m["look"](f):
                    draw(canvas, tex, cx, cy, half, col, a, add)
            frames.append(canvas)
    return m["name"], frames


def label(img, text, sub=None):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, img.size[0], 22], fill=(0, 0, 0)); d.text((8, 3), text, fill=(240, 240, 240), font=FONT_B)
    if sub: d.text((8, img.size[1] - 20), sub, fill=(200, 200, 200), font=FONT)


def make_flyers():
    subs = ["1 dot, fades in/out, darts", "5 faint discs, rise, vanish at peak", "blinks white/amber, bobs", "green additive glow, drifts",
            "halo + white core, random glow", "sharp flashes, 3 colours", "flash + soft fade, halo, low"]
    runs = [simulate(fn, 100 + i) for i, fn in enumerate(MODELS)]
    cols, rows = 4, 2
    out = []
    for k in range(SECONDS * FPS):
        sheet = Image.new("RGB", (cols * PW + (cols + 1) * 6, rows * PH + (rows + 1) * 6), (30, 32, 36))
        for i, (name, frames) in enumerate(runs):
            im = Image.fromarray((frames[k] * 255).astype(np.uint8), "RGB"); label(im, name, subs[i])
            sheet.paste(im, (6 + (i % cols) * (PW + 6), 6 + (i // cols) * (PH + 6)))
        d = ImageDraw.Draw(sheet); x0 = 6 + 3 * (PW + 6); y0 = 6 + PH + 6
        d.rectangle([x0, y0, x0 + PW, y0 + PH], fill=(22, 24, 28))
        for j, line in enumerate(["Side view, ~4 blocks away,", "10 s loop, real speeds.", "Not shown: Vibrant Visuals", "bloom (widens bright glows).",
                                  "Panel 2 = your game today,", "as the code reads (see G).", f"t = {k / FPS:4.1f} s"]):
            d.text((x0 + 14, y0 + 16 + j * 26), line, fill=(215, 215, 215), font=FONT)
        out.append(sheet)
    frames = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in out]
    frames[0].save(OUT / "firefly-B-flyers.gif", save_all=True, append_images=frames[1:], duration=int(1000 / FPS), loop=0, optimize=True)
    # a still of the busiest moment for quick viewing
    out[SECONDS * FPS // 2].save(OUT / "firefly-B-flyers-still.png")
    return runs


def make_bushes():
    names = [("default", "block/firefly_bush.png", "block/firefly_bush_emissive.png", 22)] + \
            [(f"variant {i}", f"../optifine/ctm/patrix/bush/firefly/{i}.png", f"../optifine/ctm/patrix/bush/firefly/fly/{i}.png", ft) for i, ft in ((2, 18), (3, 14), (4, 10))]
    B = []
    for nm, b, g, ft in names:
        base = Image.open((P256 / b).resolve()).convert("RGBA"); glow = Image.open((P256 / g).resolve()).convert("RGBA")
        frames = [glow.crop((0, 256 * k, 256, 256 * (k + 1))) for k in range(4)]
        night = np.asarray(base).astype(np.float32) / 255; night[..., :3] *= 0.22
        B.append((nm, night, [np.asarray(f).astype(np.float32) / 255 for f in frames], ft))
    out = []
    TICKS = 176                                                  # 8.8 s shown at 2 ticks per frame
    for tk in range(0, TICKS, 2):
        sheet = Image.new("RGB", (4 * 262 + 6, 262 + 30), (12, 14, 18)); d = ImageDraw.Draw(sheet)
        for i, (nm, night, frs, ft) in enumerate(B):
            pos = (tk / ft) % 4; a = int(pos); f = pos - a
            glow = frs[a] * (1 - f) + frs[(a + 1) % 4] * f               # interpolate: true (as the .mcmeta asks)
            bg = np.zeros((256, 256, 3), np.float32) + np.array([0.02, 0.03, 0.05])
            col = bg * (1 - night[..., 3:]) + night[..., :3] * night[..., 3:]
            col = np.clip(col + glow[..., :3] * glow[..., 3:] * 1.0, 0, 1)
            sheet.paste(Image.fromarray((col * 255).astype(np.uint8)), (6 + i * 262, 26))
            d.text((10 + i * 262, 5), f"Patrix 256 {nm} · {ft} t/frame", fill=(230, 230, 230), font=FONT)
        out.append(sheet)
    fr = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in out]
    fr[0].save(OUT / "firefly-A-bushes-night.gif", save_all=True, append_images=fr[1:], duration=100, loop=0, optimize=True)


def brightness_series(model_fn, seed, secs=12):
    rng = random.Random(seed); m = model_fn(rng)
    got = m["spawn"](0); f = got[0] if isinstance(got, list) else got
    f.life = max(getattr(f, "life", 12), secs + 0.5) if m["name"].startswith(("5", "6", "7")) else f.life
    ts, bs = [], []
    t = 0.0; dt = 1 / 20
    while t < secs:
        m["step"](f, dt); f.age += dt
        looks = m["look"](f) if f.age < f.life else []
        ts.append(t); bs.append(max((l[3] for l in looks), default=0.0)); t += dt
    return m["name"], ts, bs


def make_rhythm():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(MODELS), 1, figsize=(10, 12), sharex=True)
    fig.patch.set_facecolor("white")
    for ax, (i, fn) in zip(axes, enumerate(MODELS)):
        name, ts, bs = brightness_series(fn, 300 + i)
        ax.plot(ts, bs, color="#3a3a3a", linewidth=2)
        ax.set_ylim(-0.05, 1.08); ax.set_yticks([0, 1]); ax.set_yticklabels(["dark", "full"], fontsize=9, color="#555")
        ax.set_title(name, loc="left", fontsize=11, color="#222", pad=2)
        ax.grid(axis="x", color="#e6e6e6", linewidth=0.8); [s.set_visible(False) for s in (ax.spines["top"], ax.spines["right"])]
        ax.spines["left"].set_color("#bbb"); ax.spines["bottom"].set_color("#bbb"); ax.tick_params(colors="#666")
    axes[-1].set_xlabel("seconds (one firefly)", color="#444")
    fig.suptitle("How one firefly's glow changes over 12 seconds", x=0.02, ha="left", fontsize=14, color="#111")
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(OUT / "firefly-C-rhythm.png", dpi=110); plt.close(fig)


def make_colours():
    sw = [("Vanilla", (1, 1, 0.92)), ("Ours now A", (1, 0.92, 0.55)), ("Ours now B", (0.85, 1, 0.65)), ("VFXCore amber", (0xF0 / 255, 0xD2 / 255, 0x54 / 255)),
          ("PUREVFX green", (200 / 255, 1, 120 / 255)), ("Illum. forest/plains", (0xBF / 255, 1, 0)), ("Illum. swamp", (0, 0x9F / 255, 0)),
          ("Illum. jungle", (0, 1, 0x21 / 255)), ("Particular main", (0.733, 1, 0.42)), ("Particular cyan", (0.42, 0.98, 1)),
          ("Particular orange", (1, 0.486, 0.42)), ("PROPOSED warm", (0.86, 1, 0.45))]
    cw, ch = 150, 150; cols = 6
    img = Image.new("RGB", (cols * cw, 2 * ch + 40), (10, 12, 16)); d = ImageDraw.Draw(img)
    d.text((10, 8), "Glow colours on a night background (halo + core, same size, same brightness)", fill=(230, 230, 230), font=FONT_B)
    for i, (nm, c) in enumerate(sw):
        x0, y0 = (i % cols) * cw, 40 + (i // cols) * ch
        can = np.zeros((ch, cw, 3), np.float32) + np.array([0.02, 0.03, 0.05])
        halo = soft_disc(64, falloff=2.4); core = soft_disc(16, core=0.4, falloff=1.2)
        def put(tex, size, col, a):
            t = np.asarray(Image.fromarray((tex * 255).astype(np.uint8), "RGBA").resize((size, size), Image.LANCZOS)).astype(np.float32) / 255
            ox, oy = (cw - size) // 2, (ch - size) // 2 - 8; reg = can[oy:oy + size, ox:ox + size]
            al = t[..., 3:] * a; reg[:] = reg * (1 - al) + np.array(col) * al
        put(halo, 70, c, 0.6); put(core, 12, (1, 1, 0.9), 1.0)
        img.paste(Image.fromarray((np.clip(can, 0, 1) * 255).astype(np.uint8)), (x0, y0))
        d.text((x0 + 8, y0 + ch - 22), nm, fill=(220, 220, 220), font=FONT)
    img.save(OUT / "firefly-D-colours.png")


def make_closeup():
    global PPB, PW, PH
    save = (PPB, PW, PH); PPB, PW, PH = 240, 200, 200
    looks = []
    for i, fn in enumerate(MODELS):
        rng = random.Random(500 + i); m = fn(rng); got = m["spawn"](0); f = got[0] if isinstance(got, list) else got
        f.age = f.life * 0.4 if hasattr(f, "life") else 5; f.a = 1.0
        for attr in ("r4",):
            if hasattr(f, attr): setattr(f, attr, 0.2)
        L = m["look"](f)
        looks.append((m["name"], [(tex, half, col, 1.0 if a > 0 else 0.0, add) for tex, half, col, a, add in L]))
    img = Image.new("RGB", (len(looks) * 206 + 6, 250), (22, 24, 28)); d = ImageDraw.Draw(img)
    for i, (name, L) in enumerate(looks):
        can = np.zeros((PH, PW, 3), np.float32) + np.array([0.02, 0.03, 0.05])
        for tex, half, col, a, add in L:
            draw(can, tex, PW / 2, PH / 2, half, col, a, add)
        img.paste(Image.fromarray((can * 255).astype(np.uint8)), (6 + i * 206, 40))
        d.text((8 + i * 206, 12), name.split("  ", 1)[1][:24], fill=(230, 230, 230), font=FONT)
    img.save(OUT / "firefly-F-closeup.png")
    PPB, PW, PH = save


def make_ours_readings():
    runs = [simulate(lambda r: model_ours_now(r, "degrees"), 101), simulate(lambda r: model_ours_now(r, "ignored"), 101)]
    labs = [("READING 1 - the fade as Molang computes it", "peak ~10% brightness; each one brightens, then vanishes"),
            ("READING 2 - if the game ignored the fade", "full brightness all life")]
    k = SECONDS * FPS // 2
    sheet = Image.new("RGB", (2 * PW * 2 + 18, PH * 2 + 70), (30, 32, 36)); d = ImageDraw.Draw(sheet)
    d.text((8, 6), "OUR bush fireflies today (RP-10 minecraft:firefly_particle), same moment, two readings - which matches your screen?",
           fill=(235, 235, 235), font=FONT_B)
    for i, ((name, frames), (t1, t2)) in enumerate(zip(runs, labs)):
        im = Image.fromarray((frames[k] * 255).astype(np.uint8), "RGB").resize((PW * 2, PH * 2), Image.NEAREST)
        label(im, t1, t2); sheet.paste(im, (6 + i * (PW * 2 + 6), 34))
    sheet.save(OUT / "firefly-G-ours-two-readings.png")


def glow_size(layers):
    """Equal-area diameters (blocks) of one sprite stack at full brightness: the bright centre (>= 50% of peak) and the
    visible glow (>= 10% of peak), plus the total light it puts on screen. Rendered at 1000 px per block."""
    global PPB, PW, PH
    save = (PPB, PW, PH); PPB, PW, PH = 1000, 400, 400; _CACHE.clear()
    can = np.zeros((PH, PW, 3), np.float32)
    for tex, half, col, a, add in layers:
        draw(can, tex, PW / 2, PH / 2, half, col, a, add)
    lum = can.mean(2); peak = lum.max()
    diam = lambda frac: 2 * math.sqrt((lum >= frac * peak).sum() / math.pi) / PPB
    out = (diam(0.5), diam(0.1), lum.sum() / PPB ** 2)
    PPB, PW, PH = save; _CACHE.clear()
    return out


def make_size_check():
    """H: the OURS v2 size ruling (-20%) against VFXCore (his size reference) and v2 as first shown.
    PNG = close-ups at full brightness with measured sizes; GIF = the three side by side at ~4 blocks, 10 s loop."""
    global PPB, PW, PH
    warm = (0.86, 1.0, 0.45); vfx = TEX["vfx"]
    v2 = lambda sc: [(TEX["prop_halo"], 0.11 * sc, warm, 0.7, False), (TEX["prop_core"], 0.03 * sc, (1, 1, 0.85), 1.0, False)]
    cells = [("VFXCore smallest", [(vfx, 0.08, (1, 1, 1), 1.0, False)]), ("VFXCore average", [(vfx, 0.105, (1, 1, 1), 1.0, False)]),
             ("VFXCore largest", [(vfx, 0.13, (1, 1, 1), 1.0, False)]), ("OURS v2 FINAL (-20%)", v2(V2_SCALE)),
             ("OURS v2 as first shown", v2(1.0))]
    sizes = [glow_size(L) for _, L in cells]
    save = (PPB, PW, PH); PPB, PW, PH = 240, 200, 200; _CACHE.clear()
    img = Image.new("RGB", (len(cells) * 206 + 6, 312), (22, 24, 28)); d = ImageDraw.Draw(img)
    d.text((8, 6), "Close-up at full brightness (same scale for all; 240 px = 1 block)", fill=(235, 235, 235), font=FONT_B)
    for i, ((name, L), (c50, c10, tot)) in enumerate(zip(cells, sizes)):
        can = np.zeros((PH, PW, 3), np.float32) + np.array([0.02, 0.03, 0.05])
        for tex, half, col, a, add in L:
            draw(can, tex, PW / 2, PH / 2, half, col, a, add)
        x = 6 + i * 206
        img.paste(Image.fromarray((np.clip(can, 0, 1) * 255).astype(np.uint8)), (x, 58))
        d.text((x + 2, 32), name, fill=(255, 235, 150) if "FINAL" in name else (230, 230, 230), font=FONT_B if "FINAL" in name else FONT)
        d.text((x + 2, 262), f"bright centre {c50:.3f}", fill=(210, 210, 210), font=FONT)
        d.text((x + 2, 280), f"whole glow    {c10:.3f} blocks", fill=(210, 210, 210), font=FONT)
    img.save(OUT / "firefly-H-v2-size.png")
    PPB, PW, PH = save; _CACHE.clear()
    runs = [simulate(model_vfx, 102), simulate(lambda r: model_prop(r, V2_SCALE, "OURS v2 FINAL (-20%)"), 106),
            simulate(lambda r: model_prop(r, 1.0, "OURS v2 as first shown"), 106)]
    subs = ["his size reference", "the pick: 80% size", "for comparison"]
    frames = []
    for k in range(SECONDS * FPS):
        sheet = Image.new("RGB", (3 * PW + 4 * 6, PH + 12), (30, 32, 36))
        for i, (name, fr) in enumerate(runs):
            im = Image.fromarray((fr[k] * 255).astype(np.uint8), "RGB"); label(im, name, subs[i]); sheet.paste(im, (6 + i * (PW + 6), 6))
        frames.append(sheet)
    q = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    q[0].save(OUT / "firefly-H-v2-size.gif", save_all=True, append_images=q[1:], duration=int(1000 / FPS), loop=0, optimize=True)
    return list(zip([c[0] for c in cells], sizes))


def make_creature():
    R = ROOT / "_intake/firefly-stack/rp06/textures/sf/nba"
    body = Image.open(R / "entity/firefly.png").convert("RGBA"); glow = Image.open(R / "entity/firefly_glow.png").convert("RGBA")
    part = Image.open(R / "particle/firefly.png").convert("RGBA"); lant = Image.open(R / "particle/firefly_lantern.png").convert("RGBA")
    img = Image.new("RGB", (1020, 300), (22, 24, 28)); d = ImageDraw.Draw(img)
    d.text((10, 8), "StripMine (Naturalist) creature firefly — textures from RP-06/RP-07 (body 32², glow strip 30 frames, particles)", fill=(230, 230, 230), font=FONT_B)
    def paste(im, x, y, s, lab):
        big = im.resize((im.size[0] * s, im.size[1] * s), Image.NEAREST); bg = Image.new("RGBA", big.size, (8, 10, 14, 255)); bg.alpha_composite(big)
        img.paste(bg.convert("RGB"), (x, y)); d.text((x, y + big.size[1] + 4), lab, fill=(210, 210, 210), font=FONT)
    paste(body, 10, 40, 6, "body texture 32²")
    for k, fr in enumerate((0, 8, 15, 22, 29)):
        paste(glow.crop((0, 32 * fr, 32, 32 * fr + 32)), 220 + k * 150, 40, 4, f"glow frame {fr}")
    paste(part, 220, 200, 4, "light-burst particle 16²"); paste(lant, 400, 200, 2, "jar lantern particle")
    img.save(OUT / "firefly-E-creature.png")


if __name__ == "__main__":
    make_bushes(); print("A done")
    make_flyers(); print("B done")
    make_rhythm(); print("C done")
    make_colours(); print("D done")
    make_creature(); print("E done")
    _CACHE.clear(); make_closeup(); print("F done")
    for p in sorted(OUT.glob("firefly-*")):
        print(p.name, p.stat().st_size)

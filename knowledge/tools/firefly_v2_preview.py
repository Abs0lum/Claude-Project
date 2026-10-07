#!/usr/bin/env python3
"""firefly_v2_preview.py — side-by-side GIF: the approved simulation (H 'OURS v2 FINAL') vs the SHIPPED particle,
evaluated literally from RP-10 1.3.40's firefly_particle.particle.json with tools/molang_eval.py (degrees trig,
emitter state machine, parametric drift) and drawn with the shipped 128px sprite. Same spawn times and spawn points
in both panels, side view ~4 blocks away, 10 s loop. Output: _design/firefly-I-shipped-vs-approved.gif (+ still)."""
import json, random, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_eval as M
import firefly_compare as fc

ROOT = Path("/home/claude"); R10 = ROOT / "_build/rp10-140"
PE = json.loads((R10 / "particles/firefly_particle.particle.json").read_text())["particle_effect"]; C = PE["components"]
SPRITE = np.asarray(Image.open(R10 / "textures/particle/pw_firefly_v2.png").convert("RGBA")).astype(np.float32) / 255
HALF = C["minecraft:particle_appearance_billboard"]["size"][0]


class Shipped:
    """One emitter + its particle, stepped at 20 Hz exactly as the JSON says."""
    def __init__(self, x, y, rng):
        self.rng = rng; self.x0, self.y0 = x, y
        e = {f"v.emitter_random_{i}": rng.random() for i in range(1, 5)}
        e.update({f"v.particle_random_{i}": rng.random() for i in range(1, 5)}); e.update({"v.emitter_age": 0.0, "v.particle_age": 0.0})
        M.run(C["minecraft:emitter_initialization"]["creation_expression"], e, rng)
        e["v.particle_lifetime"] = M.run(C["minecraft:particle_lifetime_expression"]["max_lifetime"], e, rng)
        self.env = e
    @property
    def alive(self): return self.env["v.particle_age"] < self.env["v.particle_lifetime"]
    def step(self, dt):
        M.run(C["minecraft:emitter_initialization"]["per_update_expression"], self.env, self.rng)
        self.env["v.emitter_age"] += dt; self.env["v.particle_age"] += dt
    def pose(self):
        rel = C["minecraft:particle_motion_parametric"]["relative_position"]
        dx, dy = M.run(rel[0], self.env, self.rng), M.run(rel[1], self.env, self.rng)
        return self.x0 + dx, self.y0 + dy, M.run(C["minecraft:particle_appearance_tinting"]["color"][3], self.env, self.rng)


def run(seed=106):
    bg, gy = fc.background()
    sched = random.Random(seed); spawns = []; t = -15.0
    while t < fc.SECONDS:                                       # shared schedule: every ~1.4 s, same points
        spawns.append((t, sched.uniform(0.3, 5.0), sched.uniform(0.3, 1.6), sched.random())); t += sched.expovariate(1 / 1.4)
    appr, ship, frames, lit = [], [], [], []
    ma = fc.model_prop(random.Random(seed + 1), fc.V2_SCALE)
    si = 0; t = -15.0; dt = fc.DT / fc.SUB
    while t < fc.SECONDS:
        while si < len(spawns) and spawns[si][0] <= t:
            _, x, y, r = spawns[si]; si += 1
            f = ma["spawn"](t); f.x, f.y = x, y; appr.append(f); ship.append(Shipped(x, y, random.Random(int(r * 1e9))))
        for _ in range(fc.SUB):
            for f in appr:
                ma["step"](f, dt); f.x += f.vx * dt; f.y += f.vy * dt; f.age += dt
            for s in ship: s.step(dt)
            t += dt
        appr = [f for f in appr if f.age < f.life]; ship = [s for s in ship if s.alive]
        if t >= 0 and len(frames) < fc.SECONDS * fc.FPS:
            ca, cs = bg.copy(), bg.copy()
            for f in appr:
                cx, cy = fc.to_px(f.x, f.y, gy)
                for tex, half, col, a, add in ma["look"](f): fc.draw(ca, tex, cx, cy, half, col, a, add)
            for s in ship:
                x, y, a = s.pose(); cx, cy = fc.to_px(x, y, gy); fc.draw(cs, SPRITE, cx, cy, HALF, (1, 1, 1), a, False)
            frames.append((ca, cs))
            lit.append((sum(1 for f in appr if max(l[3] for l in ma["look"](f)) > 0.5), sum(1 for x in ship if x.pose()[2] > 0.5)))
    out = []
    for k, (ca, cs) in enumerate(frames):
        sheet = Image.new("RGB", (2 * fc.PW + 18, fc.PH + 12), (30, 32, 36))
        for i, (c, name, sub) in enumerate(((ca, "APPROVED  (H, OURS v2 FINAL)", "the simulation you picked"),
                                            (cs, "SHIPPED  (RP-10 1.3.40 file)", "evaluated from the particle JSON"))):
            im = Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)); fc.label(im, name, sub); sheet.paste(im, (6 + i * (fc.PW + 6), 6))
        out.append(sheet)
    q = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in out]
    q[0].save(fc.OUT / "firefly-I-shipped-vs-approved.gif", save_all=True, append_images=q[1:], duration=int(1000 / fc.FPS), loop=0, optimize=True)
    # the still = a TYPICAL moment: the frame where both panels sit closest to their own 10 s average of lit fireflies
    L = np.array(lit, float); dev = np.abs(L - L.mean(axis=0)).sum(axis=1)
    k = int(np.argmin(dev)); out[k].save(fc.OUT / "firefly-I-shipped-vs-approved-still.png")
    print(f"lit per moment (approved, shipped) mean {L.mean(axis=0).round(2).tolist()} · still at t={k / fc.FPS:.1f} s {lit[k]}")


if __name__ == "__main__":
    run(); print("I done")

#!/usr/bin/env python3
"""verify_rp02_204.py — gate for RP-02 v2.0.4 (smoke retune) + plume side-view simulation; packages on GATE OPEN."""
import json, sys, hashlib, zipfile, re
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); A, B = ROOT / "_build/rp02-203", ROOT / "_build/rp02-204"; DATE = "2026-09-22"
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
res = []
def check(n, ok, d=""): res.append((n, bool(ok))); print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {str(d)[:300]}"))
bad = []
for p in list(B.glob("particles/pw_*.json")) + [B / "manifest.json"]:
    try: load(p)
    except Exception as e: bad.append((p.name, str(e)[:60]))
check("A pw_* particles + manifest parse", not bad, bad)
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
h0, h1 = th(A), th(B); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
check("B diff vs v2.0.3: only pw_chimney_smoke, pw_hearth_puff, manifest changed; nothing added/removed", set(h0) == set(h1) and ch == {"particles/pw_chimney_smoke.json", "particles/pw_hearth_puff.json", "manifest.json"}, sorted(ch))
# Molang sanity: balanced parens, only known functions/variables
mbad = []
for n in ("pw_chimney_smoke", "pw_hearth_puff"):
    txt = json.dumps(load(B / f"particles/{n}.json"))
    for expr in re.findall(r'"(math\.[^"]*|[^"]*variable\.[^"]*)"', txt):
        if expr.count("(") != expr.count(")"): mbad.append((n, expr))
        for fn in re.findall(r"math\.(\w+)", expr):
            if fn not in ("random", "min", "max", "sin", "cos", "clamp"): mbad.append((n, fn))
        for v in re.findall(r"variable\.(\w+)", expr):
            if v not in ("particle_age", "particle_lifetime", "spin"): mbad.append((n, v))
check("C Molang: balanced, only math.random/min/... and variable.particle_age/particle_lifetime/spin", not mbad, mbad)
fb = lambda p: load(p)["particle_effect"]["components"]["minecraft:particle_appearance_billboard"]["uv"]
check("C flipbook + texture + material unchanged (Patrix big_smoke 12 frames)", all(fb(A / f"particles/{n}.json") == fb(B / f"particles/{n}.json") and load(A / f"particles/{n}.json")["particle_effect"]["description"] == load(B / f"particles/{n}.json")["particle_effect"]["description"] for n in ("pw_chimney_smoke", "pw_hearth_puff")))
# motion from the JSON: mean parameters, dv/dt = a - k v
def ev(x, lo=True):
    if isinstance(x, (int, float)): return (x, x)
    m = re.match(r"math\.random\(([-\d.]+),\s*([-\d.]+)\)(?:\s*\+\s*([-\d.]+))?", x)
    if m: a, b, c = float(m.group(1)), float(m.group(2)), float(m.group(3) or 0); return (a + c, b + c)
    return (float(x), float(x))
def params(p):
    c = load(p)["particle_effect"]["components"]
    v0 = ev(c["minecraft:particle_initial_speed"]); life = ev(c["minecraft:particle_lifetime_expression"]["max_lifetime"])
    acc = c["minecraft:particle_motion_dynamic"]["linear_acceleration"]; k = c["minecraft:particle_motion_dynamic"]["linear_drag_coefficient"]
    return v0, life, [ev(a) for a in acc], k
def rise(v0, a, k, T, dt=0.02):
    v, y, t, ys = v0, 0.0, 0.0, []
    while t < T: v += (a - k * v) * dt; y += v * dt; t += dt; ys.append(y)
    return y, np.array(ys)
rows = {}
for tag, root in (("v2.0.3", A), ("v2.0.4", B)):
    for n in ("pw_chimney_smoke", "pw_hearth_puff"):
        v0, life, acc, k = params(root / f"particles/{n}.json")
        lo = rise(v0[0], acc[1][0], k, life[0])[0]; hi = rise(v0[1], acc[1][1], k, life[1])[0]
        rows[(tag, n)] = (lo, hi, life)
        print(f"   {tag} {n}: rises {lo:.1f}-{hi:.1f} blocks over {life[0]:g}-{life[1]:g} s")
check("D chimney smoke rises >= 7 blocks at its shortest life (v2.0.3: %.1f)" % rows[("v2.0.3", "pw_chimney_smoke")][0], rows[("v2.0.4", "pw_chimney_smoke")][0] >= 7)
check("D hearth puff climbs >= 3.4 blocks at its shortest life, so it reaches a cottage chimney top (v2.0.3: %.1f)" % rows[("v2.0.3", "pw_hearth_puff")][0], rows[("v2.0.4", "pw_hearth_puff")][0] >= 3.4)
cp = load(B / "particles/pw_hearth_puff.json")["particle_effect"]["components"]
check("D hearth puff keeps expire-on-contact (ceilings of open fireplaces) and has zero sideways acceleration (stays in the flue)", cp["minecraft:particle_motion_collision"]["expire_on_contact"] is True and cp["minecraft:particle_motion_dynamic"]["linear_acceleration"][0] == 0 and cp["minecraft:particle_motion_dynamic"]["linear_acceleration"][2] == 0)
man = load(B / "manifest.json")["header"]
check("E manifest v2.0.4 + stamp, uuid unchanged", man["version"] == [2, 0, 4] and man["description"].startswith(f"v2.0.4 ({DATE})") and man["uuid"] == load(A / "manifest.json")["header"]["uuid"])
# side view: cottage (hearth at y 0, flue to y 5, chimney top 6), 60 simulated particles per version (mean motion + the random ranges)
rng = np.random.default_rng(7); TOP = 8.0   # chimney MOUTH 8 blocks above the hearth; the script spawns at (last flue block y) + 1.25 = mouth + 0.25
fig, axes = plt.subplots(1, 2, figsize=(10, 7), sharey=True, facecolor="#141416")
for ax, (tag, root) in zip(axes, (("v2.0.3 (now)", A), ("v2.0.4 (this ship)", B))):
    ax.set_facecolor("#1d2330"); ax.set_xlim(-4, 6); ax.set_ylim(-0.5, 22); ax.set_aspect("equal")
    ax.add_patch(plt.Rectangle((-3, 0), 6, 4, color="#7a5a3a", zorder=1)); ax.add_patch(plt.Polygon([(-3.5, 4), (0, 7.5), (3.5, 4)], color="#4a3a2a", zorder=1))
    ax.add_patch(plt.Rectangle((-0.5, 0), 1, TOP, color="#8a8a8a", zorder=2)); ax.add_patch(plt.Rectangle((-0.35, 0.05), 0.7, TOP - 0.05, color="#2a2a2a", zorder=2))
    ax.add_patch(plt.Rectangle((-0.4, 0.05), 0.8, 0.6, color="#ff8a1f"))
    for n, y0, col in (("pw_hearth_puff", 0.7, "#c9c2b5"), ("pw_chimney_smoke", TOP + 0.25, "#e6e0d4")):
        v0, life, acc, k = params(root / f"particles/{n}.json")
        for i in range(60 if n == "pw_chimney_smoke" else 40):
            T = rng.uniform(*life); vv = rng.uniform(*v0); ay = rng.uniform(*acc[1]); ax_ = rng.uniform(*acc[0]); dx = rng.uniform(-0.15, 0.15)
            _, ys = rise(vv, ay, k, T); _, xs = rise(dx * vv, ax_, k, T); t = np.linspace(0, 1, len(ys))
            ax.scatter(zorder=3, x=(xs[::15] + rng.uniform(-0.15, 0.15)), y=(y0 + ys[::15]), s=(8 + 60 * t[::15]) * (2 if n == "pw_chimney_smoke" else 1), color=col, alpha=0.06)
    lo, hi, life = rows[(tag.split()[0], "pw_chimney_smoke")]; plo, phi, plife = rows[(tag.split()[0], "pw_hearth_puff")]
    ax.set_title(f"{tag}\nchimney smoke {lo:.1f}-{hi:.1f} blocks above the top ({life[0]:g}-{life[1]:g} s)\nfire puff {plo:.1f}-{phi:.1f} blocks up the flue", color="#f0dca0", fontsize=10)
    ax.tick_params(colors="#bbbbbb"); ax.set_xlabel("blocks", color="#bbbbbb")
    for yy in range(0, 21, 2): ax.axhline(yy, color="#ffffff", alpha=0.05, lw=0.5)
axes[0].set_ylabel("blocks above the hearth", color="#bbbbbb")
fig.suptitle("Hearth smoke — simulated from the particle JSON (dv/dt = a - drag·v). Cottage: hearth at 0, chimney top at 8.", color="#dddddd", fontsize=11)
fig.savefig(OUT / "hearth-smoke-v2_0_4.png", dpi=110, facecolor=fig.get_facecolor()); plt.close(fig)
if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
out = OUT / "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_4.mcpack"
if out.exists(): out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(B.rglob("*")):
        if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
assert zh == th(B)
print(f"\nGATE OPEN — {len(res)} checks\n  {out.name} {out.stat().st_size:,} B md5 {hashlib.md5(out.read_bytes()).hexdigest()}")

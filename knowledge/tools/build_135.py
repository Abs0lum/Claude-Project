#!/usr/bin/env python3
"""build_135.py — RP-04 v1.3.134 -> v1.3.135: hearth fire flicker "more random and longer" (Abs0lum 17:03 CT).

The hearth flame flipbooks (pw_hearth_flame = Patrix fire_0, 30 frames; pw_hearth_flame_low = Patrix CTM tile 5, 30 frames)
played a straight 30-frame loop at 1 tick/frame = a 1.5 s cycle that visibly repeats.  Bedrock flipbook entries take an
explicit `frames` list (repeats allowed — vanilla fire uses them), so the loop becomes a seeded pseudo-random walk over the
30 frames: mostly forward steps (the flames keep rising), variable dwell (a frame held 1..3 ticks), occasional skips
(+2/+3) and short reversals (-1) for flicker, and rare jumps (a gust).  180 entries = 9 s before the pattern repeats.
Embers: slower — dwell 2..4, long holds, rare flares.  Texture strips untouched; RP-04 only.
"""
import json, random, re, shutil, datetime
from pathlib import Path
ROOT = Path("/home/claude"); SRC, DST = ROOT / "_build/rp04-134", ROOT / "_build/rp04-135"
VER = "1.3.135"; DATE = "2026-09-22"; LOG = ROOT / "_logs/phase_log.md"
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD 135 — {m}\n")
def jload(p): return json.loads(re.sub(r"//[^\n]*", "", Path(p).read_text(encoding="utf-8-sig")))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

def flicker_sequence(n_frames=30, length=180, seed=7, dwell=(1, 3), p_skip=0.18, p_reverse=0.10, p_jump=0.03, hold_bias=0.0):
    """seeded random walk over frame indices; returns a list of `length` frame numbers (repeats = dwell)."""
    rng = random.Random(seed); seq = []; f = rng.randrange(n_frames)
    while len(seq) < length:
        d = rng.randint(*dwell)
        if rng.random() < hold_bias: d += rng.randint(1, 2)
        seq += [f] * d
        r = rng.random()
        if r < p_jump: f = rng.randrange(n_frames)
        elif r < p_jump + p_reverse: f = (f - 1) % n_frames
        elif r < p_jump + p_reverse + p_skip: f = (f + rng.choice((2, 3))) % n_frames
        else: f = (f + 1) % n_frames
    return seq[:length]

LIT = flicker_sequence(30, 180, seed=7, dwell=(1, 3), p_skip=0.18, p_reverse=0.10, p_jump=0.03)
EMBERS = flicker_sequence(30, 180, seed=11, dwell=(2, 4), p_skip=0.08, p_reverse=0.12, p_jump=0.02, hold_bias=0.25)

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    p = DST / "textures/flipbook_textures.json"; fb = jload(p); n = 0
    for e in fb:
        if e.get("atlas_tile") == "pw_hearth_flame": e["frames"] = LIT; e["ticks_per_frame"] = 1; e["blend_frames"] = False; n += 1
        elif e.get("atlas_tile") == "pw_hearth_flame_low": e["frames"] = EMBERS; e["ticks_per_frame"] = 1; e["blend_frames"] = False; n += 1
    assert n == 2, n
    jdump(fb, p)
    man = jload(DST / "manifest.json")
    man["header"]["name"] = f"AbsolutRealism Basic RP v{VER}"
    man["header"]["description"] = (f"v{VER} ({DATE}) HEARTH FLICKER. The lit flame and the ember licks no longer play a straight 30-frame loop (1.5 s, visibly "
        f"repeating): each flipbook now walks a seeded pseudo-random 180-entry sequence over its 30 Patrix frames — mostly rising, frames held 1-3 ticks "
        f"(embers 2-4 with long holds), skips, short reversals and the odd gust — so the flicker is irregular and repeats only every 9 s. "
        f"flipbook_textures.json + manifest + ledger only; everything else byte-identical to v1.3.134. Pair with BP-02 v1.3.182 + RP-02 v2.0.3.")
    man["header"]["version"] = [1, 3, 135]
    for m in man["modules"]: m["version"] = [1, 3, 135]
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; t = led.read_text(encoding="utf-8"); t2 = t.replace("v1.3.134 ·", f"v{VER} ·", 1); assert t2 != t; led.write_text(t2, encoding="utf-8")
    json.dump({"lit": LIT, "embers": EMBERS}, open(ROOT / "_logs/flicker_135.json", "w"))
    log(f"tree rp04-135 built: hearth flipbooks re-sequenced (lit {len(LIT)} entries, embers {len(EMBERS)}), manifest + ledger stamped")

if __name__ == "__main__":
    main()
    import collections
    for name, s in (("lit", LIT), ("embers", EMBERS)):
        steps = collections.Counter((b - a) % 30 for a, b in zip(s, s[1:]) if a != b)
        runs = collections.Counter(); k = 1
        for a, b in zip(s, s[1:]):
            if a == b: k += 1
            else: runs[k] += 1; k = 1
        print(name, "len", len(s), "distinct", len(set(s)), "dwell histogram", dict(sorted(runs.items())), "step histogram", dict(sorted(steps.items())))

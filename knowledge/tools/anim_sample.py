#!/usr/bin/env python3
"""anim_sample.py — sample a Bedrock animation clip at time t into plain numbers (p22 retarget gates, 10-01).

Channel forms handled (rotation / position / scale of one bone):
  number or Molang string  -> broadcast to all three axes
  [x, y, z]                -> each a number or Molang string
  {"0.0": v, "0.5": v, …}  -> keyframes; v = any of the above or {"pre": v, "post": v, "lerp_mode": …}
Between two keyframes the value runs LINEARLY from the earlier key's `post` to the later key's `pre` (catmullrom is drawn as
linear: close enough for contact / explosion gates, never used for the delivered motion). Before the first key: its `pre`;
after the last: its `post`.
Molang is evaluated with molang_eval against `env`; q.anim_time / q.life_time are set to t unless env gives them.
API: sample_clip(clip, t, env) -> {bone: {"rotation": [3], "position": [3], "scale": [3]}}; clip_length(clip) -> seconds."""
import sys

sys.path.insert(0, "/home/claude/tools")
import molang_eval as ME  # noqa: E402


def _vec(v, env):
    """value -> [x, y, z] floats."""
    if isinstance(v, dict):                       # {"pre": …, "post": …}: callers pick the side before this
        v = v.get("post", v.get("pre", 0))
    if isinstance(v, (int, float, str)):
        x = ME.run(v, dict(env)) if isinstance(v, str) else float(v)
        return [x, x, x]
    out = []
    for k in range(3):
        x = v[k] if k < len(v) else 0
        out.append(ME.run(x, dict(env)) if isinstance(x, str) else float(x))
    return out


def _side(v, side):
    if isinstance(v, dict) and ("pre" in v or "post" in v):
        return v.get(side, v.get("post" if side == "pre" else "pre"))
    return v


def sample_channel(ch, t, env):
    if not isinstance(ch, dict):
        return _vec(ch, env)
    keys = sorted(((float(k), v) for k, v in ch.items()), key=lambda kv: kv[0])
    if t <= keys[0][0]:
        return _vec(_side(keys[0][1], "pre"), env)
    if t >= keys[-1][0]:
        return _vec(_side(keys[-1][1], "post"), env)
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            a = _vec(_side(v0, "post"), env)
            b = _vec(_side(v1, "pre"), env)
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return [a[i] + (b[i] - a[i]) * u for i in range(3)]
    return _vec(_side(keys[-1][1], "post"), env)


def clip_length(clip):
    if clip.get("animation_length"):
        return float(clip["animation_length"])
    last = 0.0
    for ch in (clip.get("bones") or {}).values():
        for v in ch.values():
            if isinstance(v, dict):
                try:
                    last = max(last, max(float(k) for k in v))
                except ValueError:
                    pass
    return last if last > 0 else 1.0


def sample_clip(clip, t, env=None):
    env = dict(env or {})
    env.setdefault("q.anim_time", t)
    env.setdefault("q.life_time", t)
    out = {}
    for bone, ch in (clip.get("bones") or {}).items():
        o = {}
        for c in ("rotation", "position", "scale"):
            if c in ch:
                o[c] = sample_channel(ch[c], t, env)
        out[bone] = o
    return out

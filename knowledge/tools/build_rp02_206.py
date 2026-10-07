#!/usr/bin/env python3
"""build_rp02_206.py — RP-02 Atmospheric Effects v2.0.6 = LIGHTING builds A + B (his 18:55 L3 = a; "light-handed with
saturation — biomes are supposed to have higher than normal saturation") + the saturation A/B test pack.

Mechanism (research 18:2x, D-C422 journal; Mojang vanilla JSON + MS Learn): five settings brighter than vanilla —
shadows grade gain 1.15 + gamma 2.5 (lifts blacks like a TV 'Brightness' control), the sun at noon level until late
afternoon and 175 lux just before sunset, ACES + contrast 1.25, stacked gains (+11 % in brights), saturation 1.10.

BUILD A — colour grade (overworld default + the cherry / pale biome grades; Nether / End untouched):
  tone_mapping aces -> generic (Mojang's) · midtone contrast -> 1.12 (pale 1.15) · gains -> 1.0 (cherry keeps its pink tint
  RATIO, scaled down) · highlights contrast 1.05, gain 1.0 · shadows contrast 1.10, gain 1.0, gamma 2.2 (neutral) ·
  default temperature 6000 -> 6300 K.
  SATURATION (light hand): overworld default midtones 1.10 -> 1.06; every biome grade keeps its saturation as it is.
BUILD B — sun curve (default, cherry, pale lighting): noon stays 150 lux, falls through the afternoon like vanilla
  (0.36x of noon at 0.20, 0.2x at 0.23 — vanilla 0.36x / 0.23x), sunrise mirrors sunset; moon 1.0 -> 0.5 (pale keeps its own
  moon); ambient 0.05 -> 0.02 (pale keeps its own). Sun / moon colours unchanged.
TEST PACK — "PW-LightTest Saturation-NOW" RP 1.0.0: only color_grading/color_grading.json = the new grade with the OLD
  saturation (1.10) — on top of the stack = today's saturation, off = the new one (same world, same moment)."""
import json
import re
import shutil
import uuid
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST = ROOT / "_build/rp02-205", ROOT / "_build/rp02-206"
TEST = ROOT / "_build/lighttest-sat-100"
VER = [2, 0, 6]
SUN = {"0.00": 150, "0.05": 150, "0.10": 120, "0.15": 85, "0.20": 50, "0.23": 30, "0.25": 12, "0.26": 3, "0.28": 0,
       "0.72": 0, "0.74": 3, "0.75": 12, "0.77": 30, "0.80": 50, "0.85": 85, "0.90": 120, "0.95": 150}


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def jw(p, d):
    p.write_text(json.dumps(d, indent=2))


def v3(x):
    return [round(float(x), 3)] * 3


def grade(d, kind):
    g = d["minecraft:color_grading_settings"]
    cg = g["color_grading"]
    g["tone_mapping"] = {"operator": "generic"}
    if kind == "pale":
        d["format_version"] = "1.21.90"     # 'generic' + this schema as in the default grade (pale was 1.21.40)
    mid, hi, sh = cg["midtones"], cg.get("highlights", {}), cg.get("shadows", {})
    mid["contrast"] = v3(1.15 if kind == "pale" else 1.12)
    if kind == "cherry":       # keep the pink tint ratio [1.05, 1.0, 1.05], scaled so the brightest channel is 1.0
        mid["gain"] = [round(x / max(mid["gain"]), 3) for x in mid["gain"]]
        hi["gain"] = [round(x / max(hi["gain"]), 3) for x in hi["gain"]]
    else:
        mid["gain"] = v3(1.0)
        if hi:
            hi["gain"] = v3(1.0)
    if hi:
        hi["contrast"] = v3(1.05)
    if sh:
        sh["contrast"] = v3(1.10)
        sh["gain"] = v3(1.0)
        sh["gamma"] = v3(2.2)
    if kind == "default":
        mid["saturation"] = v3(1.06)
        cg["temperature"]["temperature"] = 6300.0
    return d


def lighting(d, kind):
    ls = d["minecraft:lighting_settings"]
    ls["directional_lights"]["orbital"]["sun"]["illuminance"] = dict(SUN)
    if kind != "pale":
        moon = ls["directional_lights"]["orbital"]["moon"]["illuminance"]
        for k, v in list(moon.items()):
            if v:
                moon[k] = 0.5
        ls["ambient"]["illuminance"] = 0.02
    return d


def main():
    assert not DST.exists() and not TEST.exists(), "never rebuild a build dir"
    shutil.copytree(SRC, DST)
    report = {}
    for f, kind in (("color_grading.json", "default"), ("cherry_color_grading.json", "cherry"), ("pale_color_grading.json", "pale")):
        p = DST / "color_grading" / f
        before = jl(p)
        after = grade(jl(p), kind)
        jw(p, after)
        report[f] = {"before": before["minecraft:color_grading_settings"], "after": after["minecraft:color_grading_settings"]}
    for f, kind in (("global.json", "default"), ("cherry.json", "cherry"), ("pale.json", "pale")):
        p = DST / "lighting" / f
        jw(p, lighting(jl(p), kind))
    m = jl(DST / "manifest.json")
    old = ".".join(map(str, m["header"]["version"]))
    m["header"]["version"] = VER
    for mod in m["modules"]:
        mod["version"] = VER
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v2.0.6", m["header"]["name"])
    m["header"]["description"] = ("v2.0.6 (2026-10-01) LIGHTING A + B: Mojang's 'generic' tone mapping, neutral shadows "
                                  "(no lifted blacks), no stacked gains, contrast 1.12; overworld saturation 1.10 -> 1.06 "
                                  "(biome grades keep theirs); the sun falls through the afternoon like vanilla (noon stays "
                                  f"150 lux); moon 0.5, ambient 0.02. Includes all of v{old}.")
    jw(DST / "manifest.json", m)
    # the saturation A/B test pack
    (TEST / "color_grading").mkdir(parents=True)
    now = jl(DST / "color_grading/color_grading.json")
    now["minecraft:color_grading_settings"]["color_grading"]["midtones"]["saturation"] = v3(1.10)
    jw(TEST / "color_grading/color_grading.json", now)
    tm = {"format_version": 2, "header": {
        "name": "PW-LightTest Saturation-NOW v1.0.0",
        "description": "TEST ONLY (10-01): put it ABOVE RP-02 2.0.6 = today's overworld saturation (1.10) with the new grade; "
                       "take it off = the new saturation (1.06). Everything else identical. Not for normal play.",
        "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 120]},
        "modules": [{"description": "saturation A/B", "type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0]}]}
    jw(TEST / "manifest.json", tm)
    if (SRC / "pack_icon.png").exists():
        shutil.copy2(SRC / "pack_icon.png", TEST / "pack_icon.png")
    (ROOT / "_docs/lighting").mkdir(parents=True, exist_ok=True)
    (ROOT / "_docs/lighting/RP02-206-GRADE.json").write_text(json.dumps(report, indent=1))
    print("built", DST.name, "and", TEST.name)


if __name__ == "__main__":
    main()

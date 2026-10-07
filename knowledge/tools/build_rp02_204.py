#!/usr/bin/env python3
"""build_rp02_204.py — RP-02 v2.0.4: hearth smoke rises higher and lasts longer (Abs0lum 19:46).
Numbers (integrated dv/dt = a - drag*v, D-C225):
  pw:chimney_smoke  v2.0.3 rises 1.8-2.5 blocks over 5-8 s  ->  v2.0.4 7.8-11.5 blocks over 12-18 s, ~1 block downwind drift,
                    billboard grows 0.6 -> 2.6 (capped), fade-in 6 %, hold, long fade from 45 % to 100 % of life.
  pw:hearth_puff    v2.0.3 dies 0.9-1.6 blocks above the fire (never reaches the chimney top)  ->  v2.0.4 climbs 3.5-6 blocks
                    straight up the flue (no sideways drift so it stays inside the shaft), size capped 0.7 so it never pokes
                    through a 1-block flue's outer face; still expires on contact with a ceiling (open fireplaces).
pw:room_smoke and every other file unchanged."""
import json, shutil, datetime
from pathlib import Path
ROOT = Path("/home/claude"); SRC, DST = ROOT / "_build/rp02-203", ROOT / "_build/rp02-204"; VER = "2.0.4"; DATE = "2026-09-22"
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
def log(m):
    print(m); open(ROOT / "_logs/phase_log.md", "a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD RP-02 {VER} — {m}\n")

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    p = DST / "particles/pw_chimney_smoke.json"; d = jload(p); c = d["particle_effect"]["components"]
    c["minecraft:emitter_shape_point"]["direction"] = ["math.random(-0.15, 0.15)", 1.0, "math.random(-0.15, 0.15)"]
    c["minecraft:particle_initial_speed"] = 0.7
    c["minecraft:particle_lifetime_expression"] = {"max_lifetime": "math.random(12, 18)"}
    c["minecraft:particle_motion_dynamic"] = {"linear_acceleration": ["math.random(-0.03, 0.03) + 0.03", 0.22, "math.random(-0.03, 0.03)"], "linear_drag_coefficient": 0.35}
    sz = "math.min(0.6 + 0.14 * variable.particle_age, 2.6)"
    c["minecraft:particle_appearance_billboard"]["size"] = [sz, sz]
    c["minecraft:particle_appearance_tinting"]["color"]["gradient"] = {"0.0": "#00A8A49E", "0.06": "#B4A8A49E", "0.45": "#90B0ACA6", "0.8": "#50B4B0AA", "1.0": "#00B8B4AE"}
    jdump(d, p); log("pw:chimney_smoke: v0 0.7, a_y 0.22, drag 0.35, life 12-18 s -> rises 7.8-11.5 blocks (was 1.8-2.5), drift ~1 block, size cap 2.6, long fade")
    p = DST / "particles/pw_hearth_puff.json"; d = jload(p); c = d["particle_effect"]["components"]
    c["minecraft:emitter_shape_point"]["direction"] = ["math.random(-0.05, 0.05)", 1.0, "math.random(-0.05, 0.05)"]
    c["minecraft:particle_initial_speed"] = "math.random(0.4, 0.65)"
    c["minecraft:particle_lifetime_expression"] = {"max_lifetime": "math.random(6, 9)"}
    c["minecraft:particle_motion_dynamic"] = {"linear_acceleration": [0, 0.3, 0], "linear_drag_coefficient": 0.45}
    sz = "math.min(0.35 + 0.1 * variable.particle_age, 0.7)"
    c["minecraft:particle_appearance_billboard"]["size"] = [sz, sz]
    jdump(d, p); log("pw:hearth_puff: v0 0.4-0.65, a_y 0.30, drag 0.45, life 6-9 s -> climbs 3.5-6 blocks up the flue (was 0.9-1.6), no lateral drift, size cap 0.7")
    man = jload(DST / "manifest.json"); vv = [int(x) for x in VER.split(".")]
    man["header"]["version"] = vv
    for m in man["modules"]: m["version"] = vv
    if "name" in man["header"]: man["header"]["name"] = man["header"]["name"].replace("2.0.3", VER)
    man["header"]["description"] = (f"v{VER} ({DATE}) HEARTH SMOKE HIGHER + LONGER (Abs0lum 19:46: 'can we get smoke from our fireplace to travel higher'). "
        "pw:chimney_smoke now rises ~8-11 blocks over 12-18 s with a slow downwind drift and a long fade (was ~2 blocks over 5-8 s); "
        "pw:hearth_puff now climbs 3.5-6 blocks straight up the flue so the fire's own smoke reaches the chimney top (was dying ~1-1.5 blocks above the fire). "
        "Particle JSON only; the emitting script (BP-02 pw_homestead.js) is unchanged. Everything else byte-identical to v2.0.3. Pair with BP-02 v1.3.184 + RP-04 v1.3.138.")
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"
    if led.exists():
        t = led.read_text(encoding="utf-8"); t2 = t.replace("v2.0.3 ·", f"v{VER} ·", 1); led.write_text(t2, encoding="utf-8")
    log(f"manifest v{VER}")

if __name__ == "__main__":
    main()

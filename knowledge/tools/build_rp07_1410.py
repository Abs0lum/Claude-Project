#!/usr/bin/env python3
"""build_rp07_1410.py — RP-07 v1.4.10: the wandering trader's llamas get their BODY back.
Mechanism (D-C225): v1.4.9 bound entity/trader_llama to ONE texture, textures/entity/llama/trader_llama.png, which is
pixel-identical to equipment/llama_body/trader_llama.png — the decor layer (4.9 % opaque). The Patrix body variants
(creamy/white/brown/gray, 1024x512, 40.4 % opaque) share the model's UV layout (body at 41,11; fur/decor shells at 93,*),
so each trader variant = body variant with the decor composited over it. Four new textures + variant-array controller."""
import json, shutil, hashlib
from pathlib import Path
from PIL import Image
ROOT = Path("/home/claude"); SRC, DST = ROOT / "_build/rp07-149", ROOT / "_build/rp07-1410"; VER = "1.4.10"; DATE = "2026-09-22"
LOG = ROOT / "_logs/phase_log.md"
def log(m):
    import datetime
    print(m); open(LOG, "a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD RP-07 {VER} — {m}\n")
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
VARIANTS = ["creamy", "white", "brown", "gray"]      # query.variant 0..3 (vanilla trader_llama.json variants 0..3, same order as llama)

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    L = DST / "textures/entity/llama"
    decor = Image.open(L / "trader_llama.png").convert("RGBA")
    for v in VARIANTS:
        body = Image.open(L / f"{v}.png").convert("RGBA")
        assert body.size == decor.size == (1024, 512), (v, body.size, decor.size)
        out = body.copy(); out.alpha_composite(decor)
        out.save(L / f"trader_llama_{v}.png", optimize=True)
    log("4 composites textures/entity/llama/trader_llama_{creamy,white,brown,gray}.png = Patrix body variant + trader decor (alpha over)")
    ent = jload(DST / "entity/trader_llama.entity.json"); d = ent["minecraft:client_entity"]["description"]
    d["textures"] = {"default": "textures/entity/llama/trader_llama_creamy", **{f"variant_{i}": f"textures/entity/llama/trader_llama_{v}" for i, v in enumerate(VARIANTS)}}
    jdump(ent, DST / "entity/trader_llama.entity.json")
    rc = {"format_version": "1.10.0", "render_controllers": {"controller.render.pw_trader_llama": {
        "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
        "arrays": {"textures": {"Array.variants": [f"Texture.variant_{i}" for i in range(4)]}},
        "textures": ["Array.variants[math.clamp(query.variant, 0, 3)]"]}}}
    jdump(rc, DST / "render_controllers/pw_trader_llama.render.json")
    log("entity/trader_llama: textures default + variant_0..3 -> the composites; controller.render.pw_trader_llama picks Array.variants[query.variant] (pw_llama pattern)")
    tl = DST / "textures/textures_list.json"
    if tl.exists():
        lst = jload(tl); add = [f"textures/entity/llama/trader_llama_{v}" for v in VARIANTS]
        lst = sorted(set(lst) | set(add)); tl.write_text(json.dumps(lst, indent=1) + "\n", encoding="utf-8")
    led = DST / "PW-DEPENDENCIES.md"; t = led.read_text(encoding="utf-8")
    rows = "".join(f"| texture_path | `textures/entity/llama/trader_llama_{v}.png` | SELF |\n" for v in VARIANTS)
    anchor = "| texture_path | `textures/entity/llama/trader_llama.png` | SELF |\n"
    assert anchor in t; t = t.replace(anchor, anchor + rows, 1)
    t = t.replace("needs-hash STALE until depscan.py regenerates it.**", f"needs-hash STALE until depscan.py regenerates it.** **v{VER} amendment ({DATE}): 4 trader_llama_<variant> texture rows added by hand (still STALE).**", 1)
    led.write_text(t, encoding="utf-8")
    man = jload(DST / "manifest.json"); vv = [int(x) for x in VER.split(".")]
    man["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"; man["header"]["version"] = vv
    for m in man["modules"]: m["version"] = vv
    man["header"]["description"] = (f"v{VER} ({DATE}) TRADER LLAMA BODIES — Abs0lum witnessed (19:46) the trader's llamas invisible except the decor. "
        "Cause: v1.4.9 bound entity/trader_llama to textures/entity/llama/trader_llama.png, which is the DECOR layer only (pixel-identical to "
        "equipment/llama_body/trader_llama.png, 4.9% opaque) -> the body alpha-tested away. Fix: trader_llama_<creamy|white|brown|gray>.png = the Patrix "
        "body variant with the trader decor composited over it (same UV layout), bound as variant_0..3 and picked by query.variant (pw_llama pattern). "
        "Nothing else touched (v1.4.9 + 4 textures, entity, controller, textures_list, ledger rows).")
    jdump(man, DST / "manifest.json")
    log(f"manifest v{VER}; textures_list + ledger rows (+4)")

if __name__ == "__main__":
    main()
